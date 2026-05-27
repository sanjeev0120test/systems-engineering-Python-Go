"""
Step 17 — Monitoring agent (CPU / memory)
============================================

Long-running agents poll host metrics and write snapshots for alerting pipelines.
Graceful shutdown on Ctrl+C avoids corrupting partial writes mid-cycle.
"""

from __future__ import annotations

from solution import collect_metrics, load_agent_config, write_latest_metrics


def main() -> None:
    config = load_agent_config()
    metrics = collect_metrics()
    path = write_latest_metrics(metrics)
    print(f"Single snapshot (interval={config['check_interval_seconds']}s): {path}")
    print(metrics)


if __name__ == "__main__":
    main()
