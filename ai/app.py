from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from loguru import logger

# 기존 모듈
from config import settings
from database import chroma_loader
from chains import create_rag_chains


# ---------- Pydantic 모델 ----------
class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="사용자 질문")


class ReferenceDoc(BaseModel):
    preview: str
    metadata: dict


class ChatResponse(BaseModel):
    answer: str
    references: List[ReferenceDoc] = []


# ---------- 앱 생성 ----------
app = FastAPI(
    title="Seowon FAQ RAG API",
    description="최신 LCEL RAG 시스템의 FastAPI 버전",
    version="1.0.0",
)

# 필요한 도메인(또는 '*')로 바꿔도 됨
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # 배포 시 특정 도메인으로 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- 앱 수명주기: 시작 시 체인/DB 1회 로드 ----------
@app.on_event("startup")
def startup():
    logger.info("=" * 70)
    logger.info("[+] 최신 LCEL RAG 시스템 (FastAPI)")
    logger.info("=" * 70)

    logger.info("[+] 시스템 설정 검증...")
    if not settings.validate():
        logger.error("[!] 설정 검증 실패. 서버 기동 중단 권장")
        raise RuntimeError("환경설정 검증 실패")

    settings.log_settings()

    logger.info("\n[+] ChromaDB 로드 중...")
    vectorstore = chroma_loader.load_existing_db()
    if not vectorstore:
        raise RuntimeError("벡터 DB 로드 실패")

    logger.info("\n[+] RAG 체인들 생성 중...")
    basic_chain, advanced_chain, retriever = create_rag_chains(vectorstore)
    if not basic_chain:
        raise RuntimeError("RAG 체인 생성 실패")

    # 전역 상태로 보관
    app.state.vectorstore = vectorstore
    app.state.basic_chain = basic_chain
    app.state.advanced_chain = advanced_chain
    app.state.retriever = retriever

    logger.success("\n[+] 시스템 준비 완료!")
    logger.info("[+] 사용된 벡터 DB: 설정된 DB_MODE에 따른 Multi-DB")


# ---------- 유틸 ----------
def get_basic_chain():
    chain = getattr(app.state, "basic_chain", None)
    if not chain:
        raise HTTPException(status_code=503, detail="체인이 초기화되지 않았습니다.")
    return chain


def get_retriever():
    retriever = getattr(app.state, "retriever", None)
    if not retriever:
        raise HTTPException(status_code=503, detail="리트리버가 초기화되지 않았습니다.")
    return retriever

def pretty_metadata(meta: dict, idx: int):
    logger.info(f"\n--- Reference #{idx} ---")

    # 기본 필드
    logger.info(f"DB         : {meta.get('search_db')}")
    logger.info(f"Source     : {meta.get('source')}")
    logger.info(f"File       : {meta.get('filename')}")
    logger.info(f"Page       : {meta.get('page_number')} / {meta.get('total_pages')}")
    logger.info(f"Score      : {round(meta.get('score', 0), 4)}")

    # 전공 리스트 보기 좋게
    majors = meta.get("detected_majors")
    count = meta.get("detected_majors_count")

    if majors:
        try:
            majors_list = [m.strip() for m in majors.split(",")]
        except:
            majors_list = [majors]

        logger.info(f"Detected Majors ({count})")
        for m in majors_list:
            logger.info(f"  - {m}")

    # 기타 정보
    logger.info(f"Career Info      : {meta.get('has_career_info')}")
    logger.info(f"Curriculum Info  : {meta.get('has_curriculum')}")
    logger.info(f"Content Length   : {meta.get('content_length')} chars")
    logger.info(f"Timestamp        : {meta.get('timestamp')}")
    logger.info("-----------------------")

# ---------- 엔드포인트 ----------
@app.get("/health")
def health():
    return {"status": "ok", "vectorstore": bool(getattr(app.state, "vectorstore", None))}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """
    기본 RAG 체인을 사용한 Q&A.
    - 입력: { "question": "..." }
    - 출력: { "answer": "...", "references": [{ preview, metadata }, ...] }
    """
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="질문이 비어 있습니다.")

    logger.info(f"[+] 질문 처리: {question}")

    chain = get_basic_chain()
    retriever = get_retriever()

    try:
        # 1) 답변 생성
        answer = chain.invoke(question)

        # 2) 참조 문서 수집
        references: List[ReferenceDoc] = []
        try:
            docs = retriever.invoke(question)

            logger.info("\n[+] 검색된 참조 문서 상위 3개 (raw):")
            for idx, d in enumerate((docs or [])[:3], start=1):
                md = getattr(d, "metadata", {}) or {}
                preview_log = (d.page_content or "")[:80].replace("\n", " ")

                logger.info(
                    f"  {idx}. DB={md.get('search_db')}, "
                    f"source={md.get('source')}, "
                    f"filename={md.get('filename')}, "
                    f"type={md.get('type')}, "
                    f"score={md.get('score')}, "
                    f"preview='{preview_log}...'"
                )

                preview = (d.page_content or "")[:160].replace("\n", " ")
                references.append(
                    ReferenceDoc(
                        preview=preview,
                        metadata=md
                    )
                )
        except Exception as re:
            logger.warning(f"[!] 참조 문서 조회 중 경고: {re}")

        # 3) 최종 답변 + 메타데이터 로그

        logger.info("\n[최종 참조 메타데이터 목록]")
        if not references:
            logger.info("  (참조 없음)")
        else:
            for idx, ref in enumerate(references, start=1):
                pretty_metadata(ref.metadata, idx)

        logger.info("\n[최종 답변]")
        logger.info(answer)

        logger.success("[+] 응답 생성 완료")

        # 4) 클라이언트로 응답 반환
        return ChatResponse(answer=str(answer), references=references)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[!] 답변 생성 오류: {e}")
        raise HTTPException(status_code=500, detail="답변 생성 중 오류가 발생했습니다.")


@app.post("/query", response_model=ChatResponse)
def run_single_query(req: ChatRequest):
    """
    기존 run_single_query와 동일한 용도의 단일 질문 API.
    내부적으로는 /chat과 동일한 처리 흐름을 사용.
    """
    return chat(req)
