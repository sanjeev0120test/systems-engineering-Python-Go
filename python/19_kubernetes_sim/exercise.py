"""Step 27 exercise — Kubernetes pod scheduler simulator."""

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
        raise NotImplementedError("Implement Node.can_fit")

    def allocate(self, pod_name: str, cpu: int, memory: int) -> None:
        raise NotImplementedError("Implement Node.allocate")


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
    def __init__(self, nodes: list[Node]) -> None:
        raise NotImplementedError("Implement PodScheduler")

    def schedule(self, pods: list[Pod]) -> SchedulingResult:
        raise NotImplementedError("Implement schedule")


def cluster_utilization(nodes: list[Node]) -> dict[str, float]:
    raise NotImplementedError("Implement cluster_utilization")


def main() -> None:
    print("Implement k8s scheduler sim, then run: ./check.sh 27")


if __name__ == "__main__":
    main()
