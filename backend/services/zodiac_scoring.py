"""
별자리 규칙 기반 스코어링 서비스
태양궁 50% + 달궁 30% + 상승궁 20% 가중치 적용
성격 특성 + 적성 점수 계산
"""

# ──────────────────────────────────────────────────
# 별자리별 기본 점수 (1-10)
# ──────────────────────────────────────────────────

# 성격 특성: 적극성 / 감수성 / 창의력 / 사교성 / 직관력 / 실용성
PERSONALITY_SCORES: dict[str, dict[str, float]] = {
    "양자리":     {"적극성": 9, "감수성": 4, "창의력": 6, "사교성": 6, "직관력": 5, "실용성": 5},
    "황소자리":   {"적극성": 4, "감수성": 7, "창의력": 6, "사교성": 5, "직관력": 5, "실용성": 9},
    "쌍둥이자리": {"적극성": 7, "감수성": 5, "창의력": 8, "사교성": 9, "직관력": 6, "실용성": 5},
    "게자리":     {"적극성": 4, "감수성": 9, "창의력": 6, "사교성": 6, "직관력": 8, "실용성": 5},
    "사자자리":   {"적극성": 9, "감수성": 5, "창의력": 8, "사교성": 8, "직관력": 5, "실용성": 5},
    "처녀자리":   {"적극성": 5, "감수성": 7, "창의력": 6, "사교성": 5, "직관력": 7, "실용성": 9},
    "천칭자리":   {"적극성": 5, "감수성": 7, "창의력": 7, "사교성": 9, "직관력": 6, "실용성": 6},
    "전갈자리":   {"적극성": 7, "감수성": 9, "창의력": 7, "사교성": 4, "직관력": 9, "실용성": 6},
    "사수자리":   {"적극성": 8, "감수성": 5, "창의력": 8, "사교성": 8, "직관력": 6, "실용성": 4},
    "염소자리":   {"적극성": 7, "감수성": 4, "창의력": 5, "사교성": 5, "직관력": 5, "실용성": 9},
    "물병자리":   {"적극성": 6, "감수성": 6, "창의력": 9, "사교성": 7, "직관력": 8, "실용성": 5},
    "물고기자리": {"적극성": 3, "감수성": 9, "창의력": 8, "사교성": 6, "직관력": 9, "실용성": 4},
}

# 적성: 리더십·경영 / 예술·창작 / 의료·상담 / 비즈니스·금융 / 탐구·학문 / 사회·봉사 / 공학·기술 / 스포츠·도전
APTITUDE_SCORES: dict[str, dict[str, float]] = {
    "양자리":     {"리더십·경영": 9, "예술·창작": 5, "의료·상담": 3, "비즈니스·금융": 6, "탐구·학문": 5, "사회·봉사": 4, "공학·기술": 6, "스포츠·도전": 9},
    "황소자리":   {"리더십·경영": 5, "예술·창작": 8, "의료·상담": 5, "비즈니스·금융": 8, "탐구·학문": 5, "사회·봉사": 5, "공학·기술": 6, "스포츠·도전": 4},
    "쌍둥이자리": {"리더십·경영": 6, "예술·창작": 8, "의료·상담": 6, "비즈니스·금융": 6, "탐구·학문": 8, "사회·봉사": 7, "공학·기술": 7, "스포츠·도전": 5},
    "게자리":     {"리더십·경영": 5, "예술·창작": 7, "의료·상담": 9, "비즈니스·금융": 6, "탐구·학문": 5, "사회·봉사": 9, "공학·기술": 4, "스포츠·도전": 4},
    "사자자리":   {"리더십·경영": 9, "예술·창작": 8, "의료·상담": 5, "비즈니스·금융": 7, "탐구·학문": 5, "사회·봉사": 5, "공학·기술": 5, "스포츠·도전": 7},
    "처녀자리":   {"리더십·경영": 5, "예술·창작": 6, "의료·상담": 8, "비즈니스·금융": 7, "탐구·학문": 9, "사회·봉사": 7, "공학·기술": 8, "스포츠·도전": 4},
    "천칭자리":   {"리더십·경영": 7, "예술·창작": 9, "의료·상담": 7, "비즈니스·금융": 6, "탐구·학문": 6, "사회·봉사": 8, "공학·기술": 5, "스포츠·도전": 4},
    "전갈자리":   {"리더십·경영": 7, "예술·창작": 7, "의료·상담": 8, "비즈니스·금융": 7, "탐구·학문": 9, "사회·봉사": 6, "공학·기술": 7, "스포츠·도전": 5},
    "사수자리":   {"리더십·경영": 6, "예술·창작": 7, "의료·상담": 5, "비즈니스·금융": 6, "탐구·학문": 8, "사회·봉사": 7, "공학·기술": 5, "스포츠·도전": 8},
    "염소자리":   {"리더십·경영": 9, "예술·창작": 4, "의료·상담": 5, "비즈니스·금융": 9, "탐구·학문": 7, "사회·봉사": 4, "공학·기술": 8, "스포츠·도전": 6},
    "물병자리":   {"리더십·경영": 7, "예술·창작": 8, "의료·상담": 6, "비즈니스·금융": 5, "탐구·학문": 9, "사회·봉사": 8, "공학·기술": 9, "스포츠·도전": 5},
    "물고기자리": {"리더십·경영": 4, "예술·창작": 9, "의료·상담": 9, "비즈니스·금융": 5, "탐구·학문": 7, "사회·봉사": 9, "공학·기술": 4, "스포츠·도전": 4},
}


