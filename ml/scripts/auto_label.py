"""
분위수 기반 임계값 재설정 + 자동 라벨링
face_ratios.csv → face_labels.csv

3단계 파이프라인:
  1. 비율 수치 → 분위수 기반 속성 분류 (소/중/대 등)
  2. 속성 조합 → 관상 명칭 매핑
  3. 결과 저장
"""

import json
import csv
from pathlib import Path

import pandas as pd
import numpy as np

# ── 경로 설정 ──
BASE_DIR = Path(r"D:\dev\physiognomy")
RATIOS_CSV = BASE_DIR / "ml" / "data" / "face_ratios.csv"
OUTPUT_CSV = BASE_DIR / "ml" / "data" / "face_labels.csv"
THRESHOLDS_JSON = BASE_DIR / "ml" / "data" / "thresholds.json"


# ══════════════════════════════════════════════════
# 1단계: 분위수 기반 임계값 계산
# ══════════════════════════════════════════════════

def compute_thresholds(df):
    """25%, 75% 분위수 기반 3분류 임계값"""
    thresholds = {}

    # --- 눈 (Eyes) ---
    thresholds["eye_height_ratio"] = {
        "small": df["eye_height_ratio"].quantile(0.25),
        "large": df["eye_height_ratio"].quantile(0.75),
        "labels": ["소", "중", "대"],
    }
    thresholds["eye_width_ratio"] = {
        "small": df["eye_width_ratio"].quantile(0.25),
        "large": df["eye_width_ratio"].quantile(0.75),
        "labels": ["단", "중", "장"],
    }
    thresholds["eye_aspect_ratio"] = {
        "small": df["eye_aspect_ratio"].quantile(0.25),
        "large": df["eye_aspect_ratio"].quantile(0.75),
        "labels": ["세장형", "보통", "둥근형"],
    }
    # 눈꼬리 각도: 음수=처진눈, 양수=올라간눈 (중앙이 ~88도라 보정 필요)
    # 실제 분포에서 25%~75% 기준
    thresholds["eye_tilt_deg"] = {
        "small": df["eye_tilt_deg"].quantile(0.25),
        "large": df["eye_tilt_deg"].quantile(0.75),
        "labels": ["처진눈", "수평", "올라간눈"],
    }
    thresholds["eye_spacing_ratio"] = {
        "small": df["eye_spacing_ratio"].quantile(0.25),
        "large": df["eye_spacing_ratio"].quantile(0.75),
        "labels": ["좁음", "보통", "넓음"],
    }
    # 비대칭: 25% 기준 (상위 ~13%만 음양안 판정)
    thresholds["eye_asymmetry"] = {
        "small": 25.0,
        "large": 25.0,
        "labels": ["대칭", "비대칭"],
        "binary": True,
    }
    # 삼백안: 홍채 위치 (0.5 = 정중앙)
    thresholds["iris_vertical_pos"] = {
        "small": 0.35,
        "large": 0.65,
        "labels": ["상삼백", "정상", "하삼백"],
    }

    # --- 눈썹 (Eyebrows) ---
    thresholds["brow_length_ratio"] = {
        "small": df["brow_length_ratio"].quantile(0.25),
        "large": df["brow_length_ratio"].quantile(0.75),
        "labels": ["단", "중", "장"],
    }
    thresholds["brow_thickness_ratio"] = {
        "small": df["brow_thickness_ratio"].quantile(0.25),
        "large": df["brow_thickness_ratio"].quantile(0.75),
        "labels": ["가늘", "보통", "굵은"],
    }
    thresholds["brow_tilt_deg"] = {
        "small": df["brow_tilt_deg"].quantile(0.25),
        "large": df["brow_tilt_deg"].quantile(0.75),
        "labels": ["하강형", "수평", "상승형"],
    }
    thresholds["brow_curvature"] = {
        "small": df["brow_curvature"].quantile(0.25),
        "large": df["brow_curvature"].quantile(0.75),
        "labels": ["직선", "완만", "아치형"],
    }
    thresholds["brow_gap_ratio"] = {
        "small": df["brow_gap_ratio"].quantile(0.25),
        "large": df["brow_gap_ratio"].quantile(0.75),
        "labels": ["좁음", "보통", "넓음"],
    }
    thresholds["brow_eye_gap"] = {
        "small": df["brow_eye_gap"].quantile(0.25),
        "large": df["brow_eye_gap"].quantile(0.75),
        "labels": ["좁음", "보통", "넓음"],
    }

    # --- 코 (Nose) ---
    thresholds["nose_length_ratio"] = {
        "small": df["nose_length_ratio"].quantile(0.25),
        "large": df["nose_length_ratio"].quantile(0.75),
        "labels": ["단", "중", "장"],
    }
    thresholds["nose_width_ratio"] = {
        "small": df["nose_width_ratio"].quantile(0.25),
        "large": df["nose_width_ratio"].quantile(0.75),
        "labels": ["좁음", "보통", "넓음"],
    }
    thresholds["nose_bridge_depth"] = {
        "small": df["nose_bridge_depth"].quantile(0.25),
        "large": df["nose_bridge_depth"].quantile(0.75),
        "labels": ["낮음", "보통", "높음"],
    }
    thresholds["nose_aspect"] = {
        "small": df["nose_aspect"].quantile(0.25),
        "large": df["nose_aspect"].quantile(0.75),
        "labels": ["넓적", "균형", "길쭉"],
    }
    thresholds["nose_tip_angle"] = {
        "small": df["nose_tip_angle"].quantile(0.25),
        "large": df["nose_tip_angle"].quantile(0.75),
        "labels": ["매부리", "보통", "들창코"],
    }

    # --- 입 (Mouth) ---
    thresholds["mouth_width_ratio"] = {
        "small": df["mouth_width_ratio"].quantile(0.25),
        "large": df["mouth_width_ratio"].quantile(0.75),
        "labels": ["소", "중", "대"],
    }
    thresholds["lip_thickness_ratio"] = {
        "small": df["lip_thickness_ratio"].quantile(0.25),
        "large": df["lip_thickness_ratio"].quantile(0.75),
        "labels": ["얇음", "보통", "두꺼움"],
    }
    thresholds["lip_ratio"] = {
        "small": 0.8,
        "large": 1.2,
        "labels": ["아랫입술우세", "균형", "윗입술우세"],
    }
    thresholds["mouth_corner_angle"] = {
        "small": df["mouth_corner_angle"].quantile(0.25),
        "large": df["mouth_corner_angle"].quantile(0.75),
        "labels": ["처진입", "수평", "올라간입"],
    }

    # --- 이마 (Forehead) ---
    thresholds["forehead_height_ratio"] = {
        "small": df["forehead_height_ratio"].quantile(0.25),
        "large": df["forehead_height_ratio"].quantile(0.75),
        "labels": ["좁음", "보통", "넓음"],
    }
    thresholds["forehead_width_ratio"] = {
        "small": df["forehead_width_ratio"].quantile(0.25),
        "large": df["forehead_width_ratio"].quantile(0.75),
        "labels": ["좁음", "보통", "넓음"],
    }

    # --- 턱 (Chin/Jaw) ---
    thresholds["chin_length_ratio"] = {
        "small": df["chin_length_ratio"].quantile(0.25),
        "large": df["chin_length_ratio"].quantile(0.75),
        "labels": ["짧음", "보통", "긴"],
    }
    thresholds["jaw_width_ratio"] = {
        "small": df["jaw_width_ratio"].quantile(0.25),
        "large": df["jaw_width_ratio"].quantile(0.75),
        "labels": ["좁음", "보통", "넓음"],
    }
    thresholds["chin_angle_deg"] = {
        "small": df["chin_angle_deg"].quantile(0.25),
        "large": df["chin_angle_deg"].quantile(0.75),
        "labels": ["뾰족", "보통", "둥근"],
    }

    # --- 얼굴형 (Face Shape) ---
    thresholds["face_ratio"] = {
        "small": df["face_ratio"].quantile(0.25),
        "large": df["face_ratio"].quantile(0.75),
        "labels": ["넓적", "보통", "길쭉"],
    }
    thresholds["upper_lower_ratio"] = {
        "small": 0.9,
        "large": 1.3,
        "labels": ["삼각", "균형", "역삼각"],
    }

    # --- 인중 (Philtrum) ---
    thresholds["philtrum_length_ratio"] = {
        "small": df["philtrum_length_ratio"].quantile(0.25),
        "large": df["philtrum_length_ratio"].quantile(0.75),
        "labels": ["짧음", "보통", "긴"],
    }

    # --- 광대뼈 (Cheekbones) ---
    thresholds["cheekbone_width_ratio"] = {
        "small": df["cheekbone_width_ratio"].quantile(0.25),
        "large": df["cheekbone_width_ratio"].quantile(0.75),
        "labels": ["좁음", "보통", "넓음"],
    }
    thresholds["cheekbone_protrusion"] = {
        "small": df["cheekbone_protrusion"].quantile(0.25),
        "large": df["cheekbone_protrusion"].quantile(0.75),
        "labels": ["평탄", "보통", "돌출"],
    }
    thresholds["cheekbone_position"] = {
        "small": df["cheekbone_position"].quantile(0.25),
        "large": df["cheekbone_position"].quantile(0.75),
        "labels": ["높음", "보통", "낮음"],
    }

    return thresholds


