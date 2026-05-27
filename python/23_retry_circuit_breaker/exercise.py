"""Step 21 exercise — retry with backoff and circuit breaker."""

from __future__ import annotations

from enum import Enum
from typing import Callable, TypeVar

T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class FlakyService:
    def __init__(self, failures_before_success: int = 2) -> None:
        raise NotImplementedError("Implement FlakyService")

    def reset(self) -> None:
        raise NotImplementedError("Implement FlakyService.reset")

    def call(self) -> str:
        raise NotImplementedError("Implement FlakyService.call")


class CircuitBreakerOpenError(RuntimeError):
    pass


class CircuitBreaker:
    def __init__(
        self,
        *,
        failure_threshold: int = 3,
        recovery_timeout: float = 0.05,
        half_open_max_calls: int = 1,
    ) -> None:
        raise NotImplementedError("Implement CircuitBreaker")

    def call(self, func: Callable[[], T]) -> T:
        raise NotImplementedError("Implement CircuitBreaker.call")


def retry_with_backoff(
    func: Callable[[], T],
    *,
    max_attempts: int = 5,
    base_delay: float = 0.01,
    max_delay: float = 0.5,
    jitter: bool = False,
) -> T:
    raise NotImplementedError("Implement retry_with_backoff")


def resilient_call(
    func: Callable[[], T],
    breaker: CircuitBreaker,
    *,
    max_attempts: int = 5,
    base_delay: float = 0.01,
) -> T:
    raise NotImplementedError("Implement resilient_call")


def main() -> None:
    print("Implement retry + circuit breaker, then run: ./check.sh 21")


if __name__ == "__main__":
    main()
