"""Step 29 — Prometheus metrics exporter."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (production) ---
# You can't SLO what you don't measure. Prometheus pull model (/metrics scrape) is the
# de facto standard for service telemetry. RED metrics (Rate, Errors, Duration) on every
# handler give you burn-rate alerts before customers open tickets.

# --- Production patterns ---
# - Counter for totals, Gauge for point-in-time, Histogram for latency buckets
# - Label cardinality kills Prometheus — avoid unbounded labels (user_id, trace_id)
# - Expose /metrics on admin port or auth-protected path — not public internet

# --- Java developer note ---
# Micrometer registries export to Prometheus with similar metric types. This lesson uses
# prometheus_client directly — same exposition format Grafana scrapes.

# --- How to run ---
# ./run.sh 29              (starts server.py on :9100/metrics)
# curl http://127.0.0.1:9100/metrics
# ./check.sh 29


def main() -> None:
    from solution import metrics_payload, simulate_traffic

    simulate_traffic()
    body, content_type = metrics_payload()
    logger.info("Content-Type: %s", content_type)
    logger.info("Sample lines:\n%s", "\n".join(body.decode().splitlines()[:5]))
    logger.info("Start long-running exporter with: ./run.sh 29")


if __name__ == "__main__":
    main()
