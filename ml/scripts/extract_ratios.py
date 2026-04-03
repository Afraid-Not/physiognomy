"""
MediaPipe FaceLandmarker로 랜드마크 추출 → 얼굴 비율 수치 계산
labeling_criteria.md 기준 30+ 비율 속성 추출

중요: 정규화 좌표를 픽셀 좌표로 변환 후 비율 계산 (이미지 종횡비 보정)
"""

import math
import csv
from pathlib import Path

import cv2
import mediapipe as mp

# ── 경로 설정 ──
BASE_DIR = Path(r"D:\dev\physiognomy")
IMAGE_DIR = BASE_DIR / "ml" / "data" / "face-image-aihub"
OUTPUT_CSV = BASE_DIR / "ml" / "data" / "face_ratios.csv"
FAIL_LOG = BASE_DIR / "ml" / "data" / "face_ratios_fail.txt"
MODEL_PATH = str(BASE_DIR / "ml" / "models" / "face_landmarker.task")

# ── MediaPipe 설정 ──
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions


# ── 유틸리티 ──
def dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def angle_deg(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.degrees(math.atan2(-dy, dx))


def midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2)


def to_pixel_coords(landmarks, img_w, img_h):
    """정규화 좌표 → 픽셀 좌표 변환 (z는 얼굴 너비 기준 상대값 유지)"""
    return [
        (lm.x * img_w, lm.y * img_h, lm.z * img_w)  # z도 폭 기준 스케일
        for lm in landmarks
    ]


