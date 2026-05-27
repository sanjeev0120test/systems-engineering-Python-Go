"""Tests for Step 10 — subprocess parsing (platform-independent unit tests)."""

from __future__ import annotations

from pathlib import Path

import sys

import pytest

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

SAMPLE_PS = """\
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1  16896  1088 ?        Ss   Jan01   0:05 /sbin/init
ubuntu    1234  2.5  1.2 123456 7890 ?        Sl   10:00   0:01 python app.py
"""

SAMPLE_DF = """\
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   20G   28G  42% /
tmpfs           3.9G     0  3.9G   0% /dev/shm
"""


def test_parse_ps_output() -> None:
    processes = parse_ps_output(SAMPLE_PS)
    assert len(processes) == 2
    assert processes[0].user == "root"
    assert processes[0].pid == "1"
    assert processes[1].command == "python app.py"


def test_parse_df_output() -> None:
    mounts = parse_df_output(SAMPLE_DF)
    assert len(mounts) == 2
    assert mounts[0].filesystem == "/dev/sda1"
    assert mounts[0].use_pct == "42%"
    assert mounts[1].mounted_on == "/dev/shm"


@pytest.mark.skipif(sys.platform == "win32", reason="ps/df require WSL/Linux")
def test_run_command_ps() -> None:
    result = run_command(["ps", "aux"], timeout=5.0)
    assert result.returncode == 0
    assert "PID" in result.stdout or len(result.stdout.splitlines()) > 1


@pytest.mark.skipif(sys.platform == "win32", reason="ps/df require WSL/Linux")
def test_collect_system_snapshot() -> None:
    snapshot = collect_system_snapshot(timeout=5.0)
    assert snapshot["ps"]["returncode"] == 0  # type: ignore[index]
    assert snapshot["df"]["returncode"] == 0  # type: ignore[index]
    assert len(snapshot["ps"]["processes"]) > 0  # type: ignore[index]
    assert len(snapshot["df"]["mounts"]) > 0  # type: ignore[index]

