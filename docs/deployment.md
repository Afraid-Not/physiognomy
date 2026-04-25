# 배포 가이드 (데모용)

Backend는 ngrok, Frontend는 Vercel로 배포하는 방법입니다.

---

## 사전 준비

### 1. 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### 2. 도구 설치 

- [ngrok](https://ngrok.com/) 설치 후 인증
  ```bash
  ngrok config add-authtoken <your-token>
  ```
- [Vercel CLI](https://vercel.com/docs/cli) 설치 후 로그인
  ```bash
  npm i -g vercel
  vercel login
  ```

### 3. 의존성 설치

```bash
# Backend (conda 환경 활성화 후)
cd backend
uv pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

---

## 배포 순서

### Step 1. Backend 실행

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Step 2. ngrok 터널 열기 (새 터미널)

```bash
ngrok http 8000
```

실행 후 표시되는 **Forwarding URL**을 복사합니다.
예: `https://xxxx-xxx-xxx.ngrok-free.dev`

### Step 3. Frontend를 Vercel에 배포

ngrok URL을 환경변수로 넘겨서 Production 배포합니다.

```bash
cd frontend
npx vercel --prod --yes -e NEXT_PUBLIC_API_URL=https://xxxx-xxx-xxx.ngrok-free.dev
```

배포 완료 후 출력되는 **Production URL**을 공유하면 됩니다.

---

## 주의사항

- **CORS**: `backend/main.py`의 `allow_origins`가 `["*"]`인지 확인합니다. 로컬 전용이면 `["http://localhost:3000"]`으로 제한하세요.
- **ngrok 무료 플랜**: PC가 꺼지거나 ngrok을 종료하면 URL이 변경됩니다. URL이 바뀌면 Vercel에 다시 배포해야 합니다.
- **ngrok 경고 페이지**: 무료 플랜은 브라우저 접속 시 경고 페이지가 뜨지만, API 호출에는 영향 없습니다.
