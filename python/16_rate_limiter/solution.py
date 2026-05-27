"""Step 20 solution — token bucket rate limiter with FastAPI middleware."""

from __future__ import annotations

import time
from threading import Lock

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class TokenBucket:
    """Token bucket: smooth rate limiting with configurable burst capacity."""

    def __init__(self, capacity: int, refill_rate: float) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()
        self._lock = Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        if elapsed <= 0:
            return
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """Try to take tokens; return False when the bucket is empty."""
        if tokens <= 0:
            raise ValueError("tokens must be positive")
        with self._lock:
            self._refill()
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    @property
    def available_tokens(self) -> float:
        with self._lock:
            self._refill()
            return self.tokens


def create_app(*, capacity: int = 5, refill_rate: float = 1.0) -> FastAPI:
    """Build a demo API protected by token-bucket middleware."""
    bucket = TokenBucket(capacity=capacity, refill_rate=refill_rate)
    app = FastAPI(title="Rate Limiter Demo", version="0.1.0")

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        if not bucket.consume():
            return JSONResponse(
                status_code=429,
                content={"detail": "rate limit exceeded", "retry_after_seconds": 1},
            )
        return await call_next(request)

    @app.get("/api/data")
    def read_data() -> dict[str, str]:
        return {"status": "ok", "message": "request allowed"}

    return app


app = create_app()
