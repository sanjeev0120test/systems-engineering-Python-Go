"""Step 13 solution — GIL demo: CPU-bound vs I/O-bound workloads."""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor


def cpu_bound_task(n: int = 5000) -> int:
    """CPU-heavy work — GIL prevents true parallel threads in CPython."""
    total = 0
    for i in range(n):
        total += i * i
    return total


def io_bound_task(delay: float = 0.05) -> float:
    """Simulated I/O wait — threads can overlap waiting time."""
    time.sleep(delay)
    return delay


def run_cpu_sequential(workers: int = 2, n: int = 4000) -> dict[str, float]:
    """Run CPU tasks one after another."""
    start = time.perf_counter()
    results = [cpu_bound_task(n) for _ in range(workers)]
    elapsed = time.perf_counter() - start
    return {"mode": "cpu_sequential", "elapsed_s": round(elapsed, 4), "results": results}


def run_cpu_threaded(workers: int = 2, n: int = 4000) -> dict[str, float]:
    """Run CPU tasks in threads — typically NOT faster due to GIL."""
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda _: cpu_bound_task(n), range(workers)))
    elapsed = time.perf_counter() - start
    return {"mode": "cpu_threaded", "elapsed_s": round(elapsed, 4), "results": results}


def run_io_threaded(workers: int = 4, delay: float = 0.05) -> dict[str, float]:
    """Run I/O tasks in parallel — threads help because GIL released during sleep."""
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda _: io_bound_task(delay), range(workers)))
    elapsed = time.perf_counter() - start
    return {"mode": "io_threaded", "elapsed_s": round(elapsed, 4), "results": results}


def compare_concurrency_models() -> dict[str, dict[str, float]]:
    """Return timing comparison for lesson output."""
    return {
        "cpu_sequential": run_cpu_sequential(),
        "cpu_threaded": run_cpu_threaded(),
        "io_threaded": run_io_threaded(),
    }
