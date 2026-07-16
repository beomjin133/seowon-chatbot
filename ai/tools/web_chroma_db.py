"""
서원대학교 FAQ 크롤링 및 Chroma DB 저장 전용 코드
- 모든 페이지 (1, 2, 3... 마지막까지) 크롤링 (다음 버튼 지원)
- Chroma DB에 자동 저장
- 중복 제거 및 데이터 정제
"""

import os
import time
import re
import asyncio
from datetime import datetime
from typing import List
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from playwright.async_api import async_playwright

# .env 파일에서 환경 변수 로드
load_dotenv()


class FAQCrawlerToChroma:
    """FAQ 크롤링 및 Chroma DB 저장 전용 클래스"""

    def __init__(self, base_url: str, chroma_db_path: str = "./faq_chroma_db"):
        self.base_url = base_url
        self.chroma_db_path = chroma_db_path
        self.all_documents = []

    def _clean_text(self, text: str) -> str:
        """텍스트 정제 함수"""
        if not text:
            return ""

        # 여러 개의 공백, 탭, 개행을 단일 공백으로 변환
        text = re.sub(r'\s+', ' ', text)

        # 불필요한 문자 제거
        text = text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')

        # 앞뒤 공백 제거
        text = text.strip()

        return text

    def _extract_qa_pairs(self, text: str, page_num: int) -> List[dict]:
        """Q&A 형식의 텍스트에서 질문-답변 쌍 추출"""
        qa_pairs = []

        # Q와 A로 구분된 패턴 찾기
        qa_pattern = r'Q([^A]*?)A(.*?)(?=Q|$)'
        matches = re.findall(qa_pattern, text, re.DOTALL | re.IGNORECASE)

        print(f"   📊 페이지 {page_num}에서 {len(matches)}개의 Q&A 패턴 발견")

        for i, (question, answer) in enumerate(matches):
            question = self._clean_text(question)
            answer = self._clean_text(answer)

            # [ 서비스팀 : 날짜 ] 제거
            answer = re.sub(r'\[\s*[^]]+\s*:\s*[^]]+\s*\]', '', answer).strip()

            if question and answer and len(question) > 5 and len(answer) > 5:
                qa_pairs.append({
                    'question': question,
                    'answer': answer,
                    'page_num': page_num,
                    'index': i
                })
                print(f"      ✅ Q&A {i + 1}: {question[:50]}...")

        return qa_pairs

    def _get_page_url(self, page_num: int) -> str:
        """페이지 번호에 따른 URL 생성"""
        if page_num == 1:
            return self.base_url
        else:
            # URL 패턴에 따라 페이지 번호 추가
            # 일반적으로 &page=2 또는 &pageIndex=2 형태
            if '?' in self.base_url:
                return f"{self.base_url}&page={page_num}"
            else:
                return f"{self.base_url}?page={page_num}"

    async def _crawl_single_page(self, page_num: int) -> List[Document]:
        """단일 페이지 크롤링"""
        page_url = self._get_page_url(page_num)
        print(f"\n📄 페이지 {page_num} 크롤링 시작: {page_url}")

        faq_documents = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                # 페이지 로딩
                await page.goto(page_url, timeout=30000)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)

                # 페이지에 FAQ가 있는지 확인
                page_content = await page.inner_text('body')

                # Q로 시작하는 FAQ가 있는지 확인
                if 'Q' not in page_content or len(page_content) < 100:
                    print(f"   ⚠️ 페이지 {page_num}에 FAQ 내용이 없거나 너무 짧습니다.")
                    await browser.close()
                    return []

                # 다양한 셀렉터로 FAQ 내용 추출
                selectors_to_try = [
                    'table tr',
                    'tbody tr',
                    '.board-list tr',
                    'ul li',
                    'ol li',
                    'div[class*="faq"]',
                    'div[onclick]',
                    '.content div',
                    'article',
                    'section'
                ]

                best_content = ""
                max_items = 0

                for selector in selectors_to_try:
                    try:
                        items = await page.query_selector_all(selector)
                        if len(items) > max_items:
                            max_items = len(items)

                            content_parts = []
                            for item in items:
                                text = await item.text_content()
                                if text and len(text.strip()) > 10:
                                    content_parts.append(text.strip())

                            if content_parts:
                                best_content = "\n".join(content_parts)
                                print(f"   ✅ 최적 셀렉터: {selector} ({len(items)}개 항목)")
                    except:
                        continue

                # 최적 컨텐츠가 없으면 전체 페이지 텍스트 사용
                if not best_content:
                    best_content = page_content

                await browser.close()

                # Q&A 쌍 추출
                qa_pairs = self._extract_qa_pairs(best_content, page_num)

                if qa_pairs:
                    for qa in qa_pairs:
                        content = f"질문: {qa['question']}\n답변: {qa['answer']}"

                        # 답변 길이 확인 (디버깅용)
                        if len(qa['answer']) < 10:
                            print(f"      ⚠️ 짧은 답변 감지: Q={qa['question'][:30]}... A={qa['answer']}")

                        doc = Document(
                            page_content=content,
                            metadata={
                                'source': page_url,
                                'type': 'qa_pair',
                                'question': qa['question'],
                                'answer': qa['answer'],
                                'page_num': page_num,
                                'qa_index': qa['index'],
                                'timestamp': datetime.now().isoformat()
                            }
                        )
                        faq_documents.append(doc)

                print(f"   🎯 페이지 {page_num}에서 {len(faq_documents)}개 Q&A 추출 완료")

                # 첫 번째 Q&A의 내용 샘플 출력 (검증용)
                if faq_documents:
                    sample_doc = faq_documents[0]
                    print(f"   📝 샘플 Q&A 내용:")
                    print(f"      질문: {sample_doc.metadata['question'][:50]}...")
                    print(f"      답변: {sample_doc.metadata['answer'][:100]}...")
                    print(f"      전체 길이: 질문 {len(sample_doc.metadata['question'])}자, 답변 {len(sample_doc.metadata['answer'])}자")

        except Exception as e:
            print(f"   ❌ 페이지 {page_num} 크롤링 오류: {e}")
            return []

        return faq_documents

    async def _detect_last_page_with_navigation(self) -> int:
        """다음 버튼을 통해 모든 페이지를 탐지하여 마지막 페이지 번호 찾기"""
        print("🔍 다음 버튼을 통한 전체 페이지 탐지 중...")

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(self.base_url, timeout=30000)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(3)

                max_page = 1
                current_page = 1

                while True:
                    print(f"   📄 페이지 {current_page} 확인 중...")

                    # 현재 페이지에서 페이지 번호들 확인
                    pagination_selectors = [
                        '.pagination a',
                        '.paging a',
                        '.page-num a',
                        'a[href*="page"]',
                        'a[href*="pageIndex"]',
                        '.boardPaging a',
                        'div[class*="pag"] a',
                        'ul[class*="pag"] a'
                    ]

                    page_numbers = set()

                    for selector in pagination_selectors:
                        try:
                            links = await page.query_selector_all(selector)
                            for link in links:
                                text = await link.text_content()
                                if text and text.strip().isdigit():
                                    page_numbers.add(int(text.strip()))
                        except:
                            continue

                    if page_numbers:
                        current_max = max(page_numbers)
                        max_page = max(max_page, current_max)
                        print(f"      현재 보이는 페이지들: {sorted(page_numbers)}")

                    # 다음 버튼 찾기
                    await asyncio.sleep(1)

                    # 모든 링크 요소 검사하여 다음 버튼 찾기
                    all_links = await page.query_selector_all('a')
                    next_button = None

                    for link in all_links:
                        try:
                            is_visible = await link.is_visible()
                            if not is_visible:
                                continue

                            text = await link.text_content()
                            title = await link.get_attribute('title')
                            onclick = await link.get_attribute('onclick')
                            href = await link.get_attribute('href')

                            # 다음 버튼 판별 조건들
                            conditions = [
                                text and '다음' in text.strip(),
                                text and '>' in text.strip() and len(text.strip()) <= 3,
                                text and '>>' in text.strip(),
                                title and '다음' in title.lower(),
                                title and 'next' in title.lower(),
                                onclick and 'next' in onclick.lower(),
                                href and f'page={current_page + 1}' in href,
                                href and f'pageIndex={current_page + 1}' in href
                            ]

                            if any(conditions):
                                next_button = link
                                print(f"      다음 버튼 발견: 텍스트='{text}', 제목='{title}'")
                                break

                        except:
                            continue

                    # 다음 버튼이 없으면 중단
                    if not next_button:
                        print(f"      다음 버튼을 찾을 수 없습니다. 페이지 탐지 종료.")
                        break

                    # 다음 버튼이 비활성화되어 있는지 확인
                    try:
                        button_class = await next_button.get_attribute('class')
                        parent_class = ""
                        parent = await next_button.query_selector('xpath=..')
                        if parent:
                            parent_class = await parent.get_attribute('class') or ""

                        if (button_class and ('disabled' in button_class.lower() or 'inactive' in button_class.lower())) or \
                           (parent_class and ('disabled' in parent_class.lower() or 'inactive' in parent_class.lower())):
                            print(f"      다음 버튼이 비활성화되어 있습니다.")
                            break
                    except:
                        pass

                    # 다음 버튼 클릭 시도
                    try:
                        print(f"      다음 버튼 클릭 시도 중...")

                        # 버튼이 뷰포트에 보이도록 스크롤
                        await next_button.scroll_into_view_if_needed()
                        await asyncio.sleep(1)

                        # 클릭 시도
                        await next_button.click(timeout=5000)
                        print(f"      다음 버튼 클릭 성공!")

                        # 페이지 로딩 대기
                        await page.wait_for_load_state('networkidle', timeout=10000)
                        await asyncio.sleep(3)
                        current_page += 1

                        # 무한 루프 방지 (최대 50페이지)
                        if current_page > 50:
                            print("      안전을 위해 50페이지에서 탐지를 중단합니다.")
                            break

                    except Exception as e:
                        print(f"      다음 버튼 클릭 실패: {str(e)[:100]}...")

                        # 클릭 실패시 직접 URL 방식으로 시도
                        try:
                            next_url = self._get_page_url(current_page + 1)
                            print(f"      직접 URL로 이동 시도: 페이지 {current_page + 1}")
                            await page.goto(next_url, timeout=30000)
                            await page.wait_for_load_state('networkidle')
                            await asyncio.sleep(2)

                            # 페이지가 실제로 존재하는지 확인
                            page_content = await page.inner_text('body')
                            if 'Q' in page_content and len(page_content) > 100:
                                current_page += 1
                                print(f"      직접 URL 이동 성공!")
                                continue
                            else:
                                print(f"      페이지 {current_page + 1}이 존재하지 않습니다.")
                                break
                        except:
                            print(f"      직접 URL 이동도 실패했습니다.")
                            break

                await browser.close()

        except Exception as e:
            print(f"   ⚠️ 페이지 탐지 실패: {e}")
            max_page = 1

        print(f"   📊 탐지된 최대 페이지: {max_page}")
        return max_page

    async def _detect_last_page(self) -> int:
        """마지막 페이지 번호 자동 감지 (개선된 버전)"""
        print("🔍 마지막 페이지 번호 감지 중...")

        # 먼저 기본 방법으로 시도
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()

                await page.goto(self.base_url, timeout=30000)
                await page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)

                # 페이지네이션 영역에서 마지막 페이지 번호 찾기
                pagination_selectors = [
                    '.pagination a',
                    '.paging a',
                    '.page-num a',
                    'a[href*="page"]',
                    'a[href*="pageIndex"]',
                    '.boardPaging a'
                ]

                max_page = 1

                for selector in pagination_selectors:
                    try:
                        links = await page.query_selector_all(selector)
                        for link in links:
                            text = await link.text_content()
                            if text and text.strip().isdigit():
                                page_num = int(text.strip())
                                max_page = max(max_page, page_num)

                        if max_page > 1:
                            print(f"   ✅ 기본 페이지네이션 감지: {selector}")
                            break
                    except:
                        continue

                await browser.close()

                # 기본 방법으로 찾은 페이지가 10 이하이면 다음 버튼 탐지 방법 사용
                if max_page <= 10:
                    print(f"   🔄 기본 감지 결과({max_page}페이지)가 적어서 다음 버튼 탐지 방법 사용")
                    navigation_max = await self._detect_last_page_with_navigation()
                    max_page = max(max_page, navigation_max)

        except Exception as e:
            print(f"   ⚠️ 기본 페이지 감지 실패: {e}")
            # 기본 방법 실패시 다음 버튼 방법 시도
            max_page = await self._detect_last_page_with_navigation()

        print(f"   📊 최종 감지된 마지막 페이지: {max_page}")
        return max_page

    async def crawl_all_pages(self, max_pages: int = None) -> List[Document]:
        """모든 페이지 크롤링"""
        print("🚀 전체 페이지 크롤링 시작")
        print("=" * 60)

        # 마지막 페이지 자동 감지 (max_pages가 지정되지 않은 경우)
        if max_pages is None:
            max_pages = await self._detect_last_page()

        all_documents = []
        consecutive_empty_pages = 0

        for page_num in range(1, max_pages + 1):
            print(f"\n📖 페이지 {page_num}/{max_pages} 처리 중...")

            page_docs = await self._crawl_single_page(page_num)

            if not page_docs:
                consecutive_empty_pages += 1
                print(f"   ⚠️ 페이지 {page_num}에서 추출된 문서가 없습니다. (연속 빈 페이지: {consecutive_empty_pages})")

                # 연속으로 3페이지가 비어있으면 중단 (실제로 끝에 도달했을 가능성)
                if consecutive_empty_pages >= 3:
                    print(f"   🛑 연속으로 {consecutive_empty_pages}페이지가 비어있어 크롤링을 중단합니다.")
                    break
                continue
            else:
                consecutive_empty_pages = 0  # 문서가 있으면 카운터 리셋

            all_documents.extend(page_docs)
            print(f"   ✅ 페이지 {page_num}: {len(page_docs)}개 문서 추가 (총 {len(all_documents)}개)")

            # 페이지 간 간격 (서버 부하 방지)
            await asyncio.sleep(2)

        print(f"\n🎉 전체 크롤링 완료! 총 {len(all_documents)}개 문서 수집")
        self.all_documents = all_documents
        return all_documents

    def remove_duplicates(self, documents: List[Document]) -> List[Document]:
        """중복 문서 제거"""
        print("\n🔄 중복 문서 제거 중...")

        seen_questions = set()
        unique_documents = []

        for doc in documents:
            question = doc.metadata.get('question', '')

            # 질문을 기준으로 중복 확인
            if question and question not in seen_questions:
                seen_questions.add(question)
                unique_documents.append(doc)
            else:
                print(f"   🗑️ 중복 제거: {question[:50]}...")

        print(f"   ✅ 중복 제거 완료: {len(documents)} → {len(unique_documents)}개")
        return unique_documents

    def save_to_chroma_db(self, documents: List[Document]) -> Chroma:
        """Chroma DB에 저장"""
        print(f"\n💾 Chroma DB에 저장 중... (위치: {self.chroma_db_path})")

        if not documents:
            print("❌ 저장할 문서가 없습니다.")
            return None

        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n질문:", "\n답변:", "\n\n", "\n", ".", "?", "!", " "]
        )

        print("   📝 텍스트 분할 중...")
        chunks = text_splitter.split_documents(documents)
        print(f"   ✅ {len(chunks)}개 청크로 분할 완료")

        # 임베딩 설정
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if not openai_api_key:
            print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
            print("   .env 파일에 OPENAI_API_KEY=your-key-here 를 추가하세요.")
            return None

        try:
            embeddings = OpenAIEmbeddings(api_key=openai_api_key)
            print("   ✅ OpenAI 임베딩 준비 완료")
        except Exception as e:
            print(f"   ❌ OpenAI 임베딩 설정 실패: {e}")
            return None

        # Chroma DB 생성 및 저장
        try:
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

            return vectorstore

        except Exception as e:
            print(f"   ❌ Chroma DB 저장 실패: {e}")
            return None

    async def run_full_crawling(self, max_pages: int = None):
        """전체 크롤링 프로세스 실행"""
        print("🚀 서원대학교 FAQ 전체 크롤링 및 DB 저장 시작")
        print("=" * 60)

        # 1단계: 전체 페이지 크롤링
        all_documents = await self.crawl_all_pages(max_pages)

        if not all_documents:
            print("❌ 크롤링된 문서가 없습니다.")
            return None

        # 2단계: 중복 제거
        unique_documents = self.remove_duplicates(all_documents)

        # 3단계: Chroma DB 저장
        vectorstore = self.save_to_chroma_db(unique_documents)

        if vectorstore:
            print("\n🎉 전체 프로세스 완료!")
            print(f"📊 최종 통계:")
            print(f"   - 크롤링된 총 문서: {len(all_documents)}개")
            print(f"   - 중복 제거 후: {len(unique_documents)}개")
            print(f"   - DB 저장 위치: {self.chroma_db_path}")

        return vectorstore


