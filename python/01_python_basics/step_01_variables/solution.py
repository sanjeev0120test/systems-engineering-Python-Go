"""Step 1 solution — variables, types, f-strings, hostname parsing."""

from __future__ import annotations

from urllib.parse import urlparse


def parse_hostname_from_url(url: str) -> str:
    """Extract hostname from a URL string (ignores port and path)."""
    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        raise ValueError(f"Could not parse hostname from URL: {url!r}")
    return hostname


def parse_hostname_from_log_line(line: str) -> str | None:
    """Parse hostname= value from a key=value log line."""
    for token in line.split():
        if token.startswith("hostname="):
            return token.split("=", 1)[1]
    return None


def format_host_alert(hostname: str, status_code: int, region: str) -> str:
    """Build a human-readable alert string for paging/on-call."""
    severity = "CRITICAL" if status_code >= 500 else "WARNING"
    return f"[{severity}] {hostname} in {region} returned HTTP {status_code}"


def describe_variable_types(hostname: str, port: int, healthy: bool) -> str:
    """Demonstrate f-strings with mixed types (used in lesson demos)."""
    return (
        f"host={hostname!r} port={port} healthy={healthy} "
        f"(types: {type(hostname).__name__}, {type(port).__name__}, {type(healthy).__name__})"
    )
