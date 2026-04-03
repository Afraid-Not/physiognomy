"""
규칙 기반 사주 점수 산정
오행 균형도, 용신 강약, 대운 흐름 등을 기반으로 점수화
"""

from services.saju import SajuResult


# ══════════════════════════════════════════════════
# 개별 항목 점수 산정
# ══════════════════════════════════════════════════

def _score_element_balance(result: SajuResult) -> dict:
    """
    오행 균형도 점수 (1~10)
    완벽한 균형(각 20%)에 가까울수록 높은 점수
    """
    pcts = result.element_percentages
    ideal = 20.0
    deviation = sum(abs(v - ideal) for v in pcts.values()) / 5  # 평균 편차
    # 편차 0 -> 10점, 편차 20 -> 1점
    score = max(1.0, min(10.0, 10.0 - deviation * 0.45))

    # 결핍 오행 확인
    missing = [k for k, v in result.element_counts.items() if v == 0]
    excess = [k for k, v in pcts.items() if v >= 37.5]

    return {
        "category": "오행 균형",
        "score": round(score, 1),
        "missing_elements": missing,
        "excess_elements": excess,
    }


def _score_yongsin_strength(result: SajuResult) -> dict:
    """
    용신 강약 점수 (1~10)
    용신 오행이 사주 내에 많을수록 높은 점수
    """
    yongsin_elem = result.yongsin["yongsin"]
    heesin_elem = result.yongsin["heesin"]

    yongsin_count = result.element_counts.get(yongsin_elem, 0)
    heesin_count = result.element_counts.get(heesin_elem, 0)

    # 용신 2개 이상 + 희신 1개 이상 = 최고
    # 용신 0개 = 최저
    base = 3.0
    base += yongsin_count * 2.0
    base += heesin_count * 1.0
    score = max(1.0, min(10.0, base))

    return {
        "category": "용신 강약",
        "score": round(score, 1),
        "yongsin_element": yongsin_elem,
        "yongsin_count": yongsin_count,
    }


def _score_dayun_current(result: SajuResult, current_age: int) -> dict:
    """
    현재 대운 점수 (1~10)
    현재 대운의 오행이 용신/희신이면 높은 점수
    """
    yongsin_elem = result.yongsin["yongsin"]
    heesin_elem = result.yongsin["heesin"]

    current_dayun = None
    for d in result.dayun_list:
        if d["start_age"] <= current_age <= d["end_age"]:
            current_dayun = d
            break

    if not current_dayun:
        return {
            "category": "현재 대운",
            "score": 5.0,
            "current_dayun": None,
        }

    score = 5.0  # 기본
    gan_elem = current_dayun["gan_element"]
    zhi_elem = current_dayun["zhi_element"]

    if gan_elem == yongsin_elem:
        score += 2.0
    elif gan_elem == heesin_elem:
        score += 1.5
    if zhi_elem == yongsin_elem:
        score += 2.0
    elif zhi_elem == heesin_elem:
        score += 1.5

    # 기신 (용신을 극하는 오행) 확인
    from services.saju import CONTROLS
    if CONTROLS.get(gan_elem) == yongsin_elem:
        score -= 2.0
    if CONTROLS.get(zhi_elem) == yongsin_elem:
        score -= 2.0

    score = max(1.0, min(10.0, score))

    return {
        "category": "현재 대운",
        "score": round(score, 1),
        "current_dayun": current_dayun,
    }


def _score_sipsin_balance(result: SajuResult) -> dict:
    """
    십신 구성 점수 (1~10)
    다양한 십신이 골고루 있을수록 높은 점수
    """
    sipsin = result.sipsin_summary
    unique_count = len(sipsin)

    # 10종류 중 몇 개가 있는지 (다양성)
    # 6개 이상 = 좋음, 3개 이하 = 편중
    score = min(10.0, unique_count * 1.3 + 2.0)

    # 재성(편재+정재) 유무 -> 재물운
    has_jae = ("편재" in sipsin) or ("정재" in sipsin)
    # 관성(편관+정관) 유무 -> 직업운/명예운
    has_gwan = ("편관" in sipsin) or ("정관" in sipsin)
    # 인성(편인+정인) 유무 -> 학업/어른복
    has_in = ("편인" in sipsin) or ("정인" in sipsin)

    return {
        "category": "십신 구성",
        "score": round(max(1.0, min(10.0, score)), 1),
        "unique_sipsin": unique_count,
        "has_wealth": has_jae,
        "has_authority": has_gwan,
        "has_support": has_in,
    }


