"""
최신 LCEL RAG 시스템 (모듈화 버전)
- 모듈화된 구조로 리팩토링
- 설정, 데이터베이스, 체인, 테스트 모듈 분리
- 실시간 대화형 Q&A 시스템
"""

from loguru import logger

# 모듈화된 컴포넌트들 import
from config import settings
from database import chroma_loader
from chains import create_rag_chains

def interactive_chat(basic_chain, retriever):
    """실시간 대화형 Q&A 시스템"""
    
    logger.success("\n[+] 서원대학교 FAQ 실시간 Q&A 시스템")
    logger.info("="*70)
    logger.info("[+] 언제든지 질문해주세요! (종료: 'quit', 'exit', '종료')")
    logger.info("="*70)
    
    while True:
        try:
            # 사용자 질문 입력
            print("\n")  # 개행으로 구분
            question = input("[+] 질문: ").strip()
            
            # 종료 조건
            if question.lower() in ['quit', 'exit', '종료', 'q']:
                logger.success("[+] FAQ 시스템을 종료합니다. 감사합니다!")
                break
            
            # 빈 질문 처리
            if not question:
                logger.warning("[+] 질문을 입력해주세요.")
                continue
            
            logger.info(f"[+] 질문 처리 중: {question}")
            
            # RAG 체인으로 답변 생성
            answer = basic_chain.invoke(question)
            
            # 답변 출력
            logger.success("[+] 답변:")
            print(f"\n{answer}\n")
            
            # # 참조 문서 정보 (선택사항)
            # try:
            #     docs = retriever.invoke(question)
            #     if docs:
            #         logger.info(f"[+] 참조된 문서: {len(docs)}개")
            #         # 첫 번째 문서의 일부만 표시
            #         if len(docs) > 0:
            #             preview = docs[0].page_content[:100].replace('\n', ' ')
            #             logger.debug(f"[+] 주요 참조: {preview}...")
            # except Exception as e:
            #     logger.error(f"[!] 참조 문서 조회 중 오류: {e}")
            
            # print("-" * 70)
            
        except KeyboardInterrupt:
            logger.warning("\n\n[!] Ctrl+C 감지. 시스템을 종료합니다.")
            break
        except Exception as e:
            logger.error(f"[!] 답변 생성 중 오류: {e}")
            logger.info("[+] 다시 질문해주세요.")

def main():
    """메인 실행 함수"""
    
    logger.info("[+] 최신 LCEL RAG 시스템 (실시간 대화형)")
    logger.info("="*70)
    
    # 1. 설정 검증
    logger.info("\n[+] 시스템 설정 검증...")
    if not settings.validate():
        logger.error("[!] 설정 검증 실패. 실행을 중단합니다.")
        return
    
    settings.log_settings()
    
    # 2. ChromaDB 로드
    logger.info("\n[+] ChromaDB 로드 중...")
    vectorstore = chroma_loader.load_existing_db()
    
    if not vectorstore:
        logger.error("[!] 벡터 DB 로드에 실패했습니다.")
        return
    
    # 3. RAG 체인들 생성
    logger.info("\n[+] RAG 체인들 생성 중...")
    basic_chain, advanced_chain, retriever = create_rag_chains(vectorstore)
    
    if not basic_chain:
        logger.error("[!] RAG 체인 생성에 실패했습니다.")
        return
    
    # 4. 실시간 대화 시작
    logger.success("\n[+] 시스템 준비 완료!")
    interactive_chat(basic_chain, retriever)
    
    # 5. 완료
    logger.success("\n[+] 시스템 종료 완료!")
    logger.info("[+] 사용된 벡터 DB: ./seowon_faq_chromadb")

def run_single_query(question: str):
    """단일 질문 실행 함수 (API용)"""
    
    logger.info(f"[+] API 질문 실행: {question}")
    
    # 설정 검증
    if not settings.validate():
        return None
    
    # DB 로드
    vectorstore = chroma_loader.load_existing_db()
    if not vectorstore:
        return None
    
    # 체인 생성
    basic_chain, _, _ = create_rag_chains(vectorstore)
    if not basic_chain:
        return None
    
    # 질문 실행
    try:
        answer = basic_chain.invoke(question)
        logger.info(f"[+] 답변: {answer}")
        return answer
    except Exception as e:
        logger.error(f"[!] 답변 생성 중 오류: {e}")
        return None

if __name__ == "__main__":
    # logger.info("[+] 필요한 패키지:")
    # logger.info("[+] pip install langchain-openai langchain-community langchain-core langchain-chroma chromadb python-dotenv loguru")
    logger.info("\n" + "="*70)
    
    # 메인 실행
    main()