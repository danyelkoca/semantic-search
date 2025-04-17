from fastapi import FastAPI, Request
import dotenv
from fastapi.middleware.cors import CORSMiddleware
import weaviate
import os

# Load environment variables from a .env file
dotenv.load_dotenv()

# Connect to Weaviate
weaviate_client = weaviate.connect_to_custom(
    http_host="weaviate",  # docker-compose service name
    http_port=8080,
    http_secure=False,
    grpc_host="weaviate",
    grpc_port=50051,
    grpc_secure=False,
)
product_collection = weaviate_client.collections.get("Product")

# Create FastAPI app with metadata
app = FastAPI(
    title="Semantic Fashion Recommendation System",  # Application title
    description="A semantic search API for fashion recommendations.",  # Application description
    version="1.0.0",  # Application version
)

# Add middleware to handle Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost"]
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define an endpoint to get recommendations
@app.get("/recommendations")
def get_user_query(query: str = ""):
    if not query:
        return {"ok": False, "error": "Query parameter is missing"}

    try:
        results = product_collection.query.near_text(query, limit=5)
        print(results)
        similar_products = [obj.properties for obj in results.objects]
        print(similar_products)
        return {
            "ok": True,
            "user_query": query,
            "results": similar_products,
        }
    except Exception as e:
        return {"ok": False, "error": f"An error occurred: {str(e)}"}


@app.get("/products")
def get_all_products():
    try:
        results = product_collection.query.fetch_objects(limit=20)
        return {"ok": True, "products": [obj.properties for obj in results.objects]}
    except Exception as e:
        return {"ok": False, "error": str(e)}
