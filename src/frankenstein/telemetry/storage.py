from __future__ import annotations

import fcntl
import sqlite3
from pathlib import Path

from .events import TelemetryEvent


class TelemetryStore:
    def __init__(self, root: Path):
        self.root = root
        self.events_dir = root / "telemetry"
        self.database_dir = root / "database"
        self.events_dir.mkdir(parents=True, exist_ok=True)
        self.database_dir.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database_dir / "telemetry.sqlite", timeout=30)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA synchronous=FULL")
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                type TEXT NOT NULL,
                phase TEXT NOT NULL,
                event_json TEXT NOT NULL,
                ingested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    def close(self) -> None:
        self.connection.close()

    def ingest(self, event: TelemetryEvent) -> bool:
        encoded = event.model_dump_json()
        try:
            with self.connection:
                self.connection.execute(
                    "INSERT INTO events (event_id, timestamp, type, phase, event_json) VALUES (?, ?, ?, ?, ?)",
                    (str(event.event_id), event.timestamp.isoformat(), event.type, event.phase, encoded),
                )
                path = self.events_dir / f"{event.type.split('_', 1)[0]}.jsonl"
                with path.open("a", encoding="utf-8") as stream:
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
                    stream.write(encoded + "\n")
                    stream.flush()
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
            return True
        except sqlite3.IntegrityError:
            return False

    def events(self) -> list[TelemetryEvent]:
        rows = self.connection.execute("SELECT event_json FROM events ORDER BY timestamp, event_id")
        return [TelemetryEvent.model_validate_json(row[0]) for row in rows]
