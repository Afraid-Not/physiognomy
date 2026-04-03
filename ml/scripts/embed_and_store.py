"""
관상 지식 데이터 → OpenAI 임베딩 → Supabase 저장
4개 JSON 파일을 통합하여 임베딩 후 DB에 삽입
"""

import json
import sys
import io
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ── 설정 ──
load_dotenv(Path(r"D:\dev\physiognomy\.env"))
DATA_DIR = Path(r"D:\dev\physiognomy\ml\data")

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 50  # OpenAI 임베딩 배치


# ── 데이터 로드 ──
def load_all_data():
    all_entries = []

    # 1. 기존 부위별 관상 지식 (형식 변환 필요)
    knowledge_path = DATA_DIR / "physiognomy_knowledge.json"
    if knowledge_path.exists():
        with open(knowledge_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data.get("features", []):
            fortune = item.get("fortune", {})
            content_parts = [
                item.get("description", ""),
                f"외형적 특징: {item.get('visual_characteristics', '')}",
                f"성격: {item.get('personality', '')}",
                f"재물운: {fortune.get('wealth', '')}",
                f"연애운: {fortune.get('love', '')}",
                f"직업운: {fortune.get('career', '')}",
            ]
            all_entries.append({
                "source_type": "feature",
                "source_name": "physiognomy_knowledge_db",
                "category": item.get("category", ""),
                "title": item.get("name", ""),
                "content": "\n".join(content_parts),
                "tags": [item.get("category", "")] + item.get("famous_examples", []),
            })

    # 2~4. RAG 데이터 파일들
    rag_files = [
        ("rag_academic.json", None),
        ("rag_blogs.json", None),
        ("rag_interpretations.json", None),
        ("saju_knowledge.json", None),
    ]
    for filename, _ in rag_files:
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                entries = json.load(f)
            all_entries.extend(entries)
            print(f"  {filename}: {len(entries)}개")

    return all_entries


# ── 임베딩 생성 ──
def create_embeddings(texts):
    """텍스트 리스트 → 임베딩 벡터 리스트"""
    embeddings = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        batch_embeddings = [item.embedding for item in response.data]
        embeddings.extend(batch_embeddings)
        print(f"  임베딩: {min(i + BATCH_SIZE, len(texts))}/{len(texts)}", flush=True)
        time.sleep(0.5)  # rate limit 방지
    return embeddings


# ── Supabase 저장 ──
def store_to_supabase(entries, embeddings):
    """임베딩된 데이터를 Supabase에 저장"""
    success = 0
    failed = 0

    for i in range(0, len(entries), BATCH_SIZE):
        batch = []
        for j in range(i, min(i + BATCH_SIZE, len(entries))):
            entry = entries[j]
            tags = entry.get("tags", [])
            if isinstance(tags, str):
                tags = [tags]

            batch.append({
                "source_type": entry.get("source_type", "unknown"),
                "source_name": entry.get("source_name", ""),
                "category": entry.get("category", ""),
                "title": entry.get("title", ""),
                "content": entry.get("content", ""),
                "tags": tags,
                "embedding": embeddings[j],
            })

        try:
            supabase.table("physiognomy_knowledge").insert(batch).execute()
            success += len(batch)
        except Exception as e:
            print(f"  배치 저장 실패 (index {i}): {e}")
            # 개별 삽입 시도
            for row in batch:
                try:
                    supabase.table("physiognomy_knowledge").insert(row).execute()
                    success += 1
                except Exception as e2:
                    print(f"    개별 저장 실패: {row['title'][:30]}... - {e2}")
                    failed += 1

        print(f"  저장: {success}/{len(entries)}", flush=True)

    return success, failed


# ── 메인 ──
def main():
    print("=" * 50)
    print("관상 지식 임베딩 + Supabase 저장")
    print("=" * 50)

    # 1. 데이터 로드
    print("\n[1/3] 데이터 로드...")
    entries = load_all_data()
    print(f"총 {len(entries)}개 항목\n")

    # 2. 임베딩 텍스트 준비 (title + content 결합)
    print("[2/3] 임베딩 생성...")
    texts = [
        f"{e.get('category', '')} - {e.get('title', '')}: {e.get('content', '')}"
        for e in entries
    ]
    embeddings = create_embeddings(texts)
    print(f"임베딩 완료: {len(embeddings)}개\n")

    # 3. Supabase 저장
    print("[3/3] Supabase 저장...")
    success, failed = store_to_supabase(entries, embeddings)

    print(f"\n{'=' * 50}")
    print(f"완료!")
    print(f"  성공: {success}")
    print(f"  실패: {failed}")
    print(f"  총: {len(entries)}")


if __name__ == "__main__":
    main()
