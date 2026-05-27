"""Tests for Step 17 — monitoring agent."""

from __future__ import annotations

from pathlib import Path

import pytest
from python.common import paths as paths_module
from python.common.paths import output_path, sample_data_path
import json
from unittest.mock import patch

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

@pytest.fixture(autouse=True)
def _reset_repo_root(monkeypatch: pytest.MonkeyPatch) -> None:
    root = Path(__file__).resolve().parents[2]
    monkeypatch.setattr(paths_module, "REPO_ROOT", root, raising=False)


def test_latest_metrics_path() -> None:
    assert mod.latest_metrics_path() == sample_data_path("metrics", "latest.json")


def test_load_agent_config() -> None:
    config = mod.load_agent_config()
    assert config["check_interval_seconds"] == 10


def test_load_agent_config_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SRE_CHECK_INTERVAL_SECONDS", "5")
    config = mod.load_agent_config()
    assert config["check_interval_seconds"] == 5


def test_collect_metrics() -> None:
    metrics = mod.collect_metrics()
    assert "timestamp" in metrics
    assert "cpu_percent" in metrics
    assert "memory_percent" in metrics
    assert 0 <= metrics["cpu_percent"] <= 100
    assert 0 <= metrics["memory_percent"] <= 100


def test_write_latest_metrics(tmp_path: Path) -> None:
    target = tmp_path / "latest.json"
    metrics = {"cpu_percent": 10.0, "memory_percent": 20.0, "timestamp": "t", "host": "test"}
    mod.write_latest_metrics(metrics, path=target)
    data = json.loads(target.read_text(encoding="utf-8"))
    assert data["cpu_percent"] == 10.0


def test_run_agent_once_exits(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "latest.json"
    monkeypatch.setattr(mod, "latest_metrics_path", lambda: target)
    mod.run_agent(interval_seconds=1, once=True)
    assert target.exists()


def test_run_agent_respects_sre_agent_once_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "latest.json"
    monkeypatch.setenv("SRE_AGENT_ONCE", "1")
    monkeypatch.setattr(mod, "latest_metrics_path", lambda: target)
    mod.run_agent(interval_seconds=60)
    assert target.exists()


def test_run_agent_uses_collect_metrics(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    target = tmp_path / "latest.json"
    fake_metrics = {
        "timestamp": "2026-05-27T10:00:00Z",
        "host": "test",
        "cpu_percent": 42.0,
        "memory_percent": 55.0,
    }
    monkeypatch.setattr(mod, "collect_metrics", lambda: fake_metrics)
    monkeypatch.setattr(mod, "latest_metrics_path", lambda: target)
    mod.run_agent(once=True)
    data = json.loads(target.read_text(encoding="utf-8"))
    assert data == fake_metrics

