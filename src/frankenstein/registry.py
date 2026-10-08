from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path
from uuid import uuid4

from .contracts import CapabilityManifest


class Registry:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA foreign_keys=ON")
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS capability_versions (
                id TEXT NOT NULL,
                version TEXT NOT NULL,
                manifest_json TEXT NOT NULL,
                manifest_sha256 TEXT NOT NULL,
                status TEXT NOT NULL CHECK (
                    status IN ('candidate', 'tested', 'active', 'deprecated', 'revoked')
                ),
                active INTEGER NOT NULL DEFAULT 0 CHECK (active IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                installed_at TEXT,
                activated_at TEXT,
                PRIMARY KEY (id, version)
            );
            CREATE UNIQUE INDEX IF NOT EXISTS one_active_version
                ON capability_versions(id) WHERE active = 1;
            CREATE TABLE IF NOT EXISTS lifecycle_events (
                event_id TEXT PRIMARY KEY,
                capability_id TEXT NOT NULL,
                version TEXT NOT NULL,
                from_state TEXT,
                to_state TEXT NOT NULL,
                execution_id TEXT,
                occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (capability_id, version)
                    REFERENCES capability_versions(id, version)
            );
            CREATE TABLE IF NOT EXISTS verification_runs (
                verification_id TEXT PRIMARY KEY,
                capability_id TEXT NOT NULL,
                version TEXT NOT NULL,
                suite TEXT NOT NULL,
                passed INTEGER NOT NULL CHECK (passed IN (0, 1)),
                artifact_sha256 TEXT NOT NULL,
                execution_id TEXT,
                occurred_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (capability_id, version)
                    REFERENCES capability_versions(id, version)
            );
            """
        )

    def close(self) -> None:
        self.connection.close()

    def register_candidate(self, manifest: CapabilityManifest) -> str:
        encoded = manifest.model_dump_json()
        digest = hashlib.sha256(encoded.encode()).hexdigest()
        with self.connection:
            self.connection.execute(
                """
                INSERT INTO capability_versions
                    (id, version, manifest_json, manifest_sha256, status)
                VALUES (?, ?, ?, ?, 'candidate')
                ON CONFLICT(id, version) DO UPDATE SET
                    manifest_json = excluded.manifest_json,
                    manifest_sha256 = excluded.manifest_sha256
                WHERE capability_versions.status = 'candidate'
                """,
                (manifest.id, manifest.version, encoded, digest),
            )
            self._record_transition(manifest.id, manifest.version, None, "candidate")
        return digest

    def activate(self, capability_id: str, version: str) -> None:
        with self.connection:
            row = self.connection.execute(
                "SELECT status FROM capability_versions WHERE id = ? AND version = ?",
                (capability_id, version),
            ).fetchone()
            if row is None or row["status"] != "tested":
                raise ValueError("only a verified candidate can be activated")
            self._validate_dependencies(capability_id, version)
            self.connection.execute(
                "UPDATE capability_versions SET active = 0, status = 'deprecated' WHERE id = ? AND active = 1",
                (capability_id,),
            )
            self.connection.execute(
                """
                UPDATE capability_versions
                SET status = 'active', active = 1,
                    installed_at = COALESCE(installed_at, CURRENT_TIMESTAMP),
                    activated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND version = ?
                """,
                (capability_id, version),
            )
            self._record_transition(capability_id, version, "tested", "active")

    def _validate_dependencies(self, capability_id: str, version: str) -> None:
        def visit(current_id: str, current_version: str, path: set[str]) -> None:
            key = f"{current_id}@{current_version}"
            if key in path:
                raise ValueError(f"capability dependency cycle detected at {key}")
            row = self.connection.execute(
                "SELECT manifest_json, active FROM capability_versions WHERE id = ? AND version = ?",
                (current_id, current_version),
            ).fetchone()
            if row is None:
                raise ValueError(f"missing dependency {key}")
            if key != f"{capability_id}@{version}" and not row["active"]:
                raise ValueError(f"dependency is not active: {key}")
            manifest = json.loads(row["manifest_json"])
            for dependency in manifest["requires"]:
                dependency_id, separator, dependency_version = dependency.partition("@")
                if not separator:
                    raise ValueError(f"dependency is not pinned: {dependency}")
                visit(dependency_id, dependency_version, path | {key})

        visit(capability_id, version, set())

    def mark_tested(self, capability_id: str, version: str) -> None:
        with self.connection:
            cursor = self.connection.execute(
                """
                UPDATE capability_versions SET status = 'tested'
                WHERE id = ? AND version = ? AND status = 'candidate'
                """,
                (capability_id, version),
            )
            if cursor.rowcount != 1:
                raise ValueError("only a candidate can be marked tested")
            manifest = self.get(capability_id, version)["manifest"]
            self.connection.execute(
                """
                INSERT INTO verification_runs
                    (verification_id, capability_id, version, suite, passed, artifact_sha256)
                VALUES (?, ?, ?, ?, 1, ?)
                """,
                (
                    str(uuid4()), capability_id, version,
                    manifest["verification"]["suite"],
                    manifest["provenance"]["artifact_sha256"],
                ),
            )
            self._record_transition(capability_id, version, "candidate", "tested")

    def _record_transition(
        self, capability_id: str, version: str, from_state: str | None, to_state: str
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO lifecycle_events
                (event_id, capability_id, version, from_state, to_state)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(uuid4()), capability_id, version, from_state, to_state),
        )

    def get(self, capability_id: str, version: str | None = None) -> dict:
        query = "SELECT * FROM capability_versions WHERE id = ?"
        params: tuple[str, ...] = (capability_id,)
        if version:
            query += " AND version = ?"
            params = (capability_id, version)
        else:
            query += " AND active = 1"
        row = self.connection.execute(query, params).fetchone()
        if row is None:
            raise KeyError(capability_id)
        result = dict(row)
        result["manifest"] = json.loads(result.pop("manifest_json"))
        return result

    def list(self, status: str | None = None) -> list[dict]:
        query = "SELECT id, version, status, active, manifest_sha256 FROM capability_versions"
        params: tuple[str, ...] = ()
        if status:
            query += " WHERE status = ?"
            params = (status,)
        query += " ORDER BY id, version"
        return [dict(row) for row in self.connection.execute(query, params)]

    def search(self, query: str) -> list[dict]:
        pattern = f"%{query.lower()}%"
        rows = self.connection.execute(
            """
            SELECT id, version, status, active, manifest_json
            FROM capability_versions
            WHERE active = 1 AND (lower(id) LIKE ? OR lower(manifest_json) LIKE ?)
            ORDER BY id
            """,
            (pattern, pattern),
        )
        return [
            {
                "id": row["id"],
                "version": row["version"],
                "status": row["status"],
                "summary": json.loads(row["manifest_json"])["summary"],
            }
            for row in rows
        ]
