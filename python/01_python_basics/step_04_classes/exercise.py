"""Step 4 exercise — classes and @dataclass TODOs."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Server:
    """Single machine in the service inventory."""

    hostname: str
    role: str
    ip: str
    healthy: bool = True
    tags: list[str] = field(default_factory=list)

    def display_name(self) -> str:
        # TODO: return f"{hostname} ({role})"
        raise NotImplementedError("Implement display_name")

    def mark_unhealthy(self) -> None:
        # TODO: set healthy to False
        raise NotImplementedError("Implement mark_unhealthy")


def build_inventory(raw_hosts: list[dict[str, object]]) -> list[Server]:
    """Convert dict rows into Server objects."""
    # TODO: loop raw_hosts and construct Server instances
    raise NotImplementedError("Implement build_inventory")


def find_by_role(servers: list[Server], role: str) -> list[Server]:
    """Filter inventory by role."""
    # TODO: list comprehension filtering by role
    raise NotImplementedError("Implement find_by_role")


def unhealthy_hostnames(servers: list[Server]) -> list[str]:
    """Return hostnames that failed health checks."""
    # TODO: collect hostname where healthy is False
    raise NotImplementedError("Implement unhealthy_hostnames")


if __name__ == "__main__":
    sample = [
        {"hostname": "web-01", "role": "frontend", "ip": "10.0.0.1", "healthy": True},
        {"hostname": "api-01", "role": "backend", "ip": "10.0.0.2", "healthy": False},
    ]
    print("Exercise Step 4 — implement Server dataclass helpers.")
    print(f"Sample rows: {len(sample)}")
