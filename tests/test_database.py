import pytest
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from src.core.database import init_db, get_user_reliability, update_user_reliability, set_slack_id
from src.core.config import settings

# Test Database URL (using async sqlite for tests to avoid needing a live postgres container during local pytest runs)
TEST_DATABASE_URL = "sqlite+aiosqlite:///test_commitguard.db"

@pytest.fixture(autouse=True, scope="function")
async def setup_test_db():
    """
    Ensure we use a separate test database file and SQLModel handles creation.
    """
    # Override settings for testing
    original_url = settings.DATABASE_URL
    settings.DATABASE_URL = TEST_DATABASE_URL
    
    # We need a new engine for the test URL
    from src.core import database
    original_engine = database.engine
    database.engine = create_async_engine(TEST_DATABASE_URL)
    
    # Create tables
    async with database.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        
    yield
    
    # Cleanup
    async with database.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    await database.engine.dispose()
    database.engine = original_engine
    settings.DATABASE_URL = original_url
    
    if os.path.exists("test_commitguard.db"):
        os.remove("test_commitguard.db")

@pytest.mark.asyncio
async def test_database_init():
    # init_db is already called by the fixture, but we can verify it runs without error
    await init_db()

@pytest.mark.asyncio
async def test_user_reliability_flow():
    user_id = "test_db_user"
    
    # 1. Initial score should be 100
    score, slack_id = await get_user_reliability(user_id)
    assert score == 100.0
    assert slack_id is None
    
    # 2. Update with failure
    await update_user_reliability(user_id, was_failure=True)
    score, _ = await get_user_reliability(user_id)
    assert score == 0.0
    
    # 3. Update with success (1 success, 1 failure = 50%)
    await update_user_reliability(user_id, was_failure=False)
    score, _ = await get_user_reliability(user_id)
    assert score == 50.0

@pytest.mark.asyncio
async def test_set_slack_id():
    user_id = "johndoe"
    slack_id = "U12345"
    
    await set_slack_id(user_id, slack_id)
    _, saved_slack_id = await get_user_reliability(user_id)
    assert saved_slack_id == slack_id
