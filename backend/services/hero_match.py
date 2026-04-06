"""
한국 위인 매칭 서비스
분석 결과의 특성 조합을 기반으로 가장 유사한 한국 위인을 매칭
"""

from dataclasses import dataclass


@dataclass
class Hero:
    name: str
    title: str        # 한 줄 별명
    description: str  # 매칭 시 보여줄 설명
    tags: list[str]   # 공통 특성 태그
    # 매칭 조건 (점수 가중치)
    traits: dict[str, float]  # {"wealth": 0.8, "career": 0.9, ...}


# ══════════════════════════════════════════════════
# 한국 위인 데이터
# ══════════════════════════════════════════════════

HEROES = [
    Hero(
        name="세종대왕",
        title="학문과 창의의 성군",
        description="뛰어난 학문적 성취와 창의력으로 한글을 창제한 조선 최고의 성군입니다. 인성과 지혜가 조화를 이룬 사주를 가졌습니다.",
        tags=["학문", "창의력", "리더십", "인성"],
        traits={"career": 0.9, "wisdom": 0.9, "leadership": 0.8, "creativity": 0.9, "wealth": 0.5},
    ),
    Hero(
        name="이순신",
        title="불굴의 충무공",
        description="목숨을 걸고 나라를 지킨 불굴의 의지와 전략적 사고의 소유자입니다. 강한 관성과 결단력이 특징적인 사주입니다.",
        tags=["의지", "전략", "충성", "리더십"],
        traits={"career": 0.9, "leadership": 0.9, "authority": 0.9, "wealth": 0.3, "love": 0.3},
    ),
    Hero(
        name="허준",
        title="백성을 살린 의성",
        description="동의보감을 저술하여 의학의 새 장을 연 인물입니다. 학문에 대한 깊은 탐구심과 남을 돕고자 하는 마음이 돋보입니다.",
        tags=["학문", "봉사", "전문성", "인내"],
        traits={"career": 0.8, "wisdom": 0.9, "support": 0.8, "wealth": 0.4, "love": 0.5},
    ),
    Hero(
        name="장영실",
        title="발명과 혁신의 천재",
        description="신분의 한계를 넘어 측우기, 자격루 등 수많은 발명품을 만든 혁신가입니다. 식상의 기운이 강하게 작용하는 사주입니다.",
        tags=["혁신", "기술", "창의력", "도전"],
        traits={"career": 0.7, "creativity": 0.9, "technical": 0.9, "wealth": 0.4, "authority": 0.3},
    ),
    Hero(
        name="신사임당",
        title="예술과 지혜의 어머니",
        description="뛰어난 예술적 재능과 현명한 지혜를 겸비한 조선 최고의 여성 예술가입니다. 식신과 정인의 조화가 아름다운 사주입니다.",
        tags=["예술", "지혜", "교육", "균형"],
        traits={"creativity": 0.9, "wisdom": 0.8, "love": 0.8, "wealth": 0.6, "balance": 0.8},
    ),
    Hero(
        name="정약용",
        title="실학의 거장",
        description="다산이라는 호처럼 방대한 저술을 남긴 실학의 대가입니다. 학문과 실천을 겸비한 지식인의 전형입니다.",
        tags=["학문", "실천", "개혁", "저술"],
        traits={"wisdom": 0.9, "career": 0.7, "creativity": 0.8, "authority": 0.5, "wealth": 0.4},
    ),
    Hero(
        name="김만덕",
        title="나눔의 거상",
        description="제주의 거상으로 큰 부를 일군 뒤 기근에 시달리는 백성들에게 전 재산을 나눈 의인입니다. 재성이 강하면서도 인성이 조화로운 사주입니다.",
        tags=["재물", "나눔", "사업", "봉사"],
        traits={"wealth": 0.9, "business": 0.9, "support": 0.7, "love": 0.6, "career": 0.6},
    ),
    Hero(
        name="광개토대왕",
        title="정복과 확장의 대왕",
        description="고구려의 영토를 크게 넓힌 정복 군주입니다. 강한 비겁과 편관의 기운으로 거침없는 추진력을 보여줍니다.",
        tags=["확장", "정복", "추진력", "카리스마"],
        traits={"leadership": 0.9, "authority": 0.9, "career": 0.8, "wealth": 0.7, "love": 0.4},
    ),
    Hero(
        name="황진이",
        title="예술과 자유의 명기",
        description="빼어난 시와 가무로 조선 최고의 예술가로 이름을 남겼습니다. 도화의 기운과 식상의 재능이 어우러진 매력적인 사주입니다.",
        tags=["예술", "매력", "자유", "감성"],
        traits={"love": 0.9, "creativity": 0.9, "charm": 0.9, "career": 0.5, "wealth": 0.4},
    ),
    Hero(
        name="이황(퇴계)",
        title="성리학의 대스승",
        description="조선 성리학을 집대성한 대학자입니다. 깊은 사색과 도덕적 수양으로 후대에 큰 영향을 끼쳤습니다.",
        tags=["학문", "도덕", "수양", "인내"],
        traits={"wisdom": 0.9, "support": 0.8, "career": 0.6, "wealth": 0.3, "love": 0.4},
    ),
    Hero(
        name="김유신",
        title="삼국통일의 영웅",
        description="신라의 삼국통일을 이끈 전략가이자 무장입니다. 강한 관성과 재성이 어우러져 군사적 업적과 정치적 성공을 함께 이루었습니다.",
        tags=["전략", "통일", "무용", "정치"],
        traits={"authority": 0.9, "leadership": 0.8, "career": 0.9, "wealth": 0.7, "love": 0.5},
    ),
    Hero(
        name="유관순",
        title="독립의 불꽃",
        description="나라의 독립을 위해 목숨을 바친 의로운 영웅입니다. 강한 비겁의 기운으로 불의에 맞서는 용기를 보여줍니다.",
        tags=["의지", "용기", "희생", "정의"],
        traits={"authority": 0.7, "leadership": 0.7, "career": 0.5, "wealth": 0.2, "love": 0.4},
    ),
    Hero(
        name="장보고",
        title="해상왕",
        description="동아시아 해상무역을 장악한 해상왕입니다. 편재의 기운이 강하게 작용하여 거대한 부와 세력을 쌓았습니다.",
        tags=["무역", "사업", "개척", "재물"],
        traits={"wealth": 0.9, "business": 0.9, "leadership": 0.7, "career": 0.7, "love": 0.4},
    ),
    Hero(
        name="선덕여왕",
        title="지혜로운 여왕",
        description="신라 최초의 여왕으로 뛰어난 정치력과 문화적 감각으로 나라를 이끌었습니다. 인성과 관성이 조화를 이룬 균형 잡힌 사주입니다.",
        tags=["정치", "문화", "지혜", "균형"],
        traits={"leadership": 0.8, "wisdom": 0.8, "career": 0.8, "balance": 0.8, "love": 0.6},
    ),
    Hero(
        name="홍길동",
        title="의적의 전설",
        description="불합리한 세상에 맞서 약자를 도운 전설적 의적입니다. 상관의 기운이 강하여 기존 질서에 도전하는 혁명가 기질을 보여줍니다.",
        tags=["정의", "반항", "혁명", "자유"],
        traits={"authority": 0.3, "creativity": 0.7, "career": 0.4, "wealth": 0.5, "love": 0.5},
    ),
]


