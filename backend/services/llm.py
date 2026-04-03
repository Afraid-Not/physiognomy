"""
OpenAI API 기반 관상/사주 분석 생성 서비스
스트리밍 + 일반 모드 지원
"""

import os
import json
from pathlib import Path
from collections.abc import Generator

from dotenv import load_dotenv
from openai import OpenAI

from services.classifier import PhysiognomyFeature

load_dotenv(Path(__file__).parent.parent.parent / ".env")

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


# ══════════════════════════════════════════════════
# 관상 분석 프롬프트
# ══════════════════════════════════════════════════

SYSTEM_PROMPT = """당신은 전문 관상학자입니다.
사용자의 얼굴 특징 분석 결과와 관상학 지식을 바탕으로 솔직한 관상 해석을 제공합니다.

중요: 점수는 이미 계산되어 있으므로, 당신은 **설명(description)만** 작성합니다.

응답 규칙:
1. 반드시 아래 JSON 형식으로만 응답하세요.
2. 솔직하게 해석하세요. 좋은 상은 좋다고, 안 좋은 상은 안 좋다고 직설적으로 말하세요.
3. 점수가 낮은 부위(5점 이하)는 관상학적으로 어떤 점이 약한지 구체적으로 설명하세요.
4. 점수가 높은 부위(7점 이상)는 어떤 복이 있는지 구체적으로 설명하세요.
5. 각 부위별 description은 2-3문장으로 구체적으로 작성하세요.
6. overall은 종합적인 관상 분석으로 4-5문장으로 작성하세요. 재물운, 연애운, 직업운을 포함하되 솔직하게 쓰세요.
7. features의 category와 score는 입력 그대로 복사하세요. 변경하지 마세요.

JSON 형식:
{
  "summary": "한 줄 핵심 요약",
  "features": [
    {
      "category": "부위명 (입력 그대로)",
      "description": "해당 부위 상세 관상 해석 (당신이 작성)",
      "score": 8 (입력 그대로)
    }
  ],
  "overall": "종합 관상 분석 (재물운, 연애운, 직업운 포함)"
}"""


def _build_user_message(features: list[PhysiognomyFeature], knowledge: list[dict]) -> str:
    features_text = "\n".join([
        f"- {f.category} - {f.label} (점수: {f.score}/10, 신뢰도: {f.confidence:.0%})"
        for f in features
    ])
    knowledge_text = "\n".join([
        f"- [{k.get('category', '')}] {k.get('title', '')}: {k.get('content', '')[:200]}"
        for k in knowledge[:10]
    ])
    return f"""## 분석된 얼굴 특징
{features_text}

## 관련 관상학 지식
{knowledge_text}

위 정보를 바탕으로 종합 관상 분석 결과를 JSON 형식으로 작성해주세요."""


def generate_analysis_stream(
    features: list[PhysiognomyFeature],
    knowledge: list[dict],
) -> Generator[str, None, None]:
    """스트리밍 관상 분석 생성"""
    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_message(features, knowledge)},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
        stream=True,
    )

    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


async def generate_analysis(
    features: list[PhysiognomyFeature],
    knowledge: list[dict],
) -> dict:
    """일반 (비스트리밍) 관상 분석 생성"""
    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_message(features, knowledge)},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    result = json.loads(response.choices[0].message.content)
    if "features" in result:
        for f in result["features"]:
            f.setdefault("score", 7)
            f["score"] = max(1, min(10, int(f["score"])))
    return result


# ══════════════════════════════════════════════════
# 사주 분석 프롬프트
# ══════════════════════════════════════════════════

