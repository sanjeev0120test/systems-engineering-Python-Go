"""Step 3 — Functions: reusable disk threshold checks.

Run from repo root:
    ./run.sh 3
    python python/01_python_basics/step_03_functions/lesson.py

Run from this folder:
    python lesson.py

Java developer notes
--------------------
- `def name(arg: float, threshold: float = 90.0) -> bool:` — default args like Java
  overloads collapsed into one signature with defaults.
- Return `None` instead of Optional.empty() when no alert is needed.
- Functions are first-class: pass them as arguments later (Step 13+ concurrency).
- No method overloading — use default parameters or distinct function names.

SRE context
-----------
Disk-full incidents are common P1s. Encapsulate threshold logic once so every
monitoring script uses the same numbers (avoid alert fatigue from inconsistent thresholds).
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from solution import (  # noqa: E402
    disk_status_label,
    evaluate_hosts_disk,
    is_disk_critical,
    summarize_disk_alert,
)

SAMPLE_HOSTS: list[dict[str, object]] = [
    {"hostname": "web-01", "disk_percent": 72.0, "mount": "/"},
    {"hostname": "db-01", "disk_percent": 93.5, "mount": "/var/lib/mysql"},
    {"hostname": "cache-01", "disk_percent": 88.0, "mount": "/data"},
]


def main() -> None:
    print("=" * 60)
    print("Step 3: Functions — disk threshold checks")
    print("=" * 60)

    used = 93.5
    threshold = 90.0
    print(f"\n1) is_disk_critical({used}, {threshold}) -> {is_disk_critical(used, threshold)}")

    alert = summarize_disk_alert("db-01", used, threshold, mount="/var/lib/mysql")
    print(f"\n2) Alert message: {alert}")

    print("\n3) Per-host status labels:")
    for host in SAMPLE_HOSTS:
        hostname = str(host["hostname"])
        disk = float(host["disk_percent"])
        label = disk_status_label(disk)
        print(f"   {hostname}: {disk}% -> {label}")

    alerts = evaluate_hosts_disk(SAMPLE_HOSTS)
    print(f"\n4) Fleet alerts ({len(alerts)}):")
    for message in alerts:
        print(f"   {message}")

    print("\nNext: implement exercise.py, then ./check.sh 3")


if __name__ == "__main__":
    main()
