"""
PDF 문서 처리 및 ChromaDB 저장 모듈
- 다양한 PDF 파일 처리 (PyPDF2, Unstructured 지원)
- 텍스트 추출 및 메타데이터 보존
- 기존 ChromaDB와 호환되는 형태로 저장
- 점진적 확장 전략 지원
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# PDF 처리를 위한 다양한 로더들
try:
    from langchain_community.document_loaders import PyPDFLoader
    PDF_LOADER_AVAILABLE = True
except ImportError:
    PDF_LOADER_AVAILABLE = False

try:
    from langchain_community.document_loaders import UnstructuredPDFLoader
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False

try:
    from langchain_community.document_loaders import PDFMinerLoader
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False

load_dotenv()

class PDFProcessor:
    """PDF 문서 처리 및 ChromaDB 저장 클래스"""
    
    def __init__(self, pdf_directory: str = "./pdf_documents", 
                 chroma_db_path: str = "./seowon_pdf_chromadb"):
        self.pdf_directory = Path(pdf_directory)
        self.chroma_db_path = chroma_db_path
        self.all_documents = []
        
        # 지원되는 PDF 로더 확인
        self._check_available_loaders()
        
        # PDF 디렉토리 생성
        self.pdf_directory.mkdir(exist_ok=True)
        
    def _check_available_loaders(self):
        """사용 가능한 PDF 로더들 확인"""
        print("🔍 PDF 처리 라이브러리 확인:")
        
        loaders = []
        if PDF_LOADER_AVAILABLE:
            loaders.append("PyPDFLoader")
            print("   ✅ PyPDFLoader 사용 가능")
        
        if UNSTRUCTURED_AVAILABLE:
            loaders.append("UnstructuredPDFLoader")  
            print("   ✅ UnstructuredPDFLoader 사용 가능")
            
        if PDFMINER_AVAILABLE:
            loaders.append("PDFMinerLoader")
            print("   ✅ PDFMinerLoader 사용 가능")
        
        if not loaders:
            print("   ❌ PDF 처리 라이브러리가 설치되지 않았습니다!")
            print("   💡 설치 명령어:")
            print("   pip install pypdf2 unstructured pdfminer.six")
        else:
            print(f"   📊 총 {len(loaders)}개 로더 사용 가능: {', '.join(loaders)}")
    
    def _clean_text(self, text: str) -> str:
        """PDF에서 추출한 텍스트 정제"""
        if not text:
            return ""
        
        # 여러 개의 공백, 탭, 개행을 정리
        text = re.sub(r'\s+', ' ', text)
        
        # PDF 특유의 불필요한 문자 제거
        text = text.replace('\x00', '')  # null 문자 제거
        text = text.replace('\ufffd', '')  # 깨진 문자 제거
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        return text
    
    def _extract_metadata_from_filename(self, file_path: Path) -> Dict:
        """파일명에서 메타데이터 추출"""
        filename = file_path.name
        
        # 기본 메타데이터
        metadata = {
            'filename': filename,
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size,
            'created_date': datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
            'modified_date': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        # 파일명 패턴에서 추가 정보 추출
        filename_lower = filename.lower()
        
        # 문서 유형 추정
        if any(word in filename_lower for word in ['규정', '규칙', '내규']):
            metadata['document_type'] = '규정'
        elif any(word in filename_lower for word in ['안내', '가이드', '매뉴얼']):
            metadata['document_type'] = '안내서'
        elif any(word in filename_lower for word in ['공지', '알림']):
            metadata['document_type'] = '공지사항'
        elif any(word in filename_lower for word in ['입학', '모집']):
            metadata['document_type'] = '입학자료'
        elif any(word in filename_lower for word in ['장학', '등록금']):
            metadata['document_type'] = '학사자료'
        else:
            metadata['document_type'] = '일반문서'
        
        # 연도 추출 (파일명에서 4자리 숫자)
        year_match = re.search(r'20[0-9]{2}', filename)
        if year_match:
            metadata['year'] = year_match.group()
        
        return metadata
    
    def _load_pdf_with_fallback(self, file_path: Path) -> List[Document]:
        """여러 로더를 시도하여 PDF 로드"""
        documents = []
        
        # 시도할 로더들 (우선순위 순)
        loaders_to_try = []
        
        if PDF_LOADER_AVAILABLE:
            loaders_to_try.append(("PyPDFLoader", PyPDFLoader))
        
        if UNSTRUCTURED_AVAILABLE:
            loaders_to_try.append(("UnstructuredPDFLoader", UnstructuredPDFLoader))
        
        if PDFMINER_AVAILABLE:
            loaders_to_try.append(("PDFMinerLoader", PDFMinerLoader))
        
        for loader_name, loader_class in loaders_to_try:
            try:
                print(f"   🔄 {loader_name} 시도 중...")
                loader = loader_class(str(file_path))
                documents = loader.load()
                
                if documents and len(documents) > 0:
                    print(f"   ✅ {loader_name} 성공: {len(documents)}개 페이지 로드")
                    break
                else:
                    print(f"   ⚠️ {loader_name}: 문서가 비어있음")
                    
            except Exception as e:
                print(f"   ❌ {loader_name} 실패: {e}")
                continue
        
        return documents
    
    def process_single_pdf(self, file_path: Path) -> List[Document]:
        """단일 PDF 파일 처리"""
        print(f"📄 PDF 처리 중: {file_path.name}")
        
        if not file_path.exists():
            print(f"   ❌ 파일이 존재하지 않습니다: {file_path}")
            return []
        
        # 파일 크기 확인
        file_size_mb = file_path.stat().st_size / 1024 / 1024
        print(f"   📊 파일 크기: {file_size_mb:.2f} MB")
        
        if file_size_mb > 50:  # 50MB 초과시 경고
            print(f"   ⚠️ 큰 파일입니다. 처리에 시간이 걸릴 수 있습니다.")
        
        # PDF 로드
        raw_documents = self._load_pdf_with_fallback(file_path)
        
        if not raw_documents:
            print(f"   ❌ PDF 로드 실패")
            return []
        
        # 메타데이터 추출
        file_metadata = self._extract_metadata_from_filename(file_path)
        
        # 각 페이지를 Document 객체로 변환
        processed_documents = []
        
        for i, doc in enumerate(raw_documents):
            # 텍스트 정제
            cleaned_content = self._clean_text(doc.page_content)
            
            if len(cleaned_content) < 50:  # 너무 짧은 페이지는 제외
                print(f"   ⚠️ 페이지 {i+1}: 내용이 너무 짧음 ({len(cleaned_content)}자)")
                continue
            
            # 메타데이터 병합
            combined_metadata = {
                **file_metadata,
                'page_number': i + 1,
                'total_pages': len(raw_documents),
                'source': str(file_path),
                'type': 'pdf_document',
                'timestamp': datetime.now().isoformat()
            }
            
            # 기존 문서 메타데이터와 병합
            if hasattr(doc, 'metadata') and doc.metadata:
                combined_metadata.update(doc.metadata)
            
            # 새 Document 생성
            processed_doc = Document(
                page_content=cleaned_content,
                metadata=combined_metadata
            )
            
            processed_documents.append(processed_doc)
        
        print(f"   ✅ 처리 완료: {len(processed_documents)}개 페이지")
        
        # 첫 번째 페이지 샘플 출력
        if processed_documents:
            sample = processed_documents[0]
            print(f"   📝 샘플 내용: {sample.page_content[:100]}...")
            print(f"   📋 메타데이터: {sample.metadata['document_type']}, {sample.metadata.get('year', 'N/A')}년")
        
        return processed_documents
    
    def process_pdf_directory(self) -> List[Document]:
        """PDF 디렉토리 내 모든 PDF 파일 처리"""
        print("🚀 PDF 디렉토리 처리 시작")
        print("=" * 60)
        print(f"📁 대상 디렉토리: {self.pdf_directory}")
        
        # PDF 파일 찾기
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ PDF 파일을 찾을 수 없습니다.")
            print(f"💡 {self.pdf_directory} 디렉토리에 PDF 파일을 넣어주세요.")
            return []
        
        print(f"📊 발견된 PDF 파일: {len(pdf_files)}개")
        for pdf_file in pdf_files:
            print(f"   - {pdf_file.name}")
        
        all_documents = []
        
        # 각 PDF 파일 처리
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n📖 진행: {i}/{len(pdf_files)}")
            
            documents = self.process_single_pdf(pdf_file)
            all_documents.extend(documents)
            
            print(f"   누적 문서: {len(all_documents)}개")
        
        print(f"\n🎉 PDF 처리 완료! 총 {len(all_documents)}개 문서 생성")
        self.all_documents = all_documents
        return all_documents
    
    def save_to_chroma_db(self, documents: List[Document]) -> Optional[Chroma]:
        """ChromaDB에 저장"""
        print(f"\n💾 PDF ChromaDB에 저장 중... (위치: {self.chroma_db_path})")
        
        if not documents:
            print("❌ 저장할 문서가 없습니다.")
            return None
        
        # 텍스트 분할 (PDF는 일반적으로 긴 텍스트)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # PDF용으로 더 큰 청크
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", "!", "?", " "]
        )
        
        print("   📝 텍스트 분할 중...")
        chunks = text_splitter.split_documents(documents)
        print(f"   ✅ {len(chunks)}개 청크로 분할 완료")
        
        # 임베딩 설정
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key:
            print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
            return None
        
        try:
            embeddings = OpenAIEmbeddings(api_key=openai_api_key)
            print("   ✅ OpenAI 임베딩 준비 완료")
            
            print("   🔄 벡터 데이터베이스 생성 중...")
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=self.chroma_db_path
            )
            
            print(f"   ✅ ChromaDB 저장 완료!")
            print(f"   📁 저장 위치: {os.path.abspath(self.chroma_db_path)}")
            print(f"   📊 저장된 원본 문서: {len(documents)}개")
            print(f"   📊 저장된 청크: {len(chunks)}개")
            
            # 문서 유형별 통계
            type_counts = {}
            for doc in documents:
                doc_type = doc.metadata.get('document_type', 'unknown')
                type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
            
            print(f"   📊 문서 유형별 통계:")
            for doc_type, count in type_counts.items():
                print(f"      {doc_type}: {count}개")
            
            return vectorstore
            
        except Exception as e:
            print(f"   ❌ ChromaDB 저장 실패: {e}")
            return None
    
    def run_pdf_processing(self):
        """전체 PDF 처리 프로세s 실행"""
        print("📄 서원대학교 PDF 문서 처리 및 DB 저장")
        print("=" * 60)
        
        # PDF 처리
        documents = self.process_pdf_directory()
        
        if not documents:
            print("❌ 처리된 PDF 문서가 없습니다.")
            return None
        
        # ChromaDB 저장
        vectorstore = self.save_to_chroma_db(documents)
        
        if vectorstore:
            print("\n🎉 PDF 처리 완료!")
            print(f"📊 최종 통계:")
            print(f"   - 처리된 PDF: {len(set(doc.metadata['filename'] for doc in documents))}개")
            print(f"   - 생성된 문서: {len(documents)}개")
            print(f"   - DB 저장 위치: {self.chroma_db_path}")
            print(f"\n💡 사용법:")
            print(f"   1. config/settings.py에서 DB_MODE 설정")
            print(f"   2. 기존 크롤링 DB와 PDF DB 조합 사용")
        
        return vectorstore

def main():
    """메인 실행 함수"""
    print("📄 서원대학교 PDF 문서 처리 시스템")
    print("=" * 60)
    
    # PDF 처리기 생성
    processor = PDFProcessor(
        pdf_directory="./pdf_documents",
        chroma_db_path="./seowon_pdf_chromadb"
    )
    
    # PDF 처리 실행
    vectorstore = processor.run_pdf_processing()
    
    if vectorstore:
        print("\n✅ PDF 문서 처리가 완료되었습니다!")
        print("이제 이 PDF DB를 RAG 시스템에서 사용할 수 있습니다.")
    else:
        print("\n❌ PDF 처리에 실패했습니다.")

if __name__ == "__main__":
    print("🔧 필요한 패키지:")
    print("pip install langchain-openai langchain-community chromadb python-dotenv")
    print("pip install pypdf2 unstructured pdfminer.six")  # PDF 처리용
    print("\n📁 사용법:")
    print("1. ./pdf_documents/ 폴더에 PDF 파일들 복사")
    print("2. python pdf_processor.py 실행")
    print("\n" + "=" * 60)
    
    main() 