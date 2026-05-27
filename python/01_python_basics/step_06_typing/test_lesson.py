"""Step 6 tests."""

from __future__ import annotations

from pathlib import Path

import pytest
from python.common import paths as paths_module
from python.common.paths import output_path, sample_data_path
import json

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

def test_parse_host_metric() -> None:
    raw = {
        "host": "web-01",
        "cpu_percent": 55.0,
        "memory_percent": 70.0,
        "disk_percent": 40.0,
        "timestamp": "2026-05-27T10:00:00Z",
    }
    metric = solution.parse_host_metric(raw)
    assert metric is not None
    assert metric["host"] == "web-01"
    assert metric["timestamp"] == "2026-05-27T10:00:00Z"


def test_parse_host_metric_invalid() -> None:
    assert solution.parse_host_metric({"host": "x"}) is None


def test_is_host_overloaded() -> None:
    metric: solution.HostMetric = {
        "host": "web-01",
        "cpu_percent": 85.0,
        "memory_percent": 50.0,
        "disk_percent": 40.0,
    }
    assert solution.is_host_overloaded(metric) is True
    metric["cpu_percent"] = 10.0
    assert solution.is_host_overloaded(metric) is False


def test_load_sample_host_metric() -> None:
    metric = solution.load_sample_host_metric()
    assert metric is not None
    assert metric["host"] == "localhost"


def test_load_host_metric_file(tmp_path: Path) -> None:
    payload = {
        "host": "tmp-01",
        "cpu_percent": 1.0,
        "memory_percent": 2.0,
        "disk_percent": 3.0,
    }
    path = tmp_path / "metric.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    metric = solution.load_host_metric_file(path)
    assert metric is not None
    assert metric["host"] == "tmp-01"


def test_summarize_metric() -> None:
    assert "unavailable" in solution.summarize_metric(None)
    metric: solution.HostMetric = {
        "host": "web-01",
        "cpu_percent": 90.0,
        "memory_percent": 50.0,
        "disk_percent": 40.0,
    }
    summary = solution.summarize_metric(metric)
    assert "OVERLOADED" in summary


def test_sample_data_path_exists() -> None:
    assert sample_data_path("metrics", "host_metrics.json").exists()

