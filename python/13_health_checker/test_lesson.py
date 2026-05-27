"""Tests for Step 16 — health checker."""

from __future__ import annotations

from pathlib import Path

import pytest
from python.common import paths as paths_module
from python.common.paths import output_path, sample_data_path
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any
from unittest.mock import patch
import requests

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

@pytest.fixture(autouse=True)
def _reset_repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    root = Path(__file__).resolve().parents[2]
    monkeypatch.setattr(paths_module, "REPO_ROOT", root, raising=False)


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return


@pytest.fixture
def local_http_url() -> str:
    server = HTTPServer(("127.0.0.1", 0), _HealthHandler)
    port = server.server_address[1]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}/health"
    server.shutdown()


@pytest.fixture
def local_tcp_port() -> int:
    server = HTTPServer(("127.0.0.1", 0), _HealthHandler)
    port = server.server_address[1]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield port
    server.shutdown()


def test_health_report_path() -> None:
    assert mod.health_report_path() == output_path("health_report.json")


def test_load_health_config() -> None:
    config = mod.load_health_config()
    assert config["service_name"] == "payment-api"
    assert len(config["endpoints"]) == 2


def test_check_http_success(local_http_url: str) -> None:
    result = mod.check_http(local_http_url, timeout=2.0, retries=1)
    assert result["ok"] is True
    assert result["status_code"] == 200
    assert result["latency_ms"] >= 0


def test_check_http_retries_on_failure() -> None:
    calls = {"count": 0}

    def flaky_get(url: str, timeout: float = 2.0) -> Any:
        calls["count"] += 1
        if calls["count"] < 3:
            raise requests.ConnectionError("simulated failure")
        response = requests.Response()
        response.status_code = 200
        response._content = b"ok"  # noqa: SLF001
        return response

    with patch.object(requests, "get", side_effect=flaky_get):
        result = mod.check_http("http://127.0.0.1/test", retries=3, retry_delay=0.01)
    assert result["ok"] is True
    assert result["attempts"] == 3


def test_check_tcp_success(local_tcp_port: int) -> None:
    result = mod.check_tcp("127.0.0.1", local_tcp_port, timeout=2.0, retries=1)
    assert result["ok"] is True
    assert result["latency_ms"] >= 0


def test_run_with_retry() -> None:
    attempts = {"n": 0}

    def flaky() -> str:
        attempts["n"] += 1
        if attempts["n"] < 2:
            raise RuntimeError("not yet")
        return "ok"

    assert mod.run_with_retry(flaky, retries=3, retry_delay=0.01) == "ok"


def test_build_health_report() -> None:
    checks = [{"ok": True}, {"ok": False}]
    report = mod.build_health_report(checks, service="demo")
    assert report["service"] == "demo"
    assert report["healthy"] is False
    assert report["checks"] == checks
    assert "timestamp" in report


def test_write_and_run_health_checks(tmp_path: Path, local_http_url: str) -> None:
    report_path = tmp_path / "health_report.json"
    config = {
        "service_name": "test-api",
        "endpoints": [{"name": "health", "url": local_http_url, "timeout_seconds": 2}],
        "hosts": [],
    }
    checks = mod.run_configured_checks(config)
    report = mod.build_health_report(checks, service="test-api")
    mod.write_health_report(report, path=report_path)
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["healthy"] is True
    assert data["checks"][0]["name"] == "health"


def test_run_health_checks_writes_output(local_http_url: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    out = tmp_path / "output" / "health_report.json"
    monkeypatch.setattr(mod, "health_report_path", lambda: out)
    monkeypatch.setattr(
        mod,
        "load_health_config",
        lambda: {
            "service_name": "test-api",
            "endpoints": [{"name": "health", "url": local_http_url, "timeout_seconds": 2}],
            "hosts": [],
        },
    )
    report = mod.run_health_checks()
    assert out.exists()
    assert report["service"] == "test-api"
    assert report["healthy"] is True

