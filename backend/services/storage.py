"""
Supabase Storage 서비스
업로드 사진을 face-images 버킷에 저장
"""

import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client

load_dotenv(Path(__file__).parent.parent.parent / ".env")

_supabase = None
BUCKET = "face-images"


def _get_supabase():
    global _supabase
    if _supabase is None:
        _supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    return _supabase


async def upload_face_image(user_id: str, image_bytes: bytes, content_type: str = "image/jpeg") -> str:
    """
    사용자 폴더에 이미지 업로드 → 경로 반환
    경로: {user_id}/{uuid}.jpg
    """
    ext = "png" if "png" in content_type else "jpg"
    file_name = f"{user_id}/{uuid.uuid4().hex}.{ext}"

    _get_supabase().storage.from_(BUCKET).upload(
        file_name,
        image_bytes,
        {"content-type": content_type},
    )

    return file_name


def get_image_url(file_path: str) -> str:
    """Storage 파일 경로 → signed URL (1시간)"""
    result = _get_supabase().storage.from_(BUCKET).create_signed_url(file_path, 3600)
    return result.get("signedURL", "")
