"""
개선된 PDF 처리기 - 누락 정보 없이 완전한 전공 정보 추출
- 관대한 페이지 필터링 (10자 이상)
- 작은 청크 사이즈 (500자)로 정보 보존
- 다중 PDF 로더로 추출 성공률 향상
- 전공별 메타데이터 자동 태깅
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
from langchain_chroma import Chroma

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

class ImprovedPDFProcessor:
    """개선된 PDF 처리기 - 전공 정보 누락 방지"""
    
    def __init__(self, pdf_directory: str = "./pdf_documents", 
                 chroma_db_path: str = "./seowon_pdf_chromadb_v2"):
        self.pdf_directory = Path(pdf_directory)
        self.chroma_db_path = chroma_db_path
        self.all_documents = []
        
        # 전공/학과 키워드 패턴 (메타데이터 태깅용)
        self.major_patterns = [
            r'([가-힣]+(?:교육)?과)',  # ~과, ~교육과
            r'([가-힣]+학부)',         # ~학부
            r'([가-힣]+전공)',         # ~전공  
            r'([가-힣]+대학)',         # ~대학
        ]
        
        print("🔧 개선된 PDF 처리기 초기화")
        print(f"📁 PDF 디렉토리: {self.pdf_directory}")
        print(f"💾 ChromaDB 경로: {self.chroma_db_path}")
        
        # 사용 가능한 로더 확인
        available_loaders = []
        if PDF_LOADER_AVAILABLE:
            available_loaders.append("PyPDFLoader")
        if UNSTRUCTURED_AVAILABLE:
            available_loaders.append("UnstructuredPDFLoader")  
        if PDFMINER_AVAILABLE:
            available_loaders.append("PDFMinerLoader")
            
        print(f"🔧 사용 가능한 로더: {', '.join(available_loaders)}")
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정제 (개선된 버전)"""
        if not text:
            return ""
        
        # 기본 정제
        cleaned = text.strip()
        
        # 과도한 공백 제거 (단, 구조 유지)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)  # 3개 이상 개행 → 2개
        cleaned = re.sub(r' {3,}', '  ', cleaned)     # 3개 이상 공백 → 2개
        
        # 특수 문자 정제 (너무 공격적이지 않게)
        cleaned = re.sub(r'[^\w\s가-힣ㄱ-ㅎㅏ-ㅣ.,!?()【】\-\n]', ' ', cleaned)
        
        return cleaned
    
    def _extract_major_info(self, text: str) -> Dict[str, any]:
        """텍스트에서 전공 관련 정보 추출"""
        major_info = {
            'detected_majors': [],
            'has_curriculum': False,
            'has_career_info': False,
            'college_type': 'unknown'
        }
        
        # 전공/학과명 추출
        for pattern in self.major_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) > 2 and match not in major_info['detected_majors']:
                    major_info['detected_majors'].append(match)
        
        # 커리큘럼 정보 포함 여부
        curriculum_keywords = ['1학년', '2학년', '3학년', '4학년', '학기', '교육과정', '수업']
        if any(keyword in text for keyword in curriculum_keywords):
            major_info['has_curriculum'] = True
        
        # 진로 정보 포함 여부
        career_keywords = ['진로', '취업', '직업', '분야', '자격증', '진출']
        if any(keyword in text for keyword in career_keywords):
            major_info['has_career_info'] = True
        
        # 대학 분류
        if '사범대학' in text:
            major_info['college_type'] = '사범대학'
        elif '글로벌공공서비스' in text:
            major_info['college_type'] = '글로벌공공서비스대학'
        elif '바이오헬스' in text:
            major_info['college_type'] = '바이오헬스융합대학'
        elif '문화예술체육' in text:
            major_info['college_type'] = '문화예술체육대학'
        elif '미래대학' in text:
            major_info['college_type'] = '미래대학'
        elif '융복합' in text:
            major_info['college_type'] = '융복합대학'
        
        return major_info
    
    def _load_pdf_with_multiple_loaders(self, file_path: Path) -> List[Document]:
        """다중 로더로 PDF 로드 (성공률 향상)"""
        documents = []
        
        # 모든 로더 시도 및 결과 병합
        loaders_to_try = []
        
        if PDF_LOADER_AVAILABLE:
            loaders_to_try.append(("PyPDFLoader", PyPDFLoader))
        if UNSTRUCTURED_AVAILABLE:
            loaders_to_try.append(("UnstructuredPDFLoader", UnstructuredPDFLoader))
        if PDFMINER_AVAILABLE:
            loaders_to_try.append(("PDFMinerLoader", PDFMinerLoader))
        
        best_result = []
        best_loader = None
        
        for loader_name, loader_class in loaders_to_try:
            try:
                print(f"   🔄 {loader_name} 시도...")
                loader = loader_class(str(file_path))
                docs = loader.load()
                
                if docs and len(docs) > len(best_result):
                    best_result = docs
                    best_loader = loader_name
                    print(f"   ✅ {loader_name}: {len(docs)}개 페이지 추출")
                else:
                    print(f"   ⚠️ {loader_name}: {len(docs) if docs else 0}개 페이지")
                    
            except Exception as e:
                print(f"   ❌ {loader_name} 실패: {e}")
                continue
        
        if best_result:
            print(f"   🏆 최종 선택: {best_loader} ({len(best_result)}개 페이지)")
        
        return best_result
    
    def process_single_pdf(self, file_path: Path) -> List[Document]:
        """단일 PDF 파일 처리 (개선된 버전)"""
        print(f"📄 개선된 PDF 처리: {file_path.name}")
        
        if not file_path.exists():
            print(f"   ❌ 파일이 존재하지 않습니다: {file_path}")
            return []
        
        file_size_mb = file_path.stat().st_size / 1024 / 1024
        print(f"   📊 파일 크기: {file_size_mb:.2f} MB")
        
        # PDF 로드 (다중 로더 시도)
        raw_documents = self._load_pdf_with_multiple_loaders(file_path)
        
        if not raw_documents:
            print(f"   ❌ 모든 로더 실패")
            return []
        
        processed_documents = []
        
        for i, doc in enumerate(raw_documents):
            cleaned_content = self._clean_text(doc.page_content)
            
            # 관대한 필터링 (10자 이상이면 보존)
            if len(cleaned_content) < 10:
                print(f"   ⚠️ 페이지 {i+1}: 내용이 너무 짧음 ({len(cleaned_content)}자) - 제외")
                continue
            
            # 전공 정보 추출
            major_info = self._extract_major_info(cleaned_content)
            
            # 메타데이터 생성 (ChromaDB 호환 형식)
            metadata = {
                'filename': file_path.name,
                'page_number': i + 1,
                'total_pages': len(raw_documents),
                'source': str(file_path),
                'type': 'pdf_document',
                'timestamp': datetime.now().isoformat(),
                'content_length': len(cleaned_content),
                
                # 전공 관련 메타데이터 (ChromaDB 호환)
                'detected_majors': ', '.join(major_info['detected_majors']),  # 리스트 → 문자열
                'detected_majors_count': len(major_info['detected_majors']),  # 개수
                'has_curriculum': major_info['has_curriculum'],
                'has_career_info': major_info['has_career_info'],
                'college_type': major_info['college_type'],
            }
            
            processed_doc = Document(
                page_content=cleaned_content,
                metadata=metadata
            )
            
            processed_documents.append(processed_doc)
            
            # 전공 발견시 로깅
            if major_info['detected_majors']:
                print(f"   🎯 페이지 {i+1}: {', '.join(major_info['detected_majors'])} 발견")
        
        print(f"   ✅ 처리 완료: {len(processed_documents)}개 페이지 (원본: {len(raw_documents)}개)")
        
        return processed_documents
    
    def save_to_chroma_db(self, documents: List[Document]) -> Optional[Chroma]:
        """ChromaDB에 저장 (개선된 청킹)"""
        print(f"\n💾 개선된 ChromaDB 저장... (위치: {self.chroma_db_path})")
        
        if not documents:
            print("❌ 저장할 문서가 없습니다.")
            return None
        
        # 개선된 텍스트 분할 (더 작은 청크로 정보 보존)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,     # 작은 청크로 전공 정보 보존
            chunk_overlap=100,  # 충분한 오버랩
            separators=["\n\n", "\n", ".", "!", "?", ",", " "]  # 더 세밀한 분할
        )
        
        print("   📝 개선된 텍스트 분할 중...")
        chunks = text_splitter.split_documents(documents)
        print(f"   ✅ {len(chunks)}개 청크로 분할 완료")
        
        # 전공별 통계
        major_stats = {}
        for chunk in chunks:
            detected_majors_str = chunk.metadata.get('detected_majors', '')
            if detected_majors_str:  # 비어있지 않은 경우
                majors = [major.strip() for major in detected_majors_str.split(',')]
                for major in majors:
                    if major:  # 빈 문자열이 아닌 경우
                        major_stats[major] = major_stats.get(major, 0) + 1
        
        if major_stats:
            print("   📊 발견된 전공별 청크 수:")
            for major, count in sorted(major_stats.items()):
                print(f"      {major}: {count}개")
        
        # ChromaDB 저장
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
            return None
        
        try:
            embeddings = OpenAIEmbeddings(api_key=openai_api_key)
            
            # 기존 DB 삭제 (완전 재생성)
            if os.path.exists(self.chroma_db_path):
                import shutil
                shutil.rmtree(self.chroma_db_path)
                print(f"   🗑️ 기존 DB 삭제: {self.chroma_db_path}")
            
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=self.chroma_db_path
            )
            
            print(f"   ✅ ChromaDB 저장 완료: {len(chunks)}개 청크")
            
            return vectorstore
            
        except Exception as e:
            print(f"   ❌ ChromaDB 저장 실패: {e}")
            return None
    
    def run_improved_processing(self) -> Optional[Chroma]:
        """개선된 PDF 처리 실행"""
        print("🚀 개선된 PDF 처리 시작")
        print("=" * 80)
        
        # PDF 파일 찾기
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        
        if not pdf_files:
            print("❌ PDF 파일을 찾을 수 없습니다.")
            print(f"💡 {self.pdf_directory} 디렉토리에 PDF 파일을 넣어주세요.")
            return None
        
        print(f"📊 발견된 PDF 파일: {len(pdf_files)}개")
        for pdf_file in pdf_files:
            print(f"   📄 {pdf_file.name}")
        
        all_documents = []
        
        # 각 PDF 파일 처리
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\n📖 진행: {i}/{len(pdf_files)}")
            documents = self.process_single_pdf(pdf_file)
            all_documents.extend(documents)
            print(f"   📊 누적 문서: {len(all_documents)}개")
        
        print(f"\n🎉 PDF 처리 완료! 총 {len(all_documents)}개 문서")
        
        # ChromaDB 저장
        vectorstore = self.save_to_chroma_db(all_documents)
        
        if vectorstore:
            print("\n✅ 개선된 PDF 처리 성공!")
            print(f"💾 저장 위치: {self.chroma_db_path}")
            print("🔍 이제 모든 전공 정보가 검색 가능합니다!")
        
        return vectorstore

def main():
    """개선된 PDF 처리 실행"""
    print("📄 서원대학교 PDF 완전 처리 시스템 v2.0")
    print("=" * 80)
    
    processor = ImprovedPDFProcessor(
        pdf_directory="./pdf_documents",
        chroma_db_path="./seowon_pdf_chromadb_v2"
    )
    
    vectorstore = processor.run_improved_processing()
    
    if vectorstore:
        print("\n🎊 모든 전공 정보 처리 완료!")
        print("🔧 설정에서 새 DB 경로로 변경해주세요:")
        print("   CHROMA_PDF_DB_PATH = './seowon_pdf_chromadb_v2'")
    else:
        print("\n❌ PDF 처리에 실패했습니다.")

if __name__ == "__main__":
    main() 