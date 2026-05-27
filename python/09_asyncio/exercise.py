"""Step 15 exercise — async health poller with asyncio."""

from __future__ import annotations

from typing import Any

import httpx


async def async_check_url(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    """TODO: await client.get(url) and return structured result."""
    raise NotImplementedError("Implement async_check_url")


async def async_poll_health(
    urls: list[str],
    *,
    timeout: float = 2.0,
) -> list[dict[str, Any]]:
    """TODO: use asyncio.gather with shared AsyncClient."""
    raise NotImplementedError("Implement async_poll_health")


def poll_health_sync(urls: list[str], *, timeout: float = 2.0) -> list[dict[str, Any]]:
    raise NotImplementedError("Implement poll_health_sync using asyncio.run")


def main() -> None:
    urls = ["http://127.0.0.1:8080/health", "http://127.0.0.1:8080/ready"]
    for row in poll_health_sync(urls):
        print(row)


if __name__ == "__main__":
    main()
