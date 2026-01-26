import os
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from src.core.config import settings
from src.core import database

# Test Database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///test_commitguard.db"


@pytest.fixture(autouse=True, scope="session")
def override_db_url():
    """Override database URL for the entire test session."""
    original_url = settings.DATABASE_URL
    settings.DATABASE_URL = TEST_DATABASE_URL
    yield
    settings.DATABASE_URL = original_url


@pytest.fixture(autouse=True)
async def setup_test_db():
    """Initialize test database before each test."""
    # Ensure database engine and session maker use the test URL
    original_engine = database.engine
    original_session_local = database.AsyncSessionLocal

    database.engine = create_async_engine(TEST_DATABASE_URL)
    new_session_local = async_sessionmaker(
        bind=database.engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    database.AsyncSessionLocal = new_session_local

    # Patch src.agents.learning if it's already imported
    import sys

    if "src.agents.learning" in sys.modules:
        import src.agents.learning

        src.agents.learning.AsyncSessionLocal = new_session_local

    async with database.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield

    async with database.engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await database.engine.dispose()
    database.engine = original_engine
    database.AsyncSessionLocal = original_session_local

    if "src.agents.learning" in sys.modules:
        import src.agents.learning

        src.agents.learning.AsyncSessionLocal = original_session_local

    if os.path.exists("test_commitguard.db"):
        try:
            os.remove("test_commitguard.db")
        except PermissionError:
            pass
