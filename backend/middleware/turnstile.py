"""
Cloudflare Turnstile CAPTCHA 검증
"""

import os
from pathlib import Path

import httpx
from fastapi import HTTPException

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env")

TURNSTILE_SECRET = os.getenv("TURNSTILE_SECRET_KEY", "")
VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


async def verify_turnstile(token: str) -> bool:
    """Turnstile 토큰 검증 → 성공 여부 반환"""
    if not TURNSTILE_SECRET:
        return True  # 시크릿 미설정 시 스킵 (개발용)

    async with httpx.AsyncClient() as client:
        resp = await client.post(VERIFY_URL, data={
            "secret": TURNSTILE_SECRET,
            "response": token,
        })
        result = resp.json()
        return result.get("success", False)


async def require_turnstile(token: str | None) -> None:
    """토큰이 있으면 검증, 없으면 스킵 (위젯 로드 실패 대비)"""
    if not token:
        return  # 캡챠 위젯 미로드 시 허용
    if not await verify_turnstile(token):
        raise HTTPException(status_code=403, detail="캡챠 인증에 실패했습니다. 다시 시도해주세요.")
