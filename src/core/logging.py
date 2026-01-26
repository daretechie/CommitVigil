import logging
import sys
import structlog
from src.core.config import settings

def setup_logging():
    """
    Configure Structlog for JSON output and standard library compatibility.
    """
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.LOG_LEVEL.upper(),
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

# Use structlog.get_logger() which supports kwargs
logger = structlog.get_logger(settings.PROJECT_NAME)
