from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import requests
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CHROMA_DIR = "chroma_db"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi4:14b"

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vectorstore = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embeddings
)

class Question(BaseModel):
    question: str

# Original endpoint
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

# OpenAI compatible endpoints
@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "ghost-rag",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "local"
            }
        ]
    }

@app.post("/v1/chat/completions")
def chat_completions(request: dict):
    messages = request.get("messages", [])
    question = messages[-1].get("content", "") if messages else ""

    results = vectorstore.similarity_search(question, k=5)
    context = "\n\n".join([doc.page_content for doc in results])

    prompt = f"""You are a Ghost CMS expert assistant.
Answer the question using only the provided documentation context.
If the answer is not in the context say so clearly.

Context:
{context}

Question: {question}

Answer:"""

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    })

    answer = response.json()["response"]

    return {
        "id": "ghost-rag-response",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "ghost-rag",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": answer
                },
                "finish_reason": "stop"
            }
        ]
    }

@app.get("/health")
def health():
    return {"status": "ok"}
