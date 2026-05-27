"""Step 6 solution — type hints, Optional, TypedDict for host metrics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import NotRequired, TypedDict

from python.common.paths import sample_data_path


class HostMetric(TypedDict):
    """Structured host metric row — like a Java Map with known keys."""

    host: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    timestamp: NotRequired[str]


def parse_host_metric(raw: dict[str, object]) -> HostMetric | None:
    """Validate and coerce a raw dict into HostMetric; None if required keys missing."""
    try:
        host = str(raw["host"])
        cpu = float(raw["cpu_percent"])
        memory = float(raw["memory_percent"])
        disk = float(raw["disk_percent"])
    except (KeyError, TypeError, ValueError):
        return None

    metric: HostMetric = {
        "host": host,
        "cpu_percent": cpu,
        "memory_percent": memory,
        "disk_percent": disk,
    }
    if "timestamp" in raw:
        metric["timestamp"] = str(raw["timestamp"])
    return metric


def is_host_overloaded(metric: HostMetric, cpu_limit: float = 80.0) -> bool:
    """Return True when CPU or memory exceeds limits."""
    return metric["cpu_percent"] >= cpu_limit or metric["memory_percent"] >= cpu_limit


def load_sample_host_metric() -> HostMetric | None:
    """Load typed metric from repo sample_data (uses python.common.paths)."""
    path = sample_data_path("metrics", "host_metrics.json")
    return load_host_metric_file(path)


def load_host_metric_file(path: Path) -> HostMetric | None:
    """Load single-host metric JSON file into HostMetric."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    return parse_host_metric(data)


def summarize_metric(metric: HostMetric | None) -> str:
    """Format metric for logs; handle Optional input."""
    if metric is None:
        return "metric: unavailable"
    status = "OVERLOADED" if is_host_overloaded(metric) else "ok"
    return (
        f"metric: host={metric['host']} cpu={metric['cpu_percent']}% "
        f"mem={metric['memory_percent']}% status={status}"
    )
