"""
RAG 테스트 모듈
- 기본 RAG 체인 테스트
- 고급 RAG 체인 테스트
- 테스트 결과 분석
"""

from typing import Optional
from loguru import logger
from config.settings import settings

class RAGTester:
    """RAG 체인 테스트 클래스"""
    
    def __init__(self, basic_chain=None, advanced_chain=None, retriever=None):
        self.basic_chain = basic_chain
        self.advanced_chain = advanced_chain
        self.retriever = retriever
    
    def test_basic_rag_chain(self):
        """기본 RAG 체인 테스트"""
        
        if not self.basic_chain:
            logger.error("[!] 기본 RAG 체인이 설정되지 않았습니다.")
            return
        
        logger.info("\n" + "="*70)
        logger.info("[+] 기본 LCEL RAG 체인 테스트 시작")
        logger.info("="*70)
        
        for i, question in enumerate(settings.TEST_QUESTIONS, 1):
            logger.info(f"\n[+] 질문 {i}: {question}")
            logger.info("-" * 50)
            
            try:
                # LCEL 체인 실행
                answer = self.basic_chain.invoke(question)
                logger.info(f"[+] 답변: {answer}")
                
                # 참조 문서 확인 (retriever가 있는 경우)
                if self.retriever:
                    self._show_reference_documents(question)
                
            except Exception as e:
                logger.error(f"[!] 답변 생성 중 오류: {e}")
            
            logger.info("-" * 50)
    
    def test_advanced_rag_chain(self):
        """고급 RAG 체인 테스트 (소스 포함)"""
        
        if not self.advanced_chain:
            logger.error("[!] 고급 RAG 체인이 설정되지 않았습니다.")
            return
        
        logger.info("\n" + "="*70)
        logger.info("[+] 고급 RAG 체인 테스트 (소스 문서 포함)")
        logger.info("="*70)
        
        test_question = "국가장학금 지급 관련해서 자세히 알려주세요"
        
        try:
            result = self.advanced_chain.invoke(test_question)
            
            logger.info(f"[+] 질문: {test_question}")
            logger.info(f"[+] 답변: {result['answer']}")
            
            # 소스 문서 표시
            if result.get('source_documents'):
                self._show_source_documents(result['source_documents'])
            
        except Exception as e:
            logger.error(f"[!] 고급 RAG 체인 테스트 중 오류: {e}")
    
    def test_single_question(self, question: str, chain_type: str = "basic"):
        """단일 질문 테스트"""
        
        logger.info(f"\n[+] 단일 질문 테스트: {question}")
        logger.info("-" * 50)
        
        try:
            if chain_type == "basic" and self.basic_chain:
                answer = self.basic_chain.invoke(question)
                logger.info(f"[+] 기본 체인 답변: {answer}")
                
            elif chain_type == "advanced" and self.advanced_chain:
                result = self.advanced_chain.invoke(question)
                logger.info(f"[+] 고급 체인 답변: {result['answer']}")
                
                if result.get('source_documents'):
                    self._show_source_documents(result['source_documents'], max_docs=2)
            
            else:
                logger.error(f"[!] {chain_type} 체인이 설정되지 않았습니다.")
                
        except Exception as e:
            logger.error(f"[!] 단일 질문 테스트 중 오류: {e}")
    
    def _show_reference_documents(self, question: str, max_docs: int = 2):
        """참조 문서 표시"""
        if not self.retriever:
            return
        
        try:
            docs = self.retriever.invoke(question)
            if docs:
                logger.info(f"\n[+] 참조 문서 ({len(docs)}개):")
                for j, doc in enumerate(docs[:max_docs], 1):
                    preview = doc.page_content[:150].replace('\n', ' ')
                    logger.info(f"   {j}. {preview}...")
        except Exception as e:
            logger.warning(f"[!] 참조 문서 조회 중 오류: {e}")
    
    def _show_source_documents(self, source_documents, max_docs: int = 3):
        """소스 문서 표시"""
        logger.info(f"\n[+] 참조 문서 ({len(source_documents)}개):")
        for i, doc in enumerate(source_documents[:max_docs], 1):
            preview = doc.page_content[:200].replace('\n', ' ')
            logger.info(f"   {i}. {preview}...")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        logger.info("[+] RAG 시스템 전체 테스트 시작")
        
        # 기본 RAG 체인 테스트
        if self.basic_chain:
            self.test_basic_rag_chain()
        
        # 고급 RAG 체인 테스트
        if self.advanced_chain:
            self.test_advanced_rag_chain()
        
        logger.success("\n[+] 모든 테스트 완료!")

def run_rag_tests(basic_chain=None, advanced_chain=None, retriever=None):
    """RAG 테스트 실행 편의 함수"""
    
    tester = RAGTester(basic_chain, advanced_chain, retriever)
    tester.run_all_tests()
    
    return tester 