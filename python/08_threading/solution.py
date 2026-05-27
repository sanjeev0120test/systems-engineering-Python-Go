"""Step 14 solution — parallel I/O health checks with ThreadPoolExecutor."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import requests


def check_url(url: str, timeout: float = 2.0) -> dict[str, Any]:
    """Single HTTP GET health check with latency measurement."""
    start = time.perf_counter()
    try:
        response = requests.get(url, timeout=timeout)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "url": url,
            "ok": response.ok,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
        }
    except requests.RequestException as exc:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "url": url,
            "ok": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "error": str(exc),
        }


def parallel_health_checks(
    urls: list[str],
    *,
    max_workers: int = 4,
    timeout: float = 2.0,
) -> list[dict[str, Any]]:
    """Run health checks concurrently — ideal for I/O-bound probe fan-out."""
    if not urls:
        return []

    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(check_url, url, timeout): url for url in urls}
        for future in as_completed(futures):
            results.append(future.result())

    return sorted(results, key=lambda r: r["url"])
