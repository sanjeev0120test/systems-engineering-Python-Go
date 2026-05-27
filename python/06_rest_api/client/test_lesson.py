"""Tests for Step 11 — REST health client."""

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


class _FlakyHandler(BaseHTTPRequestHandler):
    call_count = 0

    def do_GET(self) -> None:  # noqa: N802
        type(self).call_count += 1
        if type(self).call_count < 2:
            self.send_response(503)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def log_message(self, format: str, *args: object) -> None:  # noqa: A003
        return


@pytest.fixture
def flaky_server() -> str:
    _FlakyHandler.call_count = 0
    server = HTTPServer(("127.0.0.1", 0), _FlakyHandler)
    port = server.server_address[1]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}/health"
    server.shutdown()


def test_build_session_returns_session() -> None:
    session = build_session(retries=2)
    assert session is not None


def test_poll_health_success(flaky_server: str) -> None:
    result = poll_health(flaky_server, retries=3, timeout=2.0, backoff=0.1)
    assert result["ok"] is True
    assert result["status_code"] == 200
    assert result["body"] == {"status": "ok"}
    assert _FlakyHandler.call_count >= 2


def test_poll_health_failure() -> None:
    result = poll_health("http://127.0.0.1:1/unreachable", retries=2, timeout=0.5, backoff=0.05)
    assert result["ok"] is False
    assert result["attempts"] == 2
    assert result["error"]

