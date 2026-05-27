"""Step 4 tests."""

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

RAW = [
    {"hostname": "web-01", "role": "frontend", "ip": "10.0.0.1", "healthy": True, "tags": ["prod"]},
    {"hostname": "api-01", "role": "backend", "ip": "10.0.0.2", "healthy": False, "tags": []},
    {"hostname": "db-01", "role": "backend", "ip": "10.0.0.3", "healthy": True, "tags": ["prod", "pci"]},
]


def test_server_display_name() -> None:
    server = solution.Server("web-01", "frontend", "10.0.0.1")
    assert server.display_name() == "web-01 (frontend)"


def test_mark_unhealthy() -> None:
    server = solution.Server("api-01", "backend", "10.0.0.2")
    server.mark_unhealthy()
    assert server.healthy is False


def test_build_inventory() -> None:
    servers = solution.build_inventory(RAW)
    assert len(servers) == 3
    assert servers[0].tags == ["prod"]


def test_find_by_role() -> None:
    servers = solution.build_inventory(RAW)
    backends = solution.find_by_role(servers, "backend")
    assert len(backends) == 2


def test_unhealthy_hostnames() -> None:
    servers = solution.build_inventory(RAW)
    assert solution.unhealthy_hostnames(servers) == ["api-01"]

