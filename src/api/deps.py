# Copyright (c) 2026 CommitVigil AI. All rights reserved.
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from src.core.config import settings
from src.core.logging import logger
from src.core.state import state
from arq import ArqRedis

# Define the scheme but don't auto-error yet, we handle logic manually
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(
    api_key_header: str | None = Security(api_key_header),
) -> str | None:
    """
    Enforces API Key Authentication based on settings.
    PROD: Mandatory.
    DEV: Configurable via AUTH_ENABLED.
    """
    if not settings.AUTH_ENABLED:
        logger.warning(
            "authentication_bypass", status="disabled_in_config", mode="dev_unsafe"
        )
        return None

    if not api_key_header:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing Authentication Header (X-API-Key)",
        )

    import secrets

    if not secrets.compare_digest(api_key_header, settings.API_KEY_SECRET):
        logger.warning("authentication_failed", reason="invalid_key")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )

    return api_key_header

async def get_redis() -> ArqRedis:
    """Dependency to inject Redis pool."""
    redis = state.get("redis")
    if not redis:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Redis service unavailable"
        )
    return redis
