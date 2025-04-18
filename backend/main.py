from fastapi import FastAPI, Request
import dotenv
from fastapi.middleware.cors import CORSMiddleware
import weaviate
import os
import logging
from weaviate.classes.query import Filter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv()

# Connect to Weaviate
weaviate_client = weaviate.connect_to_custom(
    http_host="weaviate",
    http_port=8080,
    http_secure=False,
    grpc_host="weaviate",
    grpc_port=50051,
    grpc_secure=False,
)

product_collection = weaviate_client.collections.get("Product")

app = FastAPI(
    title="Semantic Fashion Recommendation System",
    description="A semantic search API for fashion recommendations.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/products")
def get_products(query: str = "", product_id: str = None):
    logger.info(f"Received query: {query}, product_id: {product_id}")
    product_id = int(product_id) if product_id else None

    if product_id:
        try:
            result = product_collection.query.fetch_objects(
                filters=Filter.by_property("product_id").equal(product_id),
                limit=1,
            )

            if result.objects:
                return {"ok": True, "product": result.objects[0].properties}
            else:
                return {"ok": False, "error": "Product not found"}
        except Exception as e:
            logger.error(f"Error fetching product by ID: {e}")
            return {"ok": False, "error": str(e)}

    if query:
        try:
            result = product_collection.query.bm25(query=query, limit=20)
            return {"ok": True, "products": [obj.properties for obj in result.objects]}
        except Exception as e:
            logger.error(f"Error during BM25 search: {e}")
            return {"ok": False, "error": str(e)}
    else:
        try:
            result = product_collection.query.fetch_objects(limit=20)
            return {"ok": True, "products": [obj.properties for obj in result.objects]}
        except Exception as e:
            logger.error(f"Error fetching default products: {e}")
            return {"ok": False, "error": str(e)}
