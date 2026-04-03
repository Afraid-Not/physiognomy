FROM python:3.11-slim

# MediaPipe / OpenCV 시스템 의존성
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# pip 패키지 설치 (캐시 레이어)
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# 소스 + ML 모델 복사
COPY backend/ ./backend/
COPY ml/checkpoints/ ./ml/checkpoints/
COPY ml/models/ ./ml/models/
COPY .env.example ./.env.example

WORKDIR /app/backend

EXPOSE 13351

CMD ["python", "main.py"]
