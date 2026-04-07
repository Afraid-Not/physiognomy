"""
타로 분석 엔드포인트
POST /api/tarot
"""

import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from services.tarot import draw_three_card_spread
from services.tarot_scoring import compute_tarot_scores
from services.rag import search_tarot_knowledge
from services.llm import generate_tarot_analysis, generate_tarot_analysis_stream
from services.history import save_history
from services.hero_match import match_hero_tarot
from services.usage_log import log_anonymous_usage
from middleware.auth import get_optional_user

router = APIRouter()


class TarotRequest(BaseModel):
    category: str = Field(..., pattern=r"^(연애|재물|직업|건강|오늘의 운세)$")
    stream: bool = False


@router.post("/tarot")
async def analyze_tarot(req: TarotRequest, request: Request, user: dict | None = Depends(get_optional_user)):
    """
    카테고리 선택 → 카드 3장 뽑기 → 점수 산정 → RAG → LLM 분석
    stream=true 이면 SSE 스트리밍 응답
    """
    if not user:
        await log_anonymous_usage(request, "tarot", category=req.category)

    # Step 1: 카드 뽑기
    spread = draw_three_card_spread(req.category)
    spread_data = spread.to_dict()

    # Step 2: 규칙 기반 점수 산정
    scores = compute_tarot_scores(spread)

    # Step 3: RAG 지식 검색
    knowledge = await search_tarot_knowledge(spread_data)

    # Step 4: 위인 매칭
    hero = match_hero_tarot(spread_data, scores)

    # Step 5: LLM 분석 생성
    if req.stream:
        async def event_stream():
            # 카드 + 점수 즉시 전송
            classified = {
                "type": "classified",
                "data": {
                    "spread": spread_data,
                    "scores": scores,
                },
                "hero": hero,
            }
            yield f"data: {json.dumps(classified, ensure_ascii=False)}\n\n"

            # LLM 스트리밍
            full_text = ""
            for chunk in generate_tarot_analysis_stream(spread_data, scores, knowledge):
                full_text += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'data': chunk}, ensure_ascii=False)}\n\n"

            # 최종 파싱
            try:
                parsed = json.loads(full_text)
                # 규칙 기반 점수 강제 적용
                if "card_interpretations" in parsed:
                    for i, ci in enumerate(parsed["card_interpretations"]):
                        if i < len(scores["card_scores"]):
                            ci["score"] = scores["card_scores"][i]["adjusted_score"]
                parsed["overall_score"] = scores["overall_score"]
                yield f"data: {json.dumps({'type': 'done', 'data': parsed}, ensure_ascii=False)}\n\n"

                # 이력 저장 (로그인 사용자만)
                if user:
                    await save_history(
                        user_id=user["id"],
                        analysis_type="tarot",
                        input_data={"category": req.category},
                        result_data={
                            "spread": spread_data,
                            "scores": scores,
                            "analysis": parsed,
                            "hero": hero,
                        },
                    )
            except json.JSONDecodeError:
                yield f"data: {json.dumps({'type': 'error', 'data': 'JSON 파싱 실패'}, ensure_ascii=False)}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    # 일반 응답
    result = await generate_tarot_analysis(spread_data, scores, knowledge)
    # 규칙 기반 점수 강제 적용
    if "card_interpretations" in result:
        for i, ci in enumerate(result["card_interpretations"]):
            if i < len(scores["card_scores"]):
                ci["score"] = scores["card_scores"][i]["adjusted_score"]
    result["overall_score"] = scores["overall_score"]

    # 이력 저장 (로그인 사용자만)
    if user:
        await save_history(
            user_id=user["id"],
            analysis_type="tarot",
            input_data={"category": req.category},
            result_data={
                "spread": spread_data,
                "scores": scores,
                "analysis": result,
                "hero": hero,
            },
        )

    return {
        "spread": spread_data,
        "scores": scores,
        "analysis": result,
        "hero": hero,
    }
