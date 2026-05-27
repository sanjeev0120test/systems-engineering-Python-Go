"""Step 28 — Incident simulator with SQLite timeline."""

from __future__ import annotations

import sys
from pathlib import Path

from python.common.logging_setup import get_logger

sys.path.insert(0, str(Path(__file__).resolve().parent))

logger = get_logger(__name__)

# --- Why this matters (production) ---
# Blameless postmortems need an accurate timeline: when alerts fired, when customers
# noticed, mitigation steps, and resolution. SQLite (or structured logs) preserves
# ordering and actors — better than scrolling Slack during a sev-1.

# --- Production patterns ---
# - Severity ladder: info → warning → critical maps to response expectations
# - Incident commander (IC) owns timeline updates — reduces conflicting narratives
# - Link timeline entries to deploy IDs, feature flags, and metric snapshots

# --- Java developer note ---
# PagerDuty/Opsgenie incidents mirror this model. JDBC + SQLite uses the same SQL
# patterns you'd use with Postgres in a real incident tool.

# --- How to run ---
# ./run.sh 28
# ./check.sh 28


def main() -> None:
    from solution import IncidentStore

    store = IncidentStore()
    store.create_incident("INC-DEMO", "Synthetic probe failures")
    store.add_event("INC-DEMO", severity="warning", message="Probe success < 99%")
    store.resolve_incident("INC-DEMO")
    for event in store.get_timeline("INC-DEMO"):
        logger.info("[%s] %s — %s (%s)", event.severity, event.timestamp, event.message, event.actor)


if __name__ == "__main__":
    main()
