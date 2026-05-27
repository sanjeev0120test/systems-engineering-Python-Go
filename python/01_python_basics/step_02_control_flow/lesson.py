"""Step 2 — Control flow: if / for / while for fleet health filtering.

Run from repo root:
    ./run.sh 2
    python python/01_python_basics/step_02_control_flow/lesson.py

Run from this folder:
    python lesson.py

Java developer notes
--------------------
- `if host.get("healthy") is False` — use `is False` for booleans, not `== False`.
- `for host in hosts:` replaces enhanced for-loop (`for (Host h : hosts)`).
- `while index < len(hosts):` — Python has no classic C-style for with init/cond/inc;
  use while + manual index, or prefer `for` with `enumerate`.
- Dict `.get(key, default)` avoids NullPointerException-style KeyError.

Production context
-----------
Health dashboards and runbooks filter unhealthy hosts before paging.
Control flow is how you turn raw probe results into actionable fleet summaries.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from solution import (  # noqa: E402
    count_by_status,
    filter_unhealthy,
    first_host_exceeding_retries,
    summarize_fleet,
)

SAMPLE_HOSTS: list[dict[str, object]] = [
    {"hostname": "web-01", "healthy": True, "status": "healthy", "retry_count": 0},
    {"hostname": "web-02", "healthy": False, "status": "down", "retry_count": 5},
    {"hostname": "api-01", "healthy": True, "status": "degraded", "retry_count": 2},
    {"hostname": "api-02", "healthy": False, "status": "down", "retry_count": 8},
]


def main() -> None:
    print("=" * 60)
    print("Step 2: Control flow — filter unhealthy hosts")
    print("=" * 60)

    print(f"\n1) Fleet summary: {summarize_fleet(SAMPLE_HOSTS)}")

    unhealthy = filter_unhealthy(SAMPLE_HOSTS)
    print(f"\n2) Unhealthy hosts ({len(unhealthy)}):")
    for host in unhealthy:
        # for-loop over filtered list — same pattern as Java stream filter + forEach
        print(f"   - {host['hostname']} status={host['status']}")

    counts = count_by_status(SAMPLE_HOSTS)
    print(f"\n3) Status breakdown: {counts}")

    noisy = first_host_exceeding_retries(SAMPLE_HOSTS, limit=3)
    print(f"\n4) First host exceeding retry limit (3): {noisy!r}")

    print("\nNext: implement exercise.py, then ./check.sh 2")


if __name__ == "__main__":
    main()
