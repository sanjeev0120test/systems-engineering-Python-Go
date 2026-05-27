"""Tests for Step 18 — log parser."""

from __future__ import annotations

from pathlib import Path

import pytest
from python.common import paths as paths_module
from python.common.paths import output_path, sample_data_path
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


SAMPLE_LINE = (
    '127.0.0.1 - - [27/May/2026:10:00:03 +0000] '
    '"GET /api/orders HTTP/1.1" 500 128 0.120'
)


def test_access_log_path() -> None:
    assert mod.access_log_path() == sample_data_path("logs", "access.log")


def test_parse_access_log_line() -> None:
    record = mod.parse_access_log_line(SAMPLE_LINE)
    assert record is not None
    assert record["status"] == 500
    assert record["bytes"] == 128
    assert record["latency_ms"] == 120.0
    assert record["is_error"] is True


def test_parse_access_log_line_200() -> None:
    line = (
        '127.0.0.1 - - [27/May/2026:10:00:01 +0000] '
        '"GET /health HTTP/1.1" 200 12 0.003'
    )
    record = mod.parse_access_log_line(line)
    assert record is not None
    assert record["is_error"] is False
    assert record["latency_ms"] == 3.0


def test_parse_access_log_sample() -> None:
    records = mod.parse_access_log()
    assert len(records) == 8


def test_compute_error_rate_sample() -> None:
    records = mod.parse_access_log()
    assert mod.compute_error_rate(records) == 0.25


def test_compute_p95_latency_sample() -> None:
    records = mod.parse_access_log()
    assert mod.compute_p95_latency_ms(records) == 250.0


def test_analyze_access_log_sample() -> None:
    summary = mod.analyze_access_log()
    assert summary["total_requests"] == 8
    assert summary["error_count_5xx"] == 2
    assert summary["error_rate"] == 0.25
    assert summary["latency_p95_ms"] == 250.0


def test_analyze_empty_log(tmp_path: Path) -> None:
    empty = tmp_path / "empty.log"
    empty.write_text("", encoding="utf-8")
    summary = mod.analyze_access_log(empty)
    assert summary["total_requests"] == 0
    assert summary["error_rate"] == 0.0
    assert summary["latency_p95_ms"] == 0.0

