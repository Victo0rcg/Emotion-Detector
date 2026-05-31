"""Google Firestore persistence for emotion analysis records."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

from google.api_core.exceptions import GoogleAPICallError
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import firestore

logger = logging.getLogger(__name__)

_CLIENT: firestore.Client | None = None
_COLLECTION_NAME = "emotions"


def _get_project_id() -> str | None:
    return (
        os.environ.get("FIRESTORE_PROJECT_ID")
        or os.environ.get("GOOGLE_CLOUD_PROJECT")
        or os.environ.get("GCLOUD_PROJECT")
    )


def init_db(project_id: str | None = None) -> None:
    """Initialize Firestore client using native Google Cloud credentials."""
    global _CLIENT
    if _CLIENT is not None:
        return

    if project_id is None:
        project_id = _get_project_id()

    try:
        _CLIENT = firestore.Client(project=project_id)
        logger.info("Initialized Firestore client for project=%s", project_id or "<auto>")
    except DefaultCredentialsError as exc:
        logger.exception("Failed to authenticate Firestore client.")
        raise RuntimeError(
            "Failed to initialize Firestore client: no Google Cloud credentials found. "
            "Set GOOGLE_APPLICATION_CREDENTIALS or use Application Default Credentials."
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error initializing Firestore client.")
        raise RuntimeError("Failed to initialize Firestore client.") from exc


def _require_client() -> firestore.Client:
    if _CLIENT is None:
        raise RuntimeError("Firestore client is not initialized. Call init_db() first.")
    return _CLIENT


def _format_timestamp(timestamp: Any) -> str:
    if isinstance(timestamp, datetime):
        # Ensure UTC timestamps use the 'Z' suffix instead of '+00:00'
        iso = timestamp.isoformat()
        if iso.endswith("+00:00"):
            return iso[:-6] + "Z"
        return iso
    return str(timestamp)


def is_initialized() -> bool:
    """Return True when Firestore client has been initialized."""
    return _CLIENT is not None


def _get_collection() -> firestore.CollectionReference:
    return _require_client().collection(_COLLECTION_NAME)


def insert_emotion(emotion: str, confidence: int | float, device_id: str | None = None) -> dict[str, Any]:
    """Insert a new emotion record into Firestore."""
    normalized_emotion = emotion.strip().lower()
    normalized_confidence = float(confidence)
    if not device_id:
        raise ValueError("device_id is required to insert emotion records.")

    timestamp = datetime.now(timezone.utc).replace(microsecond=0)

    document = {
        "timestamp": timestamp,
        "emotion": normalized_emotion,
        "confidence": normalized_confidence,
        "device_id": str(device_id).strip(),
    }

    try:
        _, doc_ref = _get_collection().add(document)
        logger.info("Inserted emotion record into Firestore: %s", doc_ref.id)
    except GoogleAPICallError as exc:
        logger.exception("Firestore API error inserting emotion record.")
        raise RuntimeError("Failed to insert emotion into Firestore.") from exc
    except Exception:
        logger.exception("Unexpected error inserting emotion record.")
        raise

    return {
        "id": doc_ref.id,
        "timestamp": _format_timestamp(timestamp),
        "emotion": normalized_emotion,
        "confidence": normalized_confidence,
        "device_id": document["device_id"],
    }


def retrieve_emotions(device_id: str | None = None) -> list[dict[str, Any]]:
    """Return stored emotion records for the given device, newest first."""
    if not device_id:
        logger.warning("retrieve_emotions called without a device_id; returning empty result set.")
        return []

    try:
        query = (
            _get_collection()
            .where("device_id", "==", device_id)
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
        )
        docs = list(query.stream())
    except GoogleAPICallError as exc:
        logger.exception("Firestore API error retrieving emotion history.")
        raise RuntimeError("Failed to retrieve emotion history from Firestore.") from exc
    except Exception:
        logger.exception("Unexpected error retrieving emotion history.")
        raise

    records: list[dict[str, Any]] = []
    for doc in docs:
        data = doc.to_dict() or {}
        records.append(
            {
                "id": doc.id,
                "timestamp": _format_timestamp(data.get("timestamp", "")),
                "emotion": str(data.get("emotion", "")),
                "confidence": float(data.get("confidence", 0.0)),
            }
        )
    return records
