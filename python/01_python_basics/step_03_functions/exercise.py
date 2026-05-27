"""Step 3 exercise — functions TODOs."""

from __future__ import annotations

SAMPLE_HOSTS: list[dict[str, object]] = [
    {"hostname": "web-01", "disk_percent": 72.0, "mount": "/"},
    {"hostname": "db-01", "disk_percent": 93.5, "mount": "/var/lib/mysql"},
    {"hostname": "cache-01", "disk_percent": 88.0, "mount": "/data"},
]


def is_disk_critical(used_percent: float, threshold: float = 90.0) -> bool:
    """Return True when disk usage meets or exceeds threshold."""
    # TODO: compare used_percent to threshold
    raise NotImplementedError("Implement is_disk_critical")


def summarize_disk_alert(
    hostname: str,
    used_percent: float,
    threshold: float = 90.0,
    mount: str = "/",
) -> str | None:
    """Return alert message when critical, else None."""
    # TODO: call is_disk_critical; return formatted f-string or None
    raise NotImplementedError("Implement summarize_disk_alert")


def evaluate_hosts_disk(
    hosts: list[dict[str, object]],
    threshold: float = 90.0,
) -> list[str]:
    """Evaluate multiple hosts and return list of alert messages."""
    # TODO: loop hosts, call summarize_disk_alert, collect non-None results
    raise NotImplementedError("Implement evaluate_hosts_disk")


def disk_status_label(used_percent: float, threshold: float = 90.0) -> str:
    """Short label for dashboards: ok / warn / critical."""
    # TODO: return critical/warn/ok based on thresholds
    raise NotImplementedError("Implement disk_status_label")


if __name__ == "__main__":
    print("Exercise Step 3 — implement reusable disk check functions.")
    print(f"Sample hosts: {len(SAMPLE_HOSTS)}")
