"""Tests for Step 9 — logging."""

from __future__ import annotations

from pathlib import Path

import pytest
import json
import logging

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

import uuid


def _unique_name(prefix: str) -> str:
    return f"{prefix}.{uuid.uuid4().hex[:8]}"


def test_new_trace_id_length() -> None:
    from python.common.logging_setup import new_trace_id

    trace_id = new_trace_id()
    assert len(trace_id) == 16
    assert trace_id.isalnum()


def test_build_text_logger_format(capsys: pytest.CaptureFixture[str]) -> None:
    logger = mod.build_text_logger(_unique_name("lab.text"))
    logger.info("hello text")
    captured = capsys.readouterr().out
    assert "hello text" in captured
    assert "INFO" in captured
    # Text format should not be JSON
    with pytest.raises(json.JSONDecodeError):
        json.loads(captured.strip())


def test_build_json_logger_emits_json(capsys: pytest.CaptureFixture[str]) -> None:
    logger = mod.build_json_logger(_unique_name("lab.json"))
    trace_id = "abc123def4567890"
    mod.log_health_check(
        logger,
        trace_id=trace_id,
        service="payment-api",
        endpoint="/health",
        status_code=200,
        latency_ms=2.5,
    )
    line = capsys.readouterr().out.strip()
    payload = json.loads(line)
    assert payload["level"] == "INFO"
    assert payload["trace_id"] == trace_id
    assert payload["service"] == "payment-api"
    assert "health check" in payload["message"]
    assert "200" in payload["message"]


def test_log_health_check_warning_level(capsys: pytest.CaptureFixture[str]) -> None:
    logger = mod.build_json_logger(_unique_name("lab.json"))
    mod.log_health_check(
        logger,
        trace_id="trace-warn-001",
        service="payment-api",
        endpoint="/ready",
        status_code=503,
        latency_ms=120.0,
        level=logging.WARNING,
    )
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["level"] == "WARNING"
    assert "503" in payload["message"]


def test_summarize_status_counts(capsys: pytest.CaptureFixture[str]) -> None:
    logger = mod.build_json_logger(_unique_name("lab.json"))
    mod.summarize_status_counts(
        logger,
        trace_id="trace-summary-01",
        service="log-parser",
        status_counts={200: 5, 500: 2, 503: 1},
    )
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["trace_id"] == "trace-summary-01"
    assert "errors_5xx=3" in payload["message"]
    assert payload["service"] == "log-parser"


def test_run_health_check_demo_returns_trace_id(capsys: pytest.CaptureFixture[str]) -> None:
    trace_id, payload = mod.run_health_check_demo(
        status_code=200,
        latency_ms=4.0,
        json_logs=True,
    )
    assert trace_id == payload["trace_id"]
    assert len(trace_id) == 16
    log_line = json.loads(capsys.readouterr().out.strip())
    assert log_line["trace_id"] == trace_id

