"""Step 1 — Validate DeepFace emotion detection on a local image."""

import argparse
import sys
from pathlib import Path

from deepface import DeepFace


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate DeepFace emotion detection on a local image."
    )
    parser.add_argument(
        "image",
        type=Path,
        help="Path to a local image file containing a face",
    )
    return parser.parse_args()


def extract_face_result(analysis_result: list | dict) -> dict:
    if isinstance(analysis_result, list):
        if not analysis_result:
            raise ValueError("No face detected in the image.")
        return analysis_result[0]
    return analysis_result


def main() -> int:
    args = parse_args()
    image_path = args.image.resolve()

    if not image_path.is_file():
        print(f"Error: image not found: {image_path}", file=sys.stderr)
        return 1

    print(f"Analyzing: {image_path}")
    print("Loading model (first run may download weights)...")

    try:
        analysis = DeepFace.analyze(
            img_path=str(image_path),
            actions=["emotion"],
            enforce_detection=True,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: analysis failed: {exc}", file=sys.stderr)
        return 1

    face = extract_face_result(analysis)
    emotion = face["dominant_emotion"]
    
    # CORRECCIÓN AQUÍ: 
    # 1. Quitamos el "* 100" porque DeepFace ya lo entrega en escala 0-100.
    # 2. Usamos min() para asegurar que nunca supere el 100% por errores de redondeo.
    raw_confidence = face["emotion"][emotion]
    confidence = min(raw_confidence, 100.0)

    print()
    print("Validation successful")
    print(f"Emotion:     {emotion}")
    # Cambié a :.2f% por si quieres ver dos decimales limpios, pero puedes dejarlo en :.1f% si prefieres uno solo.
    print(f"Confidence:  {confidence:.2f}%") 

    return 0


if __name__ == "__main__":
    raise SystemExit(main())