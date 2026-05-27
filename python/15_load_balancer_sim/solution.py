"""Step 24 solution — round-robin load balancer across local backends."""

from __future__ import annotations

from collections.abc import Callable
from itertools import cycle
from threading import Lock

import httpx
from fastapi import FastAPI, Request, Response


class RoundRobinBalancer:
    """Cycle through backend base URLs in order."""

    def __init__(self, backends: list[str]) -> None:
        if not backends:
            raise ValueError("backends must not be empty")
        self.backends = backends
        self._cycle = cycle(backends)
        self._lock = Lock()

    def next_backend(self) -> str:
        with self._lock:
            return next(self._cycle)

    def remove_backend(self, backend: str) -> None:
        with self._lock:
            self.backends = [item for item in self.backends if item != backend]
            if not self.backends:
                raise RuntimeError("no backends remaining")
            self._cycle = cycle(self.backends)


def create_load_balancer_app(
    backends: list[str],
    *,
    client_factory: Callable[[], httpx.Client] | None = None,
) -> FastAPI:
    balancer = RoundRobinBalancer(backends)
    app = FastAPI(title="Load Balancer Sim", version="0.1.0")

    def _client() -> httpx.Client:
        if client_factory is not None:
            return client_factory()
        return httpx.Client(timeout=5.0)

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
    async def balanced_proxy(path: str, request: Request) -> Response:
        backend = balancer.next_backend()
        url = backend.rstrip("/") + "/" + path.lstrip("/")
        body = await request.body()
        with _client() as client:
            upstream = client.request(request.method, url, content=body or None)
        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            headers={"X-Backend-Used": backend, **dict(upstream.headers)},
            media_type=upstream.headers.get("content-type"),
        )

    @app.get("/lb/backends")
    def list_backends() -> dict[str, list[str]]:
        return {"backends": balancer.backends}

    return app


def distribute_requests(
    balancer: RoundRobinBalancer,
    paths: list[str],
) -> list[str]:
    """Return backend chosen for each path (for tests and demos)."""
    return [balancer.next_backend() + path for path in paths]
