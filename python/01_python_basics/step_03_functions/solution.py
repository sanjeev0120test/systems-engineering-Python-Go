"""Step 3 solution — reusable functions for disk threshold checks."""

from __future__ import annotations


def is_disk_critical(used_percent: float, threshold: float = 90.0) -> bool:
    """Return True when disk usage meets or exceeds threshold."""
    return used_percent >= threshold


def summarize_disk_alert(
    hostname: str,
    used_percent: float,
    threshold: float = 90.0,
    mount: str = "/",
) -> str | None:
    """Return alert message when critical, else None (no alert needed)."""
    if not is_disk_critical(used_percent, threshold):
        return None
    return (
        f"DISK CRITICAL: {hostname} mount={mount} "
        f"used={used_percent:.1f}% threshold={threshold:.1f}%"
    )


def evaluate_hosts_disk(
    hosts: list[dict[str, object]],
    threshold: float = 90.0,
) -> list[str]:
    """Evaluate multiple hosts and return list of alert messages."""
    alerts: list[str] = []
    for host in hosts:
        hostname = str(host.get("hostname", "unknown"))
        used = float(host.get("disk_percent", 0.0))
        mount = str(host.get("mount", "/"))
        message = summarize_disk_alert(hostname, used, threshold, mount)
        if message:
            alerts.append(message)
    return alerts


def disk_status_label(used_percent: float, threshold: float = 90.0) -> str:
    """Short label for dashboards: ok / warn / critical."""
    if used_percent >= threshold:
        return "critical"
    if used_percent >= threshold * 0.85:
        return "warn"
    return "ok"
