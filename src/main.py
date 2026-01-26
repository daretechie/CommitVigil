from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text

from src.api.routes import router as api_router
from src.core.config import settings
from src.core.database import engine, init_db
from src.core.logging import logger, setup_logging

from src.core.state import state

# Initialize Logging
setup_logging()


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):  # noqa: ARG001
    """
    Modern lifespan management for Enterprise FastAPI apps.
    Handles startup and shutdown logic.
    """
    logger.info("application_startup", status="initializing_resources")

    # Initialize DB
    await init_db()

    # Initialize Redis Pool (Optional for local dev)
    try:
        # We access state via the global variable for now, to ensure compatibility with routes
        # consuming it from this module.
        state["redis"] = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
        logger.info("redis_connected", url=settings.REDIS_URL)
    except Exception as e:
        logger.warning("redis_connection_failed", error=str(e), mode="local_dev")
        state["redis"] = None  # Continue without Redis

    yield

    # Cleanup
    if state["redis"]:
        await state["redis"].close()
    logger.info("application_shutdown", status="cleaning_up")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set up CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include the new authenticated router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Instrument for Prometheus Metrics
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)


@app.get("/health")
async def health_check():
    health: dict[str, str | dict[str, str]] = {
        "status": "ok",
        "app": settings.PROJECT_NAME,
        "dependencies": {},
    }
    dependencies = health["dependencies"]
    assert isinstance(dependencies, dict)

    # Check Database
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        dependencies["database"] = "healthy"
    except Exception as e:
        logger.error("health_check_failed", dependency="database", error=str(e))
        dependencies["database"] = "unhealthy"
        health["status"] = "degraded"

    # Check Redis
    if state["redis"]:
        try:
            await state["redis"].ping()
            dependencies["redis"] = "healthy"
        except Exception as e:
            logger.error("health_check_failed", dependency="redis", error=str(e))
            dependencies["redis"] = "unhealthy"
            health["status"] = "degraded"
    else:
        dependencies["redis"] = "not_initialized"
        health["status"] = "degraded"

    return health


@app.get("/")
async def root():
    msg = f"Welcome to {settings.PROJECT_NAME}. Visit /docs for API documentation."
    return {"message": msg}
