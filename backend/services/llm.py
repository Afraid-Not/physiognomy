"""
OpenAI API 기반 관상 분석 생성 서비스
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
