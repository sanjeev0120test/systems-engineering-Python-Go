"""
Step 8 — JSON & YAML for SRE configuration
==========================================

Parse human-friendly YAML service definitions and machine JSON metrics.
Production stacks merge file config with environment overrides (12-factor app).
"""

from __future__ import annotations

import json
import os

from python.common.config_loader import env, load_service_config, load_yaml
from python.common.paths import sample_data_path

# ---------------------------------------------------------------------------
# JAVA BRIDGE
# ---------------------------------------------------------------------------
# Java                          | Python
# ------------------------------|------------------------------------------
# Jackson ObjectMapper          | json.load / json.dumps
# SnakeYAML Yaml loader         | yaml.safe_load (via config_loader)
# application.yml + @Value      | YAML file + os.environ overrides
# Gson fromJson                 | json.load into dict[str, Any]
# Properties file               | env vars (preferred in K8s/containers)
#
# Never use yaml.load() without Loader= — it can execute arbitrary Python.
# Always validate unexpected types after parsing external files.

# ---------------------------------------------------------------------------
# SRE USE CASES
# ---------------------------------------------------------------------------
# - service.yaml defines health-check endpoints for synthetic monitoring
# - host_metrics.json feeds capacity alerts (CPU/memory/disk SLIs)
# - SRE_CHECK_INTERVAL_SECONDS overrides YAML in staging vs prod
# - Alert rules, Prometheus targets, and K8s manifests are all YAML/JSON


def demo_load_yaml_service() -> dict:
    """Load version-controlled service definition."""
    path = sample_data_path("configs", "service.yaml")
    config = load_yaml(path)
    print(f"Loaded {path.name}: service={config.get('service_name')!r}")
    return config


def demo_load_json_metrics() -> dict:
    """Load JSON metrics snapshot (exporter / agent output)."""
    path = sample_data_path("metrics", "host_metrics.json")
    with path.open("r", encoding="utf-8") as handle:
        metrics = json.load(handle)
    print(
        f"Host {metrics.get('host')}: "
        f"cpu={metrics.get('cpu_percent')}% mem={metrics.get('memory_percent')}%"
    )
    return metrics


def demo_env_override() -> None:
    """Show 12-factor override: env wins over YAML default."""
    path = sample_data_path("configs", "service.yaml")
    os.environ["SRE_ENVIRONMENT"] = "staging-demo"
    merged = load_service_config(path, env_prefix="SRE_")
    print(f"environment (env override): {merged.get('environment')}")
    print(f"check interval (from YAML): {merged.get('check_interval_seconds')}")
    del os.environ["SRE_ENVIRONMENT"]


def demo_env_helper() -> None:
    """Read optional env vars with defaults — common for secrets/URLs."""
    timeout = env("SRE_HTTP_TIMEOUT", "5")
    print(f"HTTP timeout default: {timeout}s (set SRE_HTTP_TIMEOUT to override)")


def main() -> None:
    demo_load_yaml_service()
    demo_load_json_metrics()
    demo_env_override()
    demo_env_helper()


if __name__ == "__main__":
    main()
