"""Tests for Step 21 — retry and circuit breaker."""

from __future__ import annotations

from pathlib import Path

import pytest

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

def test_flaky_service_succeeds_after_failures() -> None:
    service = FlakyService(failures_before_success=2)
    with pytest.raises(ConnectionError):
        service.call()
    with pytest.raises(ConnectionError):
        service.call()
    assert service.call() == "ok"


def test_retry_with_backoff_eventually_succeeds() -> None:
    service = FlakyService(failures_before_success=3)
    result = retry_with_backoff(service.call, max_attempts=5, base_delay=0.001)
    assert result == "ok"
    assert service.call_count == 4


def test_circuit_breaker_opens_after_threshold() -> None:
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=0.05)

    def fail() -> None:
        raise ConnectionError("down")

    for _ in range(2):
        with pytest.raises(ConnectionError):
            breaker.call(fail)
    assert breaker.state == CircuitState.OPEN
    with pytest.raises(CircuitBreakerOpenError):
        breaker.call(fail)


def test_resilient_call_combines_retry_and_breaker() -> None:
    service = FlakyService(failures_before_success=1)
    breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=0.05)
    assert resilient_call(service.call, breaker, max_attempts=3, base_delay=0.001) == "ok"

