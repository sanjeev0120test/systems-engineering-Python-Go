"""Step 26 solution — YAML snapshot diff and config drift detection."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from python.common.config_loader import load_yaml
from python.common.paths import output_path, sample_data_path


@dataclass(frozen=True)
class ConfigChange:
    path: str
    old_value: Any
    new_value: Any


def snapshot_config(source: Path, destination: Path) -> Path:
    """Copy YAML config to a snapshot file for later comparison."""
    data = load_yaml(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(yaml.safe_dump(data, sort_keys=True), encoding="utf-8")
    return destination


def diff_configs(old: dict[str, Any], new: dict[str, Any], prefix: str = "") -> list[ConfigChange]:
    """Deep diff two config dicts."""
    changes: list[ConfigChange] = []
    keys = sorted(set(old) | set(new))
    for key in keys:
        path = f"{prefix}.{key}" if prefix else key
        old_val = old.get(key)
        new_val = new.get(key)
        if isinstance(old_val, dict) and isinstance(new_val, dict):
            changes.extend(diff_configs(old_val, new_val, prefix=path))
        elif old_val != new_val:
            changes.append(ConfigChange(path=path, old_value=old_val, new_value=new_val))
    return changes


def detect_drift(baseline_path: Path, current_path: Path) -> list[ConfigChange]:
    """Compare two YAML snapshots and return drift entries."""
    baseline = load_yaml(baseline_path)
    current = load_yaml(current_path)
    return diff_configs(baseline, current)


def default_service_config_path() -> Path:
    return sample_data_path("configs", "service.yaml")


def write_drift_report(changes: list[ConfigChange], report_path: Path | None = None) -> Path:
    """Persist human-readable drift report under sample_data/output/."""
    target = report_path or output_path("config_drift_report.txt")
    lines = ["Config drift report", "===================="]
    if not changes:
        lines.append("No drift detected.")
    else:
        for change in changes:
            lines.append(f"- {change.path}: {change.old_value!r} -> {change.new_value!r}")
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target
