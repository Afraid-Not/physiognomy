"""
비회원 사용 로그 서비스
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Request
from supabase import create_client

load_dotenv(Path(__file__).parent.parent.parent / ".env")

_supabase = None


def _get_supabase():
    global _supabase
    if _supabase is None:
        _supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY", os.getenv("SUPABASE_KEY")),
        )
    return _supabase


def _get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def log_anonymous_usage(
    request: Request,
    analysis_type: str,
    category: str | None = None,
) -> None:
    """비회원 분석 요청 로그 저장"""
    row = {
        "analysis_type": analysis_type,
        "ip_address": _get_client_ip(request),
    }
    if category:
        row["category"] = category

    _get_supabase().table("anonymous_usage_logs").insert(row).execute()
