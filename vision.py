from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / 'dataset'
DATASET_CRIMINAL_DIR = BASE_DIR / 'dataset_criminals'
TRAINER_PATH = BASE_DIR / 'trainer.yml'
TRAINER_CRIMINAL_PATH = BASE_DIR / 'trainer_criminals.yml'
CASCADE_PATH = BASE_DIR / 'haarcascade_frontalface_default.xml'

CV_AVAILABLE = True
face_cascade = None

try:
    import cv2
    import numpy as np
    if CASCADE_PATH.exists():
        face_cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
except Exception:
    cv2 = None
    np = None
    CV_AVAILABLE = False


def _detect_faces(img):
    """Return list of face bounding boxes from a BGR image."""
    if not CV_AVAILABLE or face_cascade is None:
        return None, []
    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
        )
        return gray, list(faces)
    except Exception:
        return None, []


def process_and_save_face(image_path: str, person_id: int, is_criminal: bool = False) -> bool:
    """Detect the largest face in the image and save a grayscale crop for training."""
    if not CV_AVAILABLE:
        return False
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False
        gray, faces = _detect_faces(img)
        if gray is None or not faces:
            return False

        faces_sorted = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)
        x, y, w, h = faces_sorted[0]
        face_crop = gray[y:y + h, x:x + w]

        target_dir = DATASET_CRIMINAL_DIR if is_criminal else DATASET_DIR
        target_dir.mkdir(parents=True, exist_ok=True)
        out_path = target_dir / f'{person_id}.jpg'
        cv2.imwrite(str(out_path), face_crop)
        return True
    except Exception:
        return False


def _train(dataset_dir: Path, trainer_path: Path) -> bool:
    """Train LBPH recognizer from a dataset directory."""
    if not CV_AVAILABLE or not hasattr(cv2, 'face') or not dataset_dir.exists():
        return False
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        faces, labels = [], []
        for f in os.listdir(dataset_dir):
            if f.lower().endswith(('.jpg', '.png')):
                try:
                    person_id = int(f.split('.')[0])
                    img = cv2.imread(str(dataset_dir / f), cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        faces.append(img)
                        labels.append(person_id)
                except ValueError:
                    pass
        if faces:
            recognizer.train(faces, np.array(labels))
            recognizer.write(str(trainer_path))
            return True
    except Exception:
        pass
    return False


def train_recognizer() -> bool:
    """Train staff LBPH recognizer."""
    return _train(DATASET_DIR, TRAINER_PATH)


def train_criminal_recognizer() -> bool:
    """Train criminal LBPH recognizer."""
    return _train(DATASET_CRIMINAL_DIR, TRAINER_CRIMINAL_PATH)


def _recognize(image_path: str, trainer_path: Path, confidence_threshold: float = 75.0):
    """Return (person_id, confidence_pct) or (None, 0) if no match."""
    if not CV_AVAILABLE or not hasattr(cv2, 'face') or not trainer_path.exists():
        return None, 0
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None, 0
        gray, faces = _detect_faces(img)
        if gray is None or not faces:
            return None, 0

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(str(trainer_path))

        faces_sorted = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)
        x, y, w, h = faces_sorted[0]
        face_crop = gray[y:y + h, x:x + w]
        label, dist = recognizer.predict(face_crop)
        confidence = max(0.0, 100.0 - dist)
        if dist < confidence_threshold:
            return label, round(confidence, 2)
    except Exception:
        pass
    return None, 0


def recognize_face(image_path: str):
    """Match against authorized staff."""
    person_id, confidence = _recognize(image_path, TRAINER_PATH)
    return person_id, confidence


def recognize_criminal_face(image_path: str) -> dict:
    """Match image against criminal database.
    Returns dict with match info including basic face attributes.
    """
    result = {"match": False, "criminal_id": None, "confidence": 0, "age": None, "gender": None}

    try:
        criminal_id, confidence = _recognize(image_path, TRAINER_CRIMINAL_PATH)
        if criminal_id is not None:
            result["match"] = True
            result["criminal_id"] = criminal_id
            result["confidence"] = confidence

        # Try age/gender estimation via DeepFace (optional, graceful failure)
        try:
            from deepface import DeepFace
            analysis = DeepFace.analyze(
                img_path=image_path,
                actions=["age", "gender"],
                enforce_detection=False,
                silent=True
            )
            if isinstance(analysis, list):
                analysis = analysis[0]
            result["age"] = analysis.get("age")
            dominant_gender = analysis.get("dominant_gender", "")
            result["gender"] = "Male" if "man" in dominant_gender.lower() else "Female" if "woman" in dominant_gender.lower() else dominant_gender
        except Exception:
            pass  # DeepFace optional
    except Exception:
        pass

    return result
