"""
관상 분류 모델 학습
Input: 37개 얼굴 비율 피처
Output: 9개 부위별 관상 분류 (부위당 개별 XGBoost 모델)
"""

import json
import sys
import io
from pathlib import Path

import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ── 경로 설정 ──
BASE_DIR = Path(r"D:\dev\physiognomy")
RATIOS_CSV = BASE_DIR / "ml" / "data" / "face_ratios.csv"
LABELS_CSV = BASE_DIR / "ml" / "data" / "face_labels.csv"
MODEL_DIR = BASE_DIR / "ml" / "checkpoints"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# ── 타겟 정의 ──
TARGETS = [
    "eye_type",
    "eyebrow_type",
    "nose_type",
    "mouth_type",
    "forehead_type",
    "chin_type",
    "face_shape",
    "philtrum_type",
    "cheekbone_type",
]


def load_data():
    ratios_df = pd.read_csv(RATIOS_CSV)
    labels_df = pd.read_csv(LABELS_CSV, encoding="utf-8-sig")

    feature_cols = [c for c in ratios_df.columns if c not in ("filename", "subject_id")]
    df = ratios_df.merge(labels_df[["filename"] + TARGETS], on="filename")

    X = df[feature_cols].values
    return df, X, feature_cols


def train_one_target(X_train, X_test, y_train, y_test, feature_names):
    le = LabelEncoder()
    y_train_enc = le.fit_transform(y_train)
    y_test_enc = le.transform(y_test)
    n_classes = len(le.classes_)

    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="multi:softprob" if n_classes > 2 else "binary:logistic",
        num_class=n_classes if n_classes > 2 else None,
        eval_metric="mlogloss" if n_classes > 2 else "logloss",
        random_state=42,
        verbosity=0,
    )
    model.fit(X_train, y_train_enc)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test_enc, y_pred)

    # 피처 중요도 상위 5
    importances = model.feature_importances_
    top_idx = np.argsort(importances)[::-1][:5]
    top_features = [(feature_names[i], round(float(importances[i]), 4)) for i in top_idx]

    # 클래스별 성능
    present_labels = sorted(set(y_test_enc) | set(y_pred))
    present_names = [le.classes_[i] for i in present_labels]
    report = classification_report(
        y_test_enc, y_pred, labels=present_labels, target_names=present_names,
        output_dict=True, zero_division=0
    )

    return model, le, acc, top_features, report


def main():
    print("=" * 60)
    print("관상 분류 모델 학습")
    print("=" * 60)

    df, X, feature_names = load_data()
    print(f"데이터: {X.shape[0]}명 × {X.shape[1]} 피처\n")

    X_train, X_test, idx_train, idx_test = train_test_split(
        X, np.arange(len(X)), test_size=0.2, random_state=42
    )

    all_results = {}

    for target in TARGETS:
        y = df[target].values
        y_train, y_test = y[idx_train], y[idx_test]

        model, le, acc, top_features, report = train_one_target(
            X_train, X_test, y_train, y_test, feature_names
        )

        # 저장
        joblib.dump(model, MODEL_DIR / f"{target}_model.joblib")
        joblib.dump(le, MODEL_DIR / f"{target}_encoder.joblib")

        print(f"--- {target} (Accuracy: {acc*100:.1f}%) ---")
        print(f"  Classes: {list(le.classes_)}")
        print(f"  Top features: {top_features}")

        # 클래스별 f1-score
        for cls in le.classes_:
            if cls in report:
                f1 = report[cls]["f1-score"]
                support = int(report[cls]["support"])
                print(f"    {cls:12s}: f1={f1:.3f} (n={support})")
        print()

        all_results[target] = {
            "accuracy": round(acc, 4),
            "n_classes": len(le.classes_),
            "classes": list(le.classes_),
            "top_features": top_features,
        }

    # 전체 요약
    print("=" * 60)
    print("전체 요약")
    print("=" * 60)
    avg_acc = np.mean([r["accuracy"] for r in all_results.values()])
    print(f"평균 Accuracy: {avg_acc*100:.1f}%\n")
    for target, r in all_results.items():
        print(f"  {target:20s}: {r['accuracy']*100:5.1f}%  ({r['n_classes']} classes)")

    # JSON 저장
    with open(MODEL_DIR / "training_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # feature 이름 저장 (추론 시 필요)
    with open(MODEL_DIR / "feature_names.json", "w", encoding="utf-8") as f:
        json.dump(feature_names, f)

    print(f"\n모델 저장 완료: {MODEL_DIR}")


if __name__ == "__main__":
    main()
