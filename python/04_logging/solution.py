"""Step 9 solution — stdlib logging and JSON structured logs."""

from __future__ import annotations

import json
import logging
from typing import Any

from python.common.logging_setup import get_logger, new_trace_id


def build_text_logger(name: str = "sre.text") -> logging.Logger:
    """Human-readable logs for local debugging."""
    return get_logger(name, level=logging.DEBUG, json_logs=False)


def build_json_logger(name: str = "sre.json") -> logging.Logger:
    """One JSON object per line — ready for Loki/ELK/GCP."""
    return get_logger(name, level=logging.INFO, json_logs=True)


def log_health_check(
    logger: logging.Logger,
    *,
    trace_id: str,
    service: str,
    endpoint: str,
    status_code: int,
    latency_ms: float,
    level: int = logging.INFO,
) -> None:
    """Emit a structured health-check event with correlation ID."""
    message = f"health check {endpoint} -> {status_code} ({latency_ms:.1f}ms)"
    logger.log(
        level,
        message,
        extra={"trace_id": trace_id, "service": service},
    )


def summarize_status_counts(
    logger: logging.Logger,
    *,
    trace_id: str,
    service: str,
    status_counts: dict[int, int],
) -> None:
    """Log aggregated access-log status counts as structured context."""
    total = sum(status_counts.values())
    errors = sum(count for code, count in status_counts.items() if code >= 500)
    message = f"access log summary total={total} errors_5xx={errors}"
    logger.info(message, extra={"trace_id": trace_id, "service": service})


def run_health_check_demo(
    *,
    service: str = "payment-api",
    endpoint: str = "/health",
    status_code: int = 200,
    latency_ms: float = 3.2,
    json_logs: bool = True,
) -> tuple[str, dict[str, Any]]:
    """Return trace_id and parsed JSON log record from one health-check event."""
    trace_id = new_trace_id()
    logger = build_json_logger() if json_logs else build_text_logger()
    log_health_check(
        logger,
        trace_id=trace_id,
        service=service,
        endpoint=endpoint,
        status_code=status_code,
        latency_ms=latency_ms,
    )
    # Re-fetch last handler output is awkward; callers/tests capture stdout instead.
    payload = {
        "trace_id": trace_id,
        "service": service,
        "endpoint": endpoint,
        "status_code": status_code,
        "latency_ms": latency_ms,
    }
    return trace_id, payload


if __name__ == "__main__":
    print("--- text logger ---")
    text_logger = build_text_logger()
    tid = new_trace_id()
    log_health_check(
        text_logger,
        trace_id=tid,
        service="payment-api",
        endpoint="/ready",
        status_code=200,
        latency_ms=1.8,
    )

    print("--- json logger ---")
    json_logger = build_json_logger()
    log_health_check(
        json_logger,
        trace_id=new_trace_id(),
        service="payment-api",
        endpoint="/health",
        status_code=503,
        latency_ms=250.0,
        level=logging.WARNING,
    )
