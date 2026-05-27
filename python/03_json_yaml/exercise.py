"""Step 8 exercise — parse YAML service config and JSON metrics."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def service_config_path() -> Path:
    raise NotImplementedError("Return sample_data_path('configs', 'service.yaml').")


def host_metrics_path() -> Path:
    raise NotImplementedError("Return sample_data_path('metrics', 'host_metrics.json').")


def load_service_config_from_sample(env_prefix: str = "SRE_") -> dict[str, Any]:
    raise NotImplementedError("Use load_service_config from python.common.config_loader.")


def load_host_metrics_from_sample() -> dict[str, Any]:
    raise NotImplementedError("Use json.load with a context-managed file handle.")


def get_check_interval_seconds(config: dict[str, Any]) -> int:
    raise NotImplementedError("Read check_interval_seconds with a sensible default.")


def get_endpoint_urls(config: dict[str, Any]) -> list[str]:
    raise NotImplementedError("Extract url fields from config['endpoints'].")


def is_host_overloaded(
    metrics: dict[str, Any],
    *,
    cpu_threshold: float = 80.0,
    memory_threshold: float = 80.0,
) -> bool:
    raise NotImplementedError("Compare cpu_percent and memory_percent to thresholds.")


if __name__ == "__main__":
    print("Implement the functions above, then run: ./check.sh 8")
