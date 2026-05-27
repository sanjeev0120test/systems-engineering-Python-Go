"""
Step 9 — Logging for observable SRE tooling
============================================

Use the stdlib `logging` module locally, then JSON lines for production aggregators.
Correlation IDs (`trace_id`) tie together logs from one health check or incident.
"""

from __future__ import annotations

import json
import logging

from python.common.logging_setup import JsonFormatter, get_logger, new_trace_id

# ---------------------------------------------------------------------------
# JAVA BRIDGE
# ---------------------------------------------------------------------------
# Java                          | Python
# ------------------------------|------------------------------------------
# SLF4J LoggerFactory.getLogger | logging.getLogger("name")
# Logback pattern layout        | logging.Formatter("%(asctime)s ...")
# Logback JSON encoder          | JsonFormatter (python.common.logging_setup)
# MDC.put("traceId", id)        | logger.info(..., extra={"trace_id": id})
# log.info("msg", key, val)     | message string + extra dict for structured fields
# java.util.logging             | avoid — use `logging` module instead
#
# In Python, `extra` keys become attributes on LogRecord — custom formatters read them.

# ---------------------------------------------------------------------------
# SRE USE CASES
# ---------------------------------------------------------------------------
# - Text logs on laptop; JSON logs in staging/prod (same code, different formatter)
# - trace_id links health checker → alert → ticket during an incident
# - Log level gates noise: DEBUG locally, INFO/WARNING in prod
# - Never print() in automation — use logger so severity and structure survive


def demo_text_logging() -> None:
    """Classic human-readable format for `./run.sh 9` demos."""
    logger = get_logger("lesson9.text", json_logs=False)
    logger.setLevel(logging.DEBUG)
    logger.debug("verbose detail — usually disabled in prod")
    logger.info("health checker starting")


def demo_json_logging() -> None:
    """Each line is a JSON object — easy for Loki/Elasticsearch/Datadog."""
    logger = get_logger("lesson9.json", json_logs=True)
    trace_id = new_trace_id()
    logger.info(
        "probe succeeded",
        extra={"trace_id": trace_id, "service": "payment-api"},
    )
    print(f"(trace_id for this request: {trace_id})")


def demo_json_formatter_shape() -> None:
    """Show the exact JSON keys our formatter emits."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="demo",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="synthetic event",
        args=(),
        exc_info=None,
    )
    record.trace_id = new_trace_id()
    record.service = "lesson9"
    payload = json.loads(formatter.format(record))
    print("JSON keys:", sorted(payload.keys()))


def demo_log_levels() -> None:
    logger = get_logger("lesson9.levels", json_logs=True)
    trace = new_trace_id()
    extra = {"trace_id": trace, "service": "payment-api"}
    logger.debug("skipped if level=INFO", extra=extra)
    logger.warning("elevated latency detected", extra=extra)
    logger.error("dependency unavailable", extra=extra)


def main() -> None:
    demo_text_logging()
    demo_json_logging()
    demo_json_formatter_shape()
    demo_log_levels()


if __name__ == "__main__":
    main()
