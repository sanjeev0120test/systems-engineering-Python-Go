"""Tests for Step 24 — load balancer simulator."""

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


def test_round_robin_cycles_backends() -> None:
    balancer = RoundRobinBalancer(["http://a:8001", "http://b:8002", "http://c:8003"])
    chosen = [balancer.next_backend() for _ in range(6)]
    assert chosen == [
        "http://a:8001",
        "http://b:8002",
        "http://c:8003",
        "http://a:8001",
        "http://b:8002",
        "http://c:8003",
    ]


def test_distribute_requests_builds_urls() -> None:
    balancer = RoundRobinBalancer(["http://a:8001", "http://b:8002"])
    urls = distribute_requests(balancer, ["/health", "/metrics", "/health"])
    assert urls[0] == "http://a:8001/health"
    assert urls[1] == "http://b:8002/metrics"


def test_load_balancer_app_rotates_backends() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        host = request.url.host
        calls.append(host)
        return httpx.Response(200, json={"backend": host})

    def client_factory() -> httpx.Client:
        return httpx.Client(transport=httpx.MockTransport(handler))

    client = TestClient(
        create_load_balancer_app(
            ["http://a:8001", "http://b:8002"],
            client_factory=client_factory,
        )
    )
    client.get("/ping")
    client.get("/ping")
    assert calls == ["a", "b"]
