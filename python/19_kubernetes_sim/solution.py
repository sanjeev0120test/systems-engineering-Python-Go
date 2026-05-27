"""Step 27 solution — Kubernetes pod scheduler simulator (no real cluster)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Node:
    name: str
    cpu_capacity: int
    memory_capacity: int
    cpu_used: int = 0
    memory_used: int = 0
    pods: list[str] = field(default_factory=list)

    def can_fit(self, cpu: int, memory: int) -> bool:
        return self.cpu_used + cpu <= self.cpu_capacity and self.memory_used + memory <= self.memory_capacity

    def allocate(self, pod_name: str, cpu: int, memory: int) -> None:
        if not self.can_fit(cpu, memory):
            raise ValueError(f"node {self.name} cannot fit pod {pod_name}")
        self.cpu_used += cpu
        self.memory_used += memory
        self.pods.append(pod_name)


@dataclass(frozen=True)
class Pod:
    name: str
    cpu_request: int
    memory_request: int
    node_selector: str | None = None


@dataclass(frozen=True)
class SchedulingResult:
    scheduled: dict[str, str]
    pending: list[str]


class PodScheduler:
    """Greedy first-fit scheduler across nodes."""

    def __init__(self, nodes: list[Node]) -> None:
        self.nodes = nodes

    def schedule(self, pods: list[Pod]) -> SchedulingResult:
        scheduled: dict[str, str] = {}
        pending: list[str] = []
        for pod in pods:
            target = self._select_node(pod)
            if target is None:
                pending.append(pod.name)
                continue
            target.allocate(pod.name, pod.cpu_request, pod.memory_request)
            scheduled[pod.name] = target.name
        return SchedulingResult(scheduled=scheduled, pending=pending)

    def _select_node(self, pod: Pod) -> Node | None:
        candidates = self.nodes
        if pod.node_selector:
            candidates = [node for node in self.nodes if node.name == pod.node_selector]
        for node in candidates:
            if node.can_fit(pod.cpu_request, pod.memory_request):
                return node
        return None


def cluster_utilization(nodes: list[Node]) -> dict[str, float]:
    """Return CPU and memory utilization ratios per node."""
    stats: dict[str, float] = {}
    for node in nodes:
        cpu_ratio = node.cpu_used / node.cpu_capacity if node.cpu_capacity else 0.0
        mem_ratio = node.memory_used / node.memory_capacity if node.memory_capacity else 0.0
        stats[node.name] = round(max(cpu_ratio, mem_ratio), 4)
    return stats
