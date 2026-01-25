import pytest
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlmodel import SQLModel
from src.core.database import (
    init_db, 
    get_user_reliability, 
    update_user_reliability, 
    set_slack_id, 
    set_git_email, 
    get_user_by_git_email
)
from src.schemas.agents import UserHistory
from src.core.config import settings

# Test Database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///test_commitguard.db"

@pytest.fixture(autouse=True, scope="function")
async def setup_test_db():
    # Override settings for testing
    original_url = settings.DATABASE_URL
    settings.DATABASE_URL = TEST_DATABASE_URL
    
    from src.core import database
    original_engine = database.engine
    original_session_local = database.AsyncSessionLocal
    
    database.engine = create_async_engine(TEST_DATABASE_URL)
    database.AsyncSessionLocal = async_sessionmaker(
        bind=database.engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    
    async with database.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        
    yield
    
    async with database.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    await database.engine.dispose()
    database.engine = original_engine
    database.AsyncSessionLocal = original_session_local
    settings.DATABASE_URL = original_url
    
    if os.path.exists("test_commitguard.db"):
        os.remove("test_commitguard.db")

@pytest.mark.asyncio
async def test_database_init():
    await init_db()

@pytest.mark.asyncio
async def test_user_reliability_flow():
    user_id = "u1"
    
    # 1. Initial
    score, slack_id = await get_user_reliability(user_id)
    assert score == 100.0
    
    # 2. Add as new user with failure (covers line 56)
    await update_user_reliability(user_id, was_failure=True)
    score, _ = await get_user_reliability(user_id)
    assert score == 0.0
    
    # 3. Success for existing user (covers line 60)
    await update_user_reliability(user_id, was_failure=False)
    score, _ = await get_user_reliability(user_id)
    assert score == 50.0
    
    # 4. Failure for existing user (covers line 62)
    await update_user_reliability(user_id, was_failure=True)
    score, _ = await get_user_reliability(user_id)
    # 2 failures, 1 success -> 1/3 * 100 = 33.33
    assert 33.3 <= score <= 33.4

@pytest.mark.asyncio
async def test_set_slack_id():
    user_id = "u1"
    # Set for new user
    await set_slack_id(user_id, "s1")
    _, s_id = await get_user_reliability(user_id)
    assert s_id == "s1"
    
    # Update existing
    await set_slack_id(user_id, "s2")
    _, s_id = await get_user_reliability(user_id)
    assert s_id == "s2"

@pytest.mark.asyncio
async def test_git_email_flow():
    user_id = "u1"
    email = "test@example.com"
    
    # Set for new user
    await set_git_email(user_id, email)
    user = await get_user_by_git_email(email)
    assert user.user_id == user_id
    assert user.git_email == email
    
    # Update existing
    await set_git_email(user_id, "other@example.com")
    user = await get_user_by_git_email("other@example.com")
    assert user.git_email == "other@example.com"
    
    # Get non-existent
    user = await get_user_by_git_email("nonexistent@example.com")
    assert user is None
