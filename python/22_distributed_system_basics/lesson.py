"""Step 30 — Distributed systems: heartbeat leader election."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (production) ---
# Singleton workers (queue consumers, cron leaders, shard coordinators) must have exactly
# one active leader. Split-brain doubles processing; no leader stalls the pipeline.
# Heartbeats + leases (etcd, Consul, K8s Lease API) detect failed nodes and trigger failover.

# --- Production patterns ---
# - Fencing tokens: new leader must prove it still owns the lease before writes
# - Graceful shutdown: step down before SIGTERM completes to speed failover
# - Monitor leader_changes_total — flapping leadership indicates network partitions

# --- Java developer note ---
# Apache Curator LeaderSelector and Hazelcast cluster leadership solve the same problem.
# This simulation uses priority + heartbeat timeout only — production adds quorum.

# --- How to run ---
# ./run.sh 30
# ./check.sh 30


def main() -> None:
    from solution import LeaderElectionCluster

    cluster = LeaderElectionCluster(heartbeat_timeout=5.0)
    now = 100.0
    for node_id, priority in (("az-a", 2), ("az-b", 3), ("az-c", 1)):
        cluster.register(node_id, priority=priority)
        cluster.heartbeat(node_id, now=now)
    leader = cluster.elect_leader(now=now)
    logger.info("Elected leader: %s", leader)
    cluster.mark_dead(leader)
    logger.info("After failover, leader: %s", cluster.failover(now=now + 1))


if __name__ == "__main__":
    main()
