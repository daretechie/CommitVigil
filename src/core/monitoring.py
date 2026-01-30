# Copyright (c) 2026 CommitVigil AI. All rights reserved.
import time
from contextlib import contextmanager

from prometheus_client import Histogram
from src.core.config import settings
from src.core.logging import logger

# Native Prometheus Histogram for high-precision latency tracking
OPERATION_LATENCY = Histogram(
    "commitvigil_operation_latency_ms",
    "Latency of critical system operations in milliseconds",
    ["operation"],
    buckets=[10, 50, 100, 250, 500, 1000, 2500, 5000]
)


@contextmanager
def LatencyMonitor(operation_name: str, user_id: str):
    """
    Context manager to track latency of critical operations.
    Context manager to track latency of critical operations.
    Logs warnings if SLA > configured threshold is breached.
    """
    start_time = time.perf_counter()
    try:
        yield
    finally:
        duration = (time.perf_counter() - start_time) * 1000  # ms

        # Record Native Metric (PII-free)
        OPERATION_LATENCY.labels(operation=operation_name).observe(duration)

        # Log event (PII-free for monitoring logs)
        logger.info(
            "latency_observed",
            operation=operation_name,
            duration_ms=round(duration, 2),
        )

        if duration > settings.LATENCY_SLA_THRESHOLD_MS:
            logger.warning(
                "sla_breach_detected",
                operation=operation_name,
                duration_ms=round(duration, 2),
                threshold_ms=settings.LATENCY_SLA_THRESHOLD_MS,
                user_id=user_id,
            )
