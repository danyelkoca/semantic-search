# Semantic Search Microservice

This microservice enables natural language product search for an e-commerce fashion catalog using semantic search.

## Architecture

- **FastAPI Backend**: API for search and health check
- **Weaviate**: Vector database for semantic search
- **Redis**: Caching layer for frequent queries
- **Docker Compose**: Local development orchestration

## Setup

```bash
git clone https://github.com/danyelkoca/semantic-search.git
cd semantic-search
pip install -r requirements-dev.txt
docker-compose up --build
```

## Usage

Query products:

```bash
curl "http://localhost:8000/products?query=outfit%20for%20beach"
```

Health check:

```bash
curl "http://localhost:8000/health"
```

## Design Choices

| Component | Decision |
|:---|:---|
| Search Engine | Weaviate for fast vector retrieval |
| Framework | FastAPI for lightweight API |
| Cache | Redis for performance boost |

---
