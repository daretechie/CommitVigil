import time
from contextlib import contextmanager
from src.core.logging import logger

@contextmanager
def LatencyMonitor(operation_name: str, user_id: str):
    """
    Context manager to track latency of critical operations.
    Logs warnings if SLA > 500ms is breached.
    """
    start_time = time.perf_counter()
    try:
        yield
    finally:
        duration = (time.perf_counter() - start_time) * 1000  # ms
        
        # Log metric for Prometheus scraping (in real app, use Histogram.observe)
        logger.info(
            "latency_observed",
            operation=operation_name,
            duration_ms=round(duration, 2),
            user_id=user_id
        )

        if duration > 500:
            logger.warning(
                "sla_breach_detected",
                operation=operation_name,
                duration_ms=round(duration, 2),
                threshold_ms=500,
                user_id=user_id
            )
