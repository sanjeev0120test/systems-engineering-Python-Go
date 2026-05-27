"""Step 7 exercise — implement file handling helpers (see solution.py if stuck)."""

from __future__ import annotations

from pathlib import Path


def read_log_lines(log_path: Path) -> list[str]:
    """Read a text log file, skipping blank lines."""
    raise NotImplementedError("Use `with log_path.open(...) as handle` and return non-blank lines.")


def parse_status_code(line: str) -> int | None:
    """Extract HTTP status code from a combined log-format line."""
    raise NotImplementedError("Split on quotes and parse the token after the request.")


def count_http_statuses(lines: list[str]) -> dict[int, int]:
    """Tally status codes across log lines."""
    raise NotImplementedError("Call parse_status_code for each line and increment a dict.")


def write_status_report(counts: dict[int, int], report_path: Path) -> None:
    """Write TSV status summary (pathlib handles parent dirs)."""
    raise NotImplementedError("Write header + sorted rows with tab separators.")


def process_access_log(
    log_parts: tuple[str, ...] = ("logs", "access.log"),
    report_parts: tuple[str, ...] = ("access_log_status_counts.txt",),
) -> dict[int, int]:
    """Read sample access log, summarize statuses, write report to output/."""
    raise NotImplementedError("Use sample_data_path() and output_path() from python.common.paths.")


if __name__ == "__main__":
    print("Implement the functions above, then run: ./check.sh 7")
