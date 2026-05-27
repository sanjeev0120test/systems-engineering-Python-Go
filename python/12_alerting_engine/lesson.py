"""
Step 19 — Alerting engine (rules + SQLite dedup)
=================================================

Load threshold rules from YAML, evaluate against live metrics, and persist alerts.
SQLite deduplication prevents alert storms when the same rule fires every poll cycle.
"""

from __future__ import annotations

from solution import evaluate_all, load_metrics_snapshot, load_rules, run_alerting


def demo_rule_evaluation() -> None:
    rules = load_rules()
    metrics = load_metrics_snapshot()
    fired = evaluate_all(rules, metrics)
    print(f"Metrics snapshot: error_rate={metrics['error_rate']}, p95={metrics['latency_p95_ms']}ms")
    print(f"Rules loaded: {len(rules)}, fired: {len(fired)}")
    for alert in fired:
        print(f"  [{alert['severity']}] {alert['rule_name']}: {alert['description']}")


def main() -> None:
    demo_rule_evaluation()
    print("\n--- persist with dedup ---")
    new_alerts = run_alerting()
    print(f"New alerts inserted: {len(new_alerts)}")


if __name__ == "__main__":
    main()
