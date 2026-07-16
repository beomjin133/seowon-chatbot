"""
RAG 체인 모듈
- 기본 RAG 체인 생성
- 고급 RAG 체인 (소스 포함) 생성
- MultiDB 지원으로 체인 구성 요소 관리
"""

from typing import Optional, Tuple, Union
from loguru import logger
from langchain_openai import ChatOpenAI

# 최신 ChromaDB import (deprecated 해결)
from langchain_chroma import Chroma

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from config.settings import settings

# MultiDBVectorStore import
from database.chroma_loader import MultiDBVectorStore

class RAGChainBuilder:
    """RAG 체인 생성 및 관리 클래스 (MultiDB 지원)"""
    
    def __init__(self, vectorstore: Union[Chroma, MultiDBVectorStore]):
        self.vectorstore = vectorstore
        self.llm: Optional[ChatOpenAI] = None
        self._setup_llm()
    
    def _setup_llm(self):
        """LLM 설정"""
        try:
            self.llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=settings.OPENAI_TEMPERATURE,
                api_key=settings.OPENAI_API_KEY
            )
            logger.success("[+] ChatOpenAI LLM 설정 완료")
        except Exception as e:
            logger.error(f"[!] ChatOpenAI LLM 설정 실패: {e}")
            self.llm = None
    
    def create_basic_rag_chain(self):
        """기본 RAG 체인 생성 (MultiDB 지원)"""
        
        if not self.vectorstore:
            logger.error("[!] 벡터스토어가 없어서 RAG 체인을 생성할 수 없습니다.")
            return None, None
        
        if not self.llm:
            logger.error("[!] LLM이 설정되지 않아서 RAG 체인을 생성할 수 없습니다.")
            return None, None
        
        logger.info("[+] 기본 RAG 체인 생성 중...")
        
        try:
            # Retriever 설정 (MultiDB 또는 Chroma 모두 지원)
            if isinstance(self.vectorstore, MultiDBVectorStore):
                # MultiDB의 경우
                retriever = self.vectorstore.as_retriever(
                    search_type=settings.RETRIEVER_SEARCH_TYPE,
                    search_kwargs={
                        "k": settings.RETRIEVER_K,
                        "fetch_k": settings.RETRIEVER_FETCH_K,
                        "lambda_mult": settings.RETRIEVER_LAMBDA_MULT
                    }
                )
                logger.info("[+] MultiDB Retriever 생성 완료")
            else:
                # 기존 Chroma의 경우
                retriever = self.vectorstore.as_retriever(
                    search_type=settings.RETRIEVER_SEARCH_TYPE,
                    search_kwargs={
                        "k": settings.RETRIEVER_K,
                        "fetch_k": settings.RETRIEVER_FETCH_K,
                        "lambda_mult": settings.RETRIEVER_LAMBDA_MULT
                    }
                )
                logger.info("[+] Chroma Retriever 생성 완료")
            
            # 프롬프트 템플릿 정의
            rag_prompt = ChatPromptTemplate.from_template(settings.RAG_PROMPT_TEMPLATE)
            
            # 출력 파서
            output_parser = StrOutputParser()
            
            # 문서 포매팅 함수 (DB 출처 정보 포함)
            def format_docs(docs):
                formatted_parts = []
                for i, doc in enumerate(docs):
                    # DB 출처 정보 추가
                    search_db = doc.metadata.get('search_db', 'N/A')
                    doc_type = doc.metadata.get('type', 'N/A')
                    
                    formatted_parts.append(
                        f"문서 {i+1} (출처: {search_db} DB, 타입: {doc_type}): {doc.page_content}"
                    )
                return "\n\n".join(formatted_parts)
            
            # LCEL 체인 구성: retriever → prompt → model → output_parser
            rag_chain = (
                {
                    "context": retriever | format_docs,
                    "question": RunnablePassthrough()
                }
                | rag_prompt
                | self.llm
                | output_parser
            )
            
            logger.success("[+] 기본 RAG 체인 생성 완료!")
            logger.info("   구조: retriever → prompt → model → output_parser")
            
            return rag_chain, retriever
            
        except Exception as e:
            logger.error(f"[!] 기본 RAG 체인 생성 실패: {e}")
            return None, None
    
    def create_advanced_rag_chain_with_sources(self):
        """소스 문서를 포함한 고급 RAG 체인 생성 (MultiDB 지원)"""
        
        if not self.vectorstore:
            logger.error("[!] 벡터스토어가 없어서 고급 RAG 체인을 생성할 수 없습니다.")
            return None, None
        
        if not self.llm:
            logger.error("[!] LLM이 설정되지 않아서 고급 RAG 체인을 생성할 수 없습니다.")
            return None, None
        
        logger.info("[+] 고급 RAG 체인 생성 중...")
        
        try:
            # Retriever 설정
            if isinstance(self.vectorstore, MultiDBVectorStore):
                retriever = self.vectorstore.as_retriever(
                    search_kwargs={"k": settings.RETRIEVER_K}
                )
            else:
                retriever = self.vectorstore.as_retriever(
                    search_kwargs={"k": settings.RETRIEVER_K}
                )
            
            # 프롬프트 템플릿 정의
            rag_prompt = ChatPromptTemplate.from_template(settings.SIMPLE_RAG_PROMPT_TEMPLATE)
            
            # 문서 포매팅 함수 (DB 출처 정보 포함)
            def format_docs(docs):
                formatted_parts = []
                for doc in docs:
                    search_db = doc.metadata.get('search_db', 'N/A')
                    formatted_parts.append(f"[{search_db}] {doc.page_content}")
                return "\n\n".join(formatted_parts)
            
            # 병렬 처리로 답변과 소스 문서 동시 반환
            rag_chain_with_source = RunnableParallel({
                "answer": (
                    {
                        "context": retriever | format_docs,
                        "question": RunnablePassthrough()
                    }
                    | rag_prompt
                    | self.llm
                    | StrOutputParser()
                ),
                "source_documents": retriever
            })
            
            logger.success("[+] 고급 RAG 체인 생성 완료!")
            logger.info("   구조: retriever → [answer + source_documents]")
            
            return rag_chain_with_source, retriever
            
        except Exception as e:
            logger.error(f"[!] 고급 RAG 체인 생성 실패: {e}")
            return None, None

def create_rag_chains(vectorstore: Union[Chroma, MultiDBVectorStore]) -> Tuple[Optional[object], Optional[object], Optional[object]]:
    """RAG 체인들을 생성하는 편의 함수 (MultiDB 지원)"""
    
    if not vectorstore:
        logger.error("[!] 벡터스토어가 제공되지 않았습니다.")
        return None, None, None
    
    # RAG 체인 빌더 생성
    builder = RAGChainBuilder(vectorstore)
    
    # 기본 RAG 체인 생성
    basic_chain, retriever = builder.create_basic_rag_chain()
    
    # 고급 RAG 체인 생성
    advanced_chain, _ = builder.create_advanced_rag_chain_with_sources()
    
    return basic_chain, advanced_chain, retriever 