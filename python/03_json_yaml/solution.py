"""Step 8 solution — JSON and YAML config for service configuration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from python.common.config_loader import env, load_service_config, load_yaml
from python.common.paths import sample_data_path


def service_config_path() -> Path:
    return sample_data_path("configs", "service.yaml")


def host_metrics_path() -> Path:
    return sample_data_path("metrics", "host_metrics.json")


def load_service_config_from_sample(env_prefix: str = "LAB_") -> dict[str, Any]:
    """Load service.yaml with optional LAB_* environment overrides."""
    return load_service_config(service_config_path(), env_prefix=env_prefix)


def load_host_metrics_from_sample() -> dict[str, Any]:
    """Load JSON host metrics snapshot."""
    with host_metrics_path().open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("host_metrics.json must contain a JSON object")
    return data


def get_check_interval_seconds(config: dict[str, Any]) -> int:
    value = config.get("check_interval_seconds", 30)
    return int(value)


def get_endpoint_urls(config: dict[str, Any]) -> list[str]:
    endpoints = config.get("endpoints", [])
    urls: list[str] = []
    for item in endpoints:
        if isinstance(item, dict) and "url" in item:
            urls.append(str(item["url"]))
    return urls


def is_host_overloaded(
    metrics: dict[str, Any],
    *,
    cpu_threshold: float = 80.0,
    memory_threshold: float = 80.0,
) -> bool:
    cpu = float(metrics.get("cpu_percent", 0))
    memory = float(metrics.get("memory_percent", 0))
    return cpu >= cpu_threshold or memory >= memory_threshold


if __name__ == "__main__":
    cfg = load_service_config_from_sample()
    metrics = load_host_metrics_from_sample()
    print("Service:", cfg.get("service_name"))
    print("Endpoints:", get_endpoint_urls(cfg))
    print("Check every:", get_check_interval_seconds(cfg), "s")
    print("Overloaded:", is_host_overloaded(metrics))