# ══════════════════════════════════════════════════
# 2단계: 속성 분류
# ══════════════════════════════════════════════════

def classify_attribute(value, threshold_info):
    """비율 수치 → 속성 라벨 분류"""
    if threshold_info.get("binary"):
        return threshold_info["labels"][0] if value < threshold_info["small"] else threshold_info["labels"][1]

    if value < threshold_info["small"]:
        return threshold_info["labels"][0]
    elif value > threshold_info["large"]:
        return threshold_info["labels"][2]
    else:
        return threshold_info["labels"][1]


def classify_all_attributes(row, thresholds):
    """한 행의 모든 비율 → 속성 분류"""
    attrs = {}
    for col, thresh in thresholds.items():
        if col in row:
            attrs[f"attr_{col}"] = classify_attribute(row[col], thresh)
    return attrs


# ══════════════════════════════════════════════════
# 3단계: 관상 명칭 매핑
# ══════════════════════════════════════════════════

def map_eye_type(attrs):
    """눈 관상 매핑"""
    size = attrs.get("attr_eye_height_ratio", "중")
    length = attrs.get("attr_eye_width_ratio", "중")
    aspect = attrs.get("attr_eye_aspect_ratio", "보통")
    tilt = attrs.get("attr_eye_tilt_deg", "수평")
    symmetry = attrs.get("attr_eye_asymmetry", "대칭")
    sclera = attrs.get("attr_iris_vertical_pos", "정상")

    # 비대칭 우선
    if symmetry == "비대칭":
        return "음양안"

    # 삼백안 우선
    if sclera in ("상삼백", "하삼백"):
        return "삼백안"

    # 조합 매핑 (우선순위 순)
    if aspect == "세장형" and length == "장" and tilt == "올라간눈" and symmetry == "대칭":
        return "봉안"
    if size == "대" and length == "장" and tilt == "올라간눈":
        return "용안"
    if size == "대" and aspect == "둥근형" and tilt == "올라간눈":
        return "호안"
    if size == "대" and length == "장" and tilt == "수평" and symmetry == "대칭":
        return "공작안"
    if aspect in ("보통", "둥근형") and tilt in ("처진눈", "수평") and size in ("중", "대"):
        return "도화안"
    if size == "중" and aspect == "둥근형" and tilt == "수평" and symmetry == "대칭":
        return "원앙안"
    if aspect == "세장형" and length == "장" and tilt == "수평":
        return "학안"
    if aspect == "세장형" and size == "소" and tilt == "올라간눈":
        return "사안"
    if aspect == "세장형" and size in ("소", "중") and tilt == "올라간눈":
        return "앵안"
    if aspect == "둥근형" and tilt == "처진눈":
        return "우안"
    if size == "중" and aspect == "둥근형" and tilt == "처진눈":
        return "취안"

    return "보통눈"


