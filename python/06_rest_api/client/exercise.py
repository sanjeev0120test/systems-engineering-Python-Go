"""Step 11 exercise — implement health polling with requests."""

from __future__ import annotations

from typing import Any


def build_session(retries: int = 3, backoff: float = 0.5):
    """TODO: return requests.Session with HTTPAdapter + Retry."""
    raise NotImplementedError("Implement build_session")


def poll_health(
    url: str,
    *,
    retries: int = 3,
    timeout: float = 2.0,
    backoff: float = 0.5,
) -> dict[str, Any]:
    """TODO: GET url with retries, timeout, and exponential-ish backoff sleep."""
    raise NotImplementedError("Implement poll_health")


def main() -> None:
    result = poll_health("http://127.0.0.1:8080/health")
    print(result)


if __name__ == "__main__":
    main()
