"""12-factor config: environment variables override YAML defaults."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML safely — never use yaml.load without Loader (security risk)."""
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data if isinstance(data, dict) else {}


def env(key: str, default: str | None = None) -> str | None:
    """Read environment variable (production config source #1)."""
    return os.environ.get(key, default)


def load_service_config(yaml_path: Path, env_prefix: str = "LAB_") -> dict[str, Any]:
    """Merge YAML file with env overrides."""
    config = load_yaml(yaml_path)
    for key in list(config.keys()):
        env_key = f"{env_prefix}{key.upper()}"
        if env_key in os.environ:
            config[key] = os.environ[env_key]
    return config
