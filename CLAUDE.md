# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered physiognomy (관상) + saju (사주팔자) + tarot (타로) analysis web service. Upload a face photo, enter birth datetime, or draw tarot cards to get: MediaPipe landmark extraction -> XGBoost classification -> RAG knowledge retrieval -> LLM interpretation. Classifies 9 facial regions into traditional Korean physiognomy types, calculates four pillars of destiny, draws Major Arcana three-card spreads, and matches users to Korean historical figures.

## Deployment

- **Frontend**: Vercel (Hobby) — https://zeomzip.com (상시 가동)
- **Backend**: Railway (Docker) — 필요 시 활성화/비활성화 (`railway up` / `railway down --yes`)

## Commands

### Backend (FastAPI)

```bash
conda activate physiognomy
cd backend
python main.py                    # runs on port 13351, auto-reload
```

### Frontend (Next.js 16)

```bash
cd frontend
npm install
npm run dev                       # runs on port 13350
npm run build                     # production build
npm run lint                      # eslint
```

### ML Pipeline (run from repo root, conda env active)

```bash
python ml/scripts/extract_ratios.py   # extract face ratios from images -> face_ratios.csv
python ml/scripts/auto_label.py       # quantile-based labeling -> face_labels.csv
python ml/scripts/train.py            # train 9 XGBoost models -> ml/checkpoints/
python ml/scripts/embed_and_store.py  # embed RAG knowledge -> Supabase pgvector
```

### Tarot Embedding (타로 지식 임베딩)

```bash
# service_role key 필요 (SUPABASE_SERVICE_KEY 환경변수)
python ml/scripts/embed_tarot_only.py   # tarot knowledge -> Supabase pgvector
```

## Architecture

### Request Flow - 관상 (POST /api/analyze)

```
Image upload (multipart/form-data, requires auth)
  -> services/landmark.py    : MediaPipe FaceLandmarker -> 37 facial ratios (tries 4 rotations)
  -> services/classifier.py  : 9 XGBoost models predict physiognomy type per region
  -> services/scoring.py     : rule-based score (1-10) from BASE_SCORES dict + confidence adjustment
  -> services/hero_match.py  : match to Korean historical figure by trait similarity
  -> services/rag.py         : single OpenAI embedding -> Supabase hybrid_search RPC (15 results)
  -> services/llm.py         : GPT-4o-mini generates JSON interpretation (streaming or sync)
  -> services/storage.py     : upload face image to Supabase Storage (face-images bucket)
  -> services/history.py     : save analysis result to analysis_history table
  -> routers/analysis.py     : SSE stream (classified -> chunk -> done) or JSON response
```

### Request Flow - 사주 (POST /api/saju)

```
Birth datetime + gender (JSON body, requires auth)
  -> services/saju.py        : lunar-python -> 사주 원국 (4주), 오행, 십신, 용신, 대운 + 한국 표준시 보정
  -> services/saju_scoring.py: rule-based scores (오행균형, 용신강약, 재물운, 연애운, 직업운)
  -> services/hero_match.py  : saju-based hero matching (오행/십신 -> traits)
  -> services/rag.py         : saju knowledge hybrid search
  -> services/llm.py         : GPT-4o-mini saju interpretation (streaming or sync)
  -> routers/saju.py         : SSE stream same pattern
```

### Request Flow - 타로 (POST /api/tarot)

```
Category selection + random draw (JSON body, optional auth)
  -> services/tarot.py         : draw_three_card_spread() -> 3 random Major Arcana cards (정/역방향)
  -> services/tarot_scoring.py : rule-based scores (카드별 base score + 역방향 -2 + 위치 가중치 과거0.2/현재0.5/미래0.3)
  -> services/hero_match.py    : tarot-based hero matching (card traits -> 위인 매칭)
  -> services/rag.py           : tarot knowledge hybrid search
  -> services/llm.py           : GPT-4o-mini tarot interpretation (streaming or sync)
  -> routers/tarot.py          : SSE stream same pattern (classified -> chunk -> done)
```

5 categories: 연애, 재물, 직업, 건강, 오늘의 운세. 22장 메이저 아르카나, 쓰리카드 스프레드 (과거/현재/미래).

### Request Flow - 종합 (POST /api/combined)

```
Image + birth datetime + gender (multipart, requires auth)
  -> 관상 pipeline (landmark -> classifier -> scoring)
  -> 사주 pipeline (saju -> saju_scoring)
  -> services/hero_match.py  : combined matching (face 40% + saju 60% weighted traits)
  -> services/rag.py         : combined knowledge search
  -> services/llm.py         : GPT-4o-mini combined interpretation
  -> routers/combined.py     : SSE stream with face + saju + combined results
```

All routers post-process LLM output to force rule-based scores over any LLM-generated scores.

### Auth & User Endpoints

```
middleware/auth.py : Supabase JWT verification via ES256 (JWKS public key from /auth/v1/.well-known/jwks.json)
                     All analysis/profile/history routes use Depends(get_current_user)
                     Returns {"id": user-uuid, "email": "...", "role": "..."}

GET/PUT /api/profile  -> routers/profile.py  : read/update user profile (birth info, nickname)
GET /api/history      -> routers/history.py  : list analysis history for current user
GET /api/history/{id} -> routers/history.py  : get single history detail
```

### Hero Matching System

