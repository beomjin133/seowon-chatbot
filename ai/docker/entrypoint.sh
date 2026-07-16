#!/usr/bin/env bash
set -euo pipefail

# 기본값
: "${RAG_DB_DIR:=/app/seowon_faq_chromadb}"

# 디렉터리 보장
mkdir -p "$RAG_DB_DIR"

# 바인드 마운트여도 가능한 한 소유권 교정 시도
if chown -R appuser:appgroup "$RAG_DB_DIR" 2>/dev/null; then
  echo "[entrypoint] chown OK -> $RAG_DB_DIR → appuser:appgroup"
else
  echo "[entrypoint] chown 실패(바인드 마운트 권한 제한 가능). 현재 퍼미션:"
  ls -ld "$RAG_DB_DIR" || true
  echo "[entrypoint] 호스트에서 디렉터리 소유자를 UID 1000:GID 1000으로 바꿔주세요."
fi

# start.sh 자체도 실행 가능하도록
chmod +x /app/start.sh || true

# appuser로 권한 강등하여 실행
exec gosu appuser:appgroup "$@"
