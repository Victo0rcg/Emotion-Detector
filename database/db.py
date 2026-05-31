"""SQLite persistence for emotion analysis records."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DB_PATH: Path | None = None

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS emotions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    emotion TEXT NOT NULL,
    confidence REAL
);
"""


def _require_db_path() -> Path:
    if _DB_PATH is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _DB_PATH


def init_db(db_path: Path) -> None:
    """Create the database file and emotions table if they do not exist."""
    global _DB_PATH
    _DB_PATH = db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute(_CREATE_TABLE_SQL)
        conn.commit()


def insert_emotion(emotion: str, confidence: int | float) -> dict[str, Any]:
    """Insert a successful analysis and return the saved record."""
    db_path = _require_db_path()
    timestamp = datetime.now().replace(microsecond=0).isoformat()
    normalized_emotion = emotion.strip().lower()
    normalized_confidence = float(confidence)

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            INSERT INTO emotions (timestamp, emotion, confidence)
            VALUES (?, ?, ?)
            """,
            (timestamp, normalized_emotion, normalized_confidence),
        )
        conn.commit()
        record_id = cursor.lastrowid
        row = conn.execute(
            "SELECT id, timestamp, emotion, confidence FROM emotions WHERE id = ?",
            (record_id,),
        ).fetchone()

    if row is None:
        raise RuntimeError("Failed to retrieve inserted emotion record.")

    return dict(row)


def retrieve_emotions() -> list[dict[str, Any]]:
    """Return all stored emotion records, newest first."""
    db_path = _require_db_path()

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, timestamp, emotion, confidence
            FROM emotions
            ORDER BY id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]
