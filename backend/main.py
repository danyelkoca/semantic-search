from fastapi import FastAPI, Request
import dotenv
from fastapi.middleware.cors import CORSMiddleware
import weaviate
import logging
from weaviate.classes.query import Filter, Sort
import redis
import json
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse
import os

# Lazy Redis client connection
redis_client = None


def get_redis_client():
    global redis_client
    if redis_client is None:
        import redis.asyncio as aioredis

        redis_client = aioredis.from_url("redis://redis:6379/0", decode_responses=True)
    return redis_client


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

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # CLEAR REDIS CACHE ON STARTUP
    client = get_redis_client()
    try:
        await client.flushdb()
        logger.info("Cache cleared successfully at startup")
    except Exception as e:
        logger.error(f"Error clearing Redis cache on startup: {e}")

    yield

    # CLEAN UP
    try:
        weaviate_client.close()
        logger.info("Weaviate client closed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Semantic Fashion Recommendation System",
    description="A semantic search API for fashion recommendations.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware: Restrict to specific origins
# Define the list of allowed origins based on the environment (production or development)
origins = []

# If the environment is production, restrict to the production frontend domain
if os.getenv("ENV", "development") == "production":
    origins = ["https://your-frontend-domain.com"]
else:
    # In development, allow localhost origins for frontend development
    origins = [
        "http://localhost:4173",  # Vite default dev server
        "http://localhost:5173",  # Alternative Vite dev server
    ]

# Add the CORS middleware to the FastAPI app
# This allows cross-origin requests from the specified origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Rate Limiting Middleware
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.get("/products")
## This can be updated later using dynamic rate limiting based on server load
@limiter.limit("60/minute")  # Limit to 60 requests per minute per IP
async def get_products(request: Request, query: str = "", product_id: str = None):
    logger.info(f"Received query: {query}, product_id: {product_id}")

    try:
        product_id = int(product_id) if product_id else None
    except (ValueError, TypeError):
        return JSONResponse(
            status_code=400, content={"ok": False, "error": "Invalid product_id"}
        )

    if product_id is not None:
        # Try cache first
        cached = await get_redis_client().get(f"product_id:{product_id}")
        if cached:
            logger.info(f"Cache hit for product_id: {product_id}")
            return {"ok": True, "product": json.loads(cached)}

        # Otherwise query Weaviate
        try:
            result = product_collection.query.fetch_objects(
                filters=Filter.by_property("product_id").equal(product_id),
                limit=1,
            )

            if result.objects:
                product = result.objects[0].properties

                # Save to Redis for future
                await get_redis_client().setex(
                    f"product_id:{product_id}", 3600, json.dumps(product)
                )  # cache for 1 hour

                return {"ok": True, "product": product}
            else:
                return JSONResponse(
                    status_code=404, content={"ok": False, "error": "Product not found"}
                )
        except Exception as e:
            logger.error(f"Error fetching product by ID: {e}")
            return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

    if query:
        # Try cache first
        cached = await get_redis_client().get(f"query:{query}")
        if cached:
            logger.info(f"Cache hit for query: {query}")
            return {"ok": True, "products": json.loads(cached)}

        # Otherwise query Weaviate
        try:
            result = product_collection.query.bm25(query=query, limit=20)
            products = [obj.properties for obj in result.objects]

            # Save to Redis for future
            await get_redis_client().setex(
                f"query:{query}", 3600, json.dumps(products)
            )  # cache for 1 hour

            return {"ok": True, "products": products}
        except Exception as e:
            logger.error(f"Error during BM25 search: {e}")
            return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

    try:
        result = product_collection.query.fetch_objects(limit=20)
        return {"ok": True, "products": [obj.properties for obj in result.objects]}
    except Exception as e:
        logger.error(f"Error fetching default products: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@app.get("/products/popular")
@limiter.limit("10/minute")
async def get_popular_products(request: Request):
    logger.info("Fetching popular products")

    # Try Redis cache first
    cached = await get_redis_client().get("popular_products")
    if cached:
        logger.info("Cache hit for popular products")
        return {"ok": True, "products": json.loads(cached)}

    try:
        # Fetch top 200 products ordered by rating_number DESCENDING
        result = product_collection.query.fetch_objects(
            limit=200,
            sort=Sort.by_property(name="rating_number", ascending=False),
        )

        if not result.objects:
            return {"ok": False, "error": "No products found"}

        # Now select top 20 with highest average_rating
        top_20 = sorted(
            [obj.properties for obj in result.objects],
            key=lambda x: x.get("average_rating", 0),
            reverse=True,
        )[:20]

        # Cache for 1 hour
        await get_redis_client().setex("popular_products", 3600, json.dumps(top_20))

        return {"ok": True, "products": top_20}

    except Exception as e:
        logger.error(f"Error fetching popular products: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})
