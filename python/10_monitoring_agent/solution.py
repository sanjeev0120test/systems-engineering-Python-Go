"""Step 17 solution — CPU/memory monitoring agent."""

from __future__ import annotations

import json
import os
import signal
import time
from datetime import datetime, timezone
from typing import Any

import psutil

from python.common.config_loader import env, load_service_config
from python.common.logging_setup import get_logger, new_trace_id
from python.common.paths import sample_data_path

logger = get_logger("monitoring_agent", json_logs=True)

_shutdown_requested = False


def service_config_path() -> Any:
    return sample_data_path("configs", "service.yaml")


def latest_metrics_path() -> Any:
    return sample_data_path("metrics", "latest.json")


def load_agent_config() -> dict[str, Any]:
    """Load poll interval from service.yaml with optional env override."""
    config = load_service_config(service_config_path())
    interval_raw = env("LAB_CHECK_INTERVAL_SECONDS") or config.get("check_interval_seconds", 10)
    return {"check_interval_seconds": int(interval_raw)}


def collect_metrics() -> dict[str, Any]:
    """Snapshot current host CPU and memory utilization."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "host": os.environ.get("HOSTNAME", "localhost"),
        "cpu_percent": round(psutil.cpu_percent(interval=0.1), 1),
        "memory_percent": round(psutil.virtual_memory().percent, 1),
    }


def write_latest_metrics(metrics: dict[str, Any], path: Any | None = None) -> Any:
    """Write metrics snapshot to sample_data/metrics/latest.json."""
    target = path or latest_metrics_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)
        handle.write("\n")
    return target


def _handle_shutdown(signum: int, frame: Any) -> None:  # noqa: ARG001
    global _shutdown_requested
    _shutdown_requested = True
    logger.info("shutdown requested — finishing current cycle")


def run_agent(*, interval_seconds: int | None = None, once: bool | None = None) -> None:
    """Poll metrics until Ctrl+C or LAB_AGENT_ONCE=1."""
    global _shutdown_requested
    _shutdown_requested = False

    config = load_agent_config()
    interval = interval_seconds if interval_seconds is not None else config["check_interval_seconds"]
    run_once = once if once is not None else env("LAB_AGENT_ONCE") == "1"

    signal.signal(signal.SIGINT, _handle_shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle_shutdown)

    trace_id = new_trace_id()
    logger.info(
        f"monitoring agent starting interval={interval}s once={run_once}",
        extra={"trace_id": trace_id, "service": "monitoring_agent"},
    )

    while not _shutdown_requested:
        metrics = collect_metrics()
        path = write_latest_metrics(metrics)
        logger.info(
            f"metrics cpu={metrics['cpu_percent']}% mem={metrics['memory_percent']}%",
            extra={"trace_id": trace_id, "service": "monitoring_agent"},
        )
        print(f"Wrote {path} cpu={metrics['cpu_percent']}% mem={metrics['memory_percent']}%")

        if run_once:
            break

        time.sleep(interval)

    logger.info("monitoring agent stopped", extra={"trace_id": trace_id, "service": "monitoring_agent"})


if __name__ == "__main__":
    run_agent()
