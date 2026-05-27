"""Step 5 exercise — exceptions TODOs."""

from __future__ import annotations


def safe_int(value: str, default: int = 0) -> int:
    """Parse integer from string; return default on failure (EAFP)."""
    # TODO: try int(value) except (TypeError, ValueError) return default
    raise NotImplementedError("Implement safe_int")


def lbyl_safe_int(value: str, default: int = 0) -> int:
    """Look Before You Leap — guard clauses before int()."""
    # TODO: validate then convert (contrast with safe_int in lesson)
    raise NotImplementedError("Implement lbyl_safe_int")


def parse_threshold_config(raw: dict[str, object]) -> dict[str, int | float]:
    """Safely parse monitoring thresholds from messy config dict."""
    # TODO: parse check_interval_seconds, retry_limit, disk_threshold_percent
    # Raise ValueError with 'from exc' if disk threshold is invalid
    raise NotImplementedError("Implement parse_threshold_config")


def read_nested_timeout(config: dict[str, object], default: float = 2.0) -> float:
    """Safely read endpoints[0].timeout_seconds."""
    # TODO: EAFP access nested keys; return default on any failure
    raise NotImplementedError("Implement read_nested_timeout")


def format_config_error(key: str, exc: Exception) -> str:
    """Standard error string for ops logs."""
    # TODO: return f"config key {key!r} invalid: ..."
    raise NotImplementedError("Implement format_config_error")


if __name__ == "__main__":
    sample = {"check_interval_seconds": "10", "retry_limit": "bad", "disk_threshold_percent": 90}
    print("Exercise Step 5 — implement EAFP vs LBYL parsers.")
    print(f"Sample config keys: {list(sample.keys())}")
