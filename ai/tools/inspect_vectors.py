"""
ChromaDB 벡터 데이터 확인 스크립트
- 실제 임베딩 벡터 데이터 조회
- 벡터 차원 및 유사도 확인
- ChromaDB API를 통한 벡터 접근
"""

import os
import numpy as np
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

def safe_check_data(data):
    """데이터 존재 여부를 안전하게 체크"""
    if data is None:
        return False
    
    # 리스트나 튜플인 경우
    if isinstance(data, (list, tuple)):
        return len(data) > 0
    
    # NumPy 배열인 경우
    if hasattr(data, '__len__'):
        try:
            return len(data) > 0
        except:
            return False
    
    # 그 외의 경우
    return bool(data)

def inspect_chroma_vectors(chroma_db_path: str = "./seowon_faq_chromadb"):
    """ChromaDB의 실제 벡터 데이터 검사"""
    
    print("🔍 ChromaDB 벡터 데이터 검사")
    print("=" * 60)
    
    # API 키 확인
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ OPENAI_API_KEY가 없습니다.")
        return
    
    # DB 경로 확인
    if not os.path.exists(chroma_db_path):
        print(f"❌ ChromaDB 경로가 존재하지 않습니다: {chroma_db_path}")
        return
    
    try:
        # ChromaDB 로드
        embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        vectorstore = Chroma(
            persist_directory=chroma_db_path,
            embedding_function=embeddings
        )
        
        print("✅ ChromaDB 연결 성공!")
        
        # 1. 전체 컬렉션 정보
        print("\n1️⃣ 컬렉션 정보")
        print("-" * 40)
        
        # ChromaDB 클라이언트 직접 접근
        collection = vectorstore._collection
        print(f"📊 컬렉션 이름: {collection.name}")
        print(f"📊 총 문서 수: {collection.count()}")
        
        # 2. 샘플 문서와 벡터 확인
        print("\n2️⃣ 샘플 문서 및 벡터 데이터")
        print("-" * 40)
        
        try:
            # 모든 문서 가져오기 (최대 5개)
            results = collection.get(limit=5, include=['embeddings', 'documents', 'metadatas'])
            
            # 안전하게 데이터 확인
            has_documents = safe_check_data(results.get('documents'))
            has_embeddings = safe_check_data(results.get('embeddings'))
            has_ids = safe_check_data(results.get('ids'))
            has_metadatas = safe_check_data(results.get('metadatas'))
            
            print(f"   데이터 확인: 문서={has_documents}, 임베딩={has_embeddings}, ID={has_ids}, 메타데이터={has_metadatas}")
            
            if has_documents and has_embeddings and has_ids:
                docs = results['documents']
                embeddings_data = results['embeddings']
                ids = results['ids']
                metadatas = results.get('metadatas', [])
                
                # 데이터 개수 확인
                doc_count = len(docs) if docs else 0
                emb_count = len(embeddings_data) if embeddings_data else 0
                
                print(f"   총 {doc_count}개 문서, {emb_count}개 임베딩")
                
                # 각 문서 처리
                for i in range(min(doc_count, emb_count, 3)):  # 최대 3개만 표시
                    print(f"\n📄 문서 {i+1}:")
                    
                    # ID
                    if i < len(ids):
                        print(f"   ID: {ids[i]}")
                    
                    # 문서 내용
                    if i < len(docs):
                        doc_content = str(docs[i])[:100] if docs[i] else "내용 없음"
                        print(f"   내용: {doc_content}...")
                    
                    # 메타데이터
                    if i < len(metadatas) and metadatas[i]:
                        print(f"   메타데이터:")
                        metadata = metadatas[i]
                        if isinstance(metadata, dict):
                            for key, value in metadata.items():
                                if value:
                                    value_str = str(value)[:100] if len(str(value)) > 100 else str(value)
                                    print(f"     {key}: {value_str}")
                    
                    # 임베딩 벡터 정보
                    if i < len(embeddings_data) and embeddings_data[i]:
                        try:
                            embedding = embeddings_data[i]
                            if embedding and len(embedding) > 0:
                                print(f"   🧮 벡터 정보:")
                                print(f"     차원: {len(embedding)}차원")
                                print(f"     벡터 타입: {type(embedding)}")
                                print(f"     첫 10개 값: {embedding[:10]}")
                                print(f"     벡터 범위: {min(embedding):.6f} ~ {max(embedding):.6f}")
                                print(f"     벡터 평균: {np.mean(embedding):.6f}")
                                print(f"     벡터 표준편차: {np.std(embedding):.6f}")
                            else:
                                print(f"   🧮 벡터 정보: 빈 벡터")
                        except Exception as e:
                            print(f"   🧮 벡터 정보 처리 중 오류: {e}")
            else:
                print("   데이터를 가져올 수 없습니다.")
                
        except Exception as e:
            print(f"   데이터 가져오기 오류: {e}")
        
        # 3. 유사도 검색 테스트
        print("\n3️⃣ 유사도 검색 테스트")
        print("-" * 40)
        
        try:
            test_query = "장학금"
            print(f"🔍 검색어: '{test_query}'")
            
            # 검색어의 임베딩 벡터 생성
            query_embedding = embeddings.embed_query(test_query)
            print(f"🧮 검색어 벡터 차원: {len(query_embedding)}차원")
            print(f"🧮 검색어 벡터 샘플: {query_embedding[:10]}")
            
            # 유사도 검색 수행
            similar_docs = vectorstore.similarity_search_with_score(test_query, k=3)
            
            print(f"\n📊 유사도 검색 결과 ({len(similar_docs)}개):")
            for i, (doc, score) in enumerate(similar_docs, 1):
                print(f"   결과 {i}:")
                print(f"     유사도 점수: {score:.6f}")
                print(f"     내용: {doc.page_content[:150]}...")
                if hasattr(doc, 'metadata') and doc.metadata:
                    print(f"     소스: {doc.metadata.get('source', 'N/A')}")
                    
        except Exception as e:
            print(f"   유사도 검색 오류: {e}")
        
        # 4. 벡터 통계
        print("\n4️⃣ 전체 벡터 통계")
        print("-" * 40)
        
        try:
            # 모든 임베딩 가져오기 (처음 10개만)
            all_results = collection.get(limit=10, include=['embeddings'])
            
            if safe_check_data(all_results.get('embeddings')):
                embeddings_list = all_results['embeddings']
                print(f"📊 가져온 벡터 수: {len(embeddings_list)}개")
                
                if len(embeddings_list) > 0:
                    # 첫 번째 벡터로 차원 확인
                    first_embedding = embeddings_list[0]
                    if first_embedding and len(first_embedding) > 0:
                        print(f"📊 벡터 차원: {len(first_embedding)}")
                        
                        # 벡터들을 NumPy 배열로 변환
                        all_embeddings = np.array(embeddings_list)
                        print(f"📊 벡터 데이터 형태: {all_embeddings.shape}")
                        
                        # 평균 벡터 크기 계산
                        norms = [np.linalg.norm(emb) for emb in all_embeddings if len(emb) > 0]
                        if norms:
                            print(f"📊 평균 벡터 크기: {np.mean(norms):.6f}")
                        
                        # 코사인 유사도 계산 (안전하게)
                        if len(all_embeddings) > 1:
                            similarities = []
                            base_vector = all_embeddings[0]
                            for i in range(1, min(5, len(all_embeddings))):
                                try:
                                    other_vector = all_embeddings[i]
                                    cos_sim = np.dot(base_vector, other_vector) / (np.linalg.norm(base_vector) * np.linalg.norm(other_vector))
                                    similarities.append(cos_sim)
                                except:
                                    continue
                            
                            if similarities:
                                avg_similarity = np.mean(similarities)
                                print(f"📊 벡터 간 평균 코사인 유사도: {avg_similarity:.6f}")
                        else:
                            print("📊 벡터 간 유사도 계산: 벡터가 1개뿐이라 계산 불가")
                    else:
                        print("📊 첫 번째 벡터가 비어있습니다.")
                else:
                    print("📊 벡터 데이터가 없습니다.")
            else:
                print("📊 임베딩 데이터를 가져올 수 없습니다.")
                
        except Exception as e:
            print(f"   벡터 통계 계산 오류: {e}")
        
        print("\n✅ 벡터 데이터 검사 완료!")
        
    except Exception as e:
        print(f"❌ 벡터 데이터 검사 중 오류: {e}")

