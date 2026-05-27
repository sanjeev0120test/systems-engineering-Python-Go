"""Step 2 solution — control flow for filtering unhealthy hosts."""

from __future__ import annotations


def filter_unhealthy(hosts: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return hosts where healthy is False."""
    unhealthy: list[dict[str, object]] = []
    for host in hosts:
        if host.get("healthy") is False:
            unhealthy.append(host)
    return unhealthy


def count_by_status(hosts: list[dict[str, object]]) -> dict[str, int]:
    """Count hosts grouped by status string (healthy / degraded / down)."""
    counts: dict[str, int] = {}
    for host in hosts:
        status = str(host.get("status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    return counts


def first_host_exceeding_retries(hosts: list[dict[str, object]], limit: int) -> str | None:
    """Return hostname of first host whose retry_count exceeds limit (while-style scan)."""
    index = 0
    while index < len(hosts):
        host = hosts[index]
        retries = host.get("retry_count", 0)
        if isinstance(retries, int) and retries > limit:
            return str(host.get("hostname"))
        index += 1
    return None


def summarize_fleet(hosts: list[dict[str, object]]) -> str:
    """One-line fleet summary for a status dashboard."""
    total = len(hosts)
    unhealthy = filter_unhealthy(hosts)
    return f"fleet: {total} hosts, {len(unhealthy)} unhealthy"
