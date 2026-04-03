"""
Supabase 하이브리드 검색 RAG 서비스
최적화: 임베딩 1회만 호출 (부위별 개별 검색 제거)
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client

from services.classifier import PhysiognomyFeature

load_dotenv(Path(__file__).parent.parent.parent / ".env")

_supabase = None
_openai = None

EMBEDDING_MODEL = "text-embedding-3-small"


def _get_supabase():
    global _supabase
    if _supabase is None:
        _supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    return _supabase


def _get_openai():
    global _openai
    if _openai is None:
        _openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai


async def search_knowledge(features: list[PhysiognomyFeature]) -> list[dict]:
    """관상 특징 기반 하이브리드 검색 (임베딩 1회)"""
    # 모든 특징을 하나의 쿼리로 합침
    query_text = " ".join([f"{f.category} {f.label} 성격 운세 재물운 연애운" for f in features])
    query_embedding = _get_openai().embeddings.create(
        model=EMBEDDING_MODEL, input=[query_text],
    ).data[0].embedding

    # 하이브리드 검색 1회 (15개)
    result = _get_supabase().rpc("hybrid_search", {
        "query_text": query_text,
        "query_embedding": query_embedding,
        "match_count": 15,
    }).execute()

    return result.data
