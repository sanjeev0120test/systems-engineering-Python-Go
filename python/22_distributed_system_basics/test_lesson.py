"""Tests for Step 30 — distributed leader election."""

from __future__ import annotations

from pathlib import Path

import pytest

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

def test_elects_highest_priority_node() -> None:
    cluster = LeaderElectionCluster(heartbeat_timeout=10.0)
    now = 1000.0
    cluster.register("node-a", priority=1)
    cluster.register("node-b", priority=3)
    cluster.register("node-c", priority=2)
    for node_id in ("node-a", "node-b", "node-c"):
        cluster.heartbeat(node_id, now=now)
    assert cluster.elect_leader(now=now) == "node-b"


def test_failover_skips_dead_nodes() -> None:
    cluster = LeaderElectionCluster(heartbeat_timeout=10.0)
    now = 2000.0
    cluster.register("node-a", priority=5)
    cluster.register("node-b", priority=4)
    cluster.heartbeat("node-a", now=now)
    cluster.heartbeat("node-b", now=now)
    cluster.mark_dead("node-a")
    assert cluster.failover(now=now) == "node-b"


def test_stale_heartbeat_triggers_re_election() -> None:
    cluster = LeaderElectionCluster(heartbeat_timeout=2.0)
    t0 = 5000.0
    cluster.register("node-a", priority=2)
    cluster.register("node-b", priority=1)
    cluster.heartbeat("node-a", now=t0)
    cluster.heartbeat("node-b", now=t0)
    assert cluster.elect_leader(now=t0) == "node-a"
    cluster.heartbeat("node-b", now=t0 + 2.9)
    assert cluster.elect_leader(now=t0 + 3.0) == "node-b"

