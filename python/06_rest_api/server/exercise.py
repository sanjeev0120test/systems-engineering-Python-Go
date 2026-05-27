"""Step 12 exercise — implement FastAPI /health and /ready endpoints."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI(title="SRE Lab Service", version="0.1.0")


# TODO: add GET /health returning {"status": "ok", "service": "sre-lab"}


# TODO: add GET /ready returning {"status": "ready"}
