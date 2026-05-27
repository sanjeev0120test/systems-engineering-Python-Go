"""Step 27 — Kubernetes pod scheduler simulator."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (production) ---
# Pending pods (unschedulable) mean your cluster is out of capacity or misconfigured
# (taints, node selectors, resource requests too large). Scheduler decisions affect
# blast radius — spreading replicas across nodes/AZs avoids single-host failures.

# --- Production patterns ---
# - Requests vs limits: scheduler uses requests; oversubscription causes OOM kills
# - PodDisruptionBudgets cap voluntary evictions during node drains
# - Monitor pending pod count and cluster utilization — scale before users notice

# --- Java developer note ---
# You won't implement kube-scheduler in Java, but platform teams tune scheduling the
# same way: affinity, anti-affinity, priority classes. This sim uses first-fit only.

# --- How to run ---
# ./run.sh 27
# ./check.sh 27


def main() -> None:
    from solution import Node, Pod, PodScheduler, cluster_utilization

    nodes = [
        Node("node-a", cpu_capacity=4, memory_capacity=8192),
        Node("node-b", cpu_capacity=4, memory_capacity=8192),
    ]
    pods = [
        Pod("api-1", cpu_request=1, memory_request=512),
        Pod("api-2", cpu_request=1, memory_request=512),
        Pod("worker-1", cpu_request=2, memory_request=2048),
    ]
    result = PodScheduler(nodes).schedule(pods)
    logger.info("Scheduled: %s", result.scheduled)
    logger.info("Pending: %s", result.pending)
    logger.info("Utilization: %s", cluster_utilization(nodes))


if __name__ == "__main__":
    main()
