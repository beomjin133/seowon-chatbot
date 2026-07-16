# AI — 서원대학교 RAG 챗봇 엔진

LangChain LCEL 기반 RAG API 서버입니다. FAQ · 학과 웹페이지 · 전공안내 PDF를 각각 ChromaDB에
임베딩해 두고, 질문이 오면 **여러 DB를 동시에 검색한 뒤 유사도(score) 기준 전역 Top-k**를 뽑아
GPT로 답변을 생성합니다. `backend`(Spring Boot)가 이 서버의 `/chat`을 호출합니다.

## 구조

```
ai/
├── app.py                  # FastAPI 서버 (POST /chat, /query · GET /health) — 운영 진입점
├── main.py                 # 터미널 대화형 Q&A (로컬 디버깅용)
├── config/settings.py      # 환경변수 · DB 경로 · DB_MODE · 프롬프트 템플릿
├── database/chroma_loader.py  # 멀티 ChromaDB 로더 + 전역 Top-k 병합 retriever
├── chains/rag_chains.py    # LCEL RAG 체인 구성
├── tests/rag_tests.py      # 체인 동작 테스트
├── tools/                  # 크롤링 · PDF 처리 · 벡터 DB 빌드 스크립트
├── web_documents/          # AI소프트웨어학과 크롤링 원문 (web 벡터 DB의 소스)
└── docker/entrypoint.sh    # 권한 조정 후 appuser로 강등
```

## 벡터 DB는 저장소에 없습니다

`seowon_*_chromadb/` 디렉터리는 용량이 크고 재생성이 가능하므로 커밋하지 않습니다.
아래 스크립트로 직접 빌드해야 서버가 기동합니다. **모두 `ai/` 루트에서 실행하세요**
(스크립트가 `./seowon_...` 상대경로를 사용합니다).

| 벡터 DB | 빌드 명령 | 소스 |
|---|---|---|
| `seowon_faq_chromadb` | `python tools/web_chroma_db.py` | 학교 FAQ 페이지 크롤링 |
| `seowon_web_chromadb` | `python tools/build_manual_chroma_db.py` | `web_documents/` (저장소에 포함) |
| `seowon_pdf_chromadb_v2` | `python tools/improved_pdf_processor.py` | `pdf_documents/`의 전공안내 PDF |

PDF 원본은 저작권 자료라 커밋하지 않았습니다. PDF DB가 필요하면 `2025 서원대 전공안내` PDF를
`pdf_documents/`에 직접 넣고 위 스크립트를 실행하세요. 셋 중 일부만 있어도 동작하며,
`settings.py`가 존재하는 DB만 자동으로 골라 씁니다.

## 실행

```bash
cp .env.example .env      # OPENAI_API_KEY 입력
pip install -r requirements.txt
uvicorn app:app --reload  # http://localhost:8000/docs
```

크롤러나 PDF 처리 스크립트를 돌릴 때는 추가 의존성이 필요합니다:

```bash
pip install -r requirements-tools.txt
playwright install chromium
```

### Docker

```bash
docker compose up --build   # .env를 읽고 8000 포트로 기동
```

`docker-compose.yml`은 `./seowon_faq_chromadb`를 컨테이너에 바인드 마운트하므로,
호스트에 먼저 DB를 빌드해 두어야 합니다.

## 설정 (`config/settings.py`)

- `DB_MODE` — 검색에 사용할 DB 조합. 기본값 `"all"`(존재하는 DB 전부).
  `faq_only` · `pdf_only` · `faq_and_pdf` 등으로 좁힐 수 있습니다.
- `RETRIEVER_SEARCH_TYPE` — 기본 `mmr`. `RETRIEVER_K`(6)개를 `FETCH_K`(20)에서 다양성 있게 추립니다.
- `OPENAI_MODEL` — 기본 `gpt-3.5-turbo`.

## API

`POST /chat` — `{"question": "..."}` → `{"answer": "...", "references": [{preview, metadata}]}`
`GET /health` — 벡터 DB 로드 여부 확인 (Docker 헬스체크가 사용).
