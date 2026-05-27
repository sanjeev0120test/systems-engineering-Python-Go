"""Step 20 — Rate limiting: token bucket and FastAPI middleware."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (production) ---
# Unbounded traffic causes cascading failures: DB connection pools exhaust, latency
# spikes, and retries amplify load. Rate limits protect your service and neighbors.
# Token buckets allow short bursts (good for human traffic) while enforcing sustained
# throughput — common at API gateways (nginx limit_req, Envoy local rate limit).

# --- Production patterns ---
# - Per-tenant limits (API keys) vs global limits (protect shared dependencies)
# - Return 429 + Retry-After so clients use exponential backoff (Step 21)
# - Monitor rejected_requests_total — sustained 429s may mean misconfigured clients
#   or an attack, not just "working as designed"

# --- Java developer note ---
# Resilience4j RateLimiter ≈ TokenBucket. Spring Cloud Gateway has Redis-backed
# rate limiting for distributed enforcement across pods.

# --- How to run ---
# ./run.sh 20
# ./check.sh 20


def main() -> None:
    from solution import TokenBucket, create_app

    bucket = TokenBucket(capacity=5, refill_rate=2.0)
    logger.info("Token bucket capacity=%s refill_rate=%s/s", bucket.capacity, bucket.refill_rate)
    allowed = sum(1 for _ in range(8) if bucket.consume())
    logger.info("Immediate burst: %s/8 requests allowed (rest should wait for refill)", allowed)

    app = create_app(capacity=3, refill_rate=1.0)
    logger.info("FastAPI demo app routes: %s", [route.path for route in app.routes])
    logger.info(
        "In production, place rate limiting at the edge (ingress) AND on hot endpoints."
    )


if __name__ == "__main__":
    main()