# ══════════════════════════════════════════════════
# 특성 추출 함수
# ══════════════════════════════════════════════════

def _extract_traits_from_face(features: list) -> dict[str, float]:
    """관상 분류 결과 → 특성 점수"""
    traits = {}
    avg_score = sum(f.score for f in features) / len(features) if features else 5.0

    # 전체 평균 기반
    traits["career"] = min(1.0, avg_score / 10)
    traits["wealth"] = min(1.0, avg_score / 10)
    traits["love"] = min(1.0, avg_score / 10)

    for f in features:
        normalized = f.score / 10.0
        cat = f.category

        if cat == "눈":
            # 봉안, 용안 → 리더십/지혜
            if f.label in ("봉안", "용안", "공작안"):
                traits["leadership"] = max(traits.get("leadership", 0), normalized)
                traits["wisdom"] = max(traits.get("wisdom", 0), normalized)
            if f.label in ("도화안", "원앙안"):
                traits["love"] = max(traits.get("love", 0), normalized)
                traits["charm"] = max(traits.get("charm", 0), normalized)
        elif cat == "코":
            if f.label in ("복코", "사자코"):
                traits["wealth"] = max(traits.get("wealth", 0), normalized)
                traits["business"] = max(traits.get("business", 0), normalized)
        elif cat == "이마":
            if f.label in ("넓은이마", "높은이마"):
                traits["wisdom"] = max(traits.get("wisdom", 0), normalized)
        elif cat == "입":
            if f.label in ("복입", "용입"):
                traits["wealth"] = max(traits.get("wealth", 0), normalized)

    return traits


