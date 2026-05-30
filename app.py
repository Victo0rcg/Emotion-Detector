import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from services.emotion_service import NoFaceDetectedError, analyze_emotion

app = Flask(__name__)

UPLOAD_FOLDER = Path(app.root_path) / "uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024

app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


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


@app.route("/upload", methods=["POST"])
def upload():
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image provided."}), 400

    file = request.files["image"]

    if not file or file.filename == "":
        return jsonify({"success": False, "error": "No image selected."}), 400

    if not allowed_file(file.filename):
        return jsonify(
            {
                "success": False,
                "error": "Invalid file type. Allowed types: JPG, PNG, WEBP.",
            }
        ), 400

    extension = secure_filename(file.filename).rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"
    save_path = UPLOAD_FOLDER / filename

    try:
        file.save(save_path)
    except OSError:
        return jsonify({"success": False, "error": "Could not save image."}), 500

    return jsonify({"success": True, "filename": filename})


@app.route("/analyze", methods=["POST"])
def analyze():
    payload = request.get_json(silent=True) or {}
    filename = payload.get("filename") or request.form.get("filename")

    if not filename:
        return jsonify({"error": "No filename provided."}), 400

    image_path = resolve_upload_path(filename)
    if image_path is None:
        return jsonify({"error": "Image not found or invalid filename."}), 404

    try:
        result = analyze_emotion(image_path)
    except NoFaceDetectedError:
        return jsonify({"error": "No face detected in the image."}), 422
    except FileNotFoundError:
        return jsonify({"error": "Image not found."}), 404
    except Exception:
        return jsonify({"error": "Emotion analysis failed."}), 500

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
