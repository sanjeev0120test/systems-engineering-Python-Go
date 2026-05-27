"""Step 29 exercise — Prometheus metrics exporter."""

from __future__ import annotations


def record_request(*, method: str, endpoint: str, status: int, latency_seconds: float) -> None:
    raise NotImplementedError("Implement record_request")


def metrics_payload() -> tuple[bytes, str]:
    raise NotImplementedError("Implement metrics_payload")


def simulate_traffic() -> None:
    raise NotImplementedError("Implement simulate_traffic")


def main() -> None:
    print("Implement metrics exporter, then run: ./check.sh 29")


if __name__ == "__main__":
    main()
