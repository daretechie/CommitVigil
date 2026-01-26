from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from src.core.config import settings
from src.core.logging import logger

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

    if api_key_header != settings.API_KEY_SECRET:
        logger.warning("authentication_failed", reason="invalid_key")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key",
        )

    return api_key_header
