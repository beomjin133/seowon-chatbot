"""
ChromaDB SQLite 데이터베이스 내용 확인 스크립트
- 테이블 구조 확인
- 저장된 데이터 조회
- 임베딩 정보 확인
"""

import sqlite3
import json
import os
from pathlib import Path

def inspect_chroma_db(db_path: str = "./seowon_faq_chromadb/chroma.sqlite3"):
    """ChromaDB SQLite 파일 내용 검사"""
    
    print("🔍 ChromaDB SQLite 데이터베이스 검사")
    print("=" * 60)
    
    # 파일 존재 확인
    if not os.path.exists(db_path):
        print(f"❌ 데이터베이스 파일이 존재하지 않습니다: {db_path}")
        return
    
    # 파일 크기 확인
    file_size = os.path.getsize(db_path)
    print(f"📁 DB 파일: {db_path}")
    print(f"📊 파일 크기: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
    
    try:
        # SQLite 연결
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n1️⃣ 테이블 목록 조회")
        print("-" * 40)
        
        # 모든 테이블 목록 조회
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"📋 테이블: {table_name}")
            
            # 각 테이블의 행 수 조회
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   행 수: {count:,}개")
        
        print("\n2️⃣ 테이블 구조 상세 조회")
        print("-" * 40)
        
        for table in tables:
            table_name = table[0]
            print(f"\n📋 테이블: {table_name}")
            
            # 테이블 스키마 조회
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("   컬럼 정보:")
            for col in columns:
                col_id, name, data_type, not_null, default, pk = col
                nullable = "NOT NULL" if not_null else "NULL"
                primary = "PRIMARY KEY" if pk else ""
                print(f"     - {name} ({data_type}) {nullable} {primary}")
        
        print("\n3️⃣ 주요 테이블 데이터 샘플 조회")
        print("-" * 40)
        
        # collections 테이블 (컬렉션 정보)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%collection%'")
        collection_tables = cursor.fetchall()
        
        if collection_tables:
            for table in collection_tables:
                table_name = table[0]
                print(f"\n📊 {table_name} 테이블 데이터:")
                
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                
                if rows:
                    # 컬럼명 가져오기
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    for i, row in enumerate(rows, 1):
                        print(f"   행 {i}:")
                        for col_name, value in zip(columns, row):
                            # JSON 형태의 값은 예쁘게 출력
                            if isinstance(value, str) and value.startswith('{'):
                                try:
                                    json_value = json.loads(value)
                                    print(f"     {col_name}: {json.dumps(json_value, indent=2, ensure_ascii=False)[:200]}...")
                                except:
                                    print(f"     {col_name}: {str(value)[:100]}...")
                            else:
                                print(f"     {col_name}: {str(value)[:100]}...")
                else:
                    print("   데이터가 없습니다.")
        
        # embeddings 관련 테이블
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%embedding%'")
        embedding_tables = cursor.fetchall()
        
        if embedding_tables:
            for table in embedding_tables:
                table_name = table[0]
                print(f"\n🧮 {table_name} 테이블 정보:")
                
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"   총 임베딩 수: {count:,}개")
                
                if count > 0:
                    # 첫 번째 임베딩 샘플 확인
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    sample = cursor.fetchone()
                    if sample:
                        print(f"   샘플 데이터 길이: {len(str(sample))} 문자")
        
        # documents 관련 테이블
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%document%'")
        document_tables = cursor.fetchall()
        
        if document_tables:
            for table in document_tables:
                table_name = table[0]
                print(f"\n📄 {table_name} 테이블 데이터:")
                
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"   총 문서 수: {count:,}개")
                
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    rows = cursor.fetchall()
                    
                    # 컬럼명 가져오기
                    cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [col[1] for col in cursor.fetchall()]
                    
                    for i, row in enumerate(rows, 1):
                        print(f"   문서 {i}:")
                        for col_name, value in zip(columns, row):
                            if col_name == 'document' and value:
                                print(f"     {col_name}: {str(value)[:150]}...")
                            elif col_name == 'metadata' and value:
                                try:
                                    metadata = json.loads(value) if isinstance(value, str) else value
                                    print(f"     {col_name}: {json.dumps(metadata, ensure_ascii=False)[:100]}...")
                                except:
                                    print(f"     {col_name}: {str(value)[:100]}...")
                            else:
                                print(f"     {col_name}: {str(value)[:50]}...")
        
        print("\n4️⃣ 데이터베이스 통계")
        print("-" * 40)
        
        # 전체 테이블별 행 수
        total_rows = 0
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_rows += count
            print(f"📊 {table_name}: {count:,}개")
        
        print(f"\n📈 총 데이터 행 수: {total_rows:,}개")
        
        conn.close()
        print("\n✅ 데이터베이스 검사 완료!")
        
    except Exception as e:
        print(f"❌ 데이터베이스 검사 중 오류: {e}")

def search_specific_content(db_path: str = "./seowon_faq_chromadb/chroma.sqlite3", 
                          search_term: str = "장학금"):
    """특정 내용 검색"""
    
    print(f"\n🔍 '{search_term}' 검색 결과")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 모든 테이블에서 검색
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        found_results = []
        
        for table in tables:
            table_name = table[0]
            
            # 테이블 컬럼 정보 조회
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # 문자열 컬럼에서 검색
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                
                if 'TEXT' in col_type.upper() or 'VARCHAR' in col_type.upper():
                    try:
                        query = f"SELECT * FROM {table_name} WHERE {col_name} LIKE '%{search_term}%'"
                        cursor.execute(query)
                        results = cursor.fetchall()
                        
                        if results:
                            found_results.extend([(table_name, col_name, results)])
                            
                    except Exception as e:
                        continue
        
        if found_results:
            for table_name, col_name, results in found_results:
                print(f"\n📋 테이블: {table_name}, 컬럼: {col_name}")
                print(f"   발견된 결과: {len(results)}개")
                
                for i, result in enumerate(results[:3], 1):  # 최대 3개만 표시
                    print(f"   결과 {i}: {str(result)[:200]}...")
        else:
            print(f"'{search_term}'에 대한 검색 결과가 없습니다.")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 검색 중 오류: {e}")

if __name__ == "__main__":
    # 기본 검사
    inspect_chroma_db()
    
    # 특정 내용 검색 예시
    search_specific_content(search_term="장학금")
    search_specific_content(search_term="학생회비") 