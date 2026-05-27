"""Step 30 solution — heartbeat-based leader election simulation."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class ClusterNode:
    node_id: str
    priority: int = 0
    last_heartbeat: float = field(default_factory=time.monotonic)
    alive: bool = True

    def heartbeat(self, now: float | None = None) -> None:
        self.last_heartbeat = now if now is not None else time.monotonic()
        self.alive = True


class LeaderElectionCluster:
    """Simple distributed cluster: highest-priority alive node wins leadership."""

    def __init__(self, *, heartbeat_timeout: float = 5.0) -> None:
        self.heartbeat_timeout = heartbeat_timeout
        self.nodes: dict[str, ClusterNode] = {}

    def register(self, node_id: str, *, priority: int = 0) -> ClusterNode:
        node = ClusterNode(node_id=node_id, priority=priority)
        self.nodes[node_id] = node
        return node

    def heartbeat(self, node_id: str, now: float | None = None) -> None:
        if node_id not in self.nodes:
            raise KeyError(f"unknown node: {node_id}")
        self.nodes[node_id].heartbeat(now)

    def mark_dead(self, node_id: str) -> None:
        self.nodes[node_id].alive = False

    def _is_alive(self, node: ClusterNode, now: float) -> bool:
        if not node.alive:
            return False
        return (now - node.last_heartbeat) <= self.heartbeat_timeout

    def elect_leader(self, now: float | None = None) -> str | None:
        current = now if now is not None else time.monotonic()
        candidates = [node for node in self.nodes.values() if self._is_alive(node, current)]
        if not candidates:
            return None
        candidates.sort(key=lambda node: (-node.priority, node.node_id))
        return candidates[0].node_id

    def failover(self, now: float | None = None) -> str | None:
        """Re-run election after node loss — returns new leader id."""
        return self.elect_leader(now)
