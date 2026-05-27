"""Step 24 — Load balancer: round-robin across local backend ports."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (production) ---
# Load balancers spread traffic so no single instance saturates. Round-robin is simple
# and fair when requests are homogeneous; weighted RR or least-conn work better when
# instance sizes or latency differ. Always health-check backends — routing to dead nodes
# wastes error budget on 502/503 storms.

# --- Production patterns ---
# - Graceful drain: remove backend from pool, wait for in-flight requests, then deploy
# - Sticky sessions only when necessary (stateful apps) — complicates failover
# - Layer-4 (TCP) vs Layer-7 (HTTP) LB — HTTP LB can route on path/headers

# --- Java developer note ---
# Spring Cloud LoadBalancer and Kubernetes Services (kube-proxy) implement similar
# selection algorithms. This lesson uses explicit round-robin for clarity.

# --- How to run ---
# ./run.sh 24
# ./check.sh 24


def main() -> None:
    from solution import RoundRobinBalancer, distribute_requests

    backends = ["http://127.0.0.1:8001", "http://127.0.0.1:8002", "http://127.0.0.1:8003"]
    balancer = RoundRobinBalancer(backends)
    urls = distribute_requests(balancer, ["/health"] * 4)
    logger.info("Round-robin choices: %s", urls)
    logger.info("Compare with reverse proxy (Step 23) — LB picks among many backends.")


if __name__ == "__main__":
    main()
