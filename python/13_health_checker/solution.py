"""Step 16 solution — HTTP/TCP health checks with retry."""

from __future__ import annotations

import json
import socket
import time
from datetime import datetime, timezone
from typing import Any, Callable, TypeVar

import requests

from python.common.config_loader import load_service_config
from python.common.logging_setup import get_logger, new_trace_id
from python.common.paths import output_path, sample_data_path

T = TypeVar("T")

logger = get_logger("health_checker", json_logs=True)


def service_config_path() -> Any:
    return sample_data_path("configs", "service.yaml")


def health_report_path() -> Any:
    return output_path("health_report.json")


def load_health_config() -> dict[str, Any]:
    """Load service.yaml for endpoint definitions."""
    return load_service_config(service_config_path())


def check_http(
    url: str,
    *,
    timeout: float = 2.0,
    retries: int = 3,
    retry_delay: float = 0.2,
) -> dict[str, Any]:
    """GET *url* with retries; return structured probe result."""
    last_error: str | None = None
    for attempt in range(1, retries + 1):
        start = time.perf_counter()
        try:
            response = requests.get(url, timeout=timeout)
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                "type": "http",
                "url": url,
                "ok": response.ok,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "attempts": attempt,
            }
        except requests.RequestException as exc:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            last_error = str(exc)
            if attempt < retries:
                time.sleep(retry_delay)
            else:
                return {
                    "type": "http",
                    "url": url,
                    "ok": False,
                    "status_code": None,
                    "latency_ms": latency_ms,
                    "attempts": attempt,
                    "error": last_error,
                }


def check_tcp(
    host: str,
    port: int,
    *,
    timeout: float = 2.0,
    retries: int = 3,
    retry_delay: float = 0.2,
) -> dict[str, Any]:
    """TCP connect probe with retries."""
    last_error: str | None = None
    for attempt in range(1, retries + 1):
        start = time.perf_counter()
        try:
            with socket.create_connection((host, port), timeout=timeout):
                latency_ms = round((time.perf_counter() - start) * 1000, 2)
                return {
                    "type": "tcp",
                    "host": host,
                    "port": port,
                    "ok": True,
                    "latency_ms": latency_ms,
                    "attempts": attempt,
                }
        except OSError as exc:
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            last_error = str(exc)
            if attempt < retries:
                time.sleep(retry_delay)
            else:
                return {
                    "type": "tcp",
                    "host": host,
                    "port": port,
                    "ok": False,
                    "latency_ms": latency_ms,
                    "attempts": attempt,
                    "error": last_error,
                }


def run_with_retry(
    fn: Callable[[], T],
    *,
    retries: int = 3,
    retry_delay: float = 0.2,
) -> T:
    """Call *fn* up to *retries* times, sleeping between failures."""
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001 — teaching helper
            last_exc = exc
            if attempt < retries:
                time.sleep(retry_delay)
    assert last_exc is not None
    raise last_exc


def run_configured_checks(config: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Run HTTP checks from config endpoints and TCP checks on host IPs."""
    cfg = config or load_health_config()
    results: list[dict[str, Any]] = []

    for endpoint in cfg.get("endpoints", []):
        if not isinstance(endpoint, dict):
            continue
        url = str(endpoint.get("url", ""))
        if not url:
            continue
        timeout = float(endpoint.get("timeout_seconds", 2))
        result = check_http(url, timeout=timeout)
        result["name"] = str(endpoint.get("name", url))
        results.append(result)

    tcp_port = int(cfg.get("tcp_check_port", 8080))
    for host in cfg.get("hosts", []):
        if not isinstance(host, dict):
            continue
        hostname = str(host.get("hostname", "unknown"))
        ip = str(host.get("ip", ""))
        if not ip:
            continue
        result = check_tcp(ip, tcp_port)
        result["name"] = f"tcp-{hostname}"
        results.append(result)

    return results


def build_health_report(checks: list[dict[str, Any]], *, service: str = "payment-api") -> dict[str, Any]:
    """Aggregate probe results into a report dict."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": service,
        "healthy": all(c.get("ok") for c in checks) if checks else True,
        "checks": checks,
    }


def write_health_report(report: dict[str, Any], path: Any | None = None) -> Any:
    """Persist report as JSON under sample_data/output/."""
    target = path or health_report_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    return target


def run_health_checks(*, service: str | None = None) -> dict[str, Any]:
    """Run all checks, write report, return report dict."""
    trace_id = new_trace_id()
    config = load_health_config()
    service_name = service or str(config.get("service_name", "payment-api"))
    checks = run_configured_checks(config)
    report = build_health_report(checks, service=service_name)
    path = write_health_report(report)
    logger.info(
        "health report written",
        extra={
            "trace_id": trace_id,
            "service": service_name,
        },
    )
    print(f"Wrote {path} (healthy={report['healthy']})")
    return report


if __name__ == "__main__":
    run_health_checks()