def map_eyebrow_type(attrs):
    """눈썹 관상 매핑"""
    length = attrs.get("attr_brow_length_ratio", "중")
    thick = attrs.get("attr_brow_thickness_ratio", "보통")
    tilt = attrs.get("attr_brow_tilt_deg", "수평")
    curve = attrs.get("attr_brow_curvature", "완만")
    gap = attrs.get("attr_brow_gap_ratio", "보통")

    if gap == "좁음" and thick in ("보통", "굵은"):
        return "연미"
    if tilt == "수평" and curve == "직선":
        return "일자눈썹"
    if curve in ("완만", "아치형") and thick in ("가늘", "보통"):
        return "초승달눈썹"
    if length == "장" and thick == "가늘" and curve == "완만":
        return "유엽미"
    if thick == "굵은" and curve == "직선" and tilt == "상승형":
        return "검미"
    if tilt == "하강형" and curve == "완만":
        return "팔자눈썹"
    if tilt == "상승형" and curve == "직선" and thick == "굵은":
        return "삼각눈썹"
    if length == "단" and thick == "굵은":
        return "단미"
    if thick == "굵은" and length == "장":
        return "농미"
    if thick == "가늘" and length == "단":
        return "담미"

    return "보통눈썹"


def map_nose_type(attrs):
    """코 관상 매핑"""
    length = attrs.get("attr_nose_length_ratio", "중")
    width = attrs.get("attr_nose_width_ratio", "보통")
    bridge = attrs.get("attr_nose_bridge_depth", "보통")
    tip = attrs.get("attr_nose_tip_angle", "보통")

    if bridge == "높음" and length == "장" and tip == "매부리" and width == "좁음":
        return "독수리코"
    if bridge == "높음" and length == "장" and tip == "매부리":
        return "매부리코"
    if width == "넓음" and bridge == "높음" and length in ("중", "장"):
        return "복코"
    if width == "넓음" and bridge == "높음" and length == "장":
        return "사자코"
    if tip == "들창코" and length in ("단", "중"):
        return "들창코"
    if length == "단" and width in ("좁음", "보통"):
        return "단코"
    if width == "넓음" and bridge in ("낮음", "보통"):
        return "주먹코"

    return "보통코"


