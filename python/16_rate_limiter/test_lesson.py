"""Tests for Step 20 — token bucket rate limiter."""

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

from fastapi.testclient import TestClient


def test_token_bucket_allows_burst_then_rejects() -> None:
    bucket = TokenBucket(capacity=3, refill_rate=10.0)
    assert bucket.consume()
    assert bucket.consume()
    assert bucket.consume()
    assert not bucket.consume()


def test_token_bucket_refills_over_time() -> None:
    bucket = TokenBucket(capacity=2, refill_rate=100.0)
    assert bucket.consume()
    assert bucket.consume()
    assert not bucket.consume()
    import time

    time.sleep(0.05)
    assert bucket.consume()


def test_middleware_returns_429_when_exhausted() -> None:
    app = create_app(capacity=2, refill_rate=0.01)
    client = TestClient(app)
    assert client.get("/api/data").status_code == 200
    assert client.get("/api/data").status_code == 200
    response = client.get("/api/data")
    assert response.status_code == 429
    assert response.json()["detail"] == "rate limit exceeded"

