"""Step 10 exercise — implement subprocess helpers (see solution.py if stuck)."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ProcessInfo:
    user: str
    pid: str
    cpu_pct: str
    mem_pct: str
    command: str


@dataclass(frozen=True)
class DiskInfo:
    filesystem: str
    size: str
    used: str
    avail: str
    use_pct: str
    mounted_on: str


def run_command(cmd: Sequence[str], timeout: float = 5.0) -> subprocess.CompletedProcess[str]:
    """TODO: run cmd with subprocess.run, capture_output=True, text=True, timeout."""
    raise NotImplementedError("Implement run_command using subprocess.run")


def parse_ps_output(output: str) -> list[ProcessInfo]:
    """TODO: parse `ps aux` output — skip header line, split columns."""
    raise NotImplementedError("Implement parse_ps_output")


def parse_df_output(output: str) -> list[DiskInfo]:
    """TODO: parse `df -h` output — skip header line."""
    raise NotImplementedError("Implement parse_df_output")


def collect_system_snapshot(timeout: float = 5.0) -> dict[str, object]:
    """TODO: run ps aux and df -h, return dict with parsed processes and mounts."""
    raise NotImplementedError("Implement collect_system_snapshot")


def main() -> None:
    snapshot = collect_system_snapshot()
    print(f"Processes: {len(snapshot['ps']['processes'])}")  # type: ignore[index]
    print(f"Mounts: {len(snapshot['df']['mounts'])}")  # type: ignore[index]


if __name__ == "__main__":
    main()
