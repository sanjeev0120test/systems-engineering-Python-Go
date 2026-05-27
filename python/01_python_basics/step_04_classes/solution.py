"""Step 4 solution — classes and dataclasses for server inventory."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Server:
    """Single machine in the service inventory (like a Java record/POJO)."""

    hostname: str
    role: str
    ip: str
    healthy: bool = True
    tags: list[str] = field(default_factory=list)

    def display_name(self) -> str:
        """Short identifier for dashboards."""
        return f"{self.hostname} ({self.role})"

    def mark_unhealthy(self) -> None:
        """Flip health flag after failed probe."""
        self.healthy = False


def build_inventory(raw_hosts: list[dict[str, object]]) -> list[Server]:
    """Convert YAML/JSON dict rows into Server objects."""
    inventory: list[Server] = []
    for row in raw_hosts:
        tags_raw = row.get("tags", [])
        tags = [str(tag) for tag in tags_raw] if isinstance(tags_raw, list) else []
        server = Server(
            hostname=str(row["hostname"]),
            role=str(row.get("role", "unknown")),
            ip=str(row.get("ip", "0.0.0.0")),
            healthy=bool(row.get("healthy", True)),
            tags=tags,
        )
        inventory.append(server)
    return inventory


def find_by_role(servers: list[Server], role: str) -> list[Server]:
    """Filter inventory by role (frontend, backend, database, etc.)."""
    return [server for server in servers if server.role == role]


def unhealthy_hostnames(servers: list[Server]) -> list[str]:
    """Return hostnames that failed health checks."""
    return [server.hostname for server in servers if not server.healthy]
