"""Database compatibility layer for emotion persistence.

This module preserves the existing import surface while delegating storage to
Google Cloud Firestore via `database.firestore_db`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .firestore_db import init_db as _init_firestore_db, insert_emotion, retrieve_emotions


def init_db(db_path: Path | None = None) -> None:
    """Initialize the chosen persistence backend.

    The `db_path` argument is accepted for compatibility with the previous SQLite
    initialization path, but Firestore ignores a local path.
    """
    _init_firestore_db()
