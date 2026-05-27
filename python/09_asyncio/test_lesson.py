"""Tests for Step 15 — asyncio health poller."""

from __future__ import annotations

from pathlib import Path

import pytest
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any
import asyncio

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

import httpx
import json


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


@pytest.fixture
def local_health_url() -> str:
    server = HTTPServer(("127.0.0.1", 0), _HealthHandler)
    port = server.server_address[1]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{port}/health"
    yield url
    server.shutdown()


def test_async_check_url(local_health_url: str) -> None:
    async def _run() -> None:
        async with httpx.AsyncClient(timeout=2.0) as client:
            result = await async_check_url(client, local_health_url)
        assert result["ok"] is True
        assert result["status_code"] == 200
        assert result["body"] == {"status": "ok"}

    asyncio.run(_run())


def test_async_poll_health(local_health_url: str) -> None:
    async def _run() -> None:
        results = await async_poll_health([local_health_url], timeout=2.0)
        assert len(results) == 1
        assert results[0]["ok"] is True

    asyncio.run(_run())


def test_poll_health_sync(local_health_url: str) -> None:
    results = poll_health_sync([local_health_url], timeout=2.0)
    assert len(results) == 1
    assert results[0]["ok"] is True


def test_async_poll_health_empty() -> None:
    assert asyncio.run(async_poll_health([])) == []

