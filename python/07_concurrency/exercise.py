"""Step 13 exercise — implement GIL demonstration helpers."""

from __future__ import annotations


def cpu_bound_task(n: int = 5000) -> int:
    """TODO: sum i*i for i in range(n)."""
    raise NotImplementedError("Implement cpu_bound_task")


def io_bound_task(delay: float = 0.05) -> float:
    """TODO: time.sleep(delay) and return delay."""
    raise NotImplementedError("Implement io_bound_task")


def run_cpu_sequential(workers: int = 2, n: int = 4000) -> dict[str, float]:
    raise NotImplementedError("Implement run_cpu_sequential")


def run_cpu_threaded(workers: int = 2, n: int = 4000) -> dict[str, float]:
    raise NotImplementedError("Implement run_cpu_threaded")


def run_io_threaded(workers: int = 4, delay: float = 0.05) -> dict[str, float]:
    raise NotImplementedError("Implement run_io_threaded")


def compare_concurrency_models() -> dict[str, dict[str, float]]:
    raise NotImplementedError("Implement compare_concurrency_models")


def main() -> None:
    for name, result in compare_concurrency_models().items():
        print(f"{name}: {result['elapsed_s']}s")


if __name__ == "__main__":
    main()
