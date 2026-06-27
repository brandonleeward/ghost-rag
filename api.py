from fastapi import FastAPI
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
import requests

app = FastAPI()

CHROMA_DIR = "chroma_db"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi4:14b"

embeddings = SentenceTransformerEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embeddings
)

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask(q: Question):
    results = vectorstore.similarity_search(q.question, k=5)
    context = "\n\n".join([doc.page_content for doc in results])
    sources = list(set([doc.metadata["source"] for doc in results]))

    prompt = f"""You are a Ghost CMS expert assistant.
Answer the question using only the provided documentation context.
If the answer is not in the context say so clearly.

Context:
{context}

Question: {q.question}

Answer:"""

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    })

    return {
        "answer": response.json()["response"],
        "sources": sources
    }

@app.get("/health")
def health():
    return {"status": "ok"}
