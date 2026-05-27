"""Tests for Step 29 — Prometheus metrics exporter."""

from __future__ import annotations

from pathlib import Path

import pytest
import requests

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

def test_metrics_payload_contains_series() -> None:
    simulate_traffic()
    body, content_type = metrics_payload()
    text = body.decode("utf-8")
    assert content_type.startswith("text/plain")
    assert "lab_http_requests_total" in text
    assert "lab_request_latency_seconds" in text


def test_record_request_increments_counter() -> None:
    record_request(method="POST", endpoint="/deploy", status=202, latency_seconds=0.05)
    body, _ = metrics_payload()
    assert 'endpoint="/deploy"' in body.decode("utf-8")

