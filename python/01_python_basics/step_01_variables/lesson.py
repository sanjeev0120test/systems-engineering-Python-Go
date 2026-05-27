"""Step 1 — Variables, types, and f-strings for SRE string parsing.

Run from repo root:
    ./run.sh 1
    python python/01_python_basics/step_01_variables/lesson.py

Run from this folder:
    python lesson.py

Java developer notes
--------------------
- Python variables are dynamically typed (no `String hostname = ...` declaration).
- Use `str`, `int`, `bool` in type hints — similar to Java generics syntax but lowercase.
- f-strings (`f"host={hostname}"`) replace String.format / printf for most cases.
- `None` is like Java `null`; use `str | None` or `Optional[str]` for nullable returns.

SRE context
-----------
On-call engineers constantly parse hostnames from URLs, alert text, and log lines.
Getting the hostname wrong routes pages to the wrong team or fires duplicate alerts.

This step builds tiny parsing helpers you will reuse in health checks and log parsers.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Support running from repo root OR this step folder (same pattern as production scripts).
HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from solution import (  # noqa: E402
    describe_variable_types,
    format_host_alert,
    parse_hostname_from_log_line,
    parse_hostname_from_url,
)


def main() -> None:
    print("=" * 60)
    print("Step 1: Variables, types, and f-strings")
    print("=" * 60)

    # --- Variables and types (no explicit declaration required) ---
    hostname: str = "web-01.prod.example.com"
    port: int = 443
    healthy: bool = True

    # Java equivalent: String.format("host=%s port=%d", hostname, port)
    print(f"\n1) f-string basics: host={hostname} port={port} healthy={healthy}")
    print(f"   Type introspection: {describe_variable_types(hostname, port, healthy)}")

    # --- Parse hostname from URL (common in uptime checks) ---
    check_url = "https://api.example.com:8443/v1/health"
    parsed_host = parse_hostname_from_url(check_url)
    print(f"\n2) URL parsing: {check_url!r} -> {parsed_host!r}")

    # --- Parse hostname from unstructured log line ---
    log_line = "level=error hostname=cache-02 status=503 msg=upstream_timeout"
    log_host = parse_hostname_from_log_line(log_line)
    print(f"\n3) Log line parsing: {log_line}")
    print(f"   Extracted hostname: {log_host!r}")

    # --- f-strings for alert messages ---
    alert = format_host_alert(parsed_host, status_code=503, region="us-east-1")
    print(f"\n4) Alert formatting: {alert}")

    print("\nNext: open exercise.py, implement the TODOs, then run ./check.sh 1")


if __name__ == "__main__":
    main()