SAJU_SYSTEM_PROMPT = """당신은 전문 사주 명리학자입니다.
사용자의 사주팔자 분석 결과와 사주학 지식을 바탕으로 솔직한 사주 해석을 제공합니다.

중요: 점수는 이미 계산되어 있으므로, 당신은 **해석과 설명만** 작성합니다.

응답 규칙:
1. 반드시 아래 JSON 형식으로만 응답하세요.
2. 솔직하게 해석하세요. 좋은 점은 좋다고, 주의할 점은 주의하라고 직설적으로 말하세요.
3. 각 항목의 description은 2-3문장으로 구체적으로 작성하세요.
4. 사주 용어(십신, 오행 등)를 쉽게 풀어서 설명하세요.
5. overall은 종합적인 사주 분석으로 5-6문장으로 작성하세요. 재물운, 연애운, 직업운, 건강운을 포함하세요.
6. fortune_advice는 실생활에서 실천 가능한 조언 3가지를 작성하세요.
7. scores의 category와 score는 입력 그대로 복사하세요. 변경하지 마세요.

JSON 형식:
{
  "summary": "한 줄 핵심 요약 (예: 금 기운이 강한 결단력의 사주)",
  "personality": "성격 분석 3-4문장",
  "scores": [
    {
      "category": "항목명 (입력 그대로)",
      "description": "해당 항목 상세 해석 (당신이 작성)",
      "score": 7.5 (입력 그대로)
    }
  ],
  "overall": "종합 사주 분석 (재물운, 연애운, 직업운, 건강운 포함)",
  "fortune_advice": ["조언1", "조언2", "조언3"],
  "lucky": {
    "color": "길한 색상",
    "direction": "길한 방향",
    "number": "행운의 숫자"
  }
}"""


def _build_saju_user_message(saju_data: dict, scores: dict, knowledge: list[dict]) -> str:
    pillars = saju_data["pillars"]
    elements = saju_data["elements"]
    yongsin = saju_data["yongsin"]
    birth = saju_data["birth_info"]

    pillar_text = "\n".join([
        f"- {name}주: {p['ganzhi']} ({p['gan_element']}/{p['zhi_element']}) - 십신: {p['sipsin']}, 12운성: {p['twelve_stage']}"
        for name, p in [("년", pillars["year"]), ("월", pillars["month"]), ("일", pillars["day"]), ("시", pillars["hour"])]
    ])

    element_text = ", ".join([f"{k}: {v}개({elements['percentages'][k]}%)" for k, v in elements["counts"].items()])

    scores_text = "\n".join([
        f"- {scores[key]['category']}: {scores[key]['score']}/10"
        for key in ["element_balance", "yongsin_strength", "sipsin_balance", "wealth", "love", "career"]
        if key in scores
    ])

    dayun_text = "\n".join([
        f"- {d['start_age']}~{d['end_age']}세: {d['ganzhi']} ({d['gan_element']}/{d['zhi_element']}) - {d['sipsin']}"
        for d in saju_data.get("dayun", [])[:6]
    ])

    knowledge_text = "\n".join([
        f"- [{k.get('category', '')}] {k.get('title', '')}: {k.get('content', '')[:200]}"
        for k in knowledge[:10]
    ])

    return f"""## 생년월일 정보
- 양력: {birth['year']}년 {birth['month']}월 {birth['day']}일 {birth['hour']}시
- {birth['lunar_date']}
- 성별: {'남' if birth['gender'] == 'male' else '여'}
- 띠: {birth['animal']}

## 사주 원국 (四柱)
{pillar_text}

## 오행 분포
- {element_text}
- 일간 오행: {elements['day_element']}

## 용신 분석
- {yongsin['strength']}: {yongsin['description']}
- {yongsin['yongsin_label']}
- {yongsin['heesin_label']}

## 규칙 기반 점수 (변경 금지)
{scores_text}

## 대운 흐름
{dayun_text}

## 관련 사주학 지식
{knowledge_text}

위 정보를 바탕으로 종합 사주 분석 결과를 JSON 형식으로 작성해주세요."""


def generate_saju_analysis_stream(
    saju_data: dict,
    scores: dict,
    knowledge: list[dict],
) -> Generator[str, None, None]:
    """스트리밍 사주 분석 생성"""
    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SAJU_SYSTEM_PROMPT},
            {"role": "user", "content": _build_saju_user_message(saju_data, scores, knowledge)},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
        stream=True,
    )

    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


async def generate_saju_analysis(
    saju_data: dict,
    scores: dict,
    knowledge: list[dict],
) -> dict:
    """일반 (비스트리밍) 사주 분석 생성"""
    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SAJU_SYSTEM_PROMPT},
            {"role": "user", "content": _build_saju_user_message(saju_data, scores, knowledge)},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    return json.loads(response.choices[0].message.content)


# ══════════════════════════════════════════════════
# 종합 분석 (관상 + 사주) 프롬프트
# ══════════════════════════════════════════════════

