FROM python:3.11-slim

# MediaPipe / OpenCV 시스템 의존성 (v4)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libegl1 \
    libgles2 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/* \
    && ldconfig

WORKDIR /app

# pip 패키지 설치 (캐시 레이어)
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# 소스 + ML 모델 복사
COPY backend/ ./backend/
COPY ml/checkpoints/ ./ml/checkpoints/
COPY ml/models/ ./ml/models/

WORKDIR /app/backend

EXPOSE 13351

CMD ["python", "main.py"]
