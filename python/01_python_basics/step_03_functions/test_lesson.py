"""Step 3 tests."""

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
    {"hostname": "web-01", "disk_percent": 55.0, "mount": "/"},
    {"hostname": "db-01", "disk_percent": 93.5, "mount": "/var/lib/mysql"},
]


def test_is_disk_critical() -> None:
    assert solution.is_disk_critical(90.0) is True
    assert solution.is_disk_critical(89.9) is False
    assert solution.is_disk_critical(85.0, threshold=80.0) is True


def test_summarize_disk_alert() -> None:
    assert solution.summarize_disk_alert("db-01", 72.0) is None
    alert = solution.summarize_disk_alert("db-01", 93.5, mount="/var/lib/mysql")
    assert alert is not None
    assert "DISK CRITICAL" in alert
    assert "db-01" in alert


def test_evaluate_hosts_disk() -> None:
    alerts = solution.evaluate_hosts_disk(HOSTS)
    assert len(alerts) == 1
    assert "db-01" in alerts[0]


def test_disk_status_label() -> None:
    assert solution.disk_status_label(50.0) == "ok"
    assert solution.disk_status_label(77.0) == "warn"
    assert solution.disk_status_label(95.0) == "critical"

