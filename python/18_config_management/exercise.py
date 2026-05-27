"""Step 26 exercise — YAML config drift detector."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ConfigChange:
    path: str
    old_value: Any
    new_value: Any


def snapshot_config(source: Path, destination: Path) -> Path:
    raise NotImplementedError("Implement snapshot_config")


def diff_configs(old: dict[str, Any], new: dict[str, Any], prefix: str = "") -> list[ConfigChange]:
    raise NotImplementedError("Implement diff_configs")


def detect_drift(baseline_path: Path, current_path: Path) -> list[ConfigChange]:
    raise NotImplementedError("Implement detect_drift")


def default_service_config_path() -> Path:
    raise NotImplementedError("Implement default_service_config_path")


def write_drift_report(changes: list[ConfigChange], report_path: Path | None = None) -> Path:
    raise NotImplementedError("Implement write_drift_report")


def main() -> None:
    print("Implement config drift detector, then run: ./check.sh 26")


if __name__ == "__main__":
    main()
