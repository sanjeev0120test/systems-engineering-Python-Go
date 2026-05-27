"""Step 18 exercise — access log parser."""

from __future__ import annotations

from typing import Any


def access_log_path() -> Any:
    raise NotImplementedError("Return sample_data_path('logs', 'access.log').")


def parse_access_log_line(line: str) -> dict[str, Any] | None:
    raise NotImplementedError("Extract status, bytes, latency_ms, is_error from one line.")


def parse_access_log(path: Any | None = None) -> list[dict[str, Any]]:
    raise NotImplementedError("Parse all valid lines from access.log.")


def compute_error_rate(records: list[dict[str, Any]]) -> float:
    raise NotImplementedError("Return fraction of 5xx responses.")


def compute_p95_latency_ms(records: list[dict[str, Any]]) -> float:
    raise NotImplementedError("Return 95th percentile latency in ms.")


def analyze_access_log(path: Any | None = None) -> dict[str, Any]:
    raise NotImplementedError("Return total_requests, error_rate, latency_p95_ms summary.")


if __name__ == "__main__":
    print("Implement the functions above, then run: ./check.sh 18")
