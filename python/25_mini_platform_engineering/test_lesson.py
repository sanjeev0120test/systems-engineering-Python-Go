"""Tests for Step 31 — platform engineering capstone."""

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

def test_run_lint_rejects_invalid_service() -> None:
    bad = run_lint("bad name!")
    assert bad.success is False


def test_run_pipeline_writes_report(tmp_path: Path) -> None:
    report_path = tmp_path / "report.txt"
    report = run_pipeline("payment-api", report_path=report_path)
    assert report.passed is True
    assert report.deployed is True
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "payment-api" in content
    assert "[PASS] lint" in content


def test_write_pipeline_report_marks_failure() -> None:
    report = PipelineReport(
        service="broken",
        stages=[StageResult("lint", False, "failed"), StageResult("test", False, "skipped")],
        deployed=False,
    )
    path = write_pipeline_report(report, report_path=Path(__file__).parent / "_tmp_report.txt")
    try:
        assert "FAIL" in path.read_text(encoding="utf-8")
    finally:
        path.unlink(missing_ok=True)

