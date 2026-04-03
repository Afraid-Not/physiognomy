# Physiognomy AI

AI 기반 관상 + 사주팔자 분석 웹 서비스. 얼굴 사진과 생년월일을 입력하면 관상 분석, 사주 분석, 종합 운세 분석까지 자동으로 수행합니다.

## Features

### 관상 분석

- 얼굴 사진 업로드 → 9개 부위(눈, 눈썹, 코, 입, 이마, 턱, 얼굴형, 인중, 광대뼈) 관상 분류
- MediaPipe FaceLandmarker 기반 468+ 랜드마크 추출 및 비율 계산
- XGBoost 모델로 부위별 관상 유형 분류 (봉안, 복코, 계란형 등)

### 사주팔자 분석

- 생년월일 + 태어난 시간 입력 → 사주 원국 (년주/월주/일주/시주) 계산
- 오행 분석 (목/화/토/금/수 비율), 십신 분석, 용신/희신 판단
- 대운/세운 흐름 표시
- 한국 표준시 보정 (서머타임, 1954~1961 UTC+8:30, 경도 보정)

### 종합 분석

- 관상 + 사주를 합쳐 종합 운세 리포트 생성
- 재물운, 연애운, 직업운, 건강운 통합 분석

### 공통

- Supabase pgvector 하이브리드 검색 RAG로 관상학/사주학 지식 조회
- OpenAI GPT-4o-mini 기반 해석 생성 (SSE 스트리밍)
- 규칙 기반 점수 산정 (전통 해석 기반 1~10점)
- 한국 위인 매칭 (세종대왕, 이순신 등 15명 - 특성 조합 기반)
- 이메일/비밀번호 로그인 (Supabase Auth)
- 분석 이력 저장 및 조회
- 프로필 기반 생년월일 자동 입력
- 결과 PDF 다운로드

## Tech Stack

| Layer    | Stack                                            |
| -------- | ------------------------------------------------ |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| Backend  | FastAPI, Uvicorn, Pydantic, lunar-python         |
| ML       | MediaPipe, XGBoost (joblib), OpenCV, NumPy       |
| AI       | OpenAI API (GPT-4o-mini, text-embedding-3-small) |
| Auth     | Supabase Auth (이메일/비밀번호, JWT)             |
| DB       | Supabase (pgvector, Storage)                     |
| Deploy   | Vercel (Frontend), ngrok (Backend 데모)          |

## Project Structure

```
physiognomy/
├── backend/
│   ├── main.py                  # FastAPI 엔트리포인트
│   ├── middleware/
│   │   └── auth.py              # Supabase JWT (ES256/JWKS) 검증
│   ├── routers/
│   │   ├── analysis.py          # POST /api/analyze (관상)
│   │   ├── saju.py              # POST /api/saju (사주)
│   │   ├── combined.py          # POST /api/combined (종합)
│   │   ├── profile.py           # GET/PUT /api/profile
│   │   └── history.py           # GET /api/history
│   ├── services/
│   │   ├── landmark.py          # MediaPipe 랜드마크 + 비율 추출
│   │   ├── classifier.py        # XGBoost 관상 분류
│   │   ├── scoring.py           # 관상 규칙 기반 점수
│   │   ├── saju.py              # lunar-python 사주 계산 + 한국어 매핑
│   │   ├── saju_scoring.py      # 사주 규칙 기반 점수
│   │   ├── hero_match.py        # 한국 위인 매칭
│   │   ├── rag.py               # Supabase 하이브리드 검색
│   │   ├── llm.py               # OpenAI 분석 생성
│   │   ├── history.py           # 이력 저장
│   │   └── storage.py           # Supabase Storage 업로드
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # 메인 (관상/사주/종합 선택)
│   │   ├── login/               # 로그인 페이지
│   │   ├── signup/              # 회원가입 페이지
│   │   ├── face/                # 관상 분석 + 결과
│   │   ├── saju/                # 사주 분석 + 결과
│   │   ├── combined/            # 종합 분석 + 결과
│   │   ├── mypage/              # 프로필 + 이력 조회
│   │   ├── components/          # AuthGuard, NavBar, HeroCard
│   │   ├── hooks/               # useAuth
│   │   └── lib/                 # Supabase 클라이언트
│   └── package.json
├── ml/
│   ├── checkpoints/             # 학습된 모델 (.joblib)
│   ├── data/                    # 학습 데이터, RAG 지식 JSON
│   ├── models/                  # MediaPipe face_landmarker.task
│   └── scripts/                 # 데이터 처리, 학습 스크립트
├── supabase/
│   └── migrations/              # DB 마이그레이션 SQL
├── docs/                        # 프로젝트 문서
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
# .env 파일에 필요한 키 입력

# Backend
conda create -n physiognomy python=3.11 -y
conda activate physiognomy
cd backend
uv pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### DB Setup

Supabase SQL Editor에서 마이그레이션 실행:

```bash
supabase/migrations/001_auth_profiles_history.sql
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

| Variable                        | Description                                         |
| ------------------------------- | --------------------------------------------------- |
| `OPENAI_API_KEY`                | OpenAI API 키                                       |
| `SUPABASE_URL`                  | Supabase 프로젝트 URL                               |
| `SUPABASE_KEY`                  | Supabase anon key                                   |
| `SUPABASE_JWT_SECRET`           | Supabase JWT Secret (Settings > API)                |
| `NEXT_PUBLIC_API_URL`           | Backend API URL (default: `http://localhost:13351`) |
| `NEXT_PUBLIC_SUPABASE_URL`      | Supabase 프로젝트 URL (프론트엔드용)                |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key (프론트엔드용)                    |

## API

모든 분석 API는 `Authorization: Bearer <token>` 헤더 필수.

### `POST /api/analyze`

관상 분석. `multipart/form-data`로 `file` (image) 전송. `stream=true`로 SSE 스트리밍.

### `POST /api/saju`

사주 분석. JSON body: `{ birth_year, birth_month, birth_day, birth_hour, gender, stream }`.

### `POST /api/combined`

종합 분석 (관상+사주). `multipart/form-data`로 `file` + 생년월일 정보.

### `GET /api/profile` / `PUT /api/profile`

프로필 조회/수정.

### `GET /api/history` / `GET /api/history/{id}`

분석 이력 목록/상세 조회.

### `GET /health`

서버 상태 확인. `{ "status": "ok" }` 반환.

## Deployment

### 데모 배포 (ngrok + Vercel)

```bash
# 1. Backend 실행
cd backend && python main.py

# 2. ngrok 터널
ngrok http 13351

# 3. Vercel 배포 (ngrok URL로)
cd frontend
npx vercel --prod -e NEXT_PUBLIC_API_URL=https://xxxx.ngrok-free.dev
```

자세한 내용은 `docs/deployment.md` 참고.
