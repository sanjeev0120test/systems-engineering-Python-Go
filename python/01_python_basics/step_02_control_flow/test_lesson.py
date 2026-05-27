"""Step 2 tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

HOSTS = [
    {"hostname": "web-01", "healthy": True, "status": "healthy", "retry_count": 1},
    {"hostname": "web-02", "healthy": False, "status": "down", "retry_count": 5},
    {"hostname": "api-01", "healthy": False, "status": "degraded", "retry_count": 2},
    {"hostname": "db-01", "healthy": True, "status": "down", "retry_count": 0},
]


def test_filter_unhealthy() -> None:
    result = solution.filter_unhealthy(HOSTS)
    assert len(result) == 2
    assert all(host["healthy"] is False for host in result)


def test_count_by_status() -> None:
    counts = solution.count_by_status(HOSTS)
    assert counts["healthy"] == 1
    assert counts["degraded"] == 1
    assert counts["down"] == 2


def test_first_host_exceeding_retries() -> None:
    assert solution.first_host_exceeding_retries(HOSTS, limit=3) == "web-02"
    assert solution.first_host_exceeding_retries(HOSTS, limit=10) is None


def test_summarize_fleet() -> None:
    summary = solution.summarize_fleet(HOSTS)
    assert "4 hosts" in summary
    assert "2 unhealthy" in summary

