"""Step 23 exercise — reverse proxy simulator."""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import FastAPI


def forward_request(
    client: httpx.Client,
    *,
    method: str,
    path: str,
    backend_base_url: str,
    headers: dict[str, str] | None = None,
    content: bytes | None = None,
) -> httpx.Response:
    raise NotImplementedError("Implement forward_request")


def create_proxy_app(backend_base_url: str) -> FastAPI:
    raise NotImplementedError("Implement create_proxy_app")


def proxy_health_summary(backend_response: dict[str, Any]) -> dict[str, Any]:
    raise NotImplementedError("Implement proxy_health_summary")


def main() -> None:
    print("Implement reverse proxy, then run: ./check.sh 23")


if __name__ == "__main__":
    main()
