# Ghost RAG Pipeline

A retrieval-augmented generation system for Ghost CMS development 
using local LLMs. Query your entire Ghost stack documentation 
privately with no data leaving your machine.

## What It Does

Scrapes, embeds, and indexes documentation from every component 
of a self-hosted Ghost stack into a local ChromaDB vector database. 
Ask questions in plain English and get grounded answers pulled 
directly from official documentation.

## Tech Stack

- Python 3.11
- LangChain - RAG orchestration
- ChromaDB - vector database
- Sentence Transformers - document embedding
- Ollama - local LLM inference
- FastAPI - API endpoint (in development)

## Corpus Sources

| Source | Pages | Purpose |
|--------|-------|---------|
| Ghost CMS | 190 | Core platform, API, themes |
| Tinybird | 808 | Analytics integration |
| Caddy | 124 | Reverse proxy configuration |
| Docker Compose | 136 | Container orchestration |
| MariaDB | 713 | Database administration |
| ActivityPub | 1 | Federation protocol |
| 12-Factor App | 256 | Architecture principles |
| **Total** | **2,228** | **155,000+ chunks** |

## Setup

```bash
git clone https://github.com/brandonleeward/ghost-rag.git
cd ghost-rag
python3 -m venv venv
source venv/bin/activate
pip install langchain langchain-community langchain-chroma \
  langchain_text_splitters chromadb sentence-transformers \
  requests beautifulsoup4 python-dotenv fastapi uvicorn
cp .env.example .env
# Add your Brave Search API key to .env
```

## Build the Corpus

Scrape each documentation source:

```bash
python scraper.py https://docs.ghost.org
python scraper.py https://www.tinybird.co/docs
python scraper.py https://caddyserver.com/docs
python scraper.py https://docs.docker.com/compose
python scraper.py https://mariadb.com/docs/server/server-usage
python scraper.py https://www.w3.org/TR/activitypub/
python scraper.py https://12factor.net
```

Then ingest into ChromaDB:

```bash
python ingest.py
```

## Usage

```bash
python query.py
```

Ask any question about your Ghost stack:

How do I configure Tinybird analytics with Ghost running behind Caddy?
How do I migrate from Ghost CLI to Docker?
What are the MariaDB configuration options for Ghost?

## Architecture

scraper.py  →  docs/          →  ingest.py  →  chroma_db/

(scrape)       (text corpus)     (embed)        (vector store)

↓

query.py + Ollama

(retrieve + generate)

## Local Model

Runs Phi-4 14B via Ollama for answer generation. Switch models 
by updating the MODEL variable in query.py.

## Author

Brandon Ward - [brandonleeward.com](https://brandonleeward.com)  
GitHub: [github.com/brandonleeward](https://github.com/brandonleeward)
