"""Step 29 solution — Prometheus metrics exporter."""

from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "sre_http_requests_total",
    "Total HTTP requests observed by the demo service",
    ["method", "endpoint", "status"],
)

IN_FLIGHT = Gauge(
    "sre_in_flight_requests",
    "Number of HTTP requests currently being processed",
)

REQUEST_LATENCY = Histogram(
    "sre_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
)


def record_request(*, method: str, endpoint: str, status: int, latency_seconds: float) -> None:
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status)).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency_seconds)


def metrics_payload() -> tuple[bytes, str]:
    """Return Prometheus exposition body and content type."""
    return generate_latest(), CONTENT_TYPE_LATEST


def simulate_traffic() -> None:
    """Populate sample metrics for ./run.sh 29 demos."""
    IN_FLIGHT.set(3)
    record_request(method="GET", endpoint="/health", status=200, latency_seconds=0.004)
    record_request(method="GET", endpoint="/metrics", status=200, latency_seconds=0.002)
    record_request(method="GET", endpoint="/api/orders", status=500, latency_seconds=0.120)
