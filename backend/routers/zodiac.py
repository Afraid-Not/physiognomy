"""
별자리 분석 엔드포인트
POST /api/zodiac
"""

import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from services.zodiac import calculate_zodiac
from services.zodiac_scoring import compute_zodiac_scores
from services.rag import search_zodiac_knowledge
from services.llm import generate_zodiac_analysis, generate_zodiac_analysis_stream
from services.history import save_history
from services.hero_match import match_hero_zodiac
from services.usage_log import log_anonymous_usage
from middleware.auth import get_optional_user

router = APIRouter()


class ZodiacRequest(BaseModel):
    birth_year: int
    birth_month: int = Field(..., ge=1, le=12)
    birth_day: int = Field(..., ge=1, le=31)
    birth_hour: int = Field(..., ge=0, le=23)
    birth_minute: int = Field(default=0, ge=0, le=59)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    timezone: str = "Asia/Seoul"
    stream: bool = False


@router.post("/zodiac")
async def analyze_zodiac(
    req: ZodiacRequest,
    request: Request,
    user: dict | None = Depends(get_optional_user),
):
    """
    생년월일 + 출생시간 + 위치 → 태양궁/달궁/상승궁 계산 → 성격/적성 분석
    stream=true 이면 SSE 스트리밍 응답
    """
    if not user:
        await log_anonymous_usage(request, "zodiac")

    # Step 1: 별자리 계산
    zodiac_data = calculate_zodiac(
        birth_year=req.birth_year,
        birth_month=req.birth_month,
        birth_day=req.birth_day,
        birth_hour=req.birth_hour,
        birth_minute=req.birth_minute,
        latitude=req.latitude,
        longitude=req.longitude,
        timezone=req.timezone,
    )

    # Step 2: 규칙 기반 점수 산정
    scores = compute_zodiac_scores(
        sun_sign=zodiac_data["sun"]["sign_ko"],
        moon_sign=zodiac_data["moon"]["sign_ko"],
        ascendant_sign=zodiac_data["ascendant"]["sign_ko"],
    )

    # Step 3: RAG 지식 검색
    knowledge = await search_zodiac_knowledge(zodiac_data)

    # Step 4: 위인 매칭
    hero = match_hero_zodiac(zodiac_data, scores)

    # Step 5: LLM 분석 생성
    if req.stream:
        async def event_stream():
            # 별자리 + 점수 즉시 전송
            classified = {
                "type": "classified",
                "data": {
                    "zodiac": zodiac_data,
                    "scores": scores,
                },
                "hero": hero,
            }
            yield f"data: {json.dumps(classified, ensure_ascii=False)}\n\n"

            # LLM 스트리밍
            full_text = ""
            for chunk in generate_zodiac_analysis_stream(zodiac_data, scores, knowledge):
                full_text += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'data': chunk}, ensure_ascii=False)}\n\n"

            # 최종 파싱
            try:
                parsed = json.loads(full_text)
                parsed["overall_score"] = scores["overall_score"]
                yield f"data: {json.dumps({'type': 'done', 'data': parsed}, ensure_ascii=False)}\n\n"

                if user:
                    await save_history(
                        user_id=user["id"],
                        analysis_type="zodiac",
                        input_data={
                            "birth_year": req.birth_year, "birth_month": req.birth_month,
                            "birth_day": req.birth_day, "birth_hour": req.birth_hour,
                            "birth_minute": req.birth_minute,
                            "latitude": req.latitude, "longitude": req.longitude,
                            "timezone": req.timezone,
                        },
                        result_data={
                            "zodiac": zodiac_data,
                            "scores": scores,
                            "analysis": parsed,
                            "hero": hero,
                        },
                    )
            except json.JSONDecodeError:
                yield f"data: {json.dumps({'type': 'error', 'data': 'JSON 파싱 실패'}, ensure_ascii=False)}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    # 일반 응답
    result = await generate_zodiac_analysis(zodiac_data, scores, knowledge)
    result["overall_score"] = scores["overall_score"]

    if user:
        await save_history(
            user_id=user["id"],
            analysis_type="zodiac",
            input_data={
                "birth_year": req.birth_year, "birth_month": req.birth_month,
                "birth_day": req.birth_day, "birth_hour": req.birth_hour,
                "birth_minute": req.birth_minute,
                "latitude": req.latitude, "longitude": req.longitude,
                "timezone": req.timezone,
            },
            result_data={
                "zodiac": zodiac_data,
                "scores": scores,
                "analysis": result,
                "hero": hero,
            },
        )

    return {
        "zodiac": zodiac_data,
        "scores": scores,
        "analysis": result,
        "hero": hero,
    }
