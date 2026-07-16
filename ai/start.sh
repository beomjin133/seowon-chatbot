#!/usr/bin/env bash
set -euo pipefail

# Gunicorn을 비루트(appuser)로 실행
exec gunicorn app:app \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:"${PORT:-8000}" \
  --workers "${WORKERS:-2}" \
  --timeout "${TIMEOUT:-60}" \
  --graceful-timeout "${GRACEFUL_TIMEOUT:-30}" \
  --log-level "${LOG_LEVEL:-info}"
