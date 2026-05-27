"""Step 28 exercise — incident timeline in SQLite."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TimelineEvent:
    incident_id: str
    timestamp: str
    severity: str
    message: str
    actor: str


class IncidentStore:
    def __init__(self, db_path: Path | None = None) -> None:
        raise NotImplementedError("Implement IncidentStore")

    def create_incident(self, incident_id: str, title: str) -> None:
        raise NotImplementedError("Implement create_incident")

    def add_event(
        self,
        incident_id: str,
        *,
        severity: str,
        message: str,
        actor: str = "oncall",
    ) -> None:
        raise NotImplementedError("Implement add_event")

    def resolve_incident(self, incident_id: str) -> None:
        raise NotImplementedError("Implement resolve_incident")

    def get_timeline(self, incident_id: str) -> list[TimelineEvent]:
        raise NotImplementedError("Implement get_timeline")

    def incident_status(self, incident_id: str) -> str:
        raise NotImplementedError("Implement incident_status")


def main() -> None:
    print("Implement incident simulator, then run: ./check.sh 28")


if __name__ == "__main__":
    main()
