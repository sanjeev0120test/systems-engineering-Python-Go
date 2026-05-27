"""Tests for Step 14 — ThreadPoolExecutor health checks."""

from __future__ import annotations

from pathlib import Path

import pytest
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

import json


class _OkHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


def _start_server() -> tuple[HTTPServer, str]:
    server = HTTPServer(("127.0.0.1", 0), _OkHandler)
    port = server.server_address[1]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{port}/health"


def test_check_url_success() -> None:
    server, url = _start_server()
    try:
        result = check_url(url, timeout=2.0)
        assert result["ok"] is True
        assert result["status_code"] == 200
        assert result["latency_ms"] >= 0
    finally:
        server.shutdown()


def test_parallel_health_checks() -> None:
    servers: list[HTTPServer] = []
    urls: list[str] = []
    try:
        for _ in range(3):
            server, url = _start_server()
            servers.append(server)
            urls.append(url)
        results = parallel_health_checks(urls, max_workers=3, timeout=2.0)
        assert len(results) == 3
        assert all(r["ok"] for r in results)
    finally:
        for server in servers:
            server.shutdown()


def test_parallel_health_checks_empty() -> None:
    assert parallel_health_checks([]) == []