`services/hero_match.py` contains 15 Korean historical figures (세종대왕, 이순신, 허준, etc.) with trait vectors (wealth, career, leadership, wisdom, creativity, etc.). Matching uses weighted cosine-like similarity between user traits extracted from face/saju analysis and hero trait profiles.

### ML Training Pipeline

```
crawl.py -> extract_faces.py -> extract_ratios.py -> auto_label.py -> train.py -> embed_and_store.py
```

`auto_label.py` uses quantile-based thresholds (25th/75th percentile) to classify ratio values into attributes, then maps attribute combinations to physiognomy names via hand-written rule functions (e.g., `map_eye_type()`). This produces training labels for XGBoost.

### Frontend Pages

```
/                      : main landing (관상/사주/타로/종합 선택)
/login, /signup        : Supabase Auth email/password
/face                  : face photo upload
/face/result           : face analysis results (reads sessionStorage)
/saju                  : birth datetime input
/saju/result           : saju analysis results
/tarot                 : tarot category selection + card draw
/tarot/result          : tarot analysis results (3-card spread display)
/combined              : photo + birth input
/combined/result       : combined analysis results
/mypage                : profile edit + history list
/mypage/history/[id]   : single history detail view
```

Results pass between upload and result pages via **sessionStorage** (`analysisResult`, `uploadedImage`). No server-side state for results display. PDF export uses `html2canvas-pro` + `jspdf`.

### Key Design Decisions

- **Scores are rule-based, not ML-predicted.** `scoring.py` has a hardcoded `BASE_SCORES` dict mapping each physiognomy label to a 1-10 score based on traditional interpretations. The router overwrites any LLM-generated scores with these.
- **Singleton pattern** for expensive resources: MediaPipe landmarker, XGBoost models, Supabase/OpenAI clients are all lazily initialized and cached in module-level globals.
- **.env lives at project root** and is loaded by `dotenv` in `main.py` and individual services. Backend reads it via `Path(__file__).parent.parent / ".env"`.
- **ML scripts use hardcoded absolute paths** (`D:\dev\physiognomy`). Adjust if working from a different location.
- **Model checkpoints (.joblib) are gitignored.** The `ml/checkpoints/` files must be generated locally by running `train.py`.

### Supabase Schema

Defined in `supabase/migrations/`:

- **profiles** — extends `auth.users` (id, email, nickname, birth info, gender). RLS: own rows only. Auto-created on signup via trigger.
- **analysis_history** — stores analysis results (user_id, type [face/saju/combined/tarot], input_data JSONB, result_data JSONB, image_url). RLS: own rows only. `002_tarot_type.sql` added 'tarot' to the type CHECK constraint.
- **face-images** storage bucket — private, RLS enforces user-folder isolation (`{user_id}/filename`).
- **physiognomy_knowledge** — RAG knowledge with pgvector embeddings. Includes physiognomy, saju, and tarot knowledge (62 tarot entries added via `embed_tarot_only.py`).

## Environment Variables

Defined in root `.env` (see `.env.example`):

| Variable                        | Used by  | Description                                                    |
| ------------------------------- | -------- | -------------------------------------------------------------- |
| `OPENAI_API_KEY`                | Backend  | OpenAI embeddings (text-embedding-3-small) + LLM (gpt-4o-mini) |
| `SUPABASE_URL`                  | Backend  | Supabase project URL for pgvector RAG, storage, history        |
| `SUPABASE_KEY`                  | Backend  | Supabase anon key                                              |
| `SUPABASE_JWT_SECRET`           | Backend  | JWT secret (Settings > API) for auth middleware                |
| `NEXT_PUBLIC_API_URL`           | Frontend | Backend URL (default: `http://localhost:13351`)                |
| `NEXT_PUBLIC_SUPABASE_URL`      | Frontend | Supabase project URL for client-side auth                      |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Frontend | Supabase anon key for client-side auth                         |

## Labeling & Classification Reference

9 classification targets with physiognomy type counts:

- `eye_type`: 14 types (봉안, 용안, 도화안, 삼백안, etc.)
- `eyebrow_type`: 12 types (유엽미, 일자눈썹, 초승달눈썹, etc.)
- `nose_type`: 8 types (복코, 매부리코, 사자코, etc.)
- `mouth_type`: 8 types (복입, 앵두입, 용입, etc.)
- `forehead_type`: 7 types
- `chin_type`: 6 types
- `face_shape`: 8 types
- `philtrum_type`: 7 types
- `cheekbone_type`: 5 types

Detailed criteria in `docs/labeling_criteria.md`. Mapping rules in `ml/scripts/auto_label.py`.

## Tarot Card System

22 Major Arcana cards defined in `backend/services/tarot.py` as `MAJOR_ARCANA` list. Each `TarotCard` has:

- `name_ko`/`name_en`, `upright`/`reversed` keywords, `element` (풍/화/수/토)
- `traits` dict for hero matching (wealth, career, leadership, wisdom, creativity, etc.)
- `meanings` dict with 5 categories x 2 orientations = 10 interpretations per card

Scoring in `backend/services/tarot_scoring.py`:

- `CARD_BASE_SCORES`: 22 cards x 5 categories base scores (1-10)
- Reversed penalty: -2.0 (clamped to min 1.0)
- Position weights: 과거 0.2, 현재 0.5, 미래 0.3
- Fortune sub-scores: luck (avg base), timing (현재 card), energy (upright count)

RAG knowledge: `ml/data/tarot_knowledge.json` (62 entries — 44 card entries + 5 spread guides + 5 category guides + 5 combinations + 3 general).
