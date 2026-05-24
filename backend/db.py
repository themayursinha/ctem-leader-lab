import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Optional


DB_PATH = os.environ.get("CTEM_DB_PATH", os.path.join(os.path.dirname(__file__), "ctem.db"))


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


class Database:
    def __init__(self, path: str = DB_PATH):
        self._path = path
        self._lock = threading.Lock()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def init(self, seed: Optional[dict[str, str]] = None):
        with self._lock:
            conn = self._connect()
            try:
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS current_state (
                        key TEXT PRIMARY KEY NOT NULL,
                        value TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY NOT NULL,
                        name TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        assets TEXT NOT NULL,
                        exposures TEXT NOT NULL,
                        remediation_actions TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS audit_events (
                        id TEXT PRIMARY KEY NOT NULL,
                        created_at TEXT NOT NULL,
                        action TEXT NOT NULL,
                        resource_type TEXT NOT NULL,
                        resource_id TEXT,
                        summary TEXT NOT NULL,
                        metadata TEXT NOT NULL
                    );
                """)
                conn.commit()

                row = conn.execute("SELECT COUNT(*) as cnt FROM current_state").fetchone()
                if row["cnt"] == 0 and seed:
                    conn.executemany(
                        "INSERT OR REPLACE INTO current_state (key, value) VALUES (?, ?)",
                        list(seed.items()),
                    )
                    conn.commit()
            finally:
                conn.close()

    def load_current(self) -> dict[str, str]:
        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute("SELECT key, value FROM current_state").fetchall()
                return {row["key"]: row["value"] for row in rows}
            finally:
                conn.close()

    def save_current(self, data: dict[str, str]):
        with self._lock:
            conn = self._connect()
            try:
                conn.executemany(
                    "INSERT OR REPLACE INTO current_state (key, value) VALUES (?, ?)",
                    list(data.items()),
                )
                conn.commit()
            finally:
                conn.close()

    def save_session(self, name: str, assets: str, exposures: str, remediation_actions: str) -> str:
        session_id = str(uuid.uuid4())
        now = _iso_now()
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    """INSERT INTO sessions (id, name, created_at, updated_at, assets, exposures, remediation_actions)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (session_id, name, now, now, assets, exposures, remediation_actions),
                )
                conn.commit()
            finally:
                conn.close()
        return session_id

    def list_sessions(self) -> list[dict[str, Any]]:
        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute(
                    "SELECT id, name, created_at, updated_at FROM sessions ORDER BY updated_at DESC"
                ).fetchall()
                return [dict(row) for row in rows]
            finally:
                conn.close()

    def get_session(self, session_id: str) -> Optional[dict[str, Any]]:
        with self._lock:
            conn = self._connect()
            try:
                row = conn.execute(
                    "SELECT id, name, created_at, updated_at, assets, exposures, remediation_actions FROM sessions WHERE id = ?",
                    (session_id,),
                ).fetchone()
                return dict(row) if row else None
            finally:
                conn.close()

    def delete_session(self, session_id: str) -> bool:
        with self._lock:
            conn = self._connect()
            try:
                cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                conn.commit()
                return cursor.rowcount > 0
            finally:
                conn.close()

    def record_audit_event(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str],
        summary: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        event_id = str(uuid.uuid4())
        now = _iso_now()
        payload = json.dumps(metadata or {}, sort_keys=True)
        with self._lock:
            conn = self._connect()
            try:
                conn.execute(
                    """INSERT INTO audit_events (id, created_at, action, resource_type, resource_id, summary, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (event_id, now, action, resource_type, resource_id, summary, payload),
                )
                conn.commit()
            finally:
                conn.close()
        return event_id

    def list_audit_events(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._lock:
            conn = self._connect()
            try:
                rows = conn.execute(
                    """SELECT id, created_at, action, resource_type, resource_id, summary, metadata
                       FROM audit_events ORDER BY created_at DESC, rowid DESC LIMIT ?""",
                    (limit,),
                ).fetchall()
                events = []
                for row in rows:
                    event = dict(row)
                    try:
                        event["metadata"] = json.loads(event["metadata"])
                    except json.JSONDecodeError:
                        event["metadata"] = {}
                    events.append(event)
                return events
            finally:
                conn.close()


DB = Database()
