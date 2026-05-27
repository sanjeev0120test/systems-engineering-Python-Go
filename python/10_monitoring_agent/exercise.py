"""Step 17 exercise — CPU/memory monitoring agent."""

from __future__ import annotations

from typing import Any


def service_config_path() -> Any:
    raise NotImplementedError("Return sample_data_path('configs', 'service.yaml').")


def latest_metrics_path() -> Any:
    raise NotImplementedError("Return sample_data_path('metrics', 'latest.json').")


def load_agent_config() -> dict[str, Any]:
    raise NotImplementedError("Load poll interval from service.yaml / env.")


def collect_metrics() -> dict[str, Any]:
    raise NotImplementedError("Collect cpu_percent and memory_percent (psutil or /proc).")


def write_latest_metrics(metrics: dict[str, Any], path: Any | None = None) -> Any:
    raise NotImplementedError("Write JSON to sample_data/metrics/latest.json.")


def run_agent(*, interval_seconds: int | None = None, once: bool | None = None) -> None:
    raise NotImplementedError("Poll loop with graceful Ctrl+C; honor SRE_AGENT_ONCE=1.")


if __name__ == "__main__":
    print("Implement the functions above, then run: ./check.sh 17")
