"""Step 11 solution — HTTP health polling with retries and timeouts."""

from __future__ import annotations

import time
from typing import Any

import requests


def build_session() -> requests.Session:
    """Return a reusable HTTP session (same connection pool for multiple calls)."""
    return requests.Session()


def poll_health(
    url: str,
    *,
    retries: int = 3,
    timeout: float = 2.0,
    backoff: float = 0.5,
) -> dict[str, Any]:
    """
    Poll a health endpoint until success or retries exhausted.

    Returns dict with ok, status_code, latency_ms, attempts, body/error.
    """
    session = build_session()
    last_error: str | None = None
    attempts = 0

    for attempt in range(1, retries + 1):
        attempts = attempt
        start = time.perf_counter()
        try:
            response = session.get(url, timeout=timeout)
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            if response.ok:
                try:
                    body = response.json()
                except ValueError:
                    body = {"raw": response.text[:200]}
                return {
                    "ok": True,
                    "status_code": response.status_code,
                    "latency_ms": latency_ms,
                    "attempts": attempts,
                    "body": body,
                }
            last_error = f"HTTP {response.status_code}"
        except requests.RequestException as exc:
            last_error = str(exc)
        if attempt < retries:
            time.sleep(backoff * attempt)

    return {
        "ok": False,
        "status_code": None,
        "latency_ms": None,
        "attempts": attempts,
        "error": last_error,
    }
