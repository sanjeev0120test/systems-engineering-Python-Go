"""Tests for Step 25 — APScheduler cron jobs."""

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

def test_run_once_executes_synchronously() -> None:
    record = run_once(lambda: "snapshot_ok", job_name="backup")
    assert record.run_count == 1
    assert record.results == ["snapshot_ok"]
    assert record.last_run_at is not None


def test_cron_runner_run_job_now() -> None:
    runner = CronJobRunner()
    counter = {"n": 0}

    def job() -> str:
        counter["n"] += 1
        return f"tick-{counter['n']}"

    runner.register_job("heartbeat", job, minute="*", second="0")
    runner.start()
    try:
        assert runner.run_job_now("heartbeat") == "tick-1"
        assert runner.records["heartbeat"].run_count == 1
    finally:
        runner.shutdown()

