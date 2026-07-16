"""
서원대학교 전체 홈페이지 크롤링 시스템
- FAQ뿐만 아니라 전체 홈페이지 정보 수집
- 다양한 페이지 타입 대응 (공지사항, 학과정보, 입학안내 등)
- 사이트맵 및 네비게이션 기반 크롤링
- 스마트 콘텐츠 추출
"""

import os
import time
import re
import asyncio
from datetime import datetime
from typing import List, Dict, Set
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from playwright.async_api import async_playwright

load_dotenv()

class UniversityFullCrawler:
    """서원대학교 전체 홈페이지 크롤링 클래스"""
    
    def __init__(self, base_domain: str = "https://www.seowon.ac.kr", 
                 chroma_db_path: str = "./seowon_full_chromadb"):
        self.base_domain = base_domain
        self.chroma_db_path = chroma_db_path
        self.visited_urls: Set[str] = set()
        self.all_documents: List[Document] = []
        
        # 크롤링할 주요 섹션 정의
        self.target_sections = {
            "입학안내": [
                "/seowon/57/subview.do",  # 입학안내
                "/seowon/58/subview.do",  # 전형안내
                "/seowon/59/subview.do",  # 모집요강
            ],
            "학사안내": [
                "/seowon/441/subview.do",  # FAQ
                "/seowon/65/subview.do",   # 학사일정
                "/seowon/66/subview.do",   # 학점이수
            ],
            "공지사항": [
                "/seowon/434/subview.do",  # 일반공지
                "/seowon/435/subview.do",  # 학사공지
                "/seowon/436/subview.do",  # 입학공지
            ],
            "학과정보": [
                "/seowon/67/subview.do",   # 학과안내
                "/seowon/68/subview.do",   # 교수진
            ],
            "학생서비스": [
                "/seowon/69/subview.do",   # 장학금
                "/seowon/70/subview.do",   # 생활관
                "/seowon/71/subview.do",   # 학생회
            ]
        }
        
        # 제외할 URL 패턴
        self.exclude_patterns = [
            r'.*\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|rar)$',
            r'.*\/download\/.*',
            r'.*\/file\/.*',
            r'.*javascript:.*',
            r'.*mailto:.*',
            r'.*tel:.*'
        ]
    
    def _should_crawl_url(self, url: str) -> bool:
        """URL이 크롤링 대상인지 확인"""
        if not url or url in self.visited_urls:
            return False
        
        # 도메인 확인
        if not url.startswith(self.base_domain):
            return False
        
        # 제외 패턴 확인
        for pattern in self.exclude_patterns:
            if re.match(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    def _extract_content_by_type(self, page_content: str, url: str) -> Dict:
        """페이지 타입에 따른 콘텐츠 추출"""
        content_info = {
            'type': 'general',
            'title': '',
            'content': '',
            'metadata': {}
        }
        
        # 페이지 타입 감지
        if 'faq' in url.lower() or 'FAQ' in page_content:
            content_info['type'] = 'faq'
            # FAQ Q&A 추출 로직
            qa_pairs = self._extract_qa_pairs(page_content)
            if qa_pairs:
                content_info['qa_pairs'] = qa_pairs
                content_info['content'] = '\n'.join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_pairs])
        
        elif '공지' in url or '공지' in page_content:
            content_info['type'] = 'notice'
            # 공지사항 추출 로직
            content_info['content'] = self._extract_notice_content(page_content)
        
        elif '학과' in url or '전공' in url:
            content_info['type'] = 'department'
            # 학과 정보 추출 로직
            content_info['content'] = self._extract_department_info(page_content)
        
        elif '입학' in url:
            content_info['type'] = 'admission'
            # 입학 정보 추출 로직
            content_info['content'] = self._extract_admission_info(page_content)
        
        else:
            content_info['type'] = 'general'
            # 일반 페이지 콘텐츠 추출
            content_info['content'] = self._clean_general_content(page_content)
        
        return content_info
    
    def _extract_qa_pairs(self, text: str) -> List[Dict]:
        """Q&A 쌍 추출 (기존 로직 재사용)"""
        qa_pairs = []
        qa_pattern = r'Q([^A]*?)A(.*?)(?=Q|$)'
        matches = re.findall(qa_pattern, text, re.DOTALL | re.IGNORECASE)
        
        for i, (question, answer) in enumerate(matches):
            question = self._clean_text(question)
            answer = self._clean_text(answer)
            
            if question and answer and len(question) > 5 and len(answer) > 5:
                qa_pairs.append({
                    'question': question,
                    'answer': answer,
                    'index': i
                })
        
        return qa_pairs
    
    def _extract_notice_content(self, page_content: str) -> str:
        """공지사항 콘텐츠 추출"""
        # 공지사항 제목과 내용 추출
        cleaned = self._clean_text(page_content)
        
        # 불필요한 네비게이션, 메뉴 제거
        lines = cleaned.split('\n')
        content_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 10 and not any(skip in line for skip in ['메뉴', '로그인', '검색', '이전', '다음']):
                content_lines.append(line)
        
        return '\n'.join(content_lines[:50])  # 최대 50줄
    
    def _extract_department_info(self, page_content: str) -> str:
        """학과 정보 추출"""
        cleaned = self._clean_text(page_content)
        
        # 학과 관련 키워드가 포함된 문단 우선 추출
        keywords = ['전공', '교육과정', '졸업', '취업', '교수진', '학과장', '커리큘럼']
        lines = cleaned.split('\n')
        relevant_lines = []
        
        for line in lines:
            if any(keyword in line for keyword in keywords) and len(line) > 20:
                relevant_lines.append(line.strip())
        
        if relevant_lines:
            return '\n'.join(relevant_lines[:30])
        else:
            return cleaned[:2000]  # fallback
    
    def _extract_admission_info(self, page_content: str) -> str:
        """입학 정보 추출"""
        cleaned = self._clean_text(page_content)
        
        # 입학 관련 키워드
        keywords = ['모집', '전형', '지원', '입학', '등록금', '장학금', '일정', '요강']
        lines = cleaned.split('\n')
        relevant_lines = []
        
        for line in lines:
            if any(keyword in line for keyword in keywords) and len(line) > 15:
                relevant_lines.append(line.strip())
        
        if relevant_lines:
            return '\n'.join(relevant_lines[:40])
        else:
            return cleaned[:2000]
    
    def _clean_general_content(self, page_content: str) -> str:
        """일반 페이지 콘텐츠 정제"""
        cleaned = self._clean_text(page_content)
        
        # 의미있는 문단만 추출 (최소 길이 조건)
        lines = cleaned.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 20 and not any(skip in line.lower() for skip in 
                ['copyright', '저작권', 'quick menu', '빠른메뉴', 'sitemap']):
                meaningful_lines.append(line)
        
        return '\n'.join(meaningful_lines[:50])
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정제"""
        if not text:
            return ""
        
        # 여러 공백을 단일 공백으로
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
        text = text.strip()
        
        return text
    
    async def _discover_urls_from_sitemap(self) -> List[str]:
        """사이트맵에서 URL 목록 발견"""
        sitemap_urls = [
            f"{self.base_domain}/sitemap.xml",
            f"{self.base_domain}/sitemap/sitemap.xml",
            f"{self.base_domain}/robots.txt"
        ]
        
        discovered_urls = []
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                for sitemap_url in sitemap_urls:
                    try:
                        await page.goto(sitemap_url, timeout=15000)
                        content = await page.inner_text('body')
                        
                        # XML 사이트맵에서 URL 추출
                        url_pattern = r'<loc>(.*?)</loc>'
                        urls = re.findall(url_pattern, content)
                        
                        for url in urls:
                            if self._should_crawl_url(url):
                                discovered_urls.append(url)
                                
                    except Exception as e:
                        print(f"   사이트맵 {sitemap_url} 처리 실패: {e}")
                        continue
                
                await browser.close()
                
        except Exception as e:
            print(f"사이트맵 크롤링 실패: {e}")
        
        return discovered_urls
    
    async def _discover_urls_from_navigation(self) -> List[str]:
        """네비게이션 메뉴에서 URL 발견"""
        discovered_urls = []
        
        # 미리 정의된 섹션 URL들 추가
        for section_name, urls in self.target_sections.items():
            for url_path in urls:
                full_url = urljoin(self.base_domain, url_path)
                if self._should_crawl_url(full_url):
                    discovered_urls.append(full_url)
        
        # 메인 페이지에서 추가 링크 발견
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(self.base_domain, timeout=30000)
                await page.wait_for_load_state('networkidle')
                
                # 모든 링크 수집
                links = await page.query_selector_all('a[href]')
                
                for link in links:
                    try:
                        href = await link.get_attribute('href')
                        if href:
                            full_url = urljoin(self.base_domain, href)
                            if self._should_crawl_url(full_url):
                                discovered_urls.append(full_url)
                    except:
                        continue
                
                await browser.close()
                
        except Exception as e:
            print(f"네비게이션 크롤링 실패: {e}")
        
        return discovered_urls
    
    async def _crawl_single_url(self, url: str) -> List[Document]:
        """단일 URL 크롤링"""
        if url in self.visited_urls:
            return []
        
        self.visited_urls.add(url)
        print(f"🔍 크롤링 중: {url}")
        
        documents = []
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(url, timeout=30000)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)
                
                # 페이지 제목
                title = await page.title()
                
                # 페이지 콘텐츠
                content = await page.inner_text('body')
                
                await browser.close()
                
                # 콘텐츠가 충분히 있는 경우만 처리
                if len(content) > 100:
                    content_info = self._extract_content_by_type(content, url)
                    
                    if content_info['content']:
                        # 페이지 타입별로 문서 생성
                        if content_info['type'] == 'faq' and 'qa_pairs' in content_info:
                            # FAQ의 경우 각 Q&A를 별도 문서로
                            for qa in content_info['qa_pairs']:
                                doc = Document(
                                    page_content=f"질문: {qa['question']}\n답변: {qa['answer']}",
                                    metadata={
                                        'source': url,
                                        'type': 'faq',
                                        'title': title,
                                        'question': qa['question'],
                                        'answer': qa['answer'],
                                        'timestamp': datetime.now().isoformat()
                                    }
                                )
                                documents.append(doc)
                        else:
                            # 일반 페이지는 통째로 하나의 문서
                            doc = Document(
                                page_content=content_info['content'],
                                metadata={
                                    'source': url,
                                    'type': content_info['type'],
                                    'title': title,
                                    'timestamp': datetime.now().isoformat()
                                }
                            )
                            documents.append(doc)
        
        except Exception as e:
            print(f"   ❌ 크롤링 실패: {e}")
        
        print(f"   ✅ {len(documents)}개 문서 추출")
        return documents
    
    async def crawl_full_website(self, max_urls: int = 100) -> List[Document]:
        """전체 웹사이트 크롤링"""
        print("🚀 서원대학교 전체 홈페이지 크롤링 시작")
        print("=" * 60)
        
        # 1단계: URL 발견
        print("\n1️⃣ 크롤링 대상 URL 발견 중...")
        
        sitemap_urls = await self._discover_urls_from_sitemap()
        nav_urls = await self._discover_urls_from_navigation()
        
        all_urls = list(set(sitemap_urls + nav_urls))[:max_urls]
        
        print(f"   📊 발견된 URL: {len(all_urls)}개")
        print(f"   🎯 크롤링 예정: {min(len(all_urls), max_urls)}개")
        
        # 2단계: 각 URL 크롤링
        print(f"\n2️⃣ URL별 콘텐츠 크롤링 중...")
        
        all_documents = []
        
        for i, url in enumerate(all_urls[:max_urls], 1):
            print(f"\n📖 진행: {i}/{min(len(all_urls), max_urls)}")
            
            documents = await self._crawl_single_url(url)
            all_documents.extend(documents)
            
            print(f"   누적 문서: {len(all_documents)}개")
            
            # 서버 부하 방지
            await asyncio.sleep(1)
        
        print(f"\n🎉 크롤링 완료! 총 {len(all_documents)}개 문서 수집")
        self.all_documents = all_documents
        return all_documents
    
    def save_to_chroma_db(self, documents: List[Document]) -> Chroma:
        """Chroma DB에 저장 (기존 로직과 동일)"""
        print(f"\n💾 Chroma DB에 저장 중... (위치: {self.chroma_db_path})")
        
        if not documents:
            print("❌ 저장할 문서가 없습니다.")
            return None
        
        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,  # 더 큰 청크 크기 (다양한 콘텐츠 타입)
            chunk_overlap=100,
            separators=["\n\n질문:", "\n\n", "\n", ".", "?", "!", " "]
        )
        
        print("   📝 텍스트 분할 중...")
        chunks = text_splitter.split_documents(documents)
        print(f"   ✅ {len(chunks)}개 청크로 분할 완료")
        
        # 임베딩 및 저장
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
            
            # 문서 타입별 통계
            type_counts = {}
            for doc in documents:
                doc_type = doc.metadata.get('type', 'unknown')
                type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
            
            print(f"   📊 문서 타입별 통계:")
            for doc_type, count in type_counts.items():
                print(f"      {doc_type}: {count}개")
            
            return vectorstore
            
        except Exception as e:
            print(f"   ❌ Chroma DB 저장 실패: {e}")
            return None
    
    async def run_full_crawling(self, max_urls: int = 100):
        """전체 크롤링 프로세스 실행"""
        print("🌐 서원대학교 전체 홈페이지 크롤링 및 DB 저장")
        print("=" * 60)
        
        # 전체 크롤링
        documents = await self.crawl_full_website(max_urls)
        
        if not documents:
            print("❌ 크롤링된 문서가 없습니다.")
            return None
        
        # Chroma DB 저장
        vectorstore = self.save_to_chroma_db(documents)
        
        if vectorstore:
            print("\n🎉 전체 프로세스 완료!")
            print(f"📊 최종 통계:")
            print(f"   - 크롤링된 URL: {len(self.visited_urls)}개")
            print(f"   - 수집된 문서: {len(documents)}개")
            print(f"   - DB 저장 위치: {self.chroma_db_path}")
        
        return vectorstore


async def main():
    """메인 실행 함수"""
    print("🌐 서원대학교 전체 홈페이지 크롤링 시스템")
    print("=" * 60)
    
    # 크롤러 생성
    crawler = UniversityFullCrawler(
        base_domain="https://www.seowon.ac.kr",
        chroma_db_path="./seowon_full_chromadb"
    )
    
    # 전체 크롤링 실행 (최대 50개 URL)
    vectorstore = await crawler.run_full_crawling(max_urls=50)
    
    if vectorstore:
        print("\n✅ 전체 홈페이지 크롤링이 완료되었습니다!")
        print("이제 이 확장된 Chroma DB를 RAG 시스템에서 사용할 수 있습니다.")
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