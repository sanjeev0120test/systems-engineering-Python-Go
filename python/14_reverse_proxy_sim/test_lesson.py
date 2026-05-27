"""Tests for Step 23 — reverse proxy simulator."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod

for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)


def _backend_app() -> FastAPI:
    backend = FastAPI()

    @backend.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "backend-a"}

    @backend.get("/api/items")
    def items() -> dict[str, list[str]]:
        return {"items": ["cpu", "memory"]}

    return backend


def test_forward_request_hits_backend() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/health"
        return httpx.Response(200, json={"status": "ok", "service": "backend-a"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        response = forward_request(
            client,
            method="GET",
            path="/health",
            backend_base_url="http://backend",
        )
    assert response.status_code == 200
    assert response.json()["service"] == "backend-a"


def test_proxy_app_forwards_paths() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/items":
            return httpx.Response(200, json={"items": ["cpu", "memory"]})
        return httpx.Response(404)

    def client_factory() -> httpx.Client:
        return httpx.Client(transport=httpx.MockTransport(handler))

    proxy = TestClient(create_proxy_app("http://backend", client_factory=client_factory))
    response = proxy.get("/api/items")
    assert response.status_code == 200
    assert response.json()["items"] == ["cpu", "memory"]


def test_proxy_health_summary() -> None:
    summary = proxy_health_summary({"status": "ok", "service": "payments"})
    assert summary["proxied"] is True
    assert summary["upstream_status"] == "ok"
