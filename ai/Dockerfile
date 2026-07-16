# ---------- Build stage ----------
FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# ---------- Runtime stage ----------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates gosu \
 && rm -rf /var/lib/apt/lists/*

# 고정 UID/GID로 사용자 생성(호스트 1000:1000과 맞추면 더 매끄러움)
RUN groupadd -g 1000 appgroup && useradd -m -u 1000 -g appgroup appuser

WORKDIR /app

# wheel 설치
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# 소스 복사
COPY . /app

# 실행 스크립트 권한
RUN chmod +x /app/start.sh

# 벡터DB 경로(컨테이너 내부) + 미리 디렉터리 만들기
ENV RAG_DB_DIR=/app/seowon_faq_chromadb
RUN mkdir -p "$RAG_DB_DIR" && chown -R appuser:appgroup "$RAG_DB_DIR"

# 런타임 튜닝
ENV PORT=8000 WORKERS=2 TIMEOUT=60 GRACEFUL_TIMEOUT=30 LOG_LEVEL=info

# 볼륨(선택) - compose에서 바인드 마운트 시 권한 문제 처리 필요
VOLUME ["/app/seowon_faq_chromadb"]

# 헬스체크 (FastAPI /health)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -fsS http://127.0.0.1:${PORT}/health || exit 1

# 엔트리포인트 추가
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8000

# root로 시작 → entrypoint에서 chown 시도 후 gosu로 권한 강등
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["/app/start.sh"]
