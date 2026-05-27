"""Step 1 exercise — fill in the TODOs, then run: python exercise.py"""

from __future__ import annotations


def parse_hostname_from_url(url: str) -> str:
    """Extract hostname from a URL string (ignores port and path)."""
    # TODO: use urllib.parse.urlparse and return parsed.hostname
    # Raise ValueError if hostname is missing.
    raise NotImplementedError("Implement parse_hostname_from_url")


def parse_hostname_from_log_line(line: str) -> str | None:
    """Parse hostname= value from a key=value log line."""
    # TODO: split the line on whitespace and find token starting with "hostname="
    raise NotImplementedError("Implement parse_hostname_from_log_line")


def format_host_alert(hostname: str, status_code: int, region: str) -> str:
    """Build a human-readable alert string for paging/on-call."""
    # TODO: use an f-string; CRITICAL for status >= 500, else WARNING
    raise NotImplementedError("Implement format_host_alert")


def describe_variable_types(hostname: str, port: int, healthy: bool) -> str:
    """Demonstrate f-strings with mixed types."""
    # TODO: return an f-string showing hostname, port, healthy, and their types
    raise NotImplementedError("Implement describe_variable_types")


if __name__ == "__main__":
    sample_url = "https://api.example.com:8443/health"
    sample_log = "hostname=web-01.prod.example.com status=503 region=us-east-1"

    print("Exercise Step 1 — implement the TODOs above, then re-run this file.")
    print(f"Sample URL: {sample_url}")
    print(f"Sample log: {sample_log}")
