"""
타로 카드 규칙 기반 스코어링
카드별 카테고리별 base score + 역방향 보정 + 위치 가중치
"""

from services.tarot import TarotSpread

# ── 카드별 카테고리별 base score (1-10) ──
# [연애, 재물, 직업, 건강, 오늘의 운세]
CARD_BASE_SCORES: dict[int, dict[str, float]] = {
    0:  {"연애": 6, "재물": 4, "직업": 5, "건강": 7, "오늘의 운세": 7},    # 바보
    1:  {"연애": 7, "재물": 8, "직업": 9, "건강": 7, "오늘의 운세": 8},    # 마법사
    2:  {"연애": 6, "재물": 5, "직업": 7, "건강": 6, "오늘의 운세": 7},    # 여사제
    3:  {"연애": 9, "재물": 8, "직업": 7, "건강": 8, "오늘의 운세": 8},    # 여황제
    4:  {"연애": 7, "재물": 9, "직업": 9, "건강": 7, "오늘의 운세": 8},    # 황제
    5:  {"연애": 7, "재물": 6, "직업": 7, "건강": 6, "오늘의 운세": 7},    # 교황
    6:  {"연애": 10, "재물": 5, "직업": 6, "건강": 7, "오늘의 운세": 8},   # 연인
    7:  {"연애": 6, "재물": 7, "직업": 8, "건강": 8, "오늘의 운세": 8},    # 전차
    8:  {"연애": 7, "재물": 7, "직업": 8, "건강": 9, "오늘의 운세": 8},    # 힘
    9:  {"연애": 4, "재물": 5, "직업": 6, "건강": 6, "오늘의 운세": 5},    # 은둔자
    10: {"연애": 7, "재물": 8, "직업": 7, "건강": 6, "오늘의 운세": 9},    # 운명의 수레바퀴
    11: {"연애": 6, "재물": 7, "직업": 8, "건강": 6, "오늘의 운세": 7},    # 정의
    12: {"연애": 4, "재물": 3, "직업": 4, "건강": 4, "오늘의 운세": 4},    # 매달린 사람
    13: {"연애": 3, "재물": 4, "직업": 5, "건강": 3, "오늘의 운세": 4},    # 죽음
    14: {"연애": 7, "재물": 6, "직업": 7, "건강": 8, "오늘의 운세": 7},    # 절제
    15: {"연애": 5, "재물": 6, "직업": 5, "건강": 4, "오늘의 운세": 4},    # 악마
    16: {"연애": 2, "재물": 2, "직업": 3, "건강": 3, "오늘의 운세": 2},    # 탑
    17: {"연애": 8, "재물": 7, "직업": 7, "건강": 8, "오늘의 운세": 9},    # 별
    18: {"연애": 5, "재물": 4, "직업": 4, "건강": 5, "오늘의 운세": 5},    # 달
    19: {"연애": 9, "재물": 9, "직업": 9, "건강": 9, "오늘의 운세": 10},   # 태양
    20: {"연애": 6, "재물": 7, "직업": 7, "건강": 6, "오늘의 운세": 7},    # 심판
    21: {"연애": 9, "재물": 9, "직업": 9, "건강": 8, "오늘의 운세": 10},   # 세계
}

# 위치 가중치 (현재 카드가 가장 중요)
POSITION_WEIGHTS = {
    "과거": 0.2,
    "현재": 0.5,
    "미래": 0.3,
}

# 역방향 보정값
REVERSED_PENALTY = 2.0


def _clamp(value: float, lo: float = 1.0, hi: float = 10.0) -> float:
    return max(lo, min(hi, value))


def compute_tarot_scores(spread: TarotSpread) -> dict:
    """
    쓰리카드 스프레드에서 규칙 기반 점수 계산.

    Returns:
        {
            "category": str,
            "overall_score": float,
            "card_scores": [
                {"position", "card_name", "is_reversed", "base_score", "adjusted_score"},
                ...
            ],
            "fortune_scores": {"luck": float, "timing": float, "energy": float}
        }
    """
    category = spread.category
    card_scores = []
    weighted_sum = 0.0

    upright_count = 0

    for drawn in spread.cards:
        base = CARD_BASE_SCORES.get(drawn.card.number, {}).get(category, 5.0)
        adjusted = _clamp(base - REVERSED_PENALTY) if drawn.is_reversed else base
        weight = POSITION_WEIGHTS[drawn.position]
        weighted_sum += adjusted * weight

        if not drawn.is_reversed:
            upright_count += 1

        card_scores.append({
            "position": drawn.position,
            "card_name": drawn.card.name_ko,
            "is_reversed": drawn.is_reversed,
            "base_score": base,
            "adjusted_score": round(adjusted, 1),
        })

    overall_score = _clamp(round(weighted_sum, 1))

    # fortune sub-scores
    # luck: 3장 base score 평균
    avg_base = sum(cs["base_score"] for cs in card_scores) / 3.0
    luck = _clamp(round(avg_base, 1))

    # timing: 현재 카드 adjusted score 중심
    present_card = next((cs for cs in card_scores if cs["position"] == "현재"), card_scores[1])
    timing = _clamp(round(present_card["adjusted_score"], 1))

    # energy: 정방향 카드 수 기반 (3장 정방향=10, 2장=7.5, 1장=5, 0장=3)
    energy_map = {0: 3.0, 1: 5.0, 2: 7.5, 3: 10.0}
    energy = energy_map[upright_count]

    return {
        "category": category,
        "overall_score": overall_score,
        "card_scores": card_scores,
        "fortune_scores": {
            "luck": luck,
            "timing": timing,
            "energy": energy,
        },
    }