def map_mouth_type(attrs):
    """입 관상 매핑"""
    width = attrs.get("attr_mouth_width_ratio", "중")
    thick = attrs.get("attr_lip_thickness_ratio", "보통")
    lip_bal = attrs.get("attr_lip_ratio", "균형")
    corner = attrs.get("attr_mouth_corner_angle", "수평")

    if width == "소" and thick == "두꺼움" and corner == "올라간입":
        return "앵두입"
    if width in ("중", "대") and thick == "두꺼움" and corner == "올라간입":
        return "복입"
    if width == "대" and thick == "두꺼움" and corner == "올라간입":
        return "용입"
    if width == "중" and thick in ("얇음", "보통") and corner == "수평":
        return "일자입"
    if width == "중" and thick == "얇음" and corner in ("수평", "처진입"):
        return "박입"
    if lip_bal == "아랫입술우세" and thick == "두꺼움":
        return "받침입"
    if width in ("소", "중") and thick == "얇음":
        return "다문입"

    return "보통입"


def map_forehead_type(attrs):
    """이마 관상 매핑"""
    height = attrs.get("attr_forehead_height_ratio", "보통")
    width = attrs.get("attr_forehead_width_ratio", "보통")

    if height == "넓음" and width == "넓음":
        return "넓은이마"
    if height == "좁음" or width == "좁음":
        return "좁은이마"
    if height == "넓음":
        return "높은이마"

    return "보통이마"


def map_chin_type(attrs):
    """턱 관상 매핑"""
    length = attrs.get("attr_chin_length_ratio", "보통")
    width = attrs.get("attr_jaw_width_ratio", "보통")
    angle = attrs.get("attr_chin_angle_deg", "보통")

    if width == "넓음" and length in ("보통", "긴"):
        return "각턱"
    if width == "좁음" and angle == "뾰족":
        return "V라인턱"
    if angle == "둥근":
        return "둥근턱"
    if length == "짧음":
        return "짧은턱"
    if length == "긴":
        return "긴턱"

    return "보통턱"


