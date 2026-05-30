"""Emotion analysis service using DeepFace."""

from pathlib import Path


class NoFaceDetectedError(ValueError):
    """Raised when DeepFace cannot detect a face in the image."""


def _extract_face_result(analysis_result: list | dict) -> dict:
    if isinstance(analysis_result, list):
        if not analysis_result:
            raise NoFaceDetectedError("No face detected in the image.")
        return analysis_result[0]
    return analysis_result


def analyze_emotion(image_path: str | Path) -> dict[str, str | int]:
    """Analyze a local image and return the dominant emotion and confidence.

    Args:
        image_path: Path to an image file on disk.

    Returns:
        Dict with lowercase emotion label and integer confidence (0-100).

    Raises:
        FileNotFoundError: If the image file does not exist.
        NoFaceDetectedError: If no face is detected in the image.
        ValueError: If analysis fails for other validation reasons.
    """
    path = Path(image_path).resolve()

    if not path.is_file():
        raise FileNotFoundError(f"Image not found: {path}")

    from deepface import DeepFace

    try:
        analysis = DeepFace.analyze(
            img_path=str(path),
            actions=["emotion"],
            enforce_detection=True,
        )
    except ValueError as exc:
        raise NoFaceDetectedError(str(exc)) from exc

    face = _extract_face_result(analysis)
    emotion = face["dominant_emotion"].lower()
    raw_confidence = float(face["emotion"][face["dominant_emotion"]])
    confidence = int(round(min(raw_confidence, 100.0)))

    return {"emotion": emotion, "confidence": confidence}
