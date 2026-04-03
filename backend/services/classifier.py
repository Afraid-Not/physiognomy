"""
XGBoost 모델 기반 관상 특징 분류 서비스
학습된 9개 모델로 부위별 관상 분류
"""

import json
from pathlib import Path

import numpy as np
import joblib
from pydantic import BaseModel

from services.scoring import compute_score

CHECKPOINT_DIR = Path(__file__).parent.parent.parent / "ml" / "checkpoints"

TARGETS = [
    "eye_type", "eyebrow_type", "nose_type", "mouth_type",
    "forehead_type", "chin_type", "face_shape", "philtrum_type", "cheekbone_type",
]

CATEGORY_NAMES = {
    "eye_type": "눈",
    "eyebrow_type": "눈썹",
    "nose_type": "코",
    "mouth_type": "입",
    "forehead_type": "이마",
    "chin_type": "턱",
    "face_shape": "얼굴형",
    "philtrum_type": "인중",
    "cheekbone_type": "광대뼈",
}


class PhysiognomyFeature(BaseModel):
    target: str  # eye_type, nose_type 등 (내부용)
    category: str
    label: str
    confidence: float
    score: float
    measurements: dict[str, float]


# 모델 캐시
_models = {}
_encoders = {}
_feature_names = None


def _load_models():
    global _models, _encoders, _feature_names

    if _feature_names is not None:
        return

    with open(CHECKPOINT_DIR / "feature_names.json", "r") as f:
        _feature_names = json.load(f)

    for target in TARGETS:
        _models[target] = joblib.load(CHECKPOINT_DIR / f"{target}_model.joblib")
        _encoders[target] = joblib.load(CHECKPOINT_DIR / f"{target}_encoder.joblib")


async def classify_features(ratios: dict) -> list[PhysiognomyFeature]:
    """비율 dict → 9개 부위별 관상 분류"""
    _load_models()

    # feature vector 생성 (학습 시와 동일한 순서)
    X = np.array([[ratios.get(f, 0.0) for f in _feature_names]])

    features = []
    for target in TARGETS:
        model = _models[target]
        encoder = _encoders[target]

        proba = model.predict_proba(X)[0]
        pred_idx = np.argmax(proba)
        label = encoder.inverse_transform([pred_idx])[0]
        confidence = float(proba[pred_idx])

        # 해당 부위 관련 비율값 추출
        measurements = {}
        for key, val in ratios.items():
            if target.replace("_type", "") in key or target.replace("_shape", "") in key:
                measurements[key] = round(val, 4)

        score = compute_score(target, label, confidence)

        features.append(PhysiognomyFeature(
            target=target,
            category=CATEGORY_NAMES.get(target, target),
            label=label,
            confidence=round(confidence, 3),
            score=score,
            measurements=measurements,
        ))

    return features
