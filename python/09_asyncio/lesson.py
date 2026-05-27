"""Step 15 — Asyncio: async HTTP health poller."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (production) ---
# Async agents poll hundreds of endpoints on one thread — lower memory than
# hundreds of threads. FastAPI and modern observability tools are async-native.

# --- Java developer note ---
# asyncio + await ≈ CompletableFuture chain; async def ≈ async method returning
# a coroutine. httpx.AsyncClient ≈ non-blocking HTTP client.

# --- How to run ---
# ./run.sh 12   (optional)
# ./run.sh 15
# ./check.sh 15


def main() -> None:
    from solution import poll_health_sync

    urls = [
        "http://127.0.0.1:8080/health",
        "http://127.0.0.1:8080/ready",
        "https://httpbin.org/status/200",
    ]
    logger.info("Async polling %d URLs...", len(urls))
    results = poll_health_sync(urls, timeout=3.0)

    for row in results:
        status = "OK" if row["ok"] else "FAIL"
        logger.info("%s %s code=%s latency=%sms", status, row["url"], row.get("status_code"), row.get("latency_ms"))


if __name__ == "__main__":
    main()