# ══════════════════════════════════════════════════
# 운세별 점수 산정
# ══════════════════════════════════════════════════

def _score_wealth(result: SajuResult) -> dict:
    """재물운 점수"""
    sipsin = result.sipsin_summary
    jae_count = sipsin.get("편재", 0) + sipsin.get("정재", 0)
    sig_count = sipsin.get("식신", 0) + sipsin.get("상관", 0)  # 식상생재

    score = 5.0
    score += jae_count * 1.2
    score += sig_count * 0.8

    # 용신이 재성 관련이면 가산
    yongsin_elem = result.yongsin["yongsin"]
    day_elem = result.day_element
    from services.saju import CONTROLS
    if CONTROLS.get(day_elem) == yongsin_elem:  # 용신이 재성 방향
        score += 1.0

    return {
        "category": "재물운",
        "score": round(max(1.0, min(10.0, score)), 1),
    }


def _score_love(result: SajuResult) -> dict:
    """연애운 점수"""
    sipsin = result.sipsin_summary
    gender = result.gender

    score = 5.0
    if gender == "male":
        # 남자: 정재 = 아내, 편재 = 여자인연
        jae_count = sipsin.get("정재", 0) + sipsin.get("편재", 0)
        score += jae_count * 1.5
    else:
        # 여자: 정관 = 남편, 편관 = 남자인연
        gwan_count = sipsin.get("정관", 0) + sipsin.get("편관", 0)
        score += gwan_count * 1.5

    # 도화살 체크 (간략) - 일지 기준
    dohua_map = {"인": "묘", "신": "유", "사": "오", "해": "자"}
    day_zhi = result.day_pillar.zhi
    for p in [result.year_pillar, result.month_pillar, result.hour_pillar]:
        if dohua_map.get(day_zhi) == p.zhi:
            score += 1.5
            break

    return {
        "category": "연애운",
        "score": round(max(1.0, min(10.0, score)), 1),
    }


def _score_career(result: SajuResult) -> dict:
    """직업운 점수"""
    sipsin = result.sipsin_summary

    score = 5.0
    gwan_count = sipsin.get("정관", 0) + sipsin.get("편관", 0)
    in_count = sipsin.get("정인", 0) + sipsin.get("편인", 0)

    score += gwan_count * 1.2  # 관성 = 직업/직장
    score += in_count * 0.8    # 인성 = 학문/자격

    # 식상 = 전문기술/창의직
    sig_count = sipsin.get("식신", 0) + sipsin.get("상관", 0)
    score += sig_count * 0.6

    return {
        "category": "직업운",
        "score": round(max(1.0, min(10.0, score)), 1),
    }


# ══════════════════════════════════════════════════
# 종합 점수 계산
# ══════════════════════════════════════════════════

def compute_saju_scores(result: SajuResult, current_age: int = 30) -> dict:
    """
    사주 분석 결과 → 규칙 기반 점수 산정

    Returns:
        {
            "overall_score": float,
            "element_balance": {...},
            "yongsin_strength": {...},
            "current_dayun": {...},
            "sipsin_balance": {...},
            "wealth": {...},
            "love": {...},
            "career": {...},
        }
    """
    element = _score_element_balance(result)
    yongsin = _score_yongsin_strength(result)
    dayun = _score_dayun_current(result, current_age)
    sipsin = _score_sipsin_balance(result)
    wealth = _score_wealth(result)
    love = _score_love(result)
    career = _score_career(result)

    all_scores = [
        element["score"], yongsin["score"], dayun["score"],
        sipsin["score"], wealth["score"], love["score"], career["score"],
    ]
    overall = round(sum(all_scores) / len(all_scores), 1)

    return {
        "overall_score": overall,
        "element_balance": element,
        "yongsin_strength": yongsin,
        "current_dayun": dayun,
        "sipsin_balance": sipsin,
        "wealth": wealth,
        "love": love,
        "career": career,
    }
