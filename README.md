# 점zip (Physiognomy AI)

AI 기반 관상 + 사주팔자 + 타로 분석 웹 서비스. 얼굴 사진, 생년월일, 타로 카드로 관상 분석, 사주 분석, 타로 분석, 종합 운세 분석을 수행합니다.

**Live**: https://zeomzip.com (프론트엔드 상시 가동, 백엔드는 필요 시 활성화)

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

### 타로 분석

- 메이저 아르카나 22장 기반 쓰리카드 스프레드 (과거/현재/미래)
- 5개 카테고리: 연애운, 재물운, 직업운, 건강운, 오늘의 운세
- 카드별 정방향/역방향 해석 + 카테고리별 특화 해석
- 규칙 기반 점수 산정 (카드별 base score + 역방향 보정 + 위치 가중치)

### 종합 분석

- 관상 + 사주를 합쳐 종합 운세 리포트 생성
- 재물운, 연애운, 직업운, 건강운 통합 분석

### 공통

- 비회원도 분석 가능 (Cloudflare Turnstile CAPTCHA)
- 로그인 시 분석 이력 저장 및 조회
- Supabase pgvector 하이브리드 검색 RAG로 관상학/사주학 지식 조회
- OpenAI GPT-4o-mini 기반 해석 생성 (SSE 스트리밍)
- 긍정적/건설적 톤의 LLM 해석 (부정 표현 금지)
- 규칙 기반 점수 산정 (전통 해석 기반 1~10점, 소수점 2자리)
- 한국 위인 매칭 (세종대왕, 이순신 등 15명 - 특성 조합 기반)
- 이메일/비밀번호 로그인 (Supabase Auth)
- 프로필 기반 생년월일 자동 입력
- 결과 PDF 다운로드
- Vercel Analytics 방문자 통계
- 개인정보처리방침 및 이용약관 페이지

## Tech Stack

| Layer     | Stack                                            |
| --------- | ------------------------------------------------ |
| Frontend  | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| Backend   | FastAPI, Uvicorn, Pydantic, lunar-python         |
| ML        | MediaPipe, XGBoost (joblib), OpenCV, NumPy       |
| AI        | OpenAI API (GPT-4o-mini, text-embedding-3-small) |
| Auth      | Supabase Auth (이메일/비밀번호, JWT ES256/JWKS)  |
| DB        | Supabase (pgvector, RLS)                         |
| CAPTCHA   | Cloudflare Turnstile                             |
| Deploy    | Vercel (Frontend), Railway (Backend/Docker)      |
| Analytics | Vercel Analytics                                 |

## Project Structure

```
physiognomy/
├── backend/
│   ├── main.py                  # FastAPI 엔트리포인트
│   ├── middleware/
│   │   ├── auth.py              # Supabase JWT (ES256/JWKS) 검증 + optional auth
│   │   └── turnstile.py         # Cloudflare Turnstile CAPTCHA 검증
│   ├── routers/
│   │   ├── analysis.py          # POST /api/analyze (관상)
│   │   ├── saju.py              # POST /api/saju (사주)
│   │   ├── tarot.py             # POST /api/tarot (타로)
│   │   ├── combined.py          # POST /api/combined (종합)
│   │   ├── profile.py           # GET/PUT /api/profile
│   │   └── history.py           # GET /api/history
│   ├── services/
│   │   ├── landmark.py          # MediaPipe 랜드마크 + 비율 추출
│   │   ├── classifier.py        # XGBoost 관상 분류
│   │   ├── scoring.py           # 관상 규칙 기반 점수
│   │   ├── saju.py              # lunar-python 사주 계산 + 한국어 매핑
│   │   ├── saju_scoring.py      # 사주 규칙 기반 점수
│   │   ├── tarot.py             # 타로 카드 데이터 + 뽑기
│   │   ├── tarot_scoring.py     # 타로 규칙 기반 점수
│   │   ├── hero_match.py        # 한국 위인 매칭
│   │   ├── rag.py               # Supabase 하이브리드 검색
│   │   ├── llm.py               # OpenAI 분석 생성
│   │   └── history.py           # 이력 저장 (service_role key)
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # 메인 (관상/사주/종합 선택)
│   │   ├── login/               # 로그인 페이지
│   │   ├── signup/              # 회원가입 페이지
│   │   ├── face/                # 관상 분석 + 결과
│   │   ├── saju/                # 사주 분석 + 결과
│   │   ├── tarot/               # 타로 분석 + 결과
│   │   ├── combined/            # 종합 분석 + 결과
│   │   ├── mypage/              # 프로필 + 이력 조회
│   │   ├── privacy/             # 개인정보처리방침
│   │   ├── terms/               # 이용약관
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
├── Dockerfile                   # Railway 배포용 Docker
├── .vercelignore                # Vercel 배포 시 제외 파일
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
supabase/migrations/002_tarot_type.sql
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

| Variable                         | Used by  | Description                          |
| -------------------------------- | -------- | ------------------------------------ |
| `OPENAI_API_KEY`                 | Backend  | OpenAI API 키                        |
| `SUPABASE_URL`                   | Backend  | Supabase 프로젝트 URL                |
| `SUPABASE_KEY`                   | Backend  | Supabase anon key                    |
| `SUPABASE_SERVICE_ROLE_KEY`      | Backend  | Supabase service role key (RLS 우회) |
| `SUPABASE_JWT_SECRET`            | Backend  | Supabase JWT Secret                  |
| `TURNSTILE_SECRET_KEY`           | Backend  | Cloudflare Turnstile secret key      |
| `NEXT_PUBLIC_API_URL`            | Frontend | Backend API URL                      |
| `NEXT_PUBLIC_SUPABASE_URL`       | Frontend | Supabase 프로젝트 URL                |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY`  | Frontend | Supabase anon key                    |
| `NEXT_PUBLIC_TURNSTILE_SITE_KEY` | Frontend | Cloudflare Turnstile site key        |

