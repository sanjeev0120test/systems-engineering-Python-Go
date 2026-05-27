"""Step 6 — Type hints, Optional, TypedDict for host metrics.

Run from repo root:
    ./run.sh 6
    python python/01_python_basics/step_06_typing/lesson.py

Run from this folder:
    python lesson.py

Java developer notes
--------------------
- `HostMetric | None` is Python 3.10+ union syntax (like `@Nullable HostMetric`).
- `TypedDict` describes dict shape — useful for JSON from Prometheus/agents.
- `NotRequired[str]` marks optional keys (like `@JsonIgnoreProperties(ignoreUnknown=true)`).
- Run `mypy` in CI on production code; here we learn the patterns first.

SRE context
-----------
Metrics agents emit JSON blobs. TypedDict + Optional makes invalid payloads visible
at review time instead of failing silently in production dashboards.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from python.common.paths import REPO_ROOT, sample_data_path  # noqa: E402

from solution import (  # noqa: E402
    is_host_overloaded,
    load_sample_host_metric,
    parse_host_metric,
    summarize_metric,
)


def main() -> None:
    print("=" * 60)
    print("Step 6: Typing — HostMetric TypedDict")
    print("=" * 60)

    print(f"\n1) Repo root (python.common.paths): {REPO_ROOT}")

    metrics_file = sample_data_path("metrics", "host_metrics.json")
    print(f"\n2) Sample metrics file: {metrics_file}")

    metric = load_sample_host_metric()
    print(f"\n3) Loaded typed metric: {metric}")
    print(f"   Summary: {summarize_metric(metric)}")
    print(f"   Overloaded? {is_host_overloaded(metric) if metric else 'n/a'}")

    bad_row: dict[str, object] = {"host": "incomplete"}
    parsed = parse_host_metric(bad_row)
    print(f"\n4) Invalid row -> {parsed!r}")
    print(f"   Summary: {summarize_metric(parsed)}")

    print("\nNext: implement exercise.py, then ./check.sh 6")
    print("You finished Python basics — continue to Step 7 (file handling).")


if __name__ == "__main__":
    main()
