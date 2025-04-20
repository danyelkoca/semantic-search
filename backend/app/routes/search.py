import asyncio
import json
from typing import Literal

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.logger_setup import logger
from app.utils import get_product_collection, get_redis_client, rate_limit

router = APIRouter()


@router.get("/search")
@rate_limit("60/minute")
async def search(
    request: Request,
    query: str = "",
    query_type: Literal["vector", "hybrid", "keyword"] = "vector",
):
    logger.info(f"Received query: {query}, query_type: {query_type}")

    if not query:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": "Query must be provided."},
        )

    async with get_product_collection() as (client, product_collection):
        try:
            safe_query_key = f"query:{query_type}:{query}"
            cached = await get_redis_client().get(safe_query_key)
            if cached:
                logger.info(f"Cache hit for query: {query} with type: {query_type}")
                return {"ok": True, "products": json.loads(cached)}

            async with asyncio.timeout(10):
                if query_type == "hybrid":
                    result = product_collection.query.hybrid(query=query, limit=24)
                elif query_type == "keyword":
                    result = product_collection.query.bm25(query=query, limit=24)
                else:
                    result = product_collection.query.near_text(query=query, limit=24)

            products = [obj.properties for obj in result.objects]
            await get_redis_client().setex(safe_query_key, 3600, json.dumps(products))
            return {"ok": True, "products": products}

        except Exception as e:
            logger.error(f"Failed to fetch products: {str(e)}")
            return JSONResponse(
                status_code=500, content={"ok": False, "error": "Internal server error"}
            )
