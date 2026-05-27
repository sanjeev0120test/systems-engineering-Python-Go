"""
Step 18 — Log parser (error rate + p95 latency)
=================================================

Access logs are SLI gold mines: status codes reveal availability, latency reveals performance.
P95 ignores noisy outliers while catching real user pain.
"""

from __future__ import annotations

from solution import analyze_access_log, parse_access_log_line


def demo_line_parser() -> None:
    sample = (
        '127.0.0.1 - - [27/May/2026:10:00:03 +0000] '
        '"GET /api/orders HTTP/1.1" 500 128 0.120'
    )
    record = parse_access_log_line(sample)
    print("Parsed line:", record)


def main() -> None:
    demo_line_parser()
    print("\n--- full access.log analysis ---")
    summary = analyze_access_log()
    print(summary)


if __name__ == "__main__":
    main()
