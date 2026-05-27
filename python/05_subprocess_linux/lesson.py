"""Step 10 — Subprocess on Linux/WSL: replace shell runbooks with Python."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (SRE) ---
# On-call runbooks often say: "run ps aux | grep foo" or "check df -h".
# subprocess lets you automate those checks in health scripts and agents.

# --- Java developer note ---
# Like ProcessBuilder + waitFor(timeout), but Python's subprocess.run is one call
# with capture_output, text mode, and timeout built in.

# --- How to run ---
# ./run.sh 10          (this lesson)
# ./run.sh 10 exercise (after editing exercise.py)
# ./check.sh 10        (pytest — use WSL/Linux for live ps/df)


def main() -> None:
    if sys.platform == "win32":
        logger.warning(
            "Native Windows lacks ps/df. Run this step in WSL: "
            "wsl -d Ubuntu -- bash -lc 'cd /mnt/c/dev/systems-engineering-Python-Go && ./run.sh 10'"
        )
        return

    from solution import collect_system_snapshot, run_command

    logger.info("Running ps aux (timeout=5s)...")
    ps = run_command(["ps", "aux"], timeout=5.0)
    logger.info("ps exit code=%s, lines=%d", ps.returncode, len(ps.stdout.splitlines()))

    logger.info("Running df -h (timeout=5s)...")
    df = run_command(["df", "-h"], timeout=5.0)
    logger.info("df exit code=%s", df.returncode)

    snapshot = collect_system_snapshot()
    proc_count = len(snapshot["ps"]["processes"])  # type: ignore[index]
    mount_count = len(snapshot["df"]["mounts"])  # type: ignore[index]
    logger.info("Snapshot: %d processes, %d mounts", proc_count, mount_count)


if __name__ == "__main__":
    main()