def compare_query_with_stored_vectors(chroma_db_path: str = "./seowon_faq_chromadb"):
    """질의와 저장된 벡터들의 유사도 비교"""
    
    print("\n🔍 질의 vs 저장된 벡터 유사도 비교")
    print("=" * 60)
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        return
    
    try:
        embeddings = OpenAIEmbeddings(api_key=openai_api_key)
        vectorstore = Chroma(
            persist_directory=chroma_db_path,
            embedding_function=embeddings
        )
        
        test_queries = ["장학금 신청", "생활관", "학생회비"]
        
        for query in test_queries:
            print(f"\n💬 질의: '{query}'")
            
            try:
                # 질의 벡터 생성
                query_vector = embeddings.embed_query(query)
                print(f"   벡터 차원: {len(query_vector)}")
                
                # 유사한 문서 검색
                results = vectorstore.similarity_search_with_score(query, k=2)
                
                for i, (doc, score) in enumerate(results, 1):
                    print(f"   결과 {i}: 점수={score:.4f}, 내용={doc.page_content[:50]}...")
                    
            except Exception as e:
                print(f"   질의 '{query}' 처리 중 오류: {e}")
    
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    # 벡터 데이터 검사
    inspect_chroma_vectors()
    
    # 질의-벡터 유사도 비교
    compare_query_with_stored_vectors() 