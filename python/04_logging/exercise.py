"""Step 9 exercise — configure logging and emit structured JSON logs."""

from __future__ import annotations

import logging
from typing import Any


def build_text_logger(name: str = "lab.text") -> logging.Logger:
    raise NotImplementedError("Use get_logger(..., json_logs=False) from python.common.logging_setup.")


def build_json_logger(name: str = "lab.json") -> logging.Logger:
    raise NotImplementedError("Use get_logger(..., json_logs=True).")


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
    raise NotImplementedError("Call logger.log with extra trace_id and service fields.")


def summarize_status_counts(
    logger: logging.Logger,
    *,
    trace_id: str,
    service: str,
    status_counts: dict[int, int],
) -> None:
    raise NotImplementedError("Log totals and 5xx count with structured extra fields.")


def run_health_check_demo(
    *,
    service: str = "payment-api",
    endpoint: str = "/health",
    status_code: int = 200,
    latency_ms: float = 3.2,
    json_logs: bool = True,
) -> tuple[str, dict[str, Any]]:
    raise NotImplementedError("Generate trace_id, log event, return trace_id + payload dict.")


if __name__ == "__main__":
    print("Implement the functions above, then run: ./check.sh 9")
