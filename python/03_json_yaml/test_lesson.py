"""Tests for Step 8 — JSON and YAML."""

from __future__ import annotations

from pathlib import Path

import pytest
from python.common.paths import output_path, sample_data_path
from unittest.mock import patch

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)


def test_service_config_path_points_to_yaml() -> None:
    path = mod.service_config_path()
    assert path == sample_data_path("configs", "service.yaml")
    assert path.exists()


def test_load_service_config_from_sample() -> None:
    config = mod.load_service_config_from_sample()
    assert config["service_name"] == "payment-api"
    assert config["check_interval_seconds"] == 10
    assert len(config["endpoints"]) == 2


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LAB_ENVIRONMENT", "prod")
    config = mod.load_service_config_from_sample()
    assert config["environment"] == "prod"


def test_load_host_metrics_from_sample() -> None:
    metrics = mod.load_host_metrics_from_sample()
    assert metrics["host"] == "localhost"
    assert metrics["cpu_percent"] == 42.5
    assert metrics["memory_percent"] == 68.2


def test_get_endpoint_urls() -> None:
    config = mod.load_service_config_from_sample()
    urls = mod.get_endpoint_urls(config)
    assert urls == [
        "http://127.0.0.1:8080/health",
        "http://127.0.0.1:8080/ready",
    ]


def test_get_check_interval_seconds_default() -> None:
    assert mod.get_check_interval_seconds({}) == 30
    assert mod.get_check_interval_seconds({"check_interval_seconds": 15}) == 15


def test_is_host_overloaded() -> None:
    sample = mod.load_host_metrics_from_sample()
    assert mod.is_host_overloaded(sample, cpu_threshold=80.0, memory_threshold=80.0) is False
    assert mod.is_host_overloaded(sample, cpu_threshold=40.0, memory_threshold=80.0) is True
    assert mod.is_host_overloaded(sample, cpu_threshold=80.0, memory_threshold=65.0) is True

