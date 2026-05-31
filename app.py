import uuid
import logging
import os
import importlib
from collections import Counter
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from database.db import init_db, insert_emotion, retrieve_emotions
import database.firestore_db as firestore_db
from services.emotion_service import NoFaceDetectedError, analyze_emotion

app = Flask(__name__)

# Structured JSON logging
try:
    from pythonjsonlogger import jsonlogger
    handler = logging.StreamHandler()
    fmt = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    handler.setFormatter(fmt)
    app.logger.handlers = [handler]
    logging.getLogger().handlers = [handler]
except Exception:
    # Fallback to default logging if json logger not available
    app.logger.warning("python-json-logger not available; using default logging")

# Cloud Logging integration (optional, for GCP environments)
try:
    import google.cloud.logging as cloud_logging
    cloud_client = cloud_logging.Client()
    cloud_client.setup_logging()
    app.logger.info("Cloud Logging initialized")
except Exception:
    # Silently skip if not on GCP or if google-cloud-logging is not installed
    pass

UPLOAD_FOLDER = Path(app.root_path) / "uploads"
DATABASE_PATH = Path(app.instance_path) / "emotions.db"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024

app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
init_db(DATABASE_PATH)


def allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


def resolve_upload_path(filename: str) -> Path | None:
    safe_name = secure_filename(filename)
    if not safe_name or safe_name != filename or not allowed_file(safe_name):
        return None

    image_path = (UPLOAD_FOLDER / safe_name).resolve()
    upload_root = UPLOAD_FOLDER.resolve()

    if upload_root not in image_path.parents or not image_path.is_file():
        return None

    return image_path


@app.route("/")
def index():
    return render_template("index.html")


EMOTION_LABELS_ES = {
    "angry": "Enojado",
    "disgust": "Asco",
    "fear": "Miedo",
    "happy": "Feliz",
    "sad": "Triste",
    "surprise": "Sorprendido",
    "neutral": "Neutral",
}


def _format_emotion_label(emotion: str) -> str:
    key = emotion.lower()
    return EMOTION_LABELS_ES.get(key, emotion.capitalize())


def _format_history_timestamp(raw_timestamp: str) -> str:
    try:
        when = datetime.fromisoformat(raw_timestamp)
        return when.strftime("%d/%m/%Y · %H:%M UTC")
    except ValueError:
        return raw_timestamp


def _get_device_id() -> str | None:
    device_id = request.cookies.get("emotion_device_id")
    if device_id:
        return device_id.strip()
    return None


@app.route("/history")
def history():
    device_id = _get_device_id()
    records = []
    for row in retrieve_emotions(device_id):
        records.append(
            {
                "timestamp": _format_history_timestamp(row["timestamp"]),
                "timestamp_utc": row["timestamp"],
                "emotion": _format_emotion_label(row["emotion"]),
                "confidence": int(round(float(row["confidence"]))),
            }
        )
    return render_template("history.html", records=records)


def _compute_emotion_statistics(device_id: str | None = None) -> tuple[list[dict[str, int | float | str]], int]:
    rows = retrieve_emotions(device_id)
    total = len(rows)
    if total == 0:
        return [], 0

    counts = Counter(row["emotion"].lower() for row in rows)
    stats = []
    for emotion, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        stats.append(
            {
                "emotion": _format_emotion_label(emotion),
                "count": count,
                "percentage": round((count / total) * 100, 1),
            }
        )
    return stats, total


@app.route("/stats")
def stats():
    emotion_stats, total = _compute_emotion_statistics(_get_device_id())
    return render_template(
        "stats.html",
        emotion_stats=emotion_stats,
        total=total,
    )


@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No se proporcionó ninguna imagen."}), 400

    file = request.files["image"]

    if not file or file.filename == "":
        return jsonify({"success": False, "error": "No se seleccionó ninguna imagen."}), 400

    if not allowed_file(file.filename):
        return jsonify(
            {
                "success": False,
                "error": "Tipo de archivo no válido. Tipos permitidos: JPG, PNG, WEBP.",
            }
        ), 400

    extension = secure_filename(file.filename).rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"
    save_path = UPLOAD_FOLDER / filename

    try:
        file.save(save_path)
    except OSError:
        return jsonify({"success": False, "error": "No se pudo guardar la imagen."}), 500

    return jsonify({"success": True, "filename": filename})


@app.route("/analyze", methods=["POST"])
def analyze():
    payload = request.get_json(silent=True) or {}
    filename = payload.get("filename") or request.form.get("filename")

    if not filename:
        return jsonify({"success": False, "error": "No se proporcionó ningún nombre de archivo."}), 400

    image_path = resolve_upload_path(filename)
    if image_path is None:
        return jsonify({"success": False, "error": "Imagen no encontrada o nombre de archivo no válido."}), 404

    try:
        result = analyze_emotion(image_path)

        device_id = payload.get("device_id")
        if not device_id:
            return jsonify({"success": False, "error": "Identificador de dispositivo faltante."}), 400

        insert_emotion(
            result["emotion"],
            result["confidence"],
            device_id
        )

        return jsonify(result)

    except NoFaceDetectedError:
        return jsonify({"success": False, "error": "No se detectó ningún rostro en la imagen."}), 422

    except FileNotFoundError:
        return jsonify({"success": False, "error": "Imagen no encontrada."}), 404

    except Exception:
        app.logger.exception("Error during emotion analysis.")
        return jsonify({"success": False, "error": "Error al analizar la emoción."}), 500

    finally:
        try:
            image_path.unlink(missing_ok=True)
        except Exception:
            app.logger.warning(
                "Failed to delete temporary image: %s",
                image_path
            )


@app.errorhandler(413)
def request_entity_too_large(_error):
    return jsonify(
        {"success": False, "error": "La imagen es demasiado grande."}
    ), 413


@app.route("/health")
def health():
    """Health check that validates Firestore connectivity."""
    try:
        if not firestore_db.is_initialized():
            return jsonify({"status": "error", "firestore": "not_initialized"}), 503

        # Attempt a lightweight Firestore read with a 3-second timeout
        collection = firestore_db._get_collection()
        # Create a query that attempts to fetch at most 1 document
        query = collection.limit(1)
        
        # Set a timeout of 3 seconds
        list(query.stream(timeout=3))
        
        return jsonify({"status": "ok", "firestore": "connected"}), 200
    except Exception as e:
        app.logger.exception("Health check failed during Firestore connectivity check")
        return jsonify({"status": "error", "firestore": "unreachable"}), 503


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False,
    )
