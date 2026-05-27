"""Step 23 solution — HTTP reverse proxy forwarding to a local backend."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import httpx
from fastapi import FastAPI, Request, Response


def forward_request(
    client: httpx.Client,
    *,
    method: str,
    path: str,
    backend_base_url: str,
    headers: dict[str, str] | None = None,
    content: bytes | None = None,
) -> httpx.Response:
    """Forward an HTTP request to backend_base_url + path."""
    url = backend_base_url.rstrip("/") + "/" + path.lstrip("/")
    response = client.request(method.upper(), url, headers=headers, content=content)
    return response


def create_proxy_app(
    backend_base_url: str,
    *,
    client_factory: Callable[[], httpx.Client] | None = None,
) -> FastAPI:
    """ASGI reverse proxy: strip hop-by-hop headers, forward everything else."""
    app = FastAPI(title="Reverse Proxy Sim", version="0.1.0")
    hop_by_hop = {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    }

    def _client() -> httpx.Client:
        if client_factory is not None:
            return client_factory()
        return httpx.Client(timeout=5.0)

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
    async def proxy(path: str, request: Request) -> Response:
        headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in hop_by_hop
        }
        body = await request.body()
        with _client() as client:
            upstream = forward_request(
                client,
                method=request.method,
                path=path,
                backend_base_url=backend_base_url,
                headers=headers,
                content=body or None,
            )
        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            headers=dict(upstream.headers),
            media_type=upstream.headers.get("content-type"),
        )

    return app


def proxy_health_summary(backend_response: dict[str, Any]) -> dict[str, Any]:
    """Normalize backend health payload for observability dashboards."""
    return {
        "upstream_status": backend_response.get("status", "unknown"),
        "proxied": True,
        "service": backend_response.get("service"),
    }
