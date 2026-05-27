"""Step 21 — Retry with exponential backoff and circuit breaker."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (production) ---
# Retries without backoff create retry storms: a blip on a dependency becomes an outage
# when every client hammers it simultaneously. Exponential backoff + jitter spreads load.
# Circuit breakers fail fast when a dependency is clearly unhealthy — preserving threads,
# connection pools, and user-facing latency budgets instead of waiting on timeouts.

# --- Production patterns ---
# - Retry only idempotent operations (GET, PUT with idempotency keys) unless designed for it
# - Breaker metrics: circuit_state, failures_before_open, half_open_success_rate
# - Pair with bulkheads (thread pools per dependency) to isolate blast radius

# --- Java developer note ---
# Resilience4j Retry + CircuitBreaker mirror this lesson. Spring Retry uses @Retryable
# with backoff policies — same concepts, different annotations.

# --- How to run ---
# ./run.sh 21
# ./check.sh 21


def main() -> None:
    from solution import CircuitBreaker, FlakyService, resilient_call

    service = FlakyService(failures_before_success=2)
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=0.1)

    logger.info("Simulating flaky dependency (2 failures then success)...")
    result = resilient_call(service.call, breaker, max_attempts=4, base_delay=0.01)
    logger.info("Call result: %s after %s attempts", result, service.call_count)
    logger.info("Breaker state: %s", breaker.state.value)
    logger.info(
        "Production rule: retry transient errors, break on sustained failure, alert on open circuits."
    )


if __name__ == "__main__":
    main()
