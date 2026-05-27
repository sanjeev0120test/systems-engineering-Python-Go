"""Step 14 — Threading: parallel I/O-bound health checks."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (SRE) ---
# Monitoring 50 microservices sequentially takes 50× latency. ThreadPoolExecutor
# fans out HTTP probes — standard pattern in black-box synthetic monitoring.

# --- Java developer note ---
# ThreadPoolExecutor ≈ Java's Executors.newFixedThreadPool(n) with Future results.

# --- How to run ---
# ./run.sh 12   (optional — live server)
# ./run.sh 14
# ./check.sh 14


def main() -> None:
    from solution import parallel_health_checks

    urls = [
        "http://127.0.0.1:8080/health",
        "http://127.0.0.1:8080/ready",
        "https://httpbin.org/status/200",
    ]
    logger.info("Checking %d URLs in parallel...", len(urls))
    results = parallel_health_checks(urls, max_workers=4, timeout=3.0)

    for row in results:
        status = "OK" if row["ok"] else "FAIL"
        logger.info("%s %s code=%s latency=%sms", status, row["url"], row.get("status_code"), row.get("latency_ms"))


if __name__ == "__main__":
    main()
