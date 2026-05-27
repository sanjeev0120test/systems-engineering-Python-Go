"""Step 30 exercise — heartbeat leader election simulation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ClusterNode:
    node_id: str
    priority: int = 0
    last_heartbeat: float = 0.0
    alive: bool = True

    def heartbeat(self, now: float | None = None) -> None:
        raise NotImplementedError("Implement heartbeat")


class LeaderElectionCluster:
    def __init__(self, *, heartbeat_timeout: float = 5.0) -> None:
        raise NotImplementedError("Implement LeaderElectionCluster")

    def register(self, node_id: str, *, priority: int = 0) -> ClusterNode:
        raise NotImplementedError("Implement register")

    def heartbeat(self, node_id: str, now: float | None = None) -> None:
        raise NotImplementedError("Implement heartbeat")

    def mark_dead(self, node_id: str) -> None:
        raise NotImplementedError("Implement mark_dead")

    def elect_leader(self, now: float | None = None) -> str | None:
        raise NotImplementedError("Implement elect_leader")

    def failover(self, now: float | None = None) -> str | None:
        raise NotImplementedError("Implement failover")


def main() -> None:
    print("Implement leader election, then run: ./check.sh 30")


if __name__ == "__main__":
    main()
