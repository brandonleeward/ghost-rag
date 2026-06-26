import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

load_dotenv()

DOCS_DIR = "docs"
CHROMA_DIR = "chroma_db"

def load_documents():
    documents = []
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
                documents.append({
                    "text": text,
                    "source": filename
                })
    print(f"Loaded {len(documents)} documents")
    return documents

def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = []
    metadatas = []
    for doc in documents:
        splits = splitter.split_text(doc["text"])
        chunks.extend(splits)
        metadatas.extend([{"source": doc["source"]}] * len(splits))
    print(f"Created {len(chunks)} chunks")
    return chunks, metadatas

def ingest():
    print("Loading documents...")
    documents = load_documents()
    
    print("Chunking documents...")
    chunks, metadatas = chunk_documents(documents)
    
    print("Creating embeddings and storing in ChromaDB...")
    embeddings = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=CHROMA_DIR
    )
    
    print(f"Done. {len(chunks)} chunks stored in ChromaDB.")

if __name__ == "__main__":
    ingest()
