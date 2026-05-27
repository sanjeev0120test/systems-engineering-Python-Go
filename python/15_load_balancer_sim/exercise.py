"""Step 24 exercise — round-robin load balancer simulator."""

from __future__ import annotations

from collections.abc import Callable

import httpx
from fastapi import FastAPI


class RoundRobinBalancer:
    def __init__(self, backends: list[str]) -> None:
        raise NotImplementedError("Implement RoundRobinBalancer")

    def next_backend(self) -> str:
        raise NotImplementedError("Implement next_backend")

    def remove_backend(self, backend: str) -> None:
        raise NotImplementedError("Implement remove_backend")


def create_load_balancer_app(
    backends: list[str],
    *,
    client_factory: Callable[[], httpx.Client] | None = None,
) -> FastAPI:
    raise NotImplementedError("Implement create_load_balancer_app")


def distribute_requests(
    balancer: RoundRobinBalancer,
    paths: list[str],
) -> list[str]:
    raise NotImplementedError("Implement distribute_requests")


def main() -> None:
    print("Implement load balancer, then run: ./check.sh 24")


if __name__ == "__main__":
    main()
