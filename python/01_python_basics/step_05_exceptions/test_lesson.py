"""Step 5 tests."""

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

def test_safe_int() -> None:
    assert solution.safe_int("42") == 42
    assert solution.safe_int("not-a-number", default=7) == 7
    assert solution.safe_int("-3") == -3


def test_lbyl_safe_int() -> None:
    assert solution.lbyl_safe_int("42") == 42
    assert solution.lbyl_safe_int("12abc", default=5) == 5


def test_parse_threshold_config() -> None:
    raw = {
        "check_interval_seconds": "15",
        "retry_limit": "5",
        "disk_threshold_percent": 92.5,
    }
    parsed = solution.parse_threshold_config(raw)
    assert parsed["check_interval_seconds"] == 15
    assert parsed["retry_limit"] == 5
    assert parsed["disk_threshold_percent"] == 92.5


def test_parse_threshold_config_invalid() -> None:
    try:
        solution.parse_threshold_config({"disk_threshold_percent": "not-float"})
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "Invalid threshold config" in str(exc)


def test_read_nested_timeout() -> None:
    config = {"endpoints": [{"timeout_seconds": 5}]}
    assert solution.read_nested_timeout(config) == 5.0
    assert solution.read_nested_timeout({}) == 2.0


def test_format_config_error() -> None:
    msg = solution.format_config_error("retry_limit", ValueError("bad"))
    assert "retry_limit" in msg
    assert "ValueError" in msg

