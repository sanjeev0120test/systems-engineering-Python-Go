"""Step 12 — FastAPI server entrypoint (./run.sh 12 runs this file)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import uvicorn

from solution import app

if __name__ == "__main__":
    print("Starting Practice Lab API on http://127.0.0.1:8080")
    print("  GET /health  — liveness")
    print("  GET /ready   — readiness")
    print("Press Ctrl+C to stop.")
    uvicorn.run(app, host="127.0.0.1", port=8080)