COMBINED_SYSTEM_PROMPT = """당신은 관상학과 사주 명리학을 모두 마스터한 종합 운세 전문가입니다.
사용자의 관상 분석 결과와 사주팔자 분석 결과를 종합하여 통합 운세 해석을 제공합니다.

응답 규칙:
1. 반드시 아래 JSON 형식으로만 응답하세요.
2. 관상과 사주가 일치하는 부분은 강조하고, 상충하는 부분은 균형 잡힌 해석을 제공하세요.
3. 솔직하게 해석하되, 건설적인 조언을 함께 제공하세요.
4. overall은 7-8문장의 깊이 있는 종합 분석을 작성하세요.

JSON 형식:
{
  "summary": "한 줄 핵심 요약",
  "face_saju_synergy": "관상과 사주가 만나 나타나는 시너지/상충 분석 3-4문장",
  "wealth": {"score": 7.5, "description": "재물운 종합 해석 2-3문장"},
  "love": {"score": 7.5, "description": "연애/결혼운 종합 해석 2-3문장"},
  "career": {"score": 7.5, "description": "직업/사업운 종합 해석 2-3문장"},
  "health": {"score": 7.5, "description": "건강운 종합 해석 2-3문장"},
  "overall": "종합 운세 분석 (관상+사주 통합)",
  "fortune_advice": ["실천 조언1", "실천 조언2", "실천 조언3"],
  "lucky": {
    "color": "길한 색상",
    "direction": "길한 방향",
    "number": "행운의 숫자"
  }
}"""


def _build_combined_user_message(
    face_features: list[PhysiognomyFeature],
    face_result: dict,
    saju_data: dict,
    saju_scores: dict,
    knowledge: list[dict],
) -> str:
    # 관상 요약
    face_text = "\n".join([
        f"- {f.category} - {f.label} (점수: {f.score}/10)"
        for f in face_features
    ])
    face_overall = face_result.get("overall", "")

    # 사주 요약
    pillars = saju_data["pillars"]
    elements = saju_data["elements"]
    yongsin = saju_data["yongsin"]
    birth = saju_data["birth_info"]

    pillar_text = " / ".join([
        f"{p['ganzhi']}" for p in [pillars["year"], pillars["month"], pillars["day"], pillars["hour"]]
    ])

    saju_scores_text = "\n".join([
        f"- {saju_scores[key]['category']}: {saju_scores[key]['score']}/10"
        for key in ["wealth", "love", "career"]
        if key in saju_scores
    ])

    knowledge_text = "\n".join([
        f"- [{k.get('category', '')}] {k.get('title', '')}: {k.get('content', '')[:150]}"
        for k in knowledge[:8]
    ])

    return f"""## 관상 분석 결과
{face_text}
관상 종합: {face_overall}

## 사주 분석 결과
- 사주 원국: {pillar_text}
- 일간: {elements['day_element']} | {yongsin['strength']}
- {yongsin['yongsin_label']} / {yongsin['heesin_label']}
- 띠: {birth['animal']}
{saju_scores_text}

## 관련 지식
{knowledge_text}

위 관상 + 사주 정보를 종합하여 통합 운세 분석 결과를 JSON 형식으로 작성해주세요."""


def generate_combined_stream(
    face_features: list[PhysiognomyFeature],
    face_result: dict,
    saju_data: dict,
    saju_scores: dict,
    knowledge: list[dict],
) -> Generator[str, None, None]:
    """스트리밍 종합 분석 생성"""
    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": COMBINED_SYSTEM_PROMPT},
            {"role": "user", "content": _build_combined_user_message(
                face_features, face_result, saju_data, saju_scores, knowledge
            )},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
        stream=True,
    )

    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


async def generate_combined_analysis(
    face_features: list[PhysiognomyFeature],
    face_result: dict,
    saju_data: dict,
    saju_scores: dict,
    knowledge: list[dict],
) -> dict:
    """일반 (비스트리밍) 종합 분석 생성"""
    response = _get_client().chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": COMBINED_SYSTEM_PROMPT},
            {"role": "user", "content": _build_combined_user_message(
                face_features, face_result, saju_data, saju_scores, knowledge
            )},
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    return json.loads(response.choices[0].message.content)
