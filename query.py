import requests
import json
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

load_dotenv()

CHROMA_DIR = "chroma_db"
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi4:14b"

def load_vectorstore():
    embeddings = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    return Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )

def retrieve_context(vectorstore, question, k=5):
    results = vectorstore.similarity_search(question, k=k)
    context = "\n\n".join([doc.page_content for doc in results])
    sources = list(set([doc.metadata["source"] for doc in results]))
    return context, sources

def ask_ollama(question, context):
    prompt = f"""You are a Ghost CMS expert assistant. 
Answer the question using only the provided documentation context.
If the answer is not in the context, say so clearly.

Context:
{context}

Question: {question}

Answer:"""

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    })
    
    return response.json()["response"]

def query(question):
    print(f"\nQuestion: {question}")
    print("Searching documentation...")
    
    vectorstore = load_vectorstore()
    context, sources = retrieve_context(vectorstore, question)
    
    print(f"Found relevant chunks from: {sources}")
    print("\nGenerating answer...")
    
    answer = ask_ollama(question, context)
    
    print(f"\nAnswer:\n{answer}")
    print(f"\nSources: {sources}")
    
    return answer

if __name__ == "__main__":
    question = input("Ask a Ghost documentation question: ")
    query(question)
