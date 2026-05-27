"""Step 11 — REST client: poll /health with retries and timeouts."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (SRE) ---
# Load balancers and k8s probes hit /health repeatedly. Your scripts must
# handle transient failures (503 during deploy) with retries and bounded timeouts.

# --- Java developer note ---
# Like RestTemplate with RetryTemplate, or resilience4j retry — requests +
# urllib3 Retry gives similar behavior for GET probes.

# --- How to run ---
# Terminal 1: ./run.sh 12        (start FastAPI server)
# Terminal 2: ./run.sh 11        (this lesson polls localhost:8080)


def main() -> None:
    from solution import poll_health

    url = "http://127.0.0.1:8080/health"
    logger.info("Polling %s (start Step 12 server if connection fails)", url)
    result = poll_health(url, retries=3, timeout=2.0, backoff=0.5)

    if result["ok"]:
        logger.info(
            "Healthy: status=%s latency=%sms attempts=%s body=%s",
            result["status_code"],
            result["latency_ms"],
            result["attempts"],
            result.get("body"),
        )
    else:
        logger.error("Unhealthy after %s attempts: %s", result["attempts"], result.get("error"))
        logger.info("Tip: run ./run.sh 12 in another terminal, then retry.")


if __name__ == "__main__":
    main()
