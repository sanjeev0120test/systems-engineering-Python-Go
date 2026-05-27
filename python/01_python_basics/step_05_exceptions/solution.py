"""Step 5 solution — exceptions: EAFP vs LBYL, safe config parsing."""

from __future__ import annotations


def safe_int(value: str, default: int = 0) -> int:
    """Parse integer from string; return default on failure (EAFP style)."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def lbyl_safe_int(value: str, default: int = 0) -> int:
    """Look Before You Leap — check before converting (Java-style guard clauses)."""
    if value is None:
        return default
    stripped = str(value).strip()
    if not stripped.lstrip("-").isdigit():
        return default
    return int(stripped)


def parse_threshold_config(raw: dict[str, object]) -> dict[str, int | float]:
    """Safely parse monitoring thresholds from messy config dict."""
    result: dict[str, int | float] = {}
    try:
        result["check_interval_seconds"] = safe_int(str(raw.get("check_interval_seconds", 30)), 30)
        result["retry_limit"] = safe_int(str(raw.get("retry_limit", 3)), 3)
        disk_raw = raw.get("disk_threshold_percent", 90.0)
        result["disk_threshold_percent"] = float(disk_raw)  # may raise — caught below
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid threshold config: {raw!r}") from exc
    return result


def read_nested_timeout(config: dict[str, object], default: float = 2.0) -> float:
    """Safely read endpoints[0].timeout_seconds with EAFP."""
    try:
        endpoints = config["endpoints"]
        first = endpoints[0]  # type: ignore[index]
        return float(first["timeout_seconds"])  # type: ignore[index]
    except (KeyError, IndexError, TypeError, ValueError):
        return default


def format_config_error(key: str, exc: Exception) -> str:
    """Standard error string for ops logs."""
    return f"config key {key!r} invalid: {exc.__class__.__name__}: {exc}"