# ── 비율 계산 ──
def compute_ratios(px_landmarks):
    """픽셀 좌표 기반 비율 계산"""
    p = lambda idx: px_landmarks[idx]

    face_top = p(10)
    face_bottom = p(152)
    face_left = p(234)
    face_right = p(454)

    face_height = dist(face_top, face_bottom)
    face_width = dist(face_left, face_right)

    if face_height == 0 or face_width == 0:
        return None

    ratios = {}

    # ═══ 1. 눈 (Eyes) ═══
    r_eye_outer, r_eye_inner = p(33), p(133)
    r_eye_top, r_eye_bottom = p(159), p(145)
    l_eye_outer, l_eye_inner = p(263), p(362)
    l_eye_top, l_eye_bottom = p(386), p(374)

    r_eye_height = dist(r_eye_top, r_eye_bottom)
    r_eye_width = dist(r_eye_outer, r_eye_inner)
    l_eye_height = dist(l_eye_top, l_eye_bottom)
    l_eye_width = dist(l_eye_outer, l_eye_inner)

    avg_eye_height = (r_eye_height + l_eye_height) / 2
    avg_eye_width = (r_eye_width + l_eye_width) / 2

    ratios["eye_height_ratio"] = avg_eye_height / face_height
    ratios["eye_width_ratio"] = avg_eye_width / face_width
    ratios["eye_aspect_ratio"] = avg_eye_height / avg_eye_width if avg_eye_width > 0 else 0

    r_eye_tilt = angle_deg(r_eye_inner, r_eye_outer)
    l_eye_tilt = angle_deg(l_eye_inner, l_eye_outer)
    ratios["eye_tilt_deg"] = (r_eye_tilt + l_eye_tilt) / 2

    eye_spacing = dist(r_eye_inner, l_eye_inner)
    ratios["eye_spacing_ratio"] = eye_spacing / face_width

    r_eye_area = r_eye_height * r_eye_width
    l_eye_area = l_eye_height * l_eye_width
    avg_area = (r_eye_area + l_eye_area) / 2
    ratios["eye_asymmetry"] = abs(r_eye_area - l_eye_area) / avg_area * 100 if avg_area > 0 else 0

    # 홍채 위치
    if len(px_landmarks) > 473:
        r_iris = p(468)
        l_iris = p(473)
        r_iris_pos = (r_iris[1] - r_eye_top[1]) / r_eye_height if r_eye_height > 0 else 0.5
        l_iris_pos = (l_iris[1] - l_eye_top[1]) / l_eye_height if l_eye_height > 0 else 0.5
        ratios["iris_vertical_pos"] = (r_iris_pos + l_iris_pos) / 2
    else:
        ratios["iris_vertical_pos"] = 0.5

    # ═══ 2. 눈썹 (Eyebrows) ═══
    l_brow_inner, l_brow_peak, l_brow_outer = p(70), p(105), p(46)
    r_brow_inner, r_brow_peak, r_brow_outer = p(300), p(334), p(276)

    l_brow_length = dist(l_brow_inner, l_brow_outer)
    r_brow_length = dist(r_brow_inner, r_brow_outer)
    avg_brow_length = (l_brow_length + r_brow_length) / 2

    ratios["brow_length_ratio"] = avg_brow_length / face_width

    l_brow_thick = dist(p(63), p(66))
    r_brow_thick = dist(p(293), p(296))
    ratios["brow_thickness_ratio"] = ((l_brow_thick + r_brow_thick) / 2) / face_height

    l_brow_tilt = angle_deg(l_brow_inner, l_brow_outer)
    r_brow_tilt = angle_deg(r_brow_inner, r_brow_outer)
    ratios["brow_tilt_deg"] = (l_brow_tilt + r_brow_tilt) / 2

    l_brow_mid = midpoint(l_brow_inner, l_brow_outer)
    r_brow_mid = midpoint(r_brow_inner, r_brow_outer)
    l_curve = abs(l_brow_peak[1] - l_brow_mid[1])
    r_curve = abs(r_brow_peak[1] - r_brow_mid[1])
    ratios["brow_curvature"] = ((l_curve / l_brow_length + r_curve / r_brow_length) / 2) if l_brow_length > 0 and r_brow_length > 0 else 0

    ratios["brow_gap_ratio"] = dist(l_brow_inner, r_brow_inner) / face_width

    l_brow_eye_gap = abs(p(66)[1] - l_eye_top[1])
    r_brow_eye_gap = abs(p(296)[1] - r_eye_top[1])
    ratios["brow_eye_gap"] = ((l_brow_eye_gap + r_brow_eye_gap) / 2) / face_height

    # ═══ 3. 코 (Nose) ═══
    nose_bridge = p(6)
    nose_tip = p(1)
    nose_bottom = p(2)
    nose_left = p(48)
    nose_right = p(278)

    nose_length = dist(nose_bridge, nose_tip)
    nose_width = dist(nose_left, nose_right)

    ratios["nose_length_ratio"] = nose_length / face_height
    ratios["nose_width_ratio"] = nose_width / face_width
    ratios["nose_bridge_depth"] = nose_bridge[2]
    ratios["nose_aspect"] = nose_length / nose_width if nose_width > 0 else 0
    ratios["nose_tip_angle"] = angle_deg(nose_tip, nose_bottom)

    # ═══ 4. 입 (Mouth) ═══
    mouth_left = p(61)
    mouth_right = p(291)
    upper_lip_top = p(37)
    upper_lip_bottom = p(0)
    lower_lip_top = p(17)
    lower_lip_bottom = p(84)

    mouth_width = dist(mouth_left, mouth_right)
    lip_total_height = dist(upper_lip_top, lower_lip_bottom)
    upper_lip_height = dist(upper_lip_top, upper_lip_bottom)
    lower_lip_height = dist(upper_lip_bottom, lower_lip_bottom)

    ratios["mouth_width_ratio"] = mouth_width / face_width
    ratios["lip_thickness_ratio"] = lip_total_height / face_height
    ratios["lip_ratio"] = upper_lip_height / lower_lip_height if lower_lip_height > 0 else 1.0

    mouth_center_y = (upper_lip_bottom[1] + lower_lip_top[1]) / 2
    mouth_corner_y = (mouth_left[1] + mouth_right[1]) / 2
    ratios["mouth_corner_angle"] = (mouth_center_y - mouth_corner_y) / face_height * 100

    # ═══ 5. 이마 (Forehead) ═══
    forehead_top = p(10)
    glabella = p(9)
    forehead_left = p(21)
    forehead_right = p(251)

    ratios["forehead_height_ratio"] = dist(forehead_top, glabella) / face_height
    ratios["forehead_width_ratio"] = dist(forehead_left, forehead_right) / face_width
    ratios["forehead_curvature"] = abs(forehead_top[2] - glabella[2])

    # ═══ 6. 턱 (Chin/Jaw) ═══
    chin_tip = p(152)
    mouth_bottom = p(17)
    jaw_left = p(172)
    jaw_right = p(397)

    ratios["chin_length_ratio"] = dist(mouth_bottom, chin_tip) / face_height
    ratios["jaw_width_ratio"] = dist(jaw_left, jaw_right) / face_width

    chin_left = p(148)
    chin_right = p(377)
    v1 = (chin_left[0] - chin_tip[0], chin_left[1] - chin_tip[1])
    v2 = (chin_right[0] - chin_tip[0], chin_right[1] - chin_tip[1])
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
    cos_angle = max(-1, min(1, dot / (mag1 * mag2) if mag1 > 0 and mag2 > 0 else 0))
    ratios["chin_angle_deg"] = math.degrees(math.acos(cos_angle))

    ratios["chin_protrusion"] = chin_tip[2] - mouth_bottom[2]

    # ═══ 7. 얼굴형 (Face Shape) ═══
    ratios["face_ratio"] = face_height / face_width

    forehead_w = dist(forehead_left, forehead_right)
    jaw_w = dist(jaw_left, jaw_right)
    ratios["upper_lower_ratio"] = forehead_w / jaw_w if jaw_w > 0 else 1.0

    cheek_left = p(93)
    cheek_right = p(323)
    cheek_w = dist(cheek_left, cheek_right)
    ratios["mid_lower_ratio"] = cheek_w / jaw_w if jaw_w > 0 else 1.0

    # ═══ 8. 인중 (Philtrum) ═══
    philtrum_top = p(2)
    philtrum_bottom = p(0)

    ratios["philtrum_length_ratio"] = dist(philtrum_top, philtrum_bottom) / face_height
    ratios["philtrum_depth"] = abs(philtrum_top[2] - philtrum_bottom[2])

    # ═══ 9. 광대뼈 (Cheekbones) ═══
    ratios["cheekbone_width_ratio"] = cheek_w / face_width

    cheek_z_avg = (cheek_left[2] + cheek_right[2]) / 2
    face_z_avg = (face_left[2] + face_right[2]) / 2
    ratios["cheekbone_protrusion"] = cheek_z_avg - face_z_avg

    cheek_y_avg = (cheek_left[1] + cheek_right[1]) / 2
    ratios["cheekbone_position"] = (cheek_y_avg - face_top[1]) / face_height

    return ratios


