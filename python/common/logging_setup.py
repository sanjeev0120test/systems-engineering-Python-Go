"""Structured logging helpers for SRE practice steps.

Production teams emit JSON log lines so Loki/ELK/Datadog can index fields like
trace_id and service without regex parsing.
"""

from __future__ import annotations

import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from typing import Any


class JsonFormatter(logging.Formatter):
    """One JSON object per log line (12-factor: logs as event streams)."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("trace_id", "service"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


def new_trace_id() -> str:
    """16-char correlation ID — like a trimmed UUID for log/trace linking."""
    return uuid.uuid4().hex[:16]


def get_logger(
    name: str,
    *,
    level: int = logging.INFO,
    json_logs: bool = False,
) -> logging.Logger:
    """Return a logger writing to stdout with text or JSON formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        for handler in logger.handlers:
            handler.setLevel(level)
            if json_logs and isinstance(handler.formatter, JsonFormatter):
                return logger
            if not json_logs and not isinstance(handler.formatter, JsonFormatter):
                return logger
        logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    if json_logs:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        )
    logger.addHandler(handler)
    return logger
