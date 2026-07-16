# 서원대학교 챗봇

서원대학교 학생들이 학교 정보를 자연어로 물어볼 수 있는 RAG 챗봇입니다.
FAQ · 학과 웹페이지 · 전공안내 PDF를 벡터 DB에 임베딩해 두고, 질문이 들어오면
관련 문서를 검색해 그 내용만으로 답변을 생성합니다. 문서에 없는 내용은 지어내지 않고
학생지원팀 문의를 안내합니다.

## 구성

세 개의 모듈이 각각 독립적으로 실행됩니다.

| 모듈 | 스택 | 포트 | 역할 |
|---|---|---|---|
| [`frontend`](frontend/) | React 19 · Redux Toolkit | 3000 | 채팅 UI, 로그인·회원가입 |
| [`backend`](backend/) | Spring Boot 2.7 · MySQL | 8080 | 인증(JWT), 세션·대화 로그 저장, AI 호출 중계 |
| [`ai`](ai/) | FastAPI · LangChain · ChromaDB | 8000 | RAG 검색 및 답변 생성 |

```
사용자 → frontend :3000
           │  POST /api/chat  (JWT)
           ▼
         backend :8080 ── 대화 로그·세션을 MySQL에 저장
           │  POST /chat  {"question": "..."}
           ▼
          ai :8000 ── ChromaDB 검색 → OpenAI로 답변 생성
```

프론트엔드는 AI 서버를 직접 부르지 않습니다. 백엔드가 중계하면서 인증을 확인하고
질문·답변·응답시간을 기록합니다. 로그인하지 않은 사용자도 질문할 수 있으며, 이때는
세션에 저장하지 않고 답변만 돌려줍니다.

## 실행 순서

세 모듈을 각각 띄워야 하며, **`ai` → `backend` → `frontend`** 순서를 권장합니다.
백엔드는 기동 시 AI 서버를 호출하지 않으므로 순서가 강제되지는 않지만, 채팅을 하려면
셋 다 떠 있어야 합니다.

### 1. ai (:8000)

벡터 DB가 저장소에 포함되어 있지 않아 **처음 한 번은 직접 빌드해야 합니다.**
자세한 내용은 [`ai/README.md`](ai/README.md)를 참고하세요.

```bash
cd ai
cp .env.example .env              # OPENAI_API_KEY 입력
pip install -r requirements.txt
python tools/build_manual_chroma_db.py   # 최소 1개 벡터 DB 빌드
uvicorn app:app --reload
```

### 2. backend (:8080)

MySQL에 `chatbot` 스키마가 있어야 하며, 테이블은 JPA가 자동 생성합니다(`ddl-auto=update`).

```bash
cd backend
cp src/main/resources/application-local.properties.example \
   src/main/resources/application-local.properties   # DB 비밀번호·JWT 시크릿·메일 계정 입력
./gradlew bootRun
```

### 3. frontend (:3000)

```bash
cd frontend
npm install
npm start
```

## 설정

비밀값은 저장소에 커밋하지 않습니다. 각 모듈의 `.example` 파일을 복사해서 채우세요.

| 항목 | 위치 | 기본값 |
|---|---|---|
| `OPENAI_API_KEY` | `ai/.env` | 없음 (필수) |
| `AI_CHAT_URL` | backend 환경변수 | `http://localhost:8000/chat` |
| `CORS_ALLOWED_ORIGINS` | backend 환경변수 | `*` |
| `DB_PASSWORD` · `JWT_SECRET` · `MAIL_*` | `backend/src/main/resources/application-local.properties` | 없음 (필수) |
| `REACT_APP_API_BASE_URL` | `frontend/.env` | `http://localhost:8080/api` |

AI 서버를 다른 호스트에 띄웠다면 백엔드에 `AI_CHAT_URL`을 지정해야 합니다.
`CORS_ALLOWED_ORIGINS`는 기본값이 `*`인데, 백엔드가 인증 쿠키를 함께 허용하므로
공개 배포 시에는 실제 프론트엔드 주소로 좁히는 것이 안전합니다.

## API

백엔드가 프론트엔드에 노출하는 엔드포인트입니다. 인증 없이 호출할 수 있는 것은
`/api/chat`, `/api/auth/**`, `/api/email/**`, `/actuator/**` 뿐이고 나머지는 JWT가 필요합니다
(`SecurityConfig` 참고). Swagger UI(`/swagger-ui.html`)도 인증 대상에 포함됩니다.

| 메서드 | 경로 | 설명 |
|---|---|---|
| `POST` | `/api/chat` | 질문 전송 및 답변 수신 (비회원 허용) |
| `POST` | `/api/auth/register` · `/api/auth/login` | 회원가입 · 로그인(JWT 발급) |
| `POST` | `/api/email/send` · `/api/email/verify` | 회원가입 이메일 인증 |
| `POST` | `/api/session/create` · `/api/session/list` | 대화 세션 생성 · 목록 |
| `GET` `PUT` `DELETE` | `/api/session/{session_id}` | 세션 조회 · 제목 수정 · 삭제 |
| `PUT` | `/api/user/{email}` · `/api/user/password` | 회원정보 · 비밀번호 변경 |

AI 서버(`ai`)는 `POST /chat`과 `GET /health`만 제공하며, 백엔드만 호출합니다.
