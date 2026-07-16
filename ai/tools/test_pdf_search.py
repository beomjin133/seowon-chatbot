"""
PDF ChromaDB 테스트 스크립트
AI소프트웨어학과 데이터가 제대로 저장되어 있는지 확인
"""

import sys
import os
sys.path.append('..')

from dotenv import load_dotenv
load_dotenv()

def test_pdf_chromadb():
    print("🔍 PDF ChromaDB 테스트 시작")
    print("=" * 50)
    
    try:
        from langchain_openai import OpenAIEmbeddings
        from langchain_chroma import Chroma
        
        # API 키 확인
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
            return
        
        print("✅ OpenAI API 키 확인됨")
        
        # ChromaDB 로드
        embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        vectorstore = Chroma(
            persist_directory='../seowon_pdf_chromadb',
            embedding_function=embeddings
        )
        
        print("✅ PDF ChromaDB 로드 성공")
        
        # 컬렉션 정보 확인
        try:
            collection = vectorstore._collection
            doc_count = collection.count()
            print(f"📊 저장된 문서 수: {doc_count}개")
        except Exception as e:
            print(f"⚠️ 문서 수 확인 실패: {e}")
        
        # 다양한 검색어로 테스트
        test_queries = [
            "AI소프트웨어학과",
            "AI소프트웨어",
            "소프트웨어학과",
            "빅데이터",
            "정보보안",
            "창의적인 실무형 인재"
        ]
        
        for query in test_queries:
            print(f"\n🔍 검색어: '{query}'")
            try:
                results = vectorstore.similarity_search(query, k=2)
                print(f"   결과: {len(results)}개")
                
                for i, doc in enumerate(results, 1):
                    content_preview = doc.page_content[:200].replace('\n', ' ')
                    print(f"   {i}. {content_preview}...")
                    
                    # 메타데이터 확인
                    if hasattr(doc, 'metadata') and doc.metadata:
                        print(f"      메타데이터: {doc.metadata.get('filename', 'N/A')}")
                        print(f"      문서 타입: {doc.metadata.get('document_type', 'N/A')}")
                        
            except Exception as e:
                print(f"   ❌ 검색 실패: {e}")
        
        print("\n" + "=" * 50)
        print("✅ PDF ChromaDB 테스트 완료")
        
    except Exception as e:
        print(f"❌ 전체 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_chromadb() 