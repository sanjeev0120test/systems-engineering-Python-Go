"""Tests for Step 7 — file handling."""

from __future__ import annotations

from pathlib import Path

import pytest
from python.common.paths import output_path, sample_data_path
from unittest.mock import patch

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)


def test_read_log_lines_reads_access_log() -> None:
    log_path = sample_data_path("logs", "access.log")
    lines = mod.read_log_lines(log_path)
    assert len(lines) >= 5
    assert all('"GET' in line or '"POST' in line for line in lines)


def test_count_http_statuses() -> None:
    lines = [
        '127.0.0.1 - - [27/May/2026:10:00:01 +0000] "GET /health HTTP/1.1" 200 12 0.003',
        '127.0.0.1 - - [27/May/2026:10:00:03 +0000] "GET /api/orders HTTP/1.1" 500 128 0.120',
        '127.0.0.1 - - [27/May/2026:10:00:04 +0000] "POST /api/login HTTP/1.1" 401 64 0.015',
    ]
    counts = mod.count_http_statuses(lines)
    assert counts == {200: 1, 401: 1, 500: 1}


def test_write_status_report_creates_tsv(tmp_path: Path) -> None:
    report = tmp_path / "nested" / "report.tsv"
    mod.write_status_report({503: 2, 200: 5}, report)
    text = report.read_text(encoding="utf-8")
    assert text.startswith("status_code\tcount\n")
    assert "200\t5" in text
    assert "503\t2" in text


def test_process_access_log_writes_output() -> None:
    report = output_path("test_step7_status_counts.txt")
    if report.exists():
        report.unlink()

    counts = mod.process_access_log(report_parts=("test_step7_status_counts.txt",))
    assert counts[200] >= 2
    assert 500 in counts
    assert report.exists()
    assert "status_code" in report.read_text(encoding="utf-8")

