import os
import sys
import pytest
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from src.core.config import settings
from src.core import database

# Mock FastAPILimiter globally for all tests
@pytest.fixture(autouse=True, scope="session")
def mock_limiter():
    from fastapi_limiter import FastAPILimiter
    mock_redis = AsyncMock()
    # Mock the _check method which is called during __call__
    mock_redis.evalsha = AsyncMock(return_value=0) 
    mock_redis.script_load = AsyncMock(return_value="sha")
    
    with patch("fastapi_limiter.FastAPILimiter.redis", new=mock_redis):
        with patch("fastapi_limiter.FastAPILimiter.identifier", new=AsyncMock(return_value="test-user")):
            with patch("fastapi_limiter.FastAPILimiter.http_callback", new=AsyncMock()):
                yield




# Test Database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///test_commitvigil.db"


def pytest_addoption(parser):
    parser.addoption(
        "--run-live", action="store_true", default=False, help="run live integration tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "live: mark test as a live integration test")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-live"):
        # --run-live given in cli: do not skip live tests
        return
    skip_live = pytest.mark.skip(reason="need --run-live option to run")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


@pytest.fixture(autouse=True, scope="session")
def override_db_url(request):
    """Override database URL for the entire test session."""
    run_live = request.config.getoption("--run-live")
    
    original_url = settings.DATABASE_URL
    original_llm_provider = settings.LLM_PROVIDER
    original_openai_key = settings.OPENAI_API_KEY
    original_groq_key = settings.GROQ_API_KEY
    
    settings.DATABASE_URL = TEST_DATABASE_URL
    
    if not run_live:
        settings.LLM_PROVIDER = "mock"
        settings.OPENAI_API_KEY = None # Ensure no keys trigger auto-detection
        settings.GROQ_API_KEY = None
    
    with patch("src.main.FastAPILimiter.init", new_callable=AsyncMock):
        yield

    
    settings.DATABASE_URL = original_url
    if not run_live:
        settings.LLM_PROVIDER = original_llm_provider
        settings.OPENAI_API_KEY = original_openai_key
        settings.GROQ_API_KEY = original_groq_key


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

    if "src.agents.learning" in sys.modules:
        import src.agents.learning
        src.agents.learning.AsyncSessionLocal = new_session_local

    if "src.api.v1.reports" in sys.modules:
        import src.api.v1.reports
        src.api.v1.reports.AsyncSessionLocal = new_session_local

    if "src.api.v1.evaluation" in sys.modules:
        import src.api.v1.evaluation
        src.api.v1.evaluation.AsyncSessionLocal = new_session_local

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

    if os.path.exists("test_commitvigil.db"):
        try:
            os.remove("test_commitvigil.db")
        except PermissionError:
            pass