def _extract_traits_from_saju(saju_data: dict, scores: dict) -> dict[str, float]:
    """사주 분석 결과 → 특성 점수"""
    traits = {}

    # 점수 기반
    for key in ["wealth", "love", "career"]:
        if key in scores:
            traits[key] = scores[key]["score"] / 10.0

    # 오행 기반
    elements = saju_data.get("elements", {})
    pcts = elements.get("percentages", {})

    # 목 → 창의력, 화 → 리더십, 토 → 균형, 금 → 권위, 수 → 지혜
    traits["creativity"] = min(1.0, pcts.get("목", 0) / 40)
    traits["leadership"] = min(1.0, pcts.get("화", 0) / 40)
    traits["balance"] = 1.0 - (max(pcts.values()) - min(pcts.values())) / 50 if pcts else 0.5
    traits["authority"] = min(1.0, pcts.get("금", 0) / 40)
    traits["wisdom"] = min(1.0, pcts.get("수", 0) / 40)

    # 십신 기반
    sipsin = saju_data.get("sipsin_summary", {})
    if sipsin.get("식신", 0) + sipsin.get("상관", 0) >= 2:
        traits["creativity"] = max(traits.get("creativity", 0), 0.8)
    if sipsin.get("편관", 0) + sipsin.get("정관", 0) >= 2:
        traits["authority"] = max(traits.get("authority", 0), 0.8)
    if sipsin.get("편재", 0) + sipsin.get("정재", 0) >= 2:
        traits["business"] = max(traits.get("business", 0), 0.8)
    if sipsin.get("편인", 0) + sipsin.get("정인", 0) >= 2:
        traits["support"] = max(traits.get("support", 0), 0.8)
        traits["wisdom"] = max(traits.get("wisdom", 0), 0.7)

    return traits


# ══════════════════════════════════════════════════
# 매칭 로직
# ══════════════════════════════════════════════════

def _compute_similarity(user_traits: dict[str, float], hero: Hero) -> float:
    """사용자 특성과 위인 특성의 유사도 계산 (0~1)"""
    all_keys = set(user_traits.keys()) | set(hero.traits.keys())
    if not all_keys:
        return 0.0

    score_sum = 0.0
    weight_sum = 0.0

    for key in all_keys:
        user_val = user_traits.get(key, 0.0)
        hero_val = hero.traits.get(key, 0.0)
        weight = hero_val  # 위인의 특성 가중치가 높을수록 중요

        similarity = 1.0 - abs(user_val - hero_val)
        score_sum += similarity * weight
        weight_sum += weight

    return score_sum / weight_sum if weight_sum > 0 else 0.0


def match_hero_face(features: list) -> dict:
    """관상 분석 결과 → 위인 매칭"""
    traits = _extract_traits_from_face(features)
    return _find_best_match(traits)