## API

분석 API는 로그인 선택 (비회원도 이용 가능, 로그인 시 이력 저장).

### `POST /api/analyze`

관상 분석. `multipart/form-data`로 `file` (image) + `turnstile_token` 전송. `stream=true`로 SSE 스트리밍.

### `POST /api/saju`

사주 분석. JSON body: `{ birth_year, birth_month, birth_day, birth_hour, gender, stream, turnstile_token }`.

### `POST /api/tarot`

타로 분석. JSON body: `{ category, stream, turnstile_token }`. category는 "연애", "재물", "직업", "건강", "오늘의 운세" 중 택1.

### `POST /api/combined`

종합 분석 (관상+사주). `multipart/form-data`로 `file` + 생년월일 정보 + `turnstile_token`.

### `GET /api/profile` / `PUT /api/profile`

프로필 조회/수정. (로그인 필수)

### `GET /api/history` / `GET /api/history/{id}`

분석 이력 목록/상세 조회. (로그인 필수)

### `GET /health`

서버 상태 확인. `{ "status": "ok" }` 반환.

## Deployment

### Production (현재 구성)

| 서비스   | 플랫폼           | 도메인            | 상태             |
| -------- | ---------------- | ----------------- | ---------------- |
| Frontend | Vercel (Hobby)   | zeomzip.com       | 상시 가동 (무료) |
| Backend  | Railway (Docker) | \*.up.railway.app | 필요 시 활성화   |

**프론트엔드**는 Vercel Hobby 플랜으로 상시 가동 (비용 없음).
**백엔드**는 Railway에서 Docker로 배포. 비용 절약을 위해 평소에는 내려두고, 필요 시 활성화.

```bash
# 백엔드 활성화
railway up

# 백엔드 비활성화
railway down --yes

# 프론트엔드 배포 (변경 시)
cd /path/to/physiognomy
vercel --prod --yes
```

### Railway 환경변수

Railway 대시보드 또는 CLI에서 설정 필요:

- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_JWT_SECRET`
- `TURNSTILE_SECRET_KEY`

### Vercel 환경변수

Vercel 대시보드 또는 CLI에서 설정 필요:

- `NEXT_PUBLIC_API_URL` (Railway 백엔드 URL)
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_TURNSTILE_SITE_KEY`

### 로컬 개발

```bash
# Backend (port 13351)
conda activate physiognomy
cd backend && python main.py

# Frontend (port 13350) - 로컬 백엔드 또는 Railway 백엔드 사용 가능
cd frontend && npm run dev
```

`.env.local`에서 `NEXT_PUBLIC_API_URL`을 `http://localhost:13351` 또는 Railway URL로 설정.
