"""Step 12 solution — minimal FastAPI service with liveness and readiness probes."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="SRE Lab Service", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe — process is up (k8s restarts if this fails)."""
    return {"status": "ok", "service": "sre-lab"}


@app.get("/ready")
def ready() -> dict[str, str]:
    """Readiness probe — can accept traffic (remove from LB if not ready)."""
    return {"status": "ready"}
