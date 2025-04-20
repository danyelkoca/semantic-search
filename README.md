# Semantic Search 🚀 Deployed on AWS EC2

This microservice enables natural language product search for an e-commerce fashion catalog using semantic search techniques and LLM-based embeddings.

## Overview

Traditionally, users have relied on keyword-based search (e.g., “t-shirt” or “shorts”).
This service enables human-like queries (e.g., “I need an outfit to go to the beach this summer”) using semantic search powered by vector databases and OpenAI embeddings.

The microservice:

- Parses a user’s natural-language query
- Finds relevant products from a provided dataset using semantic search
- Exposes functionality through a clean API endpoint
- Optionally includes a minimal front-end for interaction

## Architecture

![Semantic Search Architecture](docs/architecture.jpeg)

The system includes:

- **Frontend**: SvelteKit with TailwindCSS, served via NGINX
- **Backend**: FastAPI microservice
- **Database**: Weaviate (self-hosted vector DB with OpenAI embedding)
- **Cache**: Redis for performance boost
- **Monitoring**: Prometheus + Grafana
- **Deployment**: Docker Compose managed on AWS EC2, deployed via GitHub Actions
- **Initialization**: `init_db()` at backend startup to populate Weaviate from dataset

## Setup

```bash
git clone https://github.com/danyelkoca/semantic-search.git
cd semantic-search
pip install -r requirements-dev.txt
docker-compose up --build
```

## Demo

You can try the live deployed version here:

👉 [Live Demo](http://ec2-3-25-72-5.ap-southeast-2.compute.amazonaws.com/)

## Sample Usage

Query for relevant products:

```bash
curl "http://localhost:8000/products?query=outfit%20for%20beach"
```

Health check endpoint:

```bash
curl "http://localhost:8000/health"
```

Example frontend interaction:

- User types: _"I want a light outfit for the summer beach"_
- Frontend sends request to backend
- Backend retrieves relevant product recommendations from Weaviate
- Frontend displays results dynamically

## Project Highlights

- ✅ Self-hosted Weaviate: Chosen for enhanced security, full control, and cost-efficiency compared to managed SaaS vector DBs.
- ✅ End-to-end Dockerized architecture deployed on AWS EC2.
- ✅ GitHub Actions CI/CD pipeline for automated testing and deployment.
- ✅ Lightweight, modular backend built with FastAPI.
- ✅ Real-time monitoring with Prometheus scraping and Grafana visualization.

## Key Design Decisions and Trade-offs

| Component         | Decision                                                                                       |
| :---------------- | :--------------------------------------------------------------------------------------------- |
| Vector DB         | Weaviate with OpenAI Embeddings                                                                |
| API Framework     | FastAPI for lightweight async APIs                                                             |
| Frontend          | SvelteKit + TailwindCSS for speed and reactivity                                               |
| Caching           | Redis to speed up common queries                                                               |
| Monitoring        | Prometheus + Grafana for observability                                                         |
| CI/CD             | GitHub Actions for automated deploys                                                           |
| Deployment Target | AWS EC2 (docker-compose managed)                                                               |
| Database Loading  | `init_db()` on backend startup                                                               |
| Trade-off         | Self-hosted Weaviate offers full control but requires more setup compared to managed solutions |

## (Optional) Additional Exploration

- Dataset exploration, embedding experiments, and prompt testing scripts were run separately (not included here).
- Future expansions:
  - Fine-tune retrieval with hybrid search (sparse + dense)
  - Integrate multi-modal search (e.g., text + image)

## Data Cleaning and Preparation (EDA)

This project includes a full preprocessing pipeline for the Amazon Fashion dataset before building the vector database.

### Overview

- Downloaded the dataset (JSONL format) from the McAuley Lab public datasets.
- Loaded it into a pandas DataFrame for analysis.
- Optimized the dataset to stay within GitHub’s 100MB limit.

### Steps and Workflow

- **Initial Setup**: Imported libraries (`pandas`, `matplotlib`, `requests`) and configured the environment.
- **Data Downloading and Loading**: Downloaded and extracted the Amazon Fashion dataset.
- **Exploratory Data Analysis (EDA)**:
  - Inspected structure and missing values.
  - Analyzed distributions of ratings and product categories.
- **Data Cleaning**:
  - Removed irrelevant or null-heavy columns (`bought_together`, `categories`, `videos`).
  - Kept only MAIN HIGH-RES images.
  - Concatenated multi-part descriptions into a single string.
- **Data Optimization**:
  - Converted columns to more memory-efficient data types (`float32`, `int32`, `category`).
  - Dropped 5% of rows randomly to stay within GitHub’s file size limits.
- **Data Export**:
  - Saved the cleaned dataset as a compressed CSV (`products.csv.zip`) under 100MB.

### Main Findings

- Most products lacked price information but included rich features and descriptions.
- Images followed a consistent URL pattern, making them easy to optimize.
- Features and details fields contained highly useful structured metadata.
- Concatenated product descriptions improved usability.

### Results

- Final cleaned dataset contains 784,803 rows and 9 columns.
- File size reduced to under 100MB.
- Ready for ingestion into the Weaviate vector database.

---
