"""Tests for Step 13 — concurrency demos."""

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

def test_cpu_bound_task_returns_sum() -> None:
    assert cpu_bound_task(100) == sum(i * i for i in range(100))


def test_io_bound_task_returns_delay() -> None:
    assert io_bound_task(0.01) == 0.01


def test_io_threaded_faster_than_serial() -> None:
    workers = 4
    delay = 0.05
    result = run_io_threaded(workers=workers, delay=delay)
    assert result["elapsed_s"] < workers * delay
    assert len(result["results"]) == workers


def test_compare_concurrency_models_keys() -> None:
    results = compare_concurrency_models()
    assert set(results) == {"cpu_sequential", "cpu_threaded", "io_threaded"}
    for entry in results.values():
        assert entry["elapsed_s"] > 0

