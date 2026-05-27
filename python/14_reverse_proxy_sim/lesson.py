"""Step 23 — Reverse proxy: forward HTTP to a local backend."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (SRE) ---
# Reverse proxies (nginx, Envoy, HAProxy) terminate TLS, add auth, enforce rate limits,
# and route traffic without exposing backend topology. During incidents you can drain
# nodes by removing them from the proxy pool while keeping the VIP stable.

# --- Production patterns ---
# - X-Forwarded-For / X-Request-ID propagation for distributed tracing
# - Timeouts at the proxy prevent slow backends from tying up worker threads
# - Health-checked upstream groups — unhealthy backends removed automatically

# --- Java developer note ---
# Spring Cloud Gateway and Zuul play a similar role in JVM stacks. This lesson uses
# FastAPI + httpx to show request forwarding mechanics without nginx config syntax.

# --- How to run ---
# ./run.sh 23
# ./check.sh 23


def main() -> None:
    from solution import proxy_health_summary

    summary = proxy_health_summary({"status": "ok", "service": "payments"})
    logger.info("Proxy health summary: %s", summary)
    logger.info("Run Step 12 server, point proxy at http://127.0.0.1:8080 in production drills.")


if __name__ == "__main__":
    main()
