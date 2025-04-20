import asyncio
import json
from typing import Literal

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.logger_setup import logger
from app.utils import get_product_collection, get_redis_client, rate_limit

# Routes for performing semantic, keyword, or hybrid search queries on fashion products.

router = APIRouter()


@router.get(
    "/search",
    summary="Search Products",
    description="Search products using semantic vector search, keyword-based search, or hybrid "
    "(combined) method based on the query and query_type provided.",
    response_description="Returns a list of products matching the query using selected search method.",
)
@rate_limit("60/minute")
async def search(
    query: str = "",
    query_type: Literal["vector", "hybrid", "keyword"] = "vector",
):
    """
    Search for products based on a query.

    - Supports three query types: 'vector', 'keyword', and 'hybrid'.
    - Results are cached in Redis for faster subsequent lookups.
    - Returns top 24 matching products.
    """
    logger.info(f"Received query: {query}, query_type: {query_type}")

    if not query:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": "Query must be provided."},
        )

    async with get_product_collection() as (client, product_collection):
        try:
            safe_query_key = f"query:{query_type}:{query}"

            # Check if the result is cached in Redis
            cached = await get_redis_client().get(safe_query_key)
            if cached:
                logger.info(f"Cache hit for query: {query} with type: {query_type}")
                return {"ok": True, "products": json.loads(cached)}

            # Perform search based on query_type
            async with asyncio.timeout(10):
                if query_type == "hybrid":
                    result = product_collection.query.hybrid(query=query, limit=24)
                elif query_type == "keyword":
                    result = product_collection.query.bm25(query=query, limit=24)
                else:
                    result = product_collection.query.near_text(query=query, limit=24)

            products = [obj.properties for obj in result.objects]

            # Cache the result for 1 hour
            await get_redis_client().setex(safe_query_key, 3600, json.dumps(products))
            return {"ok": True, "products": products}

        except Exception as e:
            logger.error(f"Failed to fetch products: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"ok": False, "error": "Internal server error"},
            )