# ── 메인 실행 ──
def process_images():
    all_images = []
    for d in sorted(IMAGE_DIR.iterdir()):
        if d.is_dir():
            all_images.extend(sorted(d.glob("*.png")))

    print(f"Total images: {len(all_images)}")

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
        num_faces=1,
    )

    results = []
    failed = []

    rotations = [
        None,
        cv2.ROTATE_90_CLOCKWISE,
        cv2.ROTATE_90_COUNTERCLOCKWISE,
        cv2.ROTATE_180,
    ]

    with FaceLandmarker.create_from_options(options) as landmarker:
        for i, img_path in enumerate(all_images):
            bgr = cv2.imread(str(img_path))
            if bgr is None:
                failed.append(f"{img_path.name}: failed to read")
                continue

            # 각 회전 시도 — face_ratio > 1.0 (픽셀 기준) 인 결과만 채택
            best_detection = None
            best_img_shape = None

            for rot in rotations:
                candidate = cv2.rotate(bgr, rot) if rot is not None else bgr
                img_h, img_w = candidate.shape[:2]
                rgb = cv2.cvtColor(candidate, cv2.COLOR_BGR2RGB)
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                det = landmarker.detect(image)

                if det.face_landmarks:
                    lms = det.face_landmarks[0]
                    # 픽셀 좌표로 face_ratio 검증
                    fh = dist(
                        (lms[10].x * img_w, lms[10].y * img_h),
                        (lms[152].x * img_w, lms[152].y * img_h),
                    )
                    fw = dist(
                        (lms[234].x * img_w, lms[234].y * img_h),
                        (lms[454].x * img_w, lms[454].y * img_h),
                    )
                    if fw > 0 and fh / fw > 1.0:
                        best_detection = det
                        best_img_shape = (img_w, img_h)
                        break

            if best_detection is None or not best_detection.face_landmarks:
                failed.append(f"{img_path.name}: no face detected")
                continue

            img_w, img_h = best_img_shape
            landmarks = best_detection.face_landmarks[0]
            px_landmarks = to_pixel_coords(landmarks, img_w, img_h)
            ratios = compute_ratios(px_landmarks)

            if ratios is None:
                failed.append(f"{img_path.name}: invalid landmarks")
                continue

            ratios["filename"] = img_path.name
            ratios["subject_id"] = img_path.stem.split("_")[0]
            results.append(ratios)

            if (i + 1) % 100 == 0:
                print(f"  {i + 1}/{len(all_images)} processed...", flush=True)

    # CSV 저장
    if results:
        fieldnames = ["filename", "subject_id"] + [k for k in results[0] if k not in ("filename", "subject_id")]
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

    FAIL_LOG.write_text("\n".join(failed), encoding="utf-8")

    print(f"\nDone!")
    print(f"  Success: {len(results)}")
    print(f"  Failed:  {len(failed)}")
    print(f"  Output:  {OUTPUT_CSV}")


if __name__ == "__main__":
    process_images()
