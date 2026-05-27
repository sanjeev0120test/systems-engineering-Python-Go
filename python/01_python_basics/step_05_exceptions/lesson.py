"""Step 5 — Exceptions: EAFP vs LBYL for safe config parsing.

Run from repo root:
    ./run.sh 5
    python python/01_python_basics/step_05_exceptions/lesson.py

Run from this folder:
    python lesson.py

Java developer notes
--------------------
- Python has no checked exceptions — document failures in docstrings instead.
- `try/except` replaces try/catch; use `raise ValueError(...) from exc` for cause chains
  (like Java `initCause`).
- EAFP = "Easier to Ask Forgiveness than Permission" — try the operation, catch failures.
- LBYL = "Look Before You Leap" — guard clauses before acting (closer to Java null checks).

Production context
-----------
Config from env vars, YAML, and feature flags is often partial or wrong in staging.
Robust parsers default safely and log structured errors instead of crashing the agent.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from solution import (  # noqa: E402
    format_config_error,
    lbyl_safe_int,
    parse_threshold_config,
    read_nested_timeout,
    safe_int,
)

MESSY_CONFIG: dict[str, object] = {
    "check_interval_seconds": "10",
    "retry_limit": "not-an-int",
    "disk_threshold_percent": 90.0,
    "endpoints": [
        {"name": "health", "timeout_seconds": 2},
        {"name": "ready", "timeout_seconds": "3"},
    ],
}


def main() -> None:
    print("=" * 60)
    print("Step 5: Exceptions — safe config parsing")
    print("=" * 60)

    print("\n1) EAFP safe_int vs LBYL lbyl_safe_int on bad input '12abc':")
    print(f"   EAFP -> {safe_int('12abc', default=-1)}")
    print(f"   LBYL  -> {lbyl_safe_int('12abc', default=-1)}")

    print("\n2) parse_threshold_config (retry_limit is invalid, falls back):")
    thresholds = parse_threshold_config(MESSY_CONFIG)
    print(f"   {thresholds}")

    print("\n3) Nested timeout with EAFP:")
    timeout = read_nested_timeout(MESSY_CONFIG)
    print(f"   endpoints[0].timeout_seconds = {timeout}")

    print("\n4) Structured config error message:")
    try:
        parse_threshold_config({"disk_threshold_percent": "OOPS"})
    except ValueError as exc:
        print(f"   {format_config_error('disk_threshold_percent', exc)}")

    print("\nNext: implement exercise.py, then ./check.sh 5")


if __name__ == "__main__":
    main()
