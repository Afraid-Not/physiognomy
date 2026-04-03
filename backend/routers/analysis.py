import json

from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.landmark import extract_landmarks
from services.classifier import classify_features
from services.rag import search_knowledge
from services.llm import generate_analysis, generate_analysis_stream
from services.history import save_history

from services.hero_match import match_hero_face
from middleware.auth import get_optional_user
from middleware.turnstile import require_turnstile

router = APIRouter()


class FeatureResult(BaseModel):
    category: str
    description: str
    score: float


class AnalysisResponse(BaseModel):
    summary: str
    features: list[FeatureResult]
    overall: str


@router.post("/analyze")
async def analyze_face(
    file: UploadFile = File(...),
    stream: bool = False,
    turnstile_token: str = Form(""),
    user: dict | None = Depends(get_optional_user),
):
    """
    사진 → 랜드마크 → 비율 → 모델 추론 → RAG → LLM 분석
    stream=true 이면 SSE 스트리밍 응답
    """
    # Turnstile 캡챠 검증
    await require_turnstile(turnstile_token)

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")

    image_bytes = await file.read()

    # Step 1: 랜드마크 추출 + 비율 계산
    ratios = await extract_landmarks(image_bytes)
    if ratios is None:
        raise HTTPException(status_code=422, detail="얼굴을 인식할 수 없습니다. 정면 사진을 업로드해주세요.")

    # Step 2: XGBoost 모델로 관상 특징 분류
    features = await classify_features(ratios)

    # Step 3: 하이브리드 검색으로 관상 지식 조회
    knowledge = await search_knowledge(features)

    # 위인 매칭
    hero = match_hero_face(features)

    # Step 4: LLM 분석 생성
    if stream:
        # SSE 스트리밍 (async generator)
        async def event_stream():
            # 먼저 분류 결과를 보내기 (즉시 표시)
            classified = {
                "type": "classified",
                "data": [
                    {"category": f.category, "label": f.label, "confidence": f.confidence}
                    for f in features
                ],
                "hero": hero,
            }
            yield f"data: {json.dumps(classified, ensure_ascii=False)}\n\n"

            # LLM 스트리밍
            full_text = ""
            for chunk in generate_analysis_stream(features, knowledge):
                full_text += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'data': chunk}, ensure_ascii=False)}\n\n"

            # 최종 파싱 + 규칙 기반 점수 강제 적용
            try:
                parsed = json.loads(full_text)
                if "features" in parsed:
                    for i, f in enumerate(parsed["features"]):
                        if i < len(features):
                            f["score"] = features[i].score
                            f["category"] = f"{features[i].category} - {features[i].label}"
                yield f"data: {json.dumps({'type': 'done', 'data': parsed}, ensure_ascii=False)}\n\n"

                # 이력 저장 (로그인 사용자만)
                if user:
                    await save_history(
                        user_id=user["id"],
                        analysis_type="face",
                        input_data={},
                        result_data={**parsed, "hero": hero},
                    )
            except json.JSONDecodeError:
                yield f"data: {json.dumps({'type': 'error', 'data': 'JSON 파싱 실패'}, ensure_ascii=False)}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    # 일반 응답
    result = await generate_analysis(features, knowledge)
    # 규칙 기반 점수 + 라벨 강제 적용
    if "features" in result:
        for i, f in enumerate(result["features"]):
            if i < len(features):
                f["score"] = features[i].score
                f["category"] = f"{features[i].category} - {features[i].label}"

    # 이력 저장 (로그인 사용자만)
    if user:
        await save_history(
            user_id=user["id"],
            analysis_type="face",
            input_data={},
            result_data={**result, "hero": hero},
        )

    result["hero"] = hero
    return result
