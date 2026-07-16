"""
프로젝트 설정 관리
- 환경 변수 로드
- 상수 정의
- 설정 검증
- 다중 DB 지원 (FAQ + 추가섹션 + PDF)
"""

import os
from dotenv import load_dotenv
from loguru import logger

# .env 파일에서 환경 변수 로드
load_dotenv()

class Settings:
    """애플리케이션 설정 클래스"""
    
    # OpenAI API 설정
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE = 0
    
    # ChromaDB 설정 (다중 DB 지원)
    CHROMA_FAQ_DB_PATH = "./seowon_faq_chromadb"           # FAQ 전용 DB
    CHROMA_PDF_DB_PATH = "./seowon_pdf_chromadb_v2"        # PDF 문서 DB (개선된 버전)
    CHROMA_WEB_DB_PATH = "./seowon_web_chromadb"
    
    # DB 사용 모드 선택 (확장된 옵션)
    # 단일 DB 모드:
    # "faq_only" - FAQ만 사용
    # "additional_only" - 추가 섹션만 사용
    # "pdf_only" - PDF 문서만 사용
    #
    # 조합 DB 모드:
    # "faq_and_pdf" - FAQ + PDF 조합
    # "additional_and_pdf" - 추가 섹션 + PDF 조합  
    # "faq_and_additional" - FAQ + 추가 섹션 조합
    # "all" - 모든 DB (FAQ + 추가 섹션 + PDF)
    DB_MODE = "all"  # 기본값: FAQ만 사용 (안전한 시작)
    
    # 검색 파라미터
    RETRIEVER_SEARCH_TYPE = "mmr"  # "similarity", "mmr"
    RETRIEVER_K = 6  # 기본 검색 개수 (4 → 6으로 증가)
    RETRIEVER_FETCH_K = 20  # MMR에서 초기 검색 개수
    RETRIEVER_LAMBDA_MULT = 0.5  # MMR 다양성 파라미터
    
    # 테스트 질문들 (PDF 관련 질문 추가)
    TEST_QUESTIONS = [
        "국가장학금이 지급완료 되었는데 돈이 안 들어와요",
        "현수막이나 포스터 게시는 어떻게 하나요?",
        "학생회비 추가 납부 방법을 알려주세요",
        "생활관 추가 선발 일정이 궁금합니다",
        "대학일자리플러스센터가 뭔가요?",
        "입학 모집요강 PDF에서 전형 일정을 알려주세요",  # PDF 테스트용
        "학사 규정 문서에서 학점 이수 조건을 찾아주세요"    # PDF 테스트용
    ]
    
    # 프롬프트 템플릿 (다양한 문서 타입 대응)
    RAG_PROMPT_TEMPLATE = """
당신은 서원대학교의 종합 정보 상담원입니다. 다양한 자료(FAQ, 웹페이지, PDF 문서)를 바탕으로 학생들의 질문에 정확하고 친절하게 답변해주세요.

검색된 문서 내용:
{context}

학생 질문: {question}

답변 지침:
1. 검색된 문서의 정보를 바탕으로 정확하게 답변하세요
2. 문서에 없는 정보는 추측하지 마세요
3. 친근하고 도움이 되는 톤으로 답변하세요
4. 답변은 한국어로 작성하세요
5. 문서에 관련 정보가 없다면 "해당 정보를 찾을 수 없습니다. 학생지원팀(미래창조관 1층)에 직접 문의해주세요."라고 답변하세요

답변:
"""

    SIMPLE_RAG_PROMPT_TEMPLATE = """
당신은 서원대학교 종합 정보 상담원입니다.

검색된 문서:
{context}

질문: {question}

위 문서를 참고하여 정확하고 친절한 답변을 제공하세요.

답변:
"""

    @classmethod
    def get_available_db_paths(cls) -> dict:
        """사용 가능한 DB 경로들을 반환"""
        db_paths = {}
        
        if os.path.exists(cls.CHROMA_FAQ_DB_PATH):
            db_paths['faq'] = cls.CHROMA_FAQ_DB_PATH

        if os.path.exists(cls.CHROMA_PDF_DB_PATH):
            db_paths['pdf'] = cls.CHROMA_PDF_DB_PATH

        if os.path.exists(cls.CHROMA_WEB_DB_PATH):
            db_paths['web'] = cls.CHROMA_WEB_DB_PATH

        return db_paths
    
    @classmethod
    def get_db_paths_for_mode(cls) -> list:
        """현재 DB_MODE에 따른 사용할 DB 경로들 반환"""
        available_dbs = cls.get_available_db_paths()
        
        if cls.DB_MODE == "faq_only":
            return [available_dbs.get('faq')] if 'faq' in available_dbs else []
            
        elif cls.DB_MODE == "additional_only":
            return [available_dbs.get('additional')] if 'additional' in available_dbs else []
            
        elif cls.DB_MODE == "pdf_only":
            return [available_dbs.get('pdf')] if 'pdf' in available_dbs else []
            
        elif cls.DB_MODE == "faq_and_pdf":
            paths = []
            if 'faq' in available_dbs:
                paths.append(available_dbs['faq'])
            if 'pdf' in available_dbs:
                paths.append(available_dbs['pdf'])
            return paths
            
        elif cls.DB_MODE == "additional_and_pdf":
            paths = []
            if 'additional' in available_dbs:
                paths.append(available_dbs['additional'])
            if 'pdf' in available_dbs:
                paths.append(available_dbs['pdf'])
            return paths
            
        elif cls.DB_MODE == "faq_and_additional":
            paths = []
            if 'faq' in available_dbs:
                paths.append(available_dbs['faq'])
            if 'additional' in available_dbs:
                paths.append(available_dbs['additional'])
            return paths
            
        elif cls.DB_MODE == "all":
            return list(available_dbs.values())
            
        else:
            logger.warning(f"[!] 알 수 없는 DB_MODE: {cls.DB_MODE}, FAQ DB로 대체합니다.")
            return [available_dbs.get('faq')] if 'faq' in available_dbs else []
    
    @classmethod
    def validate(cls) -> bool:
        """설정 유효성 검증"""
        if not cls.OPENAI_API_KEY:
            logger.error("[!] OPENAI_API_KEY가 설정되지 않았습니다.")
            return False
        
        # 사용 가능한 DB 확인
        available_dbs = cls.get_available_db_paths()
        
        if not available_dbs:
            logger.error("[!] 사용 가능한 ChromaDB가 없습니다.")
            logger.error(f"   확인 경로들:")
            logger.error(f"   - FAQ: {cls.CHROMA_FAQ_DB_PATH}")
            logger.error(f"   - 추가 섹션: {cls.CHROMA_ADDITIONAL_DB_PATH}")
            logger.error(f"   - PDF: {cls.CHROMA_PDF_DB_PATH}")
            return False
        
        # 현재 모드에서 사용할 DB가 있는지 확인
        mode_dbs = cls.get_db_paths_for_mode()
        if not mode_dbs or not any(mode_dbs):
            logger.error(f"[!] 현재 DB_MODE '{cls.DB_MODE}'에서 사용할 수 있는 DB가 없습니다.")
            logger.error(f"   사용 가능한 DB: {list(available_dbs.keys())}")
            return False
        
        logger.success("[+] 모든 설정이 유효합니다.")
        return True
    
    @classmethod
    def log_settings(cls):
        """현재 설정 로그 출력"""
        logger.info("[+] 현재 설정:")
        logger.info(f"   OpenAI Model: {cls.OPENAI_MODEL}")
        logger.info(f"   DB Mode: {cls.DB_MODE}")
        
        # 사용 가능한 DB들
        available_dbs = cls.get_available_db_paths()
        logger.info(f"   사용 가능한 DB:")
        for db_type, path in available_dbs.items():
            logger.info(f"      {db_type}: {path}")
        
        # 현재 모드에서 실제 사용될 DB들
        mode_dbs = cls.get_db_paths_for_mode()
        logger.info(f"   현재 모드에서 사용될 DB: {len([db for db in mode_dbs if db])}개")
        
        logger.info(f"   Retriever K: {cls.RETRIEVER_K}")
        logger.info(f"   Search Type: {cls.RETRIEVER_SEARCH_TYPE}")
    
    @classmethod
    def suggest_db_mode(cls):
        """현재 상황에 맞는 DB 모드 제안"""
        available_dbs = cls.get_available_db_paths()
        
        logger.info("\n💡 DB 모드 추천:")
        
        if len(available_dbs) == 1:
            db_type = list(available_dbs.keys())[0]
            if db_type == 'faq':
                logger.info("   추천: DB_MODE = 'faq_only' (FAQ만 사용)")
            elif db_type == 'additional':
                logger.info("   추천: DB_MODE = 'additional_only' (추가 섹션만 사용)")
            elif db_type == 'pdf':
                logger.info("   추천: DB_MODE = 'pdf_only' (PDF만 사용)")
                
        elif len(available_dbs) == 2:
            db_types = set(available_dbs.keys())
            if db_types == {'faq', 'pdf'}:
                logger.info("   추천: DB_MODE = 'faq_and_pdf' (FAQ + PDF)")
            elif db_types == {'additional', 'pdf'}:
                logger.info("   추천: DB_MODE = 'additional_and_pdf' (추가 섹션 + PDF)")
            elif db_types == {'faq', 'additional'}:
                logger.info("   추천: DB_MODE = 'faq_and_additional' (FAQ + 추가 섹션)")
                
        elif len(available_dbs) == 3:
            logger.info("   추천: DB_MODE = 'all' (모든 DB 사용)")
        
        logger.info(f"   현재 설정: DB_MODE = '{cls.DB_MODE}'")

# 전역 설정 인스턴스
settings = Settings() 