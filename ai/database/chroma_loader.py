"""
ChromaDB 로더 모듈
- FAQ, 추가 섹션, PDF, MANUAL 등 다중 DB 지원
- 실제 멀티 DB 검색 및 결과 병합
- DB 우선순위 없이 "유사도(score) 기반 전역 Top-k" 반환
"""

import os
from typing import List, Optional, Dict, Any
from loguru import logger
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
import re

from config import settings


class MultiDBVectorStore:
    """여러 ChromaDB를 실제로 검색하는 wrapper 클래스"""

    def __init__(self, vectorstores: List[Chroma], db_names: List[str]):
        self.vectorstores = vectorstores
        self.db_names = db_names
        logger.info(f"[+] MultiDB 초기화: {', '.join(db_names)} ({len(vectorstores)}개 DB)")

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        모든 DB에서 검색해서 결과 병합 (쿼리 확장 지원)
        - 전공 관련 질문이면 확장 쿼리 검색
        - 기본은 "유사도(score) 기반 전역 Top-k"
        """
        if self._is_major_related_query(query):
            logger.info(f"[+] 전공 관련 질문 감지: 다중 검색 모드")
            return self._multi_query_search(query, k * 2)
        else:
            return self._single_query_search(query, k)

    def _is_major_related_query(self, query: str) -> bool:
        keywords = ["전공", "학과", "커리큘럼", "진로", "자격증", "과목", "수강"]
        if any(kw in query for kw in keywords):
            return True

        # ✅ 특정 교수/연락처 질문은 확장검색 끄기
        if ("교수" in query) or ("교수님" in query) or ("연구실" in query) or ("전화번호" in query):
            return False

        return False

    def _multi_query_search(self, original_query: str, k: int) -> List[Document]:
        """전공 관련 질문에 대한 다중 쿼리 검색"""

        expanded_queries = [
            original_query,
            "전공 목록",
            "학과 소개",
            "대학별 전공",
            "커리큘럼",
            "진로 분야"
        ]

        all_results = []
        seen_contents = set()

        for q in expanded_queries:
            logger.debug(f"[+] 확장 쿼리 검색: '{q}'")
            results = self._single_query_search(q, k // len(expanded_queries) + 1)

            for doc in results:
                content_hash = doc.page_content[:100].strip()
                if content_hash not in seen_contents:
                    seen_contents.add(content_hash)
                    all_results.append(doc)

        return all_results[:k]

    def _single_query_search(self, query: str, k: int) -> List[Document]:
        """단일 쿼리 검색 (DB 구분 없이 유사도 점수만으로 통합 Top-k)"""
        all_scored = []  # (doc, score)

        for vectorstore, db_name in zip(self.vectorstores, self.db_names):
            try:
                # 각 DB에서 k개씩 확보 후 글로벌 정렬
                per_db_k = max(1, k)
                results = vectorstore.similarity_search_with_score(query, k=per_db_k)

                logger.debug(f"[+] {db_name} DB에서 {len(results)}개 결과(score 포함)")

                for doc, score in results:
                    if hasattr(doc, 'metadata'):
                        doc.metadata['search_db'] = db_name
                        doc.metadata['score'] = float(score)
                    all_scored.append((doc, float(score)))

            except Exception as e:
                logger.warning(f"[!] {db_name} DB 검색 실패: {e}")
                continue

        if not all_scored:
            return []

        # Chroma score는 distance(작을수록 유사)로 가정 → 오름차순
        all_scored.sort(key=lambda x: x[1])
        sorted_docs = [d for d, _ in all_scored]

        # 중복 제거 (정렬 유지)
        unique_results = self._deduplicate_results(sorted_docs)

        # 검색 결과 로깅
        db_counts = {}
        for doc in unique_results[:k]:
            dbn = doc.metadata.get('search_db', 'unknown')
            db_counts[dbn] = db_counts.get(dbn, 0) + 1

        logger.info(f"[+] 검색 결과: {len(unique_results[:k])}개")
        for dbn, count in db_counts.items():
            logger.info(f"    {dbn}: {count}개")

        return unique_results[:k]

    def similarity_search_with_score(self, query: str, k: int = 4):
        """점수와 함께 검색 (DB 우선순위 없이 전역 유사도 기준)"""
        all_scored = []

        for vectorstore, db_name in zip(self.vectorstores, self.db_names):
            try:
                per_db_k = max(1, k)
                results = vectorstore.similarity_search_with_score(query, k=per_db_k)

                for doc, score in results:
                    if hasattr(doc, 'metadata'):
                        doc.metadata['search_db'] = db_name
                        doc.metadata['score'] = float(score)
                    all_scored.append((doc, float(score)))

            except Exception as e:
                logger.warning(f"[!] {db_name} DB 점수 검색 실패: {e}")
                continue

        all_scored.sort(key=lambda x: x[1])  # distance 오름차순
        return all_scored[:k]

    def _deduplicate_results(self, results: List[Document]) -> List[Document]:
        """중복 결과 제거 (DB 우선순위 없이, 기존 정렬 유지)"""
        seen_contents = set()
        unique_results = []

        # results는 이미 '유사도(score) 순'으로 정렬되어 들어온다고 가정
        for doc in results:
            content_hash = doc.page_content[:200].strip().replace(' ', '').replace('\n', '').replace('\t', '')
            db_name = doc.metadata.get('search_db', 'unknown') if hasattr(doc, 'metadata') else 'unknown'
            doc_type = doc.metadata.get('type', 'N/A') if hasattr(doc, 'metadata') else 'N/A'

            # PDF 문서는 특별 처리 (더 관대하게)
            if db_name == 'PDF':
                content_hash = doc.page_content[:50].strip().replace(' ', '')

            if content_hash not in seen_contents or len(content_hash) < 10:
                seen_contents.add(content_hash)
                unique_results.append(doc)
                content_preview = doc.page_content[:60].replace('\n', ' ')
                logger.debug(f"    중복제거 유지: [{db_name}] {doc_type} - {content_preview}...")
            else:
                content_preview = doc.page_content[:60].replace('\n', ' ')
                logger.debug(f"    중복제거 제외: [{db_name}] {doc_type} - {content_preview}...")

        return unique_results

    def as_retriever(self, **kwargs):
        """retriever 인터페이스 제공 (LCEL 호환)"""
        return MultiDBRetriever(self, **kwargs)


class MultiDBRetriever(BaseRetriever):
    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}

    multi_db_store: MultiDBVectorStore
    search_kwargs: dict = {}
    search_type: str = "similarity"

    def __init__(self, multi_db_store: MultiDBVectorStore, **kwargs):
        super().__init__(
            multi_db_store=multi_db_store,
            search_kwargs=kwargs.get('search_kwargs', {}),
            search_type=kwargs.get('search_type', 'similarity')
        )

    def _rewrite_query_if_professor(self, query: str) -> str:
        """
        'OOO교수/교수님'이 포함된 질문이면
        검색 쿼리를 교수명 중심으로 단순화해서 recall 보장
        """
        q = query.strip()

        # "김경배교수님 연구실 위치 알려줘" -> "김경배 교수 연구실"
        m = re.search(r"([가-힣]{2,4})\s*교수(님)?", q)
        if m:
            name = m.group(1)
            # 교수 관련 핵심 토큰만 남겨서 재검색
            rewritten = f"{name} 교수 연구실"
            logger.debug(f"[QUERY REWRITE] '{q}' -> '{rewritten}'")
            return rewritten

        return q

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun):
        k = self.search_kwargs.get('k', 4)
        rq = self._rewrite_query_if_professor(query)
        return self.multi_db_store.similarity_search(rq, k=k)

    def invoke(self, input: str, config: Optional[Dict] = None):
        k = self.search_kwargs.get('k', 4)
        rq = self._rewrite_query_if_professor(input)
        return self.multi_db_store.similarity_search(rq, k=k)


class ChromaDBLoader:
    """ChromaDB 로더 클래스 (다중 DB 지원)"""

    @staticmethod
    def _load_single_db(db_path: str, db_name: str) -> Optional[Chroma]:
        """단일 DB 로드"""
        if not db_path or not os.path.exists(db_path):
            logger.warning(f"[!] {db_name} DB 경로가 존재하지 않습니다: {db_path}")
            return None

        try:
            embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
            vectorstore = Chroma(
                persist_directory=db_path,
                embedding_function=embeddings
            )
            logger.success(f"[+] {db_name} DB 로드 완료: {db_path}")
            return vectorstore

        except Exception as e:
            logger.error(f"[!] {db_name} DB 로드 실패: {e}")
            return None

    @staticmethod
    def _load_db_by_mode() -> Optional[MultiDBVectorStore]:
        """현재 설정된 DB_MODE에 따라 DB 로드"""

        db_paths = settings.get_db_paths_for_mode()

        if not db_paths:
            logger.error("[!] 현재 모드에서 사용할 DB가 없습니다.")
            settings.suggest_db_mode()
            return None

        vectorstores = []
        db_names = []

        for db_path in db_paths:
            if not db_path:
                continue

            # DB 타입 식별
            if settings.CHROMA_FAQ_DB_PATH in db_path:
                db_name = "FAQ"
            elif settings.CHROMA_PDF_DB_PATH in db_path:
                db_name = "PDF"
            elif getattr(settings, "CHROMA_WEB__PATH", None) and settings.CHROMA_WEB_DB_PATH in db_path:
                db_name = "WEB"
            else:
                db_name = "알수없음"

            vectorstore = ChromaDBLoader._load_single_db(db_path, db_name)
            if vectorstore:
                vectorstores.append(vectorstore)
                db_names.append(db_name)

        if not vectorstores:
            logger.error("[!] 로드된 DB가 없습니다.")
            return None

        logger.info(f"[+] 로드된 DB 타입: {', '.join(db_names)}")

        return MultiDBVectorStore(vectorstores, db_names)

    def load_existing_db(self):
        """인스턴스 메서드로 DB 로드 (기존 호환성 유지)"""
        return ChromaDBLoader._load_db_by_mode()


# 싱글톤 인스턴스
chroma_loader = ChromaDBLoader()