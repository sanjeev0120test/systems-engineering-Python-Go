"""Step 1 tests — verify solution.py implementations."""

from __future__ import annotations

from pathlib import Path

import pytest

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

def test_parse_hostname_from_url() -> None:
    assert solution.parse_hostname_from_url("https://api.example.com:8080/health") == "api.example.com"
    assert solution.parse_hostname_from_url("http://127.0.0.1/metrics") == "127.0.0.1"


def test_parse_hostname_from_log_line() -> None:
    line = "hostname=web-01.prod.example.com status=503 region=us-east-1"
    assert solution.parse_hostname_from_log_line(line) == "web-01.prod.example.com"
    assert solution.parse_hostname_from_log_line("level=info msg=ok") is None


def test_format_host_alert() -> None:
    assert "[CRITICAL]" in solution.format_host_alert("api-01", 503, "us-east-1")
    assert "[WARNING]" in solution.format_host_alert("api-01", 404, "us-east-1")
    assert "api-01" in solution.format_host_alert("api-01", 404, "us-east-1")


def test_describe_variable_types() -> None:
    result = solution.describe_variable_types("web-01", 443, True)
    assert "web-01" in result
    assert "443" in result
    assert "True" in result

