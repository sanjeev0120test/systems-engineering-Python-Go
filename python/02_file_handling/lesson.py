"""
Step 7 — File handling for automation workflows
========================================

Read and write logs safely using `with open(...)` and `pathlib.Path`.
Repo paths come from `python.common.paths` so scripts work on Windows, WSL, and Linux.
"""

from __future__ import annotations

from pathlib import Path

from python.common.paths import output_path, sample_data_path
from python.common.paths import REPO_ROOT

# ---------------------------------------------------------------------------
# JAVA BRIDGE
# ---------------------------------------------------------------------------
# Java                          | Python
# ------------------------------|------------------------------------------
# try (BufferedReader r = ...)  | with path.open("r") as handle:
# Files.readAllLines(path)      | path.read_text(encoding="utf-8").splitlines()
# Paths.get("logs", "app.log")  | Path("logs") / "app.log"
# FileWriter + flush/close      | with path.open("w") as handle: handle.write(...)
# NIO Files.createDirectories   | path.parent.mkdir(parents=True, exist_ok=True)
#
# Python's `with` is like try-with-resources: the file closes even on exceptions.
# Always pass encoding="utf-8" — default locale encoding breaks in CI/containers.

# ---------------------------------------------------------------------------
# PRODUCTION USE CASES
# ---------------------------------------------------------------------------
# - Tail and summarize access logs during incident triage
# - Write health-check reports under sample_data/output/ (gitignored artifacts)
# - Ship rotated logs to object storage — same read/write patterns, different Path root
# - Parse nginx/apache logs with pathlib so relative paths never depend on cwd


def demo_read_with_context_manager(log_path: Path) -> int:
    """Count lines using `with open` — preferred over manual close()."""
    line_count = 0
    with log_path.open("r", encoding="utf-8") as handle:
        for _ in handle:
            line_count += 1
    return line_count


def demo_pathlib_basics() -> None:
    """Path objects compose safely across OS path separators."""
    log_path = sample_data_path("logs", "access.log")
    print(f"Repo root:     {REPO_ROOT}")
    print(f"Log exists:    {log_path.exists()}  ({log_path})")
    print(f"Suffix/name:   {log_path.suffix!r} / {log_path.name}")


def demo_write_report(counts: dict[int, int]) -> Path:
    """Write runtime output via output_path() — parents created automatically."""
    report_path = output_path("lesson7_demo_report.txt")
    lines = [f"{code}: {count}" for code, count in sorted(counts.items())]
    with report_path.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")
    return report_path


def main() -> None:
    demo_pathlib_basics()

    access_log = sample_data_path("logs", "access.log")
    total_lines = demo_read_with_context_manager(access_log)
    print(f"Access log lines: {total_lines}")

    # Quick status tally (lesson demo — full logic lives in solution.py)
    status_counts: dict[int, int] = {}
    with access_log.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                code = int(line.split('"', 2)[2].strip().split()[0])
            except (IndexError, ValueError):
                continue
            status_counts[code] = status_counts.get(code, 0) + 1

    print("Status breakdown:", status_counts)
    report = demo_write_report(status_counts)
    print(f"Wrote demo report: {report}")


if __name__ == "__main__":
    main()
