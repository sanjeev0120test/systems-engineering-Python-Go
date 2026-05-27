"""Step 19 solution — alerting engine with SQLite deduplication."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from python.common.config_loader import load_yaml
from python.common.logging_setup import get_logger, new_trace_id
from python.common.paths import output_path, sample_data_path

logger = get_logger("alerting_engine", json_logs=True)

_OPERATORS = {
    ">": lambda value, threshold: value > threshold,
    ">=": lambda value, threshold: value >= threshold,
    "<": lambda value, threshold: value < threshold,
    "<=": lambda value, threshold: value <= threshold,
    "==": lambda value, threshold: value == threshold,
}


def rules_path() -> Path:
    return sample_data_path("alerts", "rules.yaml")


def alerts_db_path() -> Path:
    return output_path("alerts.db")


def host_metrics_path() -> Path:
    return sample_data_path("metrics", "host_metrics.json")


def load_rules(path: Path | None = None) -> list[dict[str, Any]]:
    """Load alert rules from YAML."""
    data = load_yaml(path or rules_path())
    rules = data.get("rules", [])
    return [r for r in rules if isinstance(r, dict)]


def _log_parser_summary() -> dict[str, Any]:
    """Import Step 18 log parser lazily with a unique module name."""
    import importlib.util

    parser_path = Path(__file__).resolve().parent.parent / "11_log_parser" / "solution.py"
    spec = importlib.util.spec_from_file_location("log_parser_step18_solution", parser_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load log parser from {parser_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.analyze_access_log()


def load_metrics_snapshot(
    *,
    host_metrics_file: Path | None = None,
    log_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Merge host metrics JSON with log-parser SLIs."""
    metrics: dict[str, Any] = {}
    metrics_file = host_metrics_file or host_metrics_path()
    if metrics_file.exists():
        with metrics_file.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            metrics.update(data)

    summary = log_summary if log_summary is not None else _log_parser_summary()
    metrics["error_rate"] = float(summary.get("error_rate", 0.0))
    metrics["latency_p95_ms"] = float(summary.get("latency_p95_ms", 0.0))
    return metrics


def evaluate_rule(rule: dict[str, Any], metrics: dict[str, Any]) -> bool:
    """Return True when the rule condition fires against metrics."""
    metric_name = str(rule.get("metric", ""))
    if metric_name not in metrics:
        return False
    condition = str(rule.get("condition", ">"))
    op = _OPERATORS.get(condition)
    if op is None:
        return False
    value = float(metrics[metric_name])
    threshold = float(rule.get("threshold", 0))
    return op(value, threshold)


def evaluate_all(rules: list[dict[str, Any]], metrics: dict[str, Any]) -> list[dict[str, Any]]:
    """Return fired alerts (rules whose conditions match)."""
    fired: list[dict[str, Any]] = []
    for rule in rules:
        if evaluate_rule(rule, metrics):
            metric_name = str(rule["metric"])
            fired.append(
                {
                    "rule_name": str(rule.get("name", "unknown")),
                    "severity": str(rule.get("severity", "warning")),
                    "description": str(rule.get("description", "")),
                    "metric": metric_name,
                    "metric_value": float(metrics[metric_name]),
                    "threshold": float(rule.get("threshold", 0)),
                    "fired_at": datetime.now(timezone.utc).isoformat(),
                }
            )
    return fired


def init_alerts_db(db_path: Path | None = None) -> sqlite3.Connection:
    """Create alerts table with dedup constraint."""
    path = db_path or alerts_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT NOT NULL,
            metric TEXT NOT NULL,
            metric_value REAL NOT NULL,
            threshold REAL NOT NULL,
            fired_at TEXT NOT NULL,
            dedup_key TEXT NOT NULL UNIQUE
        )
        """
    )
    conn.commit()
    return conn


def dedup_key_for_alert(alert: dict[str, Any]) -> str:
    """Stable key — one open alert per rule name."""
    return str(alert["rule_name"])


def record_alert(conn: sqlite3.Connection, alert: dict[str, Any]) -> bool:
    """Insert alert if not deduplicated. Return True when inserted."""
    key = dedup_key_for_alert(alert)
    cursor = conn.execute(
        """
        INSERT OR IGNORE INTO alerts
            (rule_name, severity, description, metric, metric_value, threshold, fired_at, dedup_key)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            alert["rule_name"],
            alert["severity"],
            alert["description"],
            alert["metric"],
            alert["metric_value"],
            alert["threshold"],
            alert["fired_at"],
            key,
        ),
    )
    conn.commit()
    return cursor.rowcount == 1


def run_alerting(
    metrics: dict[str, Any] | None = None,
    *,
    db_path: Path | None = None,
    rules_file: Path | None = None,
) -> list[dict[str, Any]]:
    """Evaluate rules, dedupe in SQLite, return newly inserted alerts."""
    trace_id = new_trace_id()
    rules = load_rules(rules_file)
    snapshot = metrics if metrics is not None else load_metrics_snapshot()
    fired = evaluate_all(rules, snapshot)

    conn = init_alerts_db(db_path)
    inserted: list[dict[str, Any]] = []
    try:
        for alert in fired:
            if record_alert(conn, alert):
                inserted.append(alert)
                logger.warning(
                    f"alert fired: {alert['rule_name']}",
                    extra={"trace_id": trace_id, "service": "alerting_engine"},
                )
    finally:
        conn.close()

    print(f"Evaluated {len(rules)} rules — {len(inserted)} new alert(s)")
    return inserted


if __name__ == "__main__":
    run_alerting()
