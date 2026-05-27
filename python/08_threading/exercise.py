"""Step 14 exercise — parallel health checks with ThreadPoolExecutor."""

from __future__ import annotations

from typing import Any


def check_url(url: str, timeout: float = 2.0) -> dict[str, Any]:
    """TODO: GET url with requests, return ok/status_code/latency_ms."""
    raise NotImplementedError("Implement check_url")


def parallel_health_checks(
    urls: list[str],
    *,
    max_workers: int = 4,
    timeout: float = 2.0,
) -> list[dict[str, Any]]:
    """TODO: use ThreadPoolExecutor + as_completed to check all urls."""
    raise NotImplementedError("Implement parallel_health_checks")


def main() -> None:
    urls = [
        "http://127.0.0.1:8080/health",
        "http://127.0.0.1:8080/ready",
    ]
    for row in parallel_health_checks(urls):
        print(row)


if __name__ == "__main__":
    main()
