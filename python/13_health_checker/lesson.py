"""
Step 16 — Health checker (HTTP/TCP probes)
============================================

Synthetic monitoring: proactively probe endpoints before users notice outages.
Retries absorb transient blips; structured JSON reports feed dashboards and alerts.
"""

from __future__ import annotations

from python.common.logging_setup import get_logger, new_trace_id

from solution import check_http, check_tcp, run_health_checks

logger = get_logger("lesson16", json_logs=True)


def demo_http_probe() -> None:
    """Probe a local-style URL using configured checks (no external cloud)."""
    trace_id = new_trace_id()
    # Use localhost pattern from service config — tests use mock servers.
    result = check_http("http://127.0.0.1:8080/health", timeout=1.0, retries=1)
    logger.info(
        f"http probe ok={result['ok']} latency={result.get('latency_ms')}ms",
        extra={"trace_id": trace_id, "service": "lesson16"},
    )
    print("HTTP probe (localhost example):", result)


def demo_tcp_probe() -> None:
    """TCP connect to a well-known resolver — no HTTP needed."""
    result = check_tcp("1.1.1.1", 53, timeout=3.0, retries=2)
    print("TCP probe:", result)


def main() -> None:
    demo_http_probe()
    demo_tcp_probe()
    print("\n--- configured checks (writes health_report.json) ---")
    run_health_checks()


if __name__ == "__main__":
    main()
