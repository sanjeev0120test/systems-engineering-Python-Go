"""Step 20 exercise — implement token bucket rate limiting."""

from __future__ import annotations

from fastapi import FastAPI


class TokenBucket:
    """TODO: implement refill-on-consume token bucket."""

    def __init__(self, capacity: int, refill_rate: float) -> None:
        raise NotImplementedError("Implement TokenBucket.__init__")

    def consume(self, tokens: int = 1) -> bool:
        raise NotImplementedError("Implement TokenBucket.consume")

    @property
    def available_tokens(self) -> float:
        raise NotImplementedError("Implement TokenBucket.available_tokens")


def create_app(*, capacity: int = 5, refill_rate: float = 1.0) -> FastAPI:
    raise NotImplementedError("Implement FastAPI app with 429 middleware")


app = create_app()


def main() -> None:
    print("Implement TokenBucket and middleware, then run: ./check.sh 20")


if __name__ == "__main__":
    main()
