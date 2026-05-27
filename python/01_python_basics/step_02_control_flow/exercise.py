"""Step 2 exercise — control flow TODOs."""

from __future__ import annotations

SAMPLE_HOSTS: list[dict[str, object]] = [
    {"hostname": "web-01", "healthy": True, "status": "healthy", "retry_count": 0},
    {"hostname": "web-02", "healthy": False, "status": "down", "retry_count": 5},
    {"hostname": "api-01", "healthy": True, "status": "degraded", "retry_count": 2},
    {"hostname": "api-02", "healthy": False, "status": "down", "retry_count": 8},
]


def filter_unhealthy(hosts: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return hosts where healthy is False."""
    # TODO: use a for loop and if statement
    raise NotImplementedError("Implement filter_unhealthy")


def count_by_status(hosts: list[dict[str, object]]) -> dict[str, int]:
    """Count hosts grouped by status string."""
    # TODO: iterate hosts and increment counts dict
    raise NotImplementedError("Implement count_by_status")


def first_host_exceeding_retries(hosts: list[dict[str, object]], limit: int) -> str | None:
    """Return hostname of first host whose retry_count exceeds limit."""
    # TODO: use a while loop with an index
    raise NotImplementedError("Implement first_host_exceeding_retries")


def summarize_fleet(hosts: list[dict[str, object]]) -> str:
    """One-line fleet summary for a status dashboard."""
    # TODO: call filter_unhealthy and build an f-string summary
    raise NotImplementedError("Implement summarize_fleet")


if __name__ == "__main__":
    print("Exercise Step 2 — implement TODOs using if/for/while.")
    print(f"Sample fleet size: {len(SAMPLE_HOSTS)}")
