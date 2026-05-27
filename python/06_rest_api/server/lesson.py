"""Step 12 — REST server: FastAPI liveness and readiness probes."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (SRE) ---
# Kubernetes uses /health (liveness) vs /ready (readiness) to decide restart vs
# remove from load balancer. Every microservice exposes both.

# --- Java developer note ---
# FastAPI ≈ lightweight Spring Boot WebFlux-style routing with automatic OpenAPI.
# uvicorn is the ASGI server (like embedded Tomcat for async Python).

# --- How to run ---
# ./run.sh 12              (starts server — blocks until Ctrl+C)
# curl http://127.0.0.1:8080/health
# curl http://127.0.0.1:8080/ready
# Then ./run.sh 11 in another terminal to poll from the client step.


def main() -> None:
    logger.info("This step runs server.py via ./run.sh 12")
    logger.info("Starting uvicorn on http://127.0.0.1:8080 ...")
    import uvicorn

    from solution import app

    uvicorn.run(app, host="127.0.0.1", port=8080)


if __name__ == "__main__":
    main()
