"""Step 6 exercise — typing TODOs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import NotRequired, TypedDict

from python.common.paths import sample_data_path


class HostMetric(TypedDict):
    """Structured host metric row."""

    host: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    timestamp: NotRequired[str]


def parse_host_metric(raw: dict[str, object]) -> HostMetric | None:
    """Validate raw dict into HostMetric."""
    # TODO: extract required keys with try/except; return None on failure
    raise NotImplementedError("Implement parse_host_metric")


def is_host_overloaded(metric: HostMetric, cpu_limit: float = 80.0) -> bool:
    """Return True when CPU or memory exceeds limits."""
    # TODO: compare cpu_percent and memory_percent to cpu_limit
    raise NotImplementedError("Implement is_host_overloaded")


def load_sample_host_metric() -> HostMetric | None:
    """Load typed metric from repo sample_data."""
    # TODO: use sample_data_path("metrics", "host_metrics.json") and load_host_metric_file
    raise NotImplementedError("Implement load_sample_host_metric")


def load_host_metric_file(path: Path) -> HostMetric | None:
    """Load single-host metric JSON file."""
    # TODO: read JSON, parse_host_metric
    raise NotImplementedError("Implement load_host_metric_file")


def summarize_metric(metric: HostMetric | None) -> str:
    """Format metric for logs; handle Optional input."""
    # TODO: return 'metric: unavailable' when None
    raise NotImplementedError("Implement summarize_metric")


if __name__ == "__main__":
    path = sample_data_path("metrics", "host_metrics.json")
    print("Exercise Step 6 — implement TypedDict helpers.")
    print(f"Sample metrics file: {path}")
