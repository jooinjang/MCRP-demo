# Python 3.11 slim 이미지 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    file \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일들 복사
COPY . .

# 디렉토리 생성 및 권한 설정
RUN mkdir -p /app/chat_data /app/images /app/dist && \
    chmod -R 755 /app

# 포트 노출
EXPOSE 5001

# 환경변수 기본값
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5001
ENV FLASK_DEBUG=false
ENV DATA_DIR=/app/chat_data
ENV EXTERNAL_API_BASE=http://your-ai-server:8000
ENV AI_API_TIMEOUT=10

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${FLASK_PORT}/ || exit 1

# 실행 명령 (디버그 모드에 따라 다르게 실행)
CMD ["sh", "-c", "if [ \"$FLASK_DEBUG\" = \"true\" ]; then python app.py; else gunicorn --bind 0.0.0.0:${FLASK_PORT} --workers 2 --threads 4 --timeout 120 --access-logfile - --error-logfile - app:app; fi"] 