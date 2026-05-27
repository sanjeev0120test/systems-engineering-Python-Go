"""Tests for Step 19 — alerting engine."""

from __future__ import annotations

from pathlib import Path

import pytest
from python.common import paths as paths_module
from python.common.paths import output_path, sample_data_path
import sqlite3
from unittest.mock import patch

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

@pytest.fixture(autouse=True)
def _reset_repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    root = Path(__file__).resolve().parents[2]
    monkeypatch.setattr(paths_module, "REPO_ROOT", root, raising=False)


@pytest.fixture
def sample_metrics() -> dict[str, float]:
    return {
        "cpu_percent": 42.5,
        "memory_percent": 68.2,
        "disk_percent": 55.0,
        "error_rate": 0.25,
        "latency_p95_ms": 250.0,
    }


def test_rules_path() -> None:
    assert mod.rules_path() == sample_data_path("alerts", "rules.yaml")


def test_alerts_db_path() -> None:
    assert mod.alerts_db_path() == output_path("alerts.db")


def test_load_rules() -> None:
    rules = mod.load_rules()
    assert len(rules) == 3
    assert rules[0]["name"] == "high_error_rate"


def test_evaluate_rule_fires(sample_metrics: dict[str, float]) -> None:
    rule = {"metric": "error_rate", "condition": ">", "threshold": 0.05}
    assert mod.evaluate_rule(rule, sample_metrics) is True


def test_evaluate_rule_no_fire(sample_metrics: dict[str, float]) -> None:
    rule = {"metric": "disk_percent", "condition": ">", "threshold": 85}
    assert mod.evaluate_rule(rule, sample_metrics) is False


def test_evaluate_all_sample(sample_metrics: dict[str, float]) -> None:
    rules = mod.load_rules()
    fired = mod.evaluate_all(rules, sample_metrics)
    names = {a["rule_name"] for a in fired}
    assert "high_error_rate" in names
    assert "high_latency_p95" in names
    assert "disk_usage_high" not in names


def test_record_alert_dedup(tmp_path: Path) -> None:
    db = tmp_path / "alerts.db"
    conn = mod.init_alerts_db(db)
    alert = {
        "rule_name": "high_error_rate",
        "severity": "critical",
        "description": "test",
        "metric": "error_rate",
        "metric_value": 0.25,
        "threshold": 0.05,
        "fired_at": "2026-05-27T10:00:00Z",
    }
    assert mod.record_alert(conn, alert) is True
    assert mod.record_alert(conn, alert) is False
    row = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()
    assert row is not None
    assert row[0] == 1
    conn.close()


def test_run_alerting_inserts_once(tmp_path: Path, sample_metrics: dict[str, float]) -> None:
    db = tmp_path / "alerts.db"
    first = mod.run_alerting(sample_metrics, db_path=db)
    second = mod.run_alerting(sample_metrics, db_path=db)
    assert len(first) >= 2
    assert len(second) == 0
    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    conn.close()
    assert count == len(first)


def test_load_metrics_snapshot_merges_log_slis(sample_metrics: dict[str, float]) -> None:
    metrics = mod.load_metrics_snapshot(
        log_summary={"error_rate": 0.1, "latency_p95_ms": 100.0},
    )
    assert metrics["error_rate"] == 0.1
    assert metrics["latency_p95_ms"] == 100.0
    assert metrics["disk_percent"] == 55.0

