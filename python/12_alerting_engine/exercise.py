"""Step 19 exercise — alerting engine with SQLite deduplication."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


def rules_path() -> Path:
    raise NotImplementedError("Return sample_data_path('alerts', 'rules.yaml').")


def alerts_db_path() -> Path:
    raise NotImplementedError("Return output_path('alerts.db').")


def load_rules(path: Path | None = None) -> list[dict[str, Any]]:
    raise NotImplementedError("Load rules list from rules.yaml.")


def load_metrics_snapshot(
    *,
    host_metrics_file: Path | None = None,
    log_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raise NotImplementedError("Merge host_metrics.json with log-parser SLIs.")


def evaluate_rule(rule: dict[str, Any], metrics: dict[str, Any]) -> bool:
    raise NotImplementedError("Compare metric to threshold using rule condition.")


def evaluate_all(rules: list[dict[str, Any]], metrics: dict[str, Any]) -> list[dict[str, Any]]:
    raise NotImplementedError("Return list of fired alert dicts.")


def init_alerts_db(db_path: Path | None = None) -> sqlite3.Connection:
    raise NotImplementedError("Create alerts table with dedup_key UNIQUE.")


def dedup_key_for_alert(alert: dict[str, Any]) -> str:
    raise NotImplementedError("Return stable dedup key (e.g. rule_name).")


def record_alert(conn: sqlite3.Connection, alert: dict[str, Any]) -> bool:
    raise NotImplementedError("INSERT OR IGNORE; return True if inserted.")


def run_alerting(
    metrics: dict[str, Any] | None = None,
    *,
    db_path: Path | None = None,
    rules_file: Path | None = None,
) -> list[dict[str, Any]]:
    raise NotImplementedError("Evaluate rules, dedupe in SQLite, return new alerts.")


if __name__ == "__main__":
    print("Implement the functions above, then run: ./check.sh 19")
