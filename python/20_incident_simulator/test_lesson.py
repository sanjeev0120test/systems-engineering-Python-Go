"""Tests for Step 28 — incident simulator."""

from __future__ import annotations

from pathlib import Path

import pytest

from python.step_loader import load_solution

STEP_DIR = Path(__file__).resolve().parent
mod = load_solution(STEP_DIR)
solution = mod


for _name in dir(mod):
    if not _name.startswith("_"):
        globals()[_name] = getattr(mod, _name)

def test_incident_timeline_lifecycle(tmp_path: Path) -> None:
    store = IncidentStore(tmp_path / "incidents.db")
    store.create_incident("INC-1", "Elevated 5xx on payment-api")
    store.add_event("INC-1", severity="warning", message="Pager fired", actor="alertmanager")
    store.add_event("INC-1", severity="critical", message="Error budget burn > 2%", actor="ic")
    store.resolve_incident("INC-1")

    timeline = store.get_timeline("INC-1")
    assert len(timeline) >= 4
    assert timeline[0].message.startswith("Incident opened")
    assert store.incident_status("INC-1") == "resolved"


def test_unknown_incident_raises(tmp_path: Path) -> None:
    store = IncidentStore(tmp_path / "incidents.db")
    try:
        store.incident_status("missing")
    except KeyError as exc:
        assert "missing" in str(exc)
    else:
        raise AssertionError("expected KeyError")

