"""
종합 분석 (관상 + 사주) 엔드포인트
POST /api/combined
"""

import json
from datetime import date

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from services.landmark import extract_landmarks
from services.classifier import classify_features
from services.saju import analyze_saju
from services.saju_scoring import compute_saju_scores
from services.rag import search_combined_knowledge
from services.llm import (
    generate_analysis,
    generate_combined_stream,
    generate_combined_analysis,
)
from services.history import save_history
from services.storage import upload_face_image
from services.hero_match import match_hero_combined
from middleware.auth import get_current_user

router = APIRouter()


@router.post("/combined")
async def analyze_combined(
    file: UploadFile = File(...),
    birth_year: int = Form(...),
    birth_month: int = Form(...),
    birth_day: int = Form(...),
    birth_hour: int = Form(...),
    birth_minute: int = Form(0),
    gender: str = Form(...),
    stream: bool = Form(False),
    user: dict = Depends(get_current_user),
):
    """
    사진 + 생년월일 → 관상 분석 + 사주 분석 → 종합 LLM 해석
    """
    # 입력 검증
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")
    try:
        date(birth_year, birth_month, birth_day)
    except ValueError:
        raise HTTPException(status_code=400, detail="유효하지 않은 날짜입니다.")
    if gender not in ("male", "female"):
        raise HTTPException(status_code=400, detail="성별은 male 또는 female이어야 합니다.")

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
    )
    saju_data = saju_result.to_dict()

    current_year = date.today().year
    current_age = current_year - birth_year + 1
    saju_scores = compute_saju_scores(saju_result, current_age)

    # ── Step 3: 관상 LLM 해석 (종합에 필요) ──
    # 관상 단독 해석을 먼저 간단히 생성 (종합 프롬프트에 넘기기 위해)
    from services.rag import search_knowledge
    face_knowledge = await search_knowledge(face_features)
    face_result = await generate_analysis(face_features, face_knowledge)
    # 규칙 기반 점수 강제 적용
    if "features" in face_result:
        for i, f in enumerate(face_result["features"]):
            if i < len(face_features):
                f["score"] = face_features[i].score
                f["category"] = f"{face_features[i].category} - {face_features[i].label}"

    # ── Step 4: 종합 RAG 검색 ──
    combined_knowledge = await search_combined_knowledge(face_features, saju_data)

    # ── Step 5: 위인 매칭 ──
    hero = match_hero_combined(face_features, saju_data, saju_scores)

    # ── Step 6: 종합 LLM 분석 ──
    if stream:
        async def event_stream():
            # 관상 + 사주 즉시 전송
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
                },
                "hero": hero,
            }
            yield f"data: {json.dumps(classified, ensure_ascii=False)}\n\n"

            # LLM 스트리밍
            full_text = ""
            for chunk in generate_combined_stream(
                face_features, face_result, saju_data, saju_scores, combined_knowledge
            ):
                full_text += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'data': chunk}, ensure_ascii=False)}\n\n"

            try:
                parsed = json.loads(full_text)
                yield f"data: {json.dumps({'type': 'done', 'data': parsed}, ensure_ascii=False)}\n\n"

                # 이력 저장
                image_path = await upload_face_image(user["id"], image_bytes, file.content_type or "image/jpeg")
                await save_history(
                    user_id=user["id"],
                    analysis_type="combined",
                    input_data={
                        "birth_year": birth_year, "birth_month": birth_month,
                        "birth_day": birth_day, "birth_hour": birth_hour,
                        "gender": gender,
                    },
                    result_data={"face": face_result, "saju": saju_data, "saju_scores": saju_scores, "combined": parsed, "hero": hero},
                    image_url=image_path,
                )
            except json.JSONDecodeError:
                yield f"data: {json.dumps({'type': 'error', 'data': 'JSON 파싱 실패'}, ensure_ascii=False)}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    # 일반 응답
    combined_result = await generate_combined_analysis(
        face_features, face_result, saju_data, saju_scores, combined_knowledge
    )

    # 이력 저장
    image_path = await upload_face_image(user["id"], image_bytes, file.content_type or "image/jpeg")
    await save_history(
        user_id=user["id"],
        analysis_type="combined",
        input_data={
            "birth_year": birth_year, "birth_month": birth_month,
            "birth_day": birth_day, "birth_hour": birth_hour,
            "gender": gender,
        },
        result_data={"face": face_result, "saju": saju_data, "saju_scores": saju_scores, "combined": combined_result, "hero": hero},
        image_url=image_path,
    )

    return {
        "face": face_result,
        "saju": saju_data,
        "saju_scores": saju_scores,
        "combined": combined_result,
        "hero": hero,
    }