def match_hero_saju(saju_data: dict, scores: dict) -> dict:
    """사주 분석 결과 → 위인 매칭"""
    traits = _extract_traits_from_saju(saju_data, scores)
    return _find_best_match(traits)


def match_hero_combined(
    features: list,
    saju_data: dict,
    scores: dict,
    spread_data: dict | None = None,
    tarot_scores: dict | None = None,
) -> dict:
    """종합 분석 → 위인 매칭 (관상 + 사주 + 타로 특성 합산)"""
    face_traits = _extract_traits_from_face(features)
    saju_traits = _extract_traits_from_saju(saju_data, scores)

    if spread_data and tarot_scores:
        tarot_traits = _extract_traits_from_tarot(spread_data, tarot_scores)
        # 관상 0.3 + 사주 0.4 + 타로 0.3
        all_keys = set(face_traits.keys()) | set(saju_traits.keys()) | set(tarot_traits.keys())
        combined_traits = {}
        for key in all_keys:
            f_val = face_traits.get(key, 0.0)
            s_val = saju_traits.get(key, 0.0)
            t_val = tarot_traits.get(key, 0.0)
            combined_traits[key] = f_val * 0.3 + s_val * 0.4 + t_val * 0.3
    else:
        # 타로 없이 기존 방식 (하위 호환)
        all_keys = set(face_traits.keys()) | set(saju_traits.keys())
        combined_traits = {}
        for key in all_keys:
            f_val = face_traits.get(key, 0.0)
            s_val = saju_traits.get(key, 0.0)
            combined_traits[key] = f_val * 0.4 + s_val * 0.6

    return _find_best_match(combined_traits)


def _extract_traits_from_tarot(spread_data: dict, scores: dict) -> dict[str, float]:
    """타로 카드 → 특성 점수"""
    traits: dict[str, float] = {}

    for card_info in spread_data["cards"]:
        card_traits = card_info.get("traits", {})
        reversal_factor = 0.7 if card_info["is_reversed"] else 1.0
        for key, val in card_traits.items():
            adjusted = val * reversal_factor
            traits[key] = max(traits.get(key, 0), adjusted)

    # overall_score 기반 기본값
    overall_norm = scores.get("overall_score", 5.0) / 10.0
    traits.setdefault("career", overall_norm)
    traits.setdefault("wealth", overall_norm)
    traits.setdefault("love", overall_norm)

    return traits


def match_hero_tarot(spread_data: dict, scores: dict) -> dict:
    """타로 분석 결과 → 위인 매칭"""
    traits = _extract_traits_from_tarot(spread_data, scores)
    return _find_best_match(traits)


def _find_best_match(traits: dict[str, float]) -> dict:
    """특성 → 가장 유사한 위인 반환"""
    best_hero = HEROES[0]
    best_score = -1.0

    for hero in HEROES:
        score = _compute_similarity(traits, hero)
        if score > best_score:
            best_score = score
            best_hero = hero

    # 매칭 이유 생성: 사용자 특성 중 위인과 겹치는 상위 3개
    common_traits = []
    for key in sorted(best_hero.traits, key=lambda k: best_hero.traits[k], reverse=True):
        if traits.get(key, 0) >= 0.5 and best_hero.traits[key] >= 0.6:
            common_traits.append(key)
        if len(common_traits) >= 3:
            break

    TRAIT_LABELS = {
        "wealth": "재물운", "love": "연애운", "career": "직업운",
        "leadership": "리더십", "wisdom": "지혜", "creativity": "창의력",
        "authority": "권위", "balance": "균형", "charm": "매력",
        "business": "사업수완", "support": "귀인복", "technical": "기술력",
    }

    return {
        "name": best_hero.name,
        "title": best_hero.title,
        "description": best_hero.description,
        "tags": best_hero.tags,
        "match_score": round(best_score * 100, 1),
        "common_traits": [TRAIT_LABELS.get(t, t) for t in common_traits],
    }
