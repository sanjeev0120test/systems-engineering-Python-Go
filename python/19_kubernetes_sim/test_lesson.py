"""Tests for Step 27 — Kubernetes scheduler simulator."""

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

def test_scheduler_places_pods_first_fit() -> None:
    nodes = [
        Node("node-a", cpu_capacity=4, memory_capacity=8192),
        Node("node-b", cpu_capacity=2, memory_capacity=4096),
    ]
    pods = [
        Pod("web-1", cpu_request=1, memory_request=512),
        Pod("web-2", cpu_request=1, memory_request=512),
        Pod("batch-1", cpu_request=2, memory_request=2048),
    ]
    result = PodScheduler(nodes).schedule(pods)
    assert result.scheduled["web-1"] == "node-a"
    assert result.scheduled["batch-1"] == "node-a"
    assert result.pending == []


def test_unschedulable_pod_goes_pending() -> None:
    nodes = [Node("small", cpu_capacity=1, memory_capacity=512)]
    pods = [Pod("huge", cpu_request=8, memory_request=4096)]
    result = PodScheduler(nodes).schedule(pods)
    assert result.pending == ["huge"]


def test_node_selector_limits_candidates() -> None:
    nodes = [
        Node("gpu-1", cpu_capacity=8, memory_capacity=16384),
        Node("cpu-1", cpu_capacity=8, memory_capacity=16384),
    ]
    pods = [Pod("training", cpu_request=2, memory_request=1024, node_selector="gpu-1")]
    result = PodScheduler(nodes).schedule(pods)
    assert result.scheduled["training"] == "gpu-1"


def test_cluster_utilization() -> None:
    node = Node("node-a", cpu_capacity=4, memory_capacity=100)
    node.allocate("p1", cpu=2, memory=50)
    util = cluster_utilization([node])
    assert util["node-a"] == 0.5

