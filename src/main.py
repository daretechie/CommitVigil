# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from sqlalchemy import text

from src.api.v1.router import api_router
from src.core.config import settings
from src.core.database import engine, init_db
from src.core.logging import logger, setup_logging
from src.core.slack import SlackConnector
from src.core.state import state


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # XSS protection (legacy but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Content Security Policy (strict default)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
        # Enable HSTS in production (requires HTTPS)
        if not settings.DEMO_MODE:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

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
        await FastAPILimiter.init(state["redis"])
        logger.info("redis_connected", url=settings.REDIS_URL)

    except Exception as e:
        logger.warning("redis_connection_failed", error=str(e), mode="local_dev")
        state["redis"] = None  # Continue without Redis

    yield

    # Cleanup
    if state["redis"]:
        await state["redis"].close()
    
    await SlackConnector.close()
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

# Security Headers Middleware (CSP, X-Frame-Options, etc.)
app.add_middleware(SecurityHeadersMiddleware)

# Include the new authenticated router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Instrument for Prometheus Metrics
instrumentator = Instrumentator()
# In production, we protect the metrics endpoint with our standard API Key
instrumentator.instrument(app)

from src.api.deps import get_api_key
from fastapi import Depends

@app.get("/metrics", dependencies=[Depends(get_api_key)], include_in_schema=False)
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


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
