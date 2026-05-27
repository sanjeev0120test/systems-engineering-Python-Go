"""Tests for Step 26 — config drift detection."""

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

def test_diff_configs_detects_nested_change() -> None:
    old = {"service_name": "api", "limits": {"cpu": 1, "memory": "512Mi"}}
    new = {"service_name": "api", "limits": {"cpu": 2, "memory": "512Mi"}}
    changes = diff_configs(old, new)
    assert len(changes) == 1
    assert changes[0].path == "limits.cpu"
    assert changes[0].new_value == 2


def test_snapshot_and_detect_drift(tmp_path: Path) -> None:
    source = tmp_path / "service.yaml"
    source.write_text("service_name: api\ncheck_interval_seconds: 10\n", encoding="utf-8")
    baseline = tmp_path / "baseline.yaml"
    snapshot_config(source, baseline)

    mutated = tmp_path / "current.yaml"
    mutated.write_text("service_name: api\ncheck_interval_seconds: 30\n", encoding="utf-8")
    drift = detect_drift(baseline, mutated)
    assert any(item.path == "check_interval_seconds" for item in drift)


def test_write_drift_report(tmp_path: Path) -> None:
    report = write_drift_report([], report_path=tmp_path / "report.txt")
    assert report.exists()
    assert "No drift detected" in report.read_text(encoding="utf-8")

