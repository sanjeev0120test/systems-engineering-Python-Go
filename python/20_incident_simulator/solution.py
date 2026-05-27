"""Step 28 solution — incident timeline stored in SQLite."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from python.common.paths import output_path


@dataclass(frozen=True)
class TimelineEvent:
    incident_id: str
    timestamp: str
    severity: str
    message: str
    actor: str


class IncidentStore:
    """SQLite-backed incident timeline for postmortems."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = db_path or output_path("incidents.db")
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    incident_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    opened_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS timeline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    FOREIGN KEY (incident_id) REFERENCES incidents (incident_id)
                )
                """
            )

    def create_incident(self, incident_id: str, title: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO incidents (incident_id, title, status, opened_at) VALUES (?, ?, ?, ?)",
                (incident_id, title, "open", now),
            )
            conn.execute(
                """
                INSERT INTO timeline (incident_id, timestamp, severity, message, actor)
                VALUES (?, ?, ?, ?, ?)
                """,
                (incident_id, now, "info", f"Incident opened: {title}", "system"),
            )

    def add_event(
        self,
        incident_id: str,
        *,
        severity: str,
        message: str,
        actor: str = "oncall",
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO timeline (incident_id, timestamp, severity, message, actor)
                VALUES (?, ?, ?, ?, ?)
                """,
                (incident_id, now, severity, message, actor),
            )

    def resolve_incident(self, incident_id: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE incidents SET status = ? WHERE incident_id = ?",
                ("resolved", incident_id),
            )
        self.add_event(incident_id, severity="info", message="Incident resolved", actor="ic")

    def get_timeline(self, incident_id: str) -> list[TimelineEvent]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT incident_id, timestamp, severity, message, actor
                FROM timeline
                WHERE incident_id = ?
                ORDER BY timestamp ASC, id ASC
                """,
                (incident_id,),
            ).fetchall()
        return [
            TimelineEvent(
                incident_id=row["incident_id"],
                timestamp=row["timestamp"],
                severity=row["severity"],
                message=row["message"],
                actor=row["actor"],
            )
            for row in rows
        ]

    def incident_status(self, incident_id: str) -> str:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT status FROM incidents WHERE incident_id = ?",
                (incident_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"unknown incident: {incident_id}")
        return str(row["status"])
