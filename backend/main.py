from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# .env 로드
load_dotenv(Path(__file__).parent.parent / ".env")

from routers import analysis, saju, combined

app = FastAPI(
    title="Physiognomy AI API",
    description="AI 기반 관상 + 사주 분석 API",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(saju.router, prefix="/api", tags=["saju"])
app.include_router(combined.router, prefix="/api", tags=["combined"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=13351, reload=True)
