# Semantic Search Microservice

This repository implements a scalable and modular semantic search microservice for an e-commerce fashion catalog. Built to enable human-like search queries (e.g., "outfit for a beach vacation") rather than traditional keyword-only searches.

---

## Repository

- GitHub: [semantic-search](https://github.com/danyelkoca/semantic-search)

---

## Live Deployment

- **Frontend**: [http://ec2-3-25-72-5.ap-southeast-2.compute.amazonaws.com](http://ec2-3-25-72-5.ap-southeast-2.compute.amazonaws.com/)
- **Backend API (Swagger UI)**: [http://ec2-3-25-72-5.ap-southeast-2.compute.amazonaws.com:8000/docs](http://ec2-3-25-72-5.ap-southeast-2.compute.amazonaws.com:8000/docs)

> **Note:**
> Normally, backend APIs are not exposed publicly for security reasons. However, I have temporarily exposed it to facilitate easy experimentation during evaluation.

---

## Architecture

![Architecture Diagram](docs/architecture.png)

Components:

- **FastAPI**: Python backend API
- **SvelteKit**: Frontend UI
- **Weaviate**: Vector database for semantic search
- **Redis**: Caching layer
- **Docker Compose**: Local orchestration
- **CI/CD**: Automated deployment to AWS EC2

---

## API Endpoints

The microservice offers several endpoints for enhanced functionality:

| Endpoint               | Method | Description                                              |
|------------------------|--------|----------------------------------------------------------|
| `/search`              | GET    | Main endpoint for semantic, hybrid, or keyword search.   |
| `/products/{product_id}` | GET    | Specific product lookup by ID.                           |
| `/metrics`             | GET    | Exposes service metrics (prometheus format).             |
| `/best-sellers`        | GET    | Returns a curated list of best-selling products.         |
| `/trending`            | GET    | Returns a curated list of trending products.             |

### `/search` Endpoint

**Parameters:**
| Name         | Type    | Required | Default  | Description                                                  |
|--------------|---------|----------|----------|--------------------------------------------------------------|
| `query`      | string  | No       | ""       | Search query in natural language.                           |
| `query_type` | string  | No       | "vector" | `"vector"`, `"keyword"`, or `"hybrid"` search types supported.|

**Example:**

```bash
curl -X 'GET' \
  'http://localhost:8000/search?query=outfit%20for%20summer&query_type=hybrid' \
  -H 'accept: application/json'
```

**Response Example (shortened):**
```json
{
  "ok": true,
  "products": [
    {
      "title": "Floerns Women's Two Piece Outfit",
      "price": 38.99,
      "average_rating": 3.7,
      "rating_number": 1502
    },
    ...
  ]
}
```

---

## Search Modes

The system supports three search types:

- **Vector**: Semantic search using embeddings
- **Keyword**: Traditional BM25 keyword search
- **Hybrid**: Combination of vector + keyword scores

The search type is configurable via query parameters.

---

## User Access

- **UI**: Search products visually through SvelteKit frontend
- **Backend API**: Swagger UI available at `/docs` for manual API exploration
- Both are accessible via the public AWS EC2 instance.

---

## Setup (Local)

```bash
git clone https://github.com/danyelkoca/semantic-search.git
cd semantic-search
pip install -r requirements-dev.txt
docker-compose up --build
```

---

## Key Design Decisions

| Component          | Choice           | Reason                            |
| ------------------ | ---------------- | --------------------------------- |
| Search Engine      | Weaviate         | Scalable vector and hybrid search |
| Backend Framework  | FastAPI          | Lightweight and fast              |
| Frontend Framework | SvelteKit        | Modern frontend with SEO support  |
| Cache Layer        | Redis            | Improve search performance        |
| Infrastructure     | Docker + AWS EC2 | Easy deployment and scaling       |

---

## Additional Notes

- Database automatically initializes with top-rated products if needed.
- Robust caching based on query and query type.
- Strict validation and input sanitation.
- Optimized product ingestion with fallback handling.
