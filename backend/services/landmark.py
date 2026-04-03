"""
MediaPipe FaceLandmarker 기반 얼굴 랜드마크 + 비율 추출 서비스
"""

import math
from pathlib import Path

import cv2
import numpy as np
import mediapipe as mp

MODEL_PATH = str(Path(__file__).parent.parent.parent / "ml" / "models" / "face_landmarker.task")

_landmarker = None


def _get_landmarker():
    global _landmarker
    if _landmarker is None:
        options = mp.tasks.vision.FaceLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1,
        )
        _landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(options)
    return _landmarker


def _dist(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def _angle_deg(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.degrees(math.atan2(-dy, dx))


def _midpoint(p1, p2):
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2)


def _to_pixel(landmarks, w, h):
    return [(lm.x * w, lm.y * h, lm.z * w) for lm in landmarks]


def _compute_ratios(px):
    p = lambda i: px[i]

    face_top, face_bottom = p(10), p(152)
    face_left, face_right = p(234), p(454)
    face_height = _dist(face_top, face_bottom)
    face_width = _dist(face_left, face_right)

    if face_height == 0 or face_width == 0:
        return None

    r = {}

    # 눈
    r_eo, r_ei, r_et, r_eb = p(33), p(133), p(159), p(145)
    l_eo, l_ei, l_et, l_eb = p(263), p(362), p(386), p(374)
    r_eh, r_ew = _dist(r_et, r_eb), _dist(r_eo, r_ei)
    l_eh, l_ew = _dist(l_et, l_eb), _dist(l_eo, l_ei)
    aeh, aew = (r_eh + l_eh) / 2, (r_ew + l_ew) / 2

    r["eye_height_ratio"] = aeh / face_height
    r["eye_width_ratio"] = aew / face_width
    r["eye_aspect_ratio"] = aeh / aew if aew > 0 else 0
    r["eye_tilt_deg"] = (_angle_deg(r_ei, r_eo) + _angle_deg(l_ei, l_eo)) / 2
    r["eye_spacing_ratio"] = _dist(r_ei, l_ei) / face_width
    ra, la = r_eh * r_ew, l_eh * l_ew
    aa = (ra + la) / 2
    r["eye_asymmetry"] = abs(ra - la) / aa * 100 if aa > 0 else 0

    if len(px) > 473:
        ri, li = p(468), p(473)
        rp = (ri[1] - r_et[1]) / r_eh if r_eh > 0 else 0.5
        lp = (li[1] - l_et[1]) / l_eh if l_eh > 0 else 0.5
        r["iris_vertical_pos"] = (rp + lp) / 2
    else:
        r["iris_vertical_pos"] = 0.5

    # 눈썹
    lbi, lbp, lbo = p(70), p(105), p(46)
    rbi, rbp, rbo = p(300), p(334), p(276)
    lbl, rbl = _dist(lbi, lbo), _dist(rbi, rbo)
    r["brow_length_ratio"] = ((lbl + rbl) / 2) / face_width
    r["brow_thickness_ratio"] = ((_dist(p(63), p(66)) + _dist(p(293), p(296))) / 2) / face_height
    r["brow_tilt_deg"] = (_angle_deg(lbi, lbo) + _angle_deg(rbi, rbo)) / 2
    lm, rm = _midpoint(lbi, lbo), _midpoint(rbi, rbo)
    lc = abs(lbp[1] - lm[1])
    rc = abs(rbp[1] - rm[1])
    r["brow_curvature"] = ((lc / lbl + rc / rbl) / 2) if lbl > 0 and rbl > 0 else 0
    r["brow_gap_ratio"] = _dist(lbi, rbi) / face_width
    r["brow_eye_gap"] = ((abs(p(66)[1] - l_et[1]) + abs(p(296)[1] - r_et[1])) / 2) / face_height

    # 코
    nb, nt, nbo, nl, nr = p(6), p(1), p(2), p(48), p(278)
    nlen, nwid = _dist(nb, nt), _dist(nl, nr)
    r["nose_length_ratio"] = nlen / face_height
    r["nose_width_ratio"] = nwid / face_width
    r["nose_bridge_depth"] = nb[2]
    r["nose_aspect"] = nlen / nwid if nwid > 0 else 0
    r["nose_tip_angle"] = _angle_deg(nt, nbo)

    # 입
    ml, mr = p(61), p(291)
    ult, ulb, llt, llb = p(37), p(0), p(17), p(84)
    mw = _dist(ml, mr)
    ulh, llh = _dist(ult, ulb), _dist(ulb, llb)
    r["mouth_width_ratio"] = mw / face_width
    r["lip_thickness_ratio"] = _dist(ult, llb) / face_height
    r["lip_ratio"] = ulh / llh if llh > 0 else 1.0
    mcy = (ulb[1] + llt[1]) / 2
    mcory = (ml[1] + mr[1]) / 2
    r["mouth_corner_angle"] = (mcy - mcory) / face_height * 100

    # 이마
    ft, gl, fl, fr = p(10), p(9), p(21), p(251)
    r["forehead_height_ratio"] = _dist(ft, gl) / face_height
    r["forehead_width_ratio"] = _dist(fl, fr) / face_width
    r["forehead_curvature"] = abs(ft[2] - gl[2])

    # 턱
    ct, mb = p(152), p(17)
    jl, jr = p(172), p(397)
    r["chin_length_ratio"] = _dist(mb, ct) / face_height
    r["jaw_width_ratio"] = _dist(jl, jr) / face_width
    cl, cr = p(148), p(377)
    v1 = (cl[0] - ct[0], cl[1] - ct[1])
    v2 = (cr[0] - ct[0], cr[1] - ct[1])
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    m1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
    m2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)
    ca = max(-1, min(1, dot / (m1 * m2) if m1 > 0 and m2 > 0 else 0))
    r["chin_angle_deg"] = math.degrees(math.acos(ca))
    r["chin_protrusion"] = ct[2] - mb[2]

    # 얼굴형
    r["face_ratio"] = face_height / face_width
    fw = _dist(fl, fr)
    jw = _dist(jl, jr)
    r["upper_lower_ratio"] = fw / jw if jw > 0 else 1.0
    ckl, ckr = p(93), p(323)
    ckw = _dist(ckl, ckr)
    r["mid_lower_ratio"] = ckw / jw if jw > 0 else 1.0

    # 인중
    r["philtrum_length_ratio"] = _dist(p(2), p(0)) / face_height
    r["philtrum_depth"] = abs(p(2)[2] - p(0)[2])

    # 광대
    r["cheekbone_width_ratio"] = ckw / face_width
    r["cheekbone_protrusion"] = (ckl[2] + ckr[2]) / 2 - (face_left[2] + face_right[2]) / 2
    r["cheekbone_position"] = ((ckl[1] + ckr[1]) / 2 - face_top[1]) / face_height

    return r


async def extract_landmarks(image_bytes: bytes) -> dict | None:
    """이미지 바이트 → 랜드마크 추출 + 비율 계산"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if bgr is None:
        return None

    landmarker = _get_landmarker()

    # 4방향 회전 시도
    rotations = [None, cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE, cv2.ROTATE_180]

    for rot in rotations:
        candidate = cv2.rotate(bgr, rot) if rot is not None else bgr
        img_h, img_w = candidate.shape[:2]
        rgb = cv2.cvtColor(candidate, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        det = landmarker.detect(image)

        if det.face_landmarks:
            lms = det.face_landmarks[0]
            fh = _dist((lms[10].x * img_w, lms[10].y * img_h), (lms[152].x * img_w, lms[152].y * img_h))
            fw = _dist((lms[234].x * img_w, lms[234].y * img_h), (lms[454].x * img_w, lms[454].y * img_h))
            if fw > 0 and fh / fw > 1.0:
                px = _to_pixel(lms, img_w, img_h)
                ratios = _compute_ratios(px)
                if ratios:
                    return ratios

    return None
