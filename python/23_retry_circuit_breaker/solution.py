"""Step 21 solution — exponential backoff retry and circuit breaker."""

from __future__ import annotations

import random
import time
from enum import Enum
from typing import Callable, TypeVar

T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class FlakyService:
    """Mock dependency that fails for the first N calls, then succeeds."""

    def __init__(self, failures_before_success: int = 2) -> None:
        self.failures_before_success = failures_before_success
        self.call_count = 0

    def reset(self) -> None:
        self.call_count = 0

    def call(self) -> str:
        self.call_count += 1
        if self.call_count <= self.failures_before_success:
            raise ConnectionError(f"transient failure #{self.call_count}")
        return "ok"


class CircuitBreakerOpenError(RuntimeError):
    """Raised when the breaker is open and fast-failing calls."""


class CircuitBreaker:
    """Three-state breaker: closed → open → half-open → closed."""

    def __init__(
        self,
        *,
        failure_threshold: int = 3,
        recovery_timeout: float = 0.05,
        half_open_max_calls: int = 1,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.opened_at: float | None = None
        self.half_open_calls = 0

    def _transition_to_open(self) -> None:
        self.state = CircuitState.OPEN
        self.opened_at = time.monotonic()
        self.half_open_calls = 0

    def _maybe_half_open(self) -> None:
        if self.state != CircuitState.OPEN or self.opened_at is None:
            return
        if time.monotonic() - self.opened_at >= self.recovery_timeout:
            self.state = CircuitState.HALF_OPEN
            self.half_open_calls = 0

    def before_call(self) -> None:
        self._maybe_half_open()
        if self.state == CircuitState.OPEN:
            raise CircuitBreakerOpenError("circuit breaker is open")
        if self.state == CircuitState.HALF_OPEN and self.half_open_calls >= self.half_open_max_calls:
            raise CircuitBreakerOpenError("circuit breaker half-open probe limit reached")

    def record_success(self) -> None:
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.opened_at = None
        self.half_open_calls = 0

    def record_failure(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self._transition_to_open()
            return
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self._transition_to_open()

    def call(self, func: Callable[[], T]) -> T:
        self.before_call()
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
        try:
            result = func()
        except Exception:
            self.record_failure()
            raise
        self.record_success()
        return result


def retry_with_backoff(
    func: Callable[[], T],
    *,
    max_attempts: int = 5,
    base_delay: float = 0.01,
    max_delay: float = 0.5,
    jitter: bool = False,
) -> T:
    """Retry transient failures with exponential backoff."""
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")

    last_error: Exception | None = None
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as exc:  # noqa: BLE001 — lesson covers broad retry targets
            last_error = exc
            if attempt == max_attempts - 1:
                break
            delay = min(max_delay, base_delay * (2**attempt))
            if jitter:
                delay *= random.uniform(0.5, 1.5)
            time.sleep(delay)
    assert last_error is not None
    raise last_error


def resilient_call(
    func: Callable[[], T],
    breaker: CircuitBreaker,
    *,
    max_attempts: int = 5,
    base_delay: float = 0.01,
) -> T:
    """Combine circuit breaker with per-attempt exponential backoff."""

    def attempt() -> T:
        return breaker.call(func)

    return retry_with_backoff(attempt, max_attempts=max_attempts, base_delay=base_delay)
