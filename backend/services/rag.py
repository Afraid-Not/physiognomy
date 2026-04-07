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
    return await _hybrid_search(query_text, 15)


async def search_saju_knowledge(saju_data: dict) -> list[dict]:
    """사주 분석 결과 기반 하이브리드 검색"""
    pillars = saju_data["pillars"]
    elements = saju_data["elements"]
    yongsin = saju_data["yongsin"]

    # 검색 쿼리 구성: 일간 오행 + 용신 + 주요 십신 + 대운
    parts = [
        f"일간 {elements['day_element']} 오행 성격 운세",
        f"{yongsin['strength']} 사주 {yongsin['yongsin']} 용신",
    ]
    for name, p in pillars.items():
        parts.append(f"{p['ganzhi']} {p['sipsin']} 천간 지지")

    query_text = " ".join(parts)
    return await _hybrid_search(query_text, 15)


async def search_combined_knowledge(
    features: list[PhysiognomyFeature],
    saju_data: dict,
    spread_data: dict | None = None,
    zodiac_data: dict | None = None,
) -> list[dict]:
    """관상 + 사주 + 타로 + 별자리 종합 검색"""
    # 관상 쿼리
    face_parts = [f"{f.category} {f.label}" for f in features]
    # 사주 쿼리
    elements = saju_data["elements"]
    yongsin = saju_data["yongsin"]
    saju_parts = [
        f"일간 {elements['day_element']}",
        f"{yongsin['strength']} 용신 {yongsin['yongsin']}",
    ]
    # 타로 쿼리
    tarot_parts = []
    if spread_data:
        for c in spread_data["cards"]:
            orientation = "정방향" if not c["is_reversed"] else "역방향"
            tarot_parts.append(f"{c['card_name']} {orientation} 타로")
    # 별자리 쿼리
    zodiac_parts = []
    if zodiac_data:
        zodiac_parts = [
            f"{zodiac_data.get('sun', {}).get('sign_ko', '')} 태양궁",
            f"{zodiac_data.get('moon', {}).get('sign_ko', '')} 달궁",
            f"{zodiac_data.get('ascendant', {}).get('sign_ko', '')} 상승궁",
        ]
    query_text = " ".join(face_parts + saju_parts + tarot_parts + zodiac_parts + ["종합 운세 재물운 연애운 직업운"])
    return await _hybrid_search(query_text, 20)


async def search_zodiac_knowledge(zodiac_data: dict) -> list[dict]:
    """별자리 분석 결과 기반 하이브리드 검색"""
    sun = zodiac_data.get("sun", {})
    moon = zodiac_data.get("moon", {})
    asc = zodiac_data.get("ascendant", {})
    parts = [
        f"{sun.get('sign_ko', '')} 태양궁 성격 적성",
        f"{moon.get('sign_ko', '')} 달궁 감정 내면",
        f"{asc.get('sign_ko', '')} 상승궁 첫인상",
        "별자리 서양 점성술",
    ]
    query_text = " ".join(parts)
    return await _hybrid_search(query_text, 10)


async def search_zodiac_knowledge(zodiac_data: dict) -> list[dict]:
    """별자리 분석 결과 기반 하이브리드 검색"""
    sun = zodiac_data.get("sun", {})
    moon = zodiac_data.get("moon", {})
    asc = zodiac_data.get("ascendant", {})
    parts = [
        f"{sun.get('sign_ko', '')} 태양궁 성격 적성",
        f"{moon.get('sign_ko', '')} 달궁 감정 내면",
        f"{asc.get('sign_ko', '')} 상승궁 첫인상",
        "별자리 서양 점성술",
    ]
    query_text = " ".join(parts)
    return await _hybrid_search(query_text, 10)


async def search_tarot_knowledge(spread_data: dict) -> list[dict]:
    """타로 카드 기반 하이브리드 검색"""
    cards = spread_data["cards"]
    parts = []
    for c in cards:
        orientation = "정방향" if not c["is_reversed"] else "역방향"
        parts.append(f"{c['card_name']} {orientation} {spread_data['category']} 타로 해석")
    query_text = " ".join(parts)
    return await _hybrid_search(query_text, 10)


async def _hybrid_search(query_text: str, match_count: int) -> list[dict]:
    """하이브리드 검색 공통 함수"""
    query_embedding = _get_openai().embeddings.create(
        model=EMBEDDING_MODEL, input=[query_text],
    ).data[0].embedding

    result = _get_supabase().rpc("hybrid_search", {
        "query_text": query_text,
        "query_embedding": query_embedding,
        "match_count": match_count,
    }).execute()

    return result.data
