"""Step 18 solution — access log parser (error rate + p95 latency)."""

from __future__ import annotations

import math
import re
from typing import Any

from python.common.logging_setup import get_logger, new_trace_id
from python.common.paths import sample_data_path

logger = get_logger("log_parser", json_logs=True)

# Combined log: IP - - [ts] "METHOD path HTTP/1.x" status bytes latency_seconds
_ACCESS_LOG_RE = re.compile(
    r'"[A-Z]+ [^"]+" (?P<status>\d{3}) (?P<bytes>\d+) (?P<latency_sec>[\d.]+)$'
)


def access_log_path() -> Any:
    return sample_data_path("logs", "access.log")


def parse_access_log_line(line: str) -> dict[str, Any] | None:
    """Parse one access.log line; return None for blank or malformed lines."""
    stripped = line.strip()
    if not stripped:
        return None
    match = _ACCESS_LOG_RE.search(stripped)
    if not match:
        return None
    status = int(match.group("status"))
    latency_ms = round(float(match.group("latency_sec")) * 1000, 3)
    return {
        "status": status,
        "bytes": int(match.group("bytes")),
        "latency_ms": latency_ms,
        "is_error": status >= 500,
    }


def parse_access_log(path: Any | None = None) -> list[dict[str, Any]]:
    """Parse all valid lines from the access log file."""
    log_path = path or access_log_path()
    records: list[dict[str, Any]] = []
    with log_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            record = parse_access_log_line(line)
            if record is not None:
                records.append(record)
    return records


def compute_error_rate(records: list[dict[str, Any]]) -> float:
    """Fraction of requests with HTTP 5xx status."""
    if not records:
        return 0.0
    errors = sum(1 for r in records if r.get("is_error"))
    return round(errors / len(records), 4)


def compute_p95_latency_ms(records: list[dict[str, Any]]) -> float:
    """Nearest-rank 95th percentile latency in milliseconds."""
    latencies = sorted(float(r["latency_ms"]) for r in records)
    if not latencies:
        return 0.0
    index = min(len(latencies) - 1, max(0, math.ceil(0.95 * len(latencies)) - 1))
    return latencies[index]


def analyze_access_log(path: Any | None = None) -> dict[str, Any]:
    """Return summary stats for an access log file."""
    records = parse_access_log(path)
    return {
        "total_requests": len(records),
        "error_count_5xx": sum(1 for r in records if r.get("is_error")),
        "error_rate": compute_error_rate(records),
        "latency_p95_ms": compute_p95_latency_ms(records),
    }


def main() -> None:
    trace_id = new_trace_id()
    summary = analyze_access_log()
    logger.info(
        f"parsed {summary['total_requests']} requests error_rate={summary['error_rate']}",
        extra={"trace_id": trace_id, "service": "log_parser"},
    )
    print("Access log summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
