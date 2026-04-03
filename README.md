# Physiognomy AI

AI 기반 관상 분석 웹 서비스. 얼굴 사진을 업로드하면 MediaPipe 랜드마크 추출 → XGBoost 분류 → RAG 지식 검색 → LLM 해석까지 자동으로 수행합니다.

## Features

- 얼굴 사진 업로드 → 9개 부위(눈, 눈썹, 코, 입, 이마, 턱, 얼굴형, 인중, 광대뼈) 관상 분류
- MediaPipe FaceLandmarker 기반 468+ 랜드마크 추출 및 비율 계산
- XGBoost 모델로 부위별 관상 유형 분류 (봉안, 복코, 계란형 등)
- Supabase pgvector 하이브리드 검색 RAG로 관상학 지식 조회
- OpenAI GPT-4o-mini 기반 종합 관상 해석 생성 (SSE 스트리밍)
- 규칙 기반 관상 점수 산정 (전통 해석 기반 1~10점)
- 결과 PDF 다운로드

## Tech Stack

| Layer    | Stack                                            |
| -------- | ------------------------------------------------ |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| Backend  | FastAPI, Uvicorn, Pydantic                       |
| ML       | MediaPipe, XGBoost (joblib), OpenCV, NumPy       |
| AI       | OpenAI API (GPT-4o-mini, text-embedding-3-small) |
| DB       | Supabase (pgvector)                              |
| Deploy   | Vercel (Frontend)                                |

## Project Structure

```
physiognomy/
├── backend/
│   ├── main.py              # FastAPI 엔트리포인트
│   ├── routers/
│   │   └── analysis.py      # /api/analyze 엔드포인트
│   ├── services/
│   │   ├── landmark.py      # MediaPipe 랜드마크 + 비율 추출
│   │   ├── classifier.py    # XGBoost 관상 분류
│   │   ├── scoring.py       # 규칙 기반 점수 산정
│   │   ├── rag.py           # Supabase 하이브리드 검색
│   │   └── llm.py           # OpenAI 분석 생성
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # 메인 업로드 페이지
│   │   └── result/          # 분석 결과 페이지
│   └── package.json
├── ml/
│   ├── checkpoints/         # 학습된 모델 (.joblib)
│   ├── data/                # 학습 데이터, RAG 지식 JSON
│   ├── models/              # MediaPipe face_landmarker.task
│   └── scripts/             # 데이터 처리, 학습 스크립트
├── docs/                    # 프로젝트 문서
└── .env.example
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- conda (가상환경)

### Installation

```bash
# 환경 변수 설정
cp .env.example .env
# .env 파일에 OpenAI API Key, Supabase URL/Key 입력

# Backend
conda create -n physiognomy python=3.11 -y
conda activate physiognomy
cd backend
uv pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Running

```bash
# Backend (port 13351)
cd backend
python main.py

# Frontend (port 13350)
cd frontend
npm run dev
```

## Environment Variables

| Variable              | Description                                         |
| --------------------- | --------------------------------------------------- |
| `OPENAI_API_KEY`      | OpenAI API 키                                       |
| `SUPABASE_URL`        | Supabase 프로젝트 URL                               |
| `SUPABASE_KEY`        | Supabase anon key                                   |
| `NEXT_PUBLIC_API_URL` | Backend API URL (default: `http://localhost:13351`) |

## API

### `POST /api/analyze`

얼굴 사진을 분석하여 관상 결과를 반환합니다.

- **Content-Type**: `multipart/form-data`
- **Body**: `file` (image), `stream` (bool, optional)
- **Response** (`stream=false`): JSON `{ summary, features[], overall }`
- **Response** (`stream=true`): SSE stream (`classified` → `chunk` → `done`)

### `GET /health`

서버 상태 확인. `{ "status": "ok" }` 반환.
# physiognomy
