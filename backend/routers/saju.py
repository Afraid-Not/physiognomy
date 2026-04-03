"""
사주팔자 분석 엔드포인트
POST /api/saju
"""

import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from services.saju import analyze_saju
from services.saju_scoring import compute_saju_scores
from services.rag import search_saju_knowledge
from services.llm import generate_saju_analysis, generate_saju_analysis_stream
from services.history import save_history
from services.hero_match import match_hero_saju
from middleware.auth import get_optional_user
from middleware.turnstile import require_turnstile

router = APIRouter()


class SajuRequest(BaseModel):
    birth_year: int = Field(..., ge=1900, le=2100)
    birth_month: int = Field(..., ge=1, le=12)
    birth_day: int = Field(..., ge=1, le=31)
    birth_hour: int = Field(..., ge=0, le=23)
    birth_minute: int = Field(0, ge=0, le=59)
    gender: str = Field(..., pattern="^(male|female)$")
    stream: bool = False
    turnstile_token: str = ""


@router.post("/saju")
async def analyze_saju_endpoint(req: SajuRequest, user: dict | None = Depends(get_optional_user)):
    """
    생년월일시 → 사주 원국 → 점수 산정 → RAG → LLM 분석
    stream=true 이면 SSE 스트리밍 응답
    """
    # Turnstile 캡챠 검증
    await require_turnstile(req.turnstile_token)

    # 날짜 유효성 검증
    try:
        date(req.birth_year, req.birth_month, req.birth_day)
    except ValueError:
        raise HTTPException(status_code=400, detail="유효하지 않은 날짜입니다.")

    # Step 1: 사주 원국 계산
    saju_result = analyze_saju(
        req.birth_year, req.birth_month, req.birth_day,
        req.birth_hour, req.birth_minute,
        gender=req.gender,
    )
    saju_data = saju_result.to_dict()

    # Step 2: 규칙 기반 점수 산정
    current_year = date.today().year
    current_age = current_year - req.birth_year + 1  # 한국 나이
    scores = compute_saju_scores(saju_result, current_age)

    # Step 3: RAG 지식 검색
    knowledge = await search_saju_knowledge(saju_data)

    # 위인 매칭
    hero = match_hero_saju(saju_data, scores)

    # Step 4: LLM 분석 생성
    if req.stream:
        async def event_stream():
            # 먼저 사주 원국 + 점수 즉시 전송
            classified = {
                "type": "classified",
                "data": {
                    "pillars": saju_data["pillars"],
                    "elements": saju_data["elements"],
                    "yongsin": saju_data["yongsin"],
                    "birth_info": saju_data["birth_info"],
                    "dayun": saju_data["dayun"],
                    "scores": scores,
                },
                "hero": hero,
            }
            yield f"data: {json.dumps(classified, ensure_ascii=False)}\n\n"

            # LLM 스트리밍
            full_text = ""
            for chunk in generate_saju_analysis_stream(saju_data, scores, knowledge):
                full_text += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'data': chunk}, ensure_ascii=False)}\n\n"

            # 최종 파싱
            try:
                parsed = json.loads(full_text)
                # 규칙 기반 점수 강제 적용
                if "scores" in parsed:
                    score_keys = ["element_balance", "yongsin_strength", "sipsin_balance", "wealth", "love", "career"]
                    for i, key in enumerate(score_keys):
                        if i < len(parsed["scores"]) and key in scores:
                            parsed["scores"][i]["score"] = scores[key]["score"]
                            parsed["scores"][i]["category"] = scores[key]["category"]
                yield f"data: {json.dumps({'type': 'done', 'data': parsed}, ensure_ascii=False)}\n\n"

                # 이력 저장 (로그인 사용자만)
                if user:
                    await save_history(
                        user_id=user["id"],
                        analysis_type="saju",
                        input_data={
                            "birth_year": req.birth_year, "birth_month": req.birth_month,
                            "birth_day": req.birth_day, "birth_hour": req.birth_hour,
                            "gender": req.gender,
                        },
                        result_data={"saju": saju_data, "scores": scores, "analysis": parsed, "hero": hero},
                    )
            except json.JSONDecodeError:
                yield f"data: {json.dumps({'type': 'error', 'data': 'JSON 파싱 실패'}, ensure_ascii=False)}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    # 일반 응답
    result = await generate_saju_analysis(saju_data, scores, knowledge)
    # 규칙 기반 점수 강제 적용
    if "scores" in result:
        score_keys = ["element_balance", "yongsin_strength", "sipsin_balance", "wealth", "love", "career"]
        for i, key in enumerate(score_keys):
            if i < len(result["scores"]) and key in scores:
                result["scores"][i]["score"] = scores[key]["score"]
                result["scores"][i]["category"] = scores[key]["category"]

    # 이력 저장 (로그인 사용자만)
    if user:
        await save_history(
            user_id=user["id"],
            analysis_type="saju",
            input_data={
                "birth_year": req.birth_year, "birth_month": req.birth_month,
                "birth_day": req.birth_day, "birth_hour": req.birth_hour,
                "gender": req.gender,
            },
            result_data={"saju": saju_data, "scores": scores, "analysis": result, "hero": hero},
        )

    return {
        "saju": saju_data,
        "scores": scores,
        "analysis": result,
        "hero": hero,
    }
