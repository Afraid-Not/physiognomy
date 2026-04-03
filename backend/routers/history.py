"""
분석 이력 조회 엔드포인트
GET /api/history, GET /api/history/{id}
"""

import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from dotenv import load_dotenv
from supabase import create_client

from middleware.auth import get_current_user
from services.storage import get_image_url

load_dotenv(Path(__file__).parent.parent.parent / ".env")

router = APIRouter()

_supabase = None


def _get_supabase():
    global _supabase
    if _supabase is None:
        _supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    return _supabase


@router.get("/history")
async def list_history(
    limit: int = 20,
    offset: int = 0,
    type: str | None = None,
    user: dict = Depends(get_current_user),
):
    """분석 이력 목록 (최신순)"""
    query = (
        _get_supabase()
        .table("analysis_history")
        .select("id, type, created_at, input_data, image_url")
        .eq("user_id", user["id"])
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
    )
    if type:
        query = query.eq("type", type)

    result = query.execute()
    return {"items": result.data, "total": len(result.data)}


@router.get("/history/{history_id}")
async def get_history_detail(history_id: str, user: dict = Depends(get_current_user)):
    """분석 이력 상세 조회"""
    result = (
        _get_supabase()
        .table("analysis_history")
        .select("*")
        .eq("id", history_id)
        .eq("user_id", user["id"])
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="이력을 찾을 수 없습니다.")

    data = result.data
    # 이미지 URL이 있으면 signed URL로 변환
    if data.get("image_url"):
        data["image_signed_url"] = get_image_url(data["image_url"])

    return data