def map_face_shape(attrs):
    """얼굴형 관상 매핑"""
    ratio = attrs.get("attr_face_ratio", "보통")
    balance = attrs.get("attr_upper_lower_ratio", "균형")
    jaw = attrs.get("attr_jaw_width_ratio", "보통")
    chin_angle = attrs.get("attr_chin_angle_deg", "보통")

    if ratio in ("보통", "길쭉") and balance == "균형" and chin_angle in ("보통", "둥근"):
        return "계란형"
    if ratio == "넓적" and balance == "균형":
        return "둥근형"
    if ratio in ("넓적", "보통") and jaw == "넓음":
        return "각진형"
    if balance == "역삼각":
        return "역삼각형"
    if ratio == "길쭉" and balance == "균형":
        return "긴형"

    return "보통형"


def map_philtrum_type(attrs):
    """인중 관상 매핑"""
    length = attrs.get("attr_philtrum_length_ratio", "보통")
    if length == "긴":
        return "긴인중"
    if length == "짧음":
        return "짧은인중"
    return "보통인중"


def map_cheekbone_type(attrs):
    """광대뼈 관상 매핑"""
    width = attrs.get("attr_cheekbone_width_ratio", "보통")
    protrusion = attrs.get("attr_cheekbone_protrusion", "보통")
    position = attrs.get("attr_cheekbone_position", "보통")

    if position == "높음" and protrusion == "돌출":
        return "높은광대"
    if width == "넓음" and protrusion == "돌출":
        return "넓은광대"
    if protrusion == "평탄":
        return "평평한광대"
    if position == "낮음":
        return "낮은광대"

    return "보통광대"


# ══════════════════════════════════════════════════
# 메인 실행
# ══════════════════════════════════════════════════

def main():
    df = pd.read_csv(RATIOS_CSV)
    print(f"Loaded {len(df)} rows from {RATIOS_CSV}")

    # 1. 임계값 계산
    thresholds = compute_thresholds(df)

    # 임계값 저장 (JSON)
    thresholds_serializable = {}
    for k, v in thresholds.items():
        thresholds_serializable[k] = {
            "small": float(v["small"]),
            "large": float(v["large"]),
            "labels": v["labels"],
        }
        if v.get("binary"):
            thresholds_serializable[k]["binary"] = True

    with open(THRESHOLDS_JSON, "w", encoding="utf-8") as f:
        json.dump(thresholds_serializable, f, ensure_ascii=False, indent=2)
    print(f"Thresholds saved to {THRESHOLDS_JSON}")

    # 2. 속성 분류 + 관상 매핑
    results = []
    for _, row in df.iterrows():
        attrs = classify_all_attributes(row.to_dict(), thresholds)

        # 관상 명칭 매핑
        labels = {
            "filename": row["filename"],
            "subject_id": row["subject_id"],
        }
        labels.update(attrs)
        labels["eye_type"] = map_eye_type(attrs)
        labels["eyebrow_type"] = map_eyebrow_type(attrs)
        labels["nose_type"] = map_nose_type(attrs)
        labels["mouth_type"] = map_mouth_type(attrs)
        labels["forehead_type"] = map_forehead_type(attrs)
        labels["chin_type"] = map_chin_type(attrs)
        labels["face_shape"] = map_face_shape(attrs)
        labels["philtrum_type"] = map_philtrum_type(attrs)
        labels["cheekbone_type"] = map_cheekbone_type(attrs)

        results.append(labels)

    # 3. 저장
    result_df = pd.DataFrame(results)
    result_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"Labels saved to {OUTPUT_CSV}")

    # 4. 분포 요약
    print("\n=== 관상 분류 분포 ===\n")
    type_cols = ["eye_type", "eyebrow_type", "nose_type", "mouth_type",
                 "forehead_type", "chin_type", "face_shape", "philtrum_type", "cheekbone_type"]
    for col in type_cols:
        print(f"--- {col} ---")
        print(result_df[col].value_counts().to_string())
        print()


if __name__ == "__main__":
    main()
