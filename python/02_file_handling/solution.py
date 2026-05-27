"""Step 7 solution — file I/O with pathlib and context managers."""

from __future__ import annotations

from pathlib import Path

from python.common.paths import output_path, sample_data_path


def read_log_lines(log_path: Path) -> list[str]:
    """Read a text log file, skipping blank lines."""
    with log_path.open("r", encoding="utf-8") as handle:
        return [line.rstrip("\n") for line in handle if line.strip()]


def parse_status_code(line: str) -> int | None:
    """Extract HTTP status code from a combined log-format line."""
    # Example: 127.0.0.1 - - [...] "GET /health HTTP/1.1" 200 12 0.003
    try:
        after_request = line.split('"', 2)[2].strip()
        return int(after_request.split()[0])
    except (IndexError, ValueError):
        return None


def count_http_statuses(lines: list[str]) -> dict[int, int]:
    """Tally status codes across log lines."""
    counts: dict[int, int] = {}
    for line in lines:
        code = parse_status_code(line)
        if code is not None:
            counts[code] = counts.get(code, 0) + 1
    return counts


def write_status_report(counts: dict[int, int], report_path: Path) -> None:
    """Write TSV status summary (pathlib handles parent dirs)."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [f"{code}\t{count}" for code, count in sorted(counts.items())]
    with report_path.open("w", encoding="utf-8") as handle:
        handle.write("status_code\tcount\n")
        handle.write("\n".join(rows))
        handle.write("\n")


def process_access_log(
    log_parts: tuple[str, ...] = ("logs", "access.log"),
    report_parts: tuple[str, ...] = ("access_log_status_counts.txt",),
) -> dict[int, int]:
    """Read sample access log, summarize statuses, write report to output/."""
    log_path = sample_data_path(*log_parts)
    report_path = output_path(*report_parts)
    lines = read_log_lines(log_path)
    counts = count_http_statuses(lines)
    write_status_report(counts, report_path)
    return counts


if __name__ == "__main__":
    summary = process_access_log()
    print("Status counts:", summary)
