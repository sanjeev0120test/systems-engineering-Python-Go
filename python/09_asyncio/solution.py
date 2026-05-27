"""Step 15 solution — async health poller with asyncio and httpx."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx


async def async_check_url(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    """Single async GET with latency measurement."""
    start = time.perf_counter()
    try:
        response = await client.get(url)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        body: dict[str, Any] | None = None
        try:
            body = response.json()
        except ValueError:
            body = None
        return {
            "url": url,
            "ok": response.is_success,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "body": body,
        }
    except httpx.HTTPError as exc:
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "url": url,
            "ok": False,
            "status_code": None,
            "latency_ms": latency_ms,
            "error": str(exc),
        }


async def async_poll_health(
    urls: list[str],
    *,
    timeout: float = 2.0,
) -> list[dict[str, Any]]:
    """Poll all URLs concurrently with asyncio.gather."""
    if not urls:
        return []

    limits = httpx.Limits(max_connections=len(urls), max_keepalive_connections=len(urls))
    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        tasks = [async_check_url(client, url) for url in urls]
        results = await asyncio.gather(*tasks)

    return sorted(results, key=lambda r: r["url"])


def poll_health_sync(urls: list[str], *, timeout: float = 2.0) -> list[dict[str, Any]]:
    """Sync wrapper for scripts and tests."""
    return asyncio.run(async_poll_health(urls, timeout=timeout))
