"""별자리 지식만 임베딩하여 Supabase에 저장"""

import json
import os
import time
import io
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

load_dotenv(Path(r"D:\dev\physiognomy\.env"))

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_KEY")),
)

DATA_PATH = Path(r"D:\dev\physiognomy\ml\data\zodiac_knowledge.json")

with open(DATA_PATH, "r", encoding="utf-8") as f:
    entries = json.load(f)
print(f"별자리 지식 {len(entries)}개 로드")

texts = [f"{e['category']} - {e['title']}: {e['content']}" for e in entries]
embeddings = []
for i in range(0, len(texts), 50):
    batch = texts[i : i + 50]
    resp = openai_client.embeddings.create(model="text-embedding-3-small", input=batch)
    embeddings.extend([item.embedding for item in resp.data])
    print(f"  임베딩: {min(i + 50, len(texts))}/{len(texts)}")
    time.sleep(0.5)

success = 0
failed = 0
for i, e in enumerate(entries):
    tags = e.get("tags", [])
    row = {
        "source_type": e.get("source_type", ""),
        "source_name": e.get("source_name", ""),
        "category": e.get("category", ""),
        "title": e.get("title", ""),
        "content": e.get("content", ""),
        "tags": tags,
        "embedding": embeddings[i],
    }
    try:
        supabase.table("physiognomy_knowledge").insert(row).execute()
        success += 1
    except Exception as ex:
        print(f"  실패: {e['title'][:30]} - {ex}")
        failed += 1

print(f"완료: 성공 {success}, 실패 {failed}")