async def main():
    """메인 실행 함수"""

    # 서원대학교 FAQ 페이지 URL (1페이지)
    base_url = "https://www.seowon.ac.kr/seowon/441/subview.do?enc=Zm5jdDF8QEB8JTJGYmJzJTJGc2Vvd29uJTJGNzAzJTJGYXJ0Y2xMaXN0LmRvJTNGaXNWaWV3TWluZSUzRGZhbHNlJTI2YmJzQ2xTZXElM0QlMjZzcmNoV3JkJTNEJTI2YmJzT3BlbldyZFNlcSUzRCUyNnNyY2hDb2x1bW4lM0RzaiUyNg%3D%3D"

    # Chroma DB 저장 경로
    chroma_db_path = "./seowon_faq_chromadb"

    # 크롤러 생성 및 실행
    crawler = FAQCrawlerToChroma(base_url, chroma_db_path)

    # 전체 크롤링 실행 (max_pages=None이면 자동 감지)
    vectorstore = await crawler.run_full_crawling(max_pages=None)

    if vectorstore:
        print("\n✅ 크롤링 및 DB 저장이 성공적으로 완료되었습니다!")
        print("이제 이 Chroma DB를 RAG 시스템에서 사용할 수 있습니다.")
    else:
        print("\n❌ 크롤링 또는 DB 저장에 실패했습니다.")


if __name__ == "__main__":
    print("🔧 필요한 패키지:")
    print("pip install langchain-openai langchain-community chromadb playwright python-dotenv")
    print("playwright install chromium")
    print("\n.env 파일에 OPENAI_API_KEY 설정이 필요합니다.")
    print("\n" + "=" * 60)

    # 비동기 함수 실행
    asyncio.run(main())