def _weighted_scores(
    sun_scores: dict[str, float],
    moon_scores: dict[str, float],
    asc_scores: dict[str, float],
) -> dict[str, float]:
    """태양궁 50% + 달궁 30% + 상승궁 20% 가중 평균"""
    all_keys = set(sun_scores) | set(moon_scores) | set(asc_scores)
    result = {}
    for k in all_keys:
        s = sun_scores.get(k, 5.0)
        m = moon_scores.get(k, 5.0)
        a = asc_scores.get(k, 5.0)
        result[k] = round(s * 0.5 + m * 0.3 + a * 0.2, 1)
    return result


def compute_zodiac_scores(
    sun_sign: str,
    moon_sign: str,
    ascendant_sign: str,
) -> dict:
    """
    성격 + 적성 점수 계산
    Returns:
        personality_scores: dict[trait, score]
        aptitude_scores: dict[trait, score]
        overall_score: float
        top_personality: list[dict]  — 상위 3개 성격 특성
        top_aptitude: list[dict]     — 상위 3개 적성
    """
    sun_p = PERSONALITY_SCORES.get(sun_sign, {k: 5.0 for k in PERSONALITY_SCORES["양자리"]})
    moon_p = PERSONALITY_SCORES.get(moon_sign, {k: 5.0 for k in PERSONALITY_SCORES["양자리"]})
    asc_p = PERSONALITY_SCORES.get(ascendant_sign, {k: 5.0 for k in PERSONALITY_SCORES["양자리"]})
    personality_scores = _weighted_scores(sun_p, moon_p, asc_p)

    sun_a = APTITUDE_SCORES.get(sun_sign, {k: 5.0 for k in APTITUDE_SCORES["양자리"]})
    moon_a = APTITUDE_SCORES.get(moon_sign, {k: 5.0 for k in APTITUDE_SCORES["양자리"]})
    asc_a = APTITUDE_SCORES.get(ascendant_sign, {k: 5.0 for k in APTITUDE_SCORES["양자리"]})
    aptitude_scores = _weighted_scores(sun_a, moon_a, asc_a)

    overall = round(sum(personality_scores.values()) / len(personality_scores), 1)

    top_personality = sorted(
        [{"trait": k, "score": v} for k, v in personality_scores.items()],
        key=lambda x: x["score"], reverse=True,
    )[:3]

    top_aptitude = sorted(
        [{"trait": k, "score": v} for k, v in aptitude_scores.items()],
        key=lambda x: x["score"], reverse=True,
    )[:3]

    return {
        "personality_scores": personality_scores,
        "aptitude_scores": aptitude_scores,
        "overall_score": overall,
        "top_personality": top_personality,
        "top_aptitude": top_aptitude,
    }
