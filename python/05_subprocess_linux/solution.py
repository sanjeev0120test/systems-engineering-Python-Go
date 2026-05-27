"""Step 10 solution — run Linux commands via subprocess and parse output."""

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
    """Run a shell command with timeout; capture stdout/stderr as text."""
    return subprocess.run(
        list(cmd),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def parse_ps_output(output: str) -> list[ProcessInfo]:
    """Parse `ps aux` lines into structured records (skips header)."""
    processes: list[ProcessInfo] = []
    for line in output.strip().splitlines()[1:]:
        parts = line.split(None, 10)
        if len(parts) < 11:
            continue
        processes.append(
            ProcessInfo(
                user=parts[0],
                pid=parts[1],
                cpu_pct=parts[2],
                mem_pct=parts[3],
                command=parts[10],
            )
        )
    return processes


def parse_df_output(output: str) -> list[DiskInfo]:
    """Parse `df -h` lines into structured records (skips header)."""
    mounts: list[DiskInfo] = []
    for line in output.strip().splitlines()[1:]:
        parts = line.split()
        if len(parts) < 6:
            continue
        mounts.append(
            DiskInfo(
                filesystem=parts[0],
                size=parts[1],
                used=parts[2],
                avail=parts[3],
                use_pct=parts[4],
                mounted_on=parts[5],
            )
        )
    return mounts


def collect_system_snapshot(timeout: float = 5.0) -> dict[str, object]:
    """Run ps + df and return parsed snapshot for runbooks / health scripts."""
    ps_result = run_command(["ps", "aux"], timeout=timeout)
    df_result = run_command(["df", "-h"], timeout=timeout)

    return {
        "ps": {
            "returncode": ps_result.returncode,
            "processes": [p.__dict__ for p in parse_ps_output(ps_result.stdout)],
            "stderr": ps_result.stderr.strip(),
        },
        "df": {
            "returncode": df_result.returncode,
            "mounts": [m.__dict__ for m in parse_df_output(df_result.stdout)],
            "stderr": df_result.stderr.strip(),
        },
    }
