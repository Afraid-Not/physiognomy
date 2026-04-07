"""
종합 분석 (관상 + 사주 + 타로) 엔드포인트
POST /api/combined
"""

import json
from datetime import date

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from services.landmark import extract_landmarks
from services.classifier import classify_features
from services.saju import analyze_saju
from services.saju_scoring import compute_saju_scores
from services.tarot import draw_three_card_spread
from services.tarot_scoring import compute_tarot_scores
from services.rag import search_combined_knowledge
from services.llm import (
    generate_analysis,
    generate_combined_stream,
    generate_combined_analysis,
)
from services.history import save_history
from services.hero_match import match_hero_combined
from services.usage_log import log_anonymous_usage
from middleware.auth import get_optional_user

router = APIRouter()


@router.post("/combined")
async def analyze_combined(
    request: Request,
    file: UploadFile = File(...),
    birth_year: int = Form(...),
    birth_month: int = Form(...),
    birth_day: int = Form(...),
    birth_hour: int = Form(...),
    birth_minute: int = Form(0),
    gender: str = Form(...),
    is_lunar: bool = Form(False),
    is_leap_month: bool = Form(False),
    tarot_category: str = Form("오늘의 운세"),
    stream: bool = Form(False),
    user: dict | None = Depends(get_optional_user),
):
    """
    사진 + 생년월일 + 타로 → 관상 + 사주 + 타로 → 종합 LLM 해석
    """
    # 입력 검증
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")
    if not is_lunar:
        try:
            date(birth_year, birth_month, birth_day)
        except ValueError:
            raise HTTPException(status_code=400, detail="유효하지 않은 날짜입니다.")
    if gender not in ("male", "female"):
        raise HTTPException(status_code=400, detail="성별은 male 또는 female이어야 합니다.")
    if tarot_category not in ("연애", "재물", "직업", "건강", "오늘의 운세"):
        raise HTTPException(status_code=400, detail="유효하지 않은 타로 카테고리입니다.")

    if not user:
        await log_anonymous_usage(request, "combined", category=tarot_category)

    image_bytes = await file.read()

    # ── Step 1: 관상 분석 ──
    ratios = await extract_landmarks(image_bytes)
    if ratios is None:
        raise HTTPException(status_code=422, detail="얼굴을 인식할 수 없습니다. 정면 사진을 업로드해주세요.")

    face_features = await classify_features(ratios)

    # ── Step 2: 사주 분석 ──
    saju_result = analyze_saju(
        birth_year, birth_month, birth_day,
        birth_hour, birth_minute,
        gender=gender,
        is_lunar=is_lunar,
        is_leap_month=is_leap_month,
    )
    saju_data = saju_result.to_dict()

    current_year = date.today().year
    current_age = current_year - birth_year + 1
    saju_scores = compute_saju_scores(saju_result, current_age)

    # ── Step 3: 타로 분석 ──
    spread = draw_three_card_spread(tarot_category)
    spread_data = spread.to_dict()
    tarot_scores = compute_tarot_scores(spread)

    # ── Step 4: 관상 LLM 해석 (종합에 필요) ──
    from services.rag import search_knowledge
    face_knowledge = await search_knowledge(face_features)
    face_result = await generate_analysis(face_features, face_knowledge)
    # 규칙 기반 점수 강제 적용
    if "features" in face_result:
        for i, f in enumerate(face_result["features"]):
            if i < len(face_features):
                f["score"] = face_features[i].score
                f["category"] = f"{face_features[i].category} - {face_features[i].label}"

    # ── Step 5: 종합 RAG 검색 ──
    combined_knowledge = await search_combined_knowledge(face_features, saju_data, spread_data)

    # ── Step 6: 위인 매칭 (관상 + 사주 + 타로) ──
    hero = match_hero_combined(face_features, saju_data, saju_scores, spread_data, tarot_scores)

    # ── Step 7: 종합 LLM 분석 ──
    if stream:
        async def event_stream():
            # 관상 + 사주 + 타로 즉시 전송
            classified = {
                "type": "classified",
                "data": {
                    "face": {
                        "features": [
                            {"category": f.category, "label": f.label, "confidence": f.confidence, "score": f.score}
                            for f in face_features
                        ],
                    },
                    "saju": {
                        "pillars": saju_data["pillars"],
                        "elements": saju_data["elements"],
                        "yongsin": saju_data["yongsin"],
                        "birth_info": saju_data["birth_info"],
                        "dayun": saju_data["dayun"],
                        "scores": saju_scores,
                    },
                    "tarot": {
                        "spread": spread_data,
                        "scores": tarot_scores,
                    },
                },
                "hero": hero,
            }
            yield f"data: {json.dumps(classified, ensure_ascii=False)}\n\n"

            # LLM 스트리밍
            full_text = ""
            for chunk in generate_combined_stream(
                face_features, face_result, saju_data, saju_scores,
                spread_data, tarot_scores, combined_knowledge,
            ):
                full_text += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'data': chunk}, ensure_ascii=False)}\n\n"

            try:
                parsed = json.loads(full_text)
                yield f"data: {json.dumps({'type': 'done', 'data': parsed}, ensure_ascii=False)}\n\n"

                # 이력 저장 (로그인 사용자만)
                if user:
                    await save_history(
                        user_id=user["id"],
                        analysis_type="combined",
                        input_data={
                            "birth_year": birth_year, "birth_month": birth_month,
                            "birth_day": birth_day, "birth_hour": birth_hour,
                            "gender": gender, "is_lunar": is_lunar,
                            "is_leap_month": is_leap_month,
                            "tarot_category": tarot_category,
                        },
                        result_data={
                            "face": face_result, "saju": saju_data, "saju_scores": saju_scores,
                            "tarot": {"spread": spread_data, "scores": tarot_scores},
                            "combined": parsed, "hero": hero,
                        },
                    )
            except json.JSONDecodeError:
                yield f"data: {json.dumps({'type': 'error', 'data': 'JSON 파싱 실패'}, ensure_ascii=False)}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    # 일반 응답
    combined_result = await generate_combined_analysis(
        face_features, face_result, saju_data, saju_scores,
        spread_data, tarot_scores, combined_knowledge,
    )

    # 이력 저장 (로그인 사용자만)
    if user:
        await save_history(
            user_id=user["id"],
            analysis_type="combined",
            input_data={
                "birth_year": birth_year, "birth_month": birth_month,
                "birth_day": birth_day, "birth_hour": birth_hour,
                "gender": gender, "tarot_category": tarot_category,
            },
            result_data={
                "face": face_result, "saju": saju_data, "saju_scores": saju_scores,
                "tarot": {"spread": spread_data, "scores": tarot_scores},
                "combined": combined_result, "hero": hero,
            },
        )

    return {
        "face": face_result,
        "saju": saju_data,
        "saju_scores": saju_scores,
        "tarot": {"spread": spread_data, "scores": tarot_scores},
        "combined": combined_result,
        "hero": hero,
    }
