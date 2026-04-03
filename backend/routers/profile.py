"""
프로필 CRUD 엔드포인트
GET /api/profile, PUT /api/profile
"""

import os
from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client

from middleware.auth import get_current_user

load_dotenv(Path(__file__).parent.parent.parent / ".env")

router = APIRouter()

_supabase = None


def _get_supabase():
    global _supabase
    if _supabase is None:
        _supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    return _supabase


class ProfileUpdate(BaseModel):
    nickname: str | None = None
    birth_year: int | None = None
    birth_month: int | None = None
    birth_day: int | None = None
    birth_hour: int | None = None
    gender: str | None = None


@router.get("/profile")
async def get_profile(user: dict = Depends(get_current_user)):
    """현재 사용자 프로필 조회"""
    result = _get_supabase().table("profiles").select("*").eq("id", user["id"]).single().execute()
    return result.data


@router.put("/profile")
async def update_profile(body: ProfileUpdate, user: dict = Depends(get_current_user)):
    """프로필 수정"""
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    if not update_data:
        return {"message": "변경할 항목이 없습니다."}

    result = _get_supabase().table("profiles").update(update_data).eq("id", user["id"]).execute()
    return result.data[0] if result.data else {"message": "업데이트 완료"}
