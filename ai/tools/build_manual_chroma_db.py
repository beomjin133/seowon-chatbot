import os
from glob import glob
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# ========= 설정 =========
MANUAL_DIR = "./web_documents"
NEW_DB_DIR = "./seowon_web_chromadb"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80
# =======================


def load_manual_files():
    """manual_documents 아래 txt/md 파일을 Document로 로드"""
    paths = glob(os.path.join(MANUAL_DIR, "**/*.*"), recursive=True)
    docs = []

    for p in paths:
        ext = os.path.splitext(p)[1].lower()
        if ext not in [".txt", ".md"]:
            continue

        with open(p, "r", encoding="utf-8") as f:
            text = f.read().strip()

        if not text:
            continue

        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": "web",
                    "filename": os.path.basename(p),
                    "path": p,
                    "type": "Web_note"
                }
            )
        )

    return docs


def build_new_db():
    # 0) 새 DB 폴더가 이미 있으면 삭제(완전 새로 만들기)
    if os.path.exists(NEW_DB_DIR):
        for root, dirs, files in os.walk(NEW_DB_DIR, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(NEW_DB_DIR)

    # 1) 수동 문서 로드
    raw_docs = load_manual_files()
    if not raw_docs:
        print("❌ web_documents에 읽을 파일이 없음")
        return

    # 2) 분할(청크)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(raw_docs)

    # 3) 임베딩/DB 생성 (persist_directory 지정 시 자동 저장됨)
    embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=NEW_DB_DIR
    )

    print("✅ 새 manual ChromaDB 생성 완료")
    print(f"   raw_docs={len(raw_docs)}")
    print(f"   chunks={len(chunks)}")
    print(f"   persist_dir={NEW_DB_DIR}")


if __name__ == "__main__":
    build_new_db()
