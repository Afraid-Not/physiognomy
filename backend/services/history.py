"""
분석 이력 저장 서비스
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).parent.parent.parent / ".env")

_supabase = None


def _get_supabase():
    global _supabase
    if _supabase is None:
        _supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    return _supabase


async def save_history(
    user_id: str,
    analysis_type: str,
    input_data: dict,
    result_data: dict,
    image_url: str | None = None,
) -> str:
    """
    분석 이력 저장 → history id 반환
    """
    row = {
        "user_id": user_id,
        "type": analysis_type,
        "input_data": input_data,
        "result_data": result_data,
    }
    if image_url:
        row["image_url"] = image_url

    result = _get_supabase().table("analysis_history").insert(row).execute()
    return result.data[0]["id"] if result.data else ""
