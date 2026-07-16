"""
서원대학교 추가 섹션 크롤링 시스템
- 기존 FAQ DB는 유지 (web_chroma_db.py 사용)
- FAQ 외의 추가 섹션들만 크롤링 (공지사항, 입학안내, 학과정보 등)
- 점진적 확장을 위한 별도 DB 생성
"""

import os
import time
import re
import asyncio
from datetime import datetime
from typing import List, Dict
from urllib.parse import urljoin
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from playwright.async_api import async_playwright

load_dotenv()

class AdditionalSectionsCrawler:
    """FAQ 외의 추가 섹션들을 크롤링하는 클래스"""
    
    def __init__(self, base_domain: str = "https://www.seowon.ac.kr", 
                 chroma_db_path: str = "./seowon_additional_chromadb"):
        self.base_domain = base_domain
        self.chroma_db_path = chroma_db_path
        self.all_documents = []
        
        # FAQ 제외한 주요 섹션들
        self.target_sections = {
            "공지사항": {
                "일반공지": "https://www.seowon.ac.kr/seowon/434/subview.do",
                "학사공지": "https://www.seowon.ac.kr/seowon/435/subview.do", 
                "입학공지": "https://www.seowon.ac.kr/seowon/436/subview.do",
            },
            "입학안내": {
                "입학안내": "https://www.seowon.ac.kr/seowon/57/subview.do",
                "전형안내": "https://www.seowon.ac.kr/seowon/58/subview.do",
                "모집요강": "https://www.seowon.ac.kr/seowon/59/subview.do",
            },
            "학생서비스": {
                "장학금안내": "https://www.seowon.ac.kr/seowon/69/subview.do",
                "생활관안내": "https://www.seowon.ac.kr/seowon/70/subview.do",
                "학생회": "https://www.seowon.ac.kr/seowon/71/subview.do",
            }
        }
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정제"""
        if not text:
            return ""
        
        # 여러 공백을 단일 공백으로
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
        text = text.strip()
        
        return text
    
    def _extract_notice_content(self, page_content: str, page_title: str) -> List[Dict]:
        """공지사항 콘텐츠 추출 - 게시글 목록 형태"""
        notices = []
        
        # 공지사항은 보통 테이블 형태로 되어있음
        # 제목, 작성자, 날짜 등이 포함된 행들을 찾아서 추출
        
        lines = page_content.split('\n')
        current_notice = {}
        
        for line in lines:
            line = line.strip()
            if len(line) < 5:
                continue
            
            # 날짜 패턴 감지 (2024-01-01, 2024.01.01 등)
            date_pattern = r'202[3-9][-.]?[0-1]?[0-9][-.]?[0-3]?[0-9]'
            if re.search(date_pattern, line):
                if current_notice and 'title' in current_notice:
                    notices.append(current_notice)
                    current_notice = {}
                current_notice['date'] = line
            
            # 제목으로 보이는 라인 (길이가 적당하고 의미있는 내용)
            elif len(line) > 10 and len(line) < 200:
                # 메뉴나 네비게이션이 아닌 실제 공지 제목
                skip_keywords = ['메뉴', '로그인', '검색', '이전', '다음', '목록', '등록', '수정', '삭제']
                if not any(keyword in line for keyword in skip_keywords):
                    if 'title' not in current_notice:
                        current_notice['title'] = line
                    elif 'content' not in current_notice:
                        current_notice['content'] = line
        
        # 마지막 공지사항 추가
        if current_notice and 'title' in current_notice:
            notices.append(current_notice)
        
        # 공지사항이 제대로 추출되지 않은 경우 전체 텍스트를 의미있는 단위로 분할
        if len(notices) == 0:
            cleaned_text = self._clean_text(page_content)
            if len(cleaned_text) > 100:
                # 문단별로 나누어서 공지사항으로 처리
                paragraphs = [p.strip() for p in cleaned_text.split('.') if len(p.strip()) > 50]
                for i, paragraph in enumerate(paragraphs[:10]):  # 최대 10개
                    notices.append({
                        'title': f"{page_title} - 내용 {i+1}",
                        'content': paragraph,
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
        
        return notices
    
    def _extract_admission_content(self, page_content: str, page_title: str) -> List[Dict]:
        """입학 관련 콘텐츠 추출"""
        admissions = []
        
        # 입학 관련 키워드가 포함된 문단들 추출
        keywords = ['모집', '전형', '지원', '입학', '등록금', '장학금', '일정', '요강', '선발', '전공']
        
        # 텍스트를 문장 단위로 분할
        sentences = re.split(r'[.!?]', page_content)
        
        current_section = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
            
            # 입학 관련 키워드가 포함된 문장들 그룹화
            if any(keyword in sentence for keyword in keywords):
                current_section.append(sentence)
            else:
                # 섹션이 충분히 쌓이면 하나의 입학 정보로 저장
                if len(current_section) >= 2:
                    admissions.append({
                        'title': f"{page_title} - {current_section[0][:50]}...",
                        'content': '. '.join(current_section),
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
                current_section = []
        
        # 마지막 섹션 처리
        if len(current_section) >= 2:
            admissions.append({
                'title': f"{page_title} - {current_section[0][:50]}...",
                'content': '. '.join(current_section),
                'date': datetime.now().strftime('%Y-%m-%d')
            })
        
        # 추출된 내용이 없으면 전체를 하나의 문서로
        if len(admissions) == 0:
            cleaned_text = self._clean_text(page_content)
            if len(cleaned_text) > 100:
                admissions.append({
                    'title': page_title,
                    'content': cleaned_text[:2000],  # 최대 2000자
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
        
        return admissions
    
    def _extract_student_service_content(self, page_content: str, page_title: str) -> List[Dict]:
        """학생 서비스 관련 콘텐츠 추출"""
        services = []
        
        # 학생 서비스 키워드
        keywords = ['장학금', '생활관', '기숙사', '학생회', '동아리', '복지', '지원', '신청', '선발']
        
        # 리스트나 테이블 형태의 정보 추출
        lines = page_content.split('\n')
        current_service = {}
        content_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) < 10:
                continue
            
            # 서비스 관련 키워드가 포함된 라인
            if any(keyword in line for keyword in keywords):
                # 이전 서비스 정보 저장
                if content_lines:
                    services.append({
                        'title': f"{page_title} - {content_lines[0][:50]}...",
                        'content': '\n'.join(content_lines),
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
                    content_lines = []
                
                content_lines.append(line)
            elif content_lines:  # 이미 서비스 관련 내용을 수집 중인 경우
                content_lines.append(line)
                
                # 내용이 충분히 쌓이면 하나의 서비스로 저장
                if len(content_lines) >= 5:
                    services.append({
                        'title': f"{page_title} - {content_lines[0][:50]}...",
                        'content': '\n'.join(content_lines),
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
                    content_lines = []
        
        # 마지막 서비스 정보 저장
        if content_lines:
            services.append({
                'title': f"{page_title} - {content_lines[0][:50]}...",
                'content': '\n'.join(content_lines),
                'date': datetime.now().strftime('%Y-%m-%d')
            })
        
        # 추출된 내용이 없으면 전체를 하나의 문서로
        if len(services) == 0:
            cleaned_text = self._clean_text(page_content)
            if len(cleaned_text) > 100:
                services.append({
                    'title': page_title,
                    'content': cleaned_text[:2000],
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
        
        return services
    
    async def _crawl_section_page(self, section_name: str, page_name: str, url: str) -> List[Document]:
        """개별 섹션 페이지 크롤링"""
        print(f"🔍 크롤링 중: {section_name} > {page_name}")
        print(f"   URL: {url}")
        
        documents = []
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(url, timeout=30000)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)
                
                # 페이지 제목과 내용 추출
                title = await page.title()
                content = await page.inner_text('body')
                
                await browser.close()
                
                if len(content) < 100:
                    print(f"   ⚠️ 콘텐츠가 너무 짧습니다 ({len(content)}자)")
                    return []
                
                # 섹션 타입에 따른 콘텐츠 추출
                extracted_items = []
                
                if "공지사항" in section_name:
                    extracted_items = self._extract_notice_content(content, page_name)
                elif "입학안내" in section_name:
                    extracted_items = self._extract_admission_content(content, page_name)
                elif "학생서비스" in section_name:
                    extracted_items = self._extract_student_service_content(content, page_name)
                else:
                    # 기본 처리
                    cleaned_content = self._clean_text(content)
                    if len(cleaned_content) > 100:
                        extracted_items = [{
                            'title': title,
                            'content': cleaned_content[:2000],
                            'date': datetime.now().strftime('%Y-%m-%d')
                        }]
                
                # Document 객체로 변환
                for item in extracted_items:
                    if item.get('content') and len(item['content']) > 50:
                        doc = Document(
                            page_content=f"제목: {item['title']}\n내용: {item['content']}",
                            metadata={
                                'source': url,
                                'section': section_name,
                                'page_name': page_name,
                                'type': section_name.lower().replace(' ', '_'),
                                'title': item['title'],
                                'date': item.get('date', ''),
                                'timestamp': datetime.now().isoformat()
                            }
                        )
                        documents.append(doc)
                
                print(f"   ✅ {len(documents)}개 문서 추출 완료")
                
                # 첫 번째 문서 샘플 출력
                if documents:
                    sample = documents[0]
                    print(f"   📝 샘플: {sample.metadata['title'][:50]}...")
                
        except Exception as e:
            print(f"   ❌ 크롤링 실패: {e}")
        
        return documents
    
    async def crawl_additional_sections(self) -> List[Document]:
        """추가 섹션들 크롤링"""
        print("🚀 추가 섹션 크롤링 시작 (FAQ 제외)")
        print("=" * 60)
        
        all_documents = []
        
        for section_name, pages in self.target_sections.items():
            print(f"\n📂 섹션: {section_name}")
            print("-" * 40)
            
            for page_name, url in pages.items():
                documents = await self._crawl_section_page(section_name, page_name, url)
                all_documents.extend(documents)
                
                print(f"   누적 문서: {len(all_documents)}개")
                
                # 서버 부하 방지
                await asyncio.sleep(2)
        
        print(f"\n🎉 추가 섹션 크롤링 완료! 총 {len(all_documents)}개 문서 수집")
        self.all_documents = all_documents
        return all_documents
    
    def save_to_chroma_db(self, documents: List[Document]) -> Chroma:
        """Chroma DB에 저장"""
        print(f"\n💾 추가 섹션 Chroma DB에 저장 중... (위치: {self.chroma_db_path})")
        
        if not documents:
            print("❌ 저장할 문서가 없습니다.")
            return None
        
        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=50,
            separators=["\n제목:", "\n내용:", "\n\n", "\n", ".", "?", "!", " "]
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
            
            print(f"   ✅ Chroma DB 저장 완료!")
            print(f"   📁 저장 위치: {os.path.abspath(self.chroma_db_path)}")
            print(f"   📊 저장된 문서: {len(documents)}개")
            print(f"   📊 저장된 청크: {len(chunks)}개")
            
            # 섹션별 통계
            section_counts = {}
            for doc in documents:
                section = doc.metadata.get('section', 'unknown')
                section_counts[section] = section_counts.get(section, 0) + 1
            
            print(f"   📊 섹션별 문서 통계:")
            for section, count in section_counts.items():
                print(f"      {section}: {count}개")
            
            return vectorstore
            
        except Exception as e:
            print(f"   ❌ Chroma DB 저장 실패: {e}")
            return None
    
    async def run_crawling(self):
        """전체 크롤링 프로세스 실행"""
        print("📚 서원대학교 추가 섹션 크롤링 및 DB 저장")
        print("=" * 60)
        
        # 추가 섹션 크롤링
        documents = await self.crawl_additional_sections()
        
        if not documents:
            print("❌ 크롤링된 문서가 없습니다.")
            return None
        
        # Chroma DB 저장
        vectorstore = self.save_to_chroma_db(documents)
        
        if vectorstore:
            print("\n🎉 추가 섹션 크롤링 완료!")
            print(f"📊 최종 통계:")
            print(f"   - 수집된 문서: {len(documents)}개")
            print(f"   - DB 저장 위치: {self.chroma_db_path}")
            print(f"\n💡 사용법:")
            print(f"   1. 기존 FAQ: ./seowon_faq_chromadb")
            print(f"   2. 추가 섹션: ./seowon_additional_chromadb")
            print(f"   3. 두 DB를 합쳐서 사용하거나 선택적 사용 가능")
        
        return vectorstore


async def main():
    """메인 실행 함수"""
    print("📚 서원대학교 추가 섹션 크롤링 시스템")
    print("=" * 60)
    
    # 크롤러 생성
    crawler = AdditionalSectionsCrawler(
        base_domain="https://www.seowon.ac.kr",
        chroma_db_path="./seowon_additional_chromadb"
    )
    
    # 추가 섹션 크롤링 실행
    vectorstore = await crawler.run_crawling()
    
    if vectorstore:
        print("\n✅ 추가 섹션 크롤링이 완료되었습니다!")
        print("이제 기존 FAQ DB와 함께 사용할 수 있습니다.")
    else:
        print("\n❌ 크롤링에 실패했습니다.")


if __name__ == "__main__":
    print("🔧 필요한 패키지:")
    print("pip install langchain-openai langchain-community chromadb playwright python-dotenv")
    print("playwright install chromium")
    print("\n.env 파일에 OPENAI_API_KEY 설정이 필요합니다.")
    print("\n" + "=" * 60)
    
    # 비동기 함수 실행
    asyncio.run(main()) 