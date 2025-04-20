import asyncio
import json
from typing import Literal

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from weaviate.classes.query import Filter

from app.logger_setup import logger
from app.utils import get_product_collection, get_redis_client, rate_limit

router = APIRouter()


@router.get("/products")
@rate_limit("60/minute")
async def get_products(
    request: Request,
    query: str = "",
    product_id: str = None,
    query_type: Literal["vector", "hybrid", "keyword"] = "vector",
):
    logger.info(
        f"Received query: {query}, product_id: {product_id}, query_type: {query_type}"
    )
    if not query and product_id is None:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": "Query or product_id must be provided."},
        )
    try:
        product_id = int(product_id) if product_id else None
        if product_id is not None and product_id <= 0:
            raise ValueError
    except (ValueError, TypeError):
        logger.error(f"Invalid product_id received: {product_id}")
        return JSONResponse(
            status_code=400, content={"ok": False, "error": "Invalid product_id"}
        )

    async with get_product_collection() as (client, product_collection):
        try:
            if product_id is not None:
                safe_key = f"product_id:{str(product_id)}"
                cached = await get_redis_client().get(safe_key)
                if cached:
                    logger.info(f"Cache hit for product_id: {product_id}")
                    return {"ok": True, "product": json.loads(cached)}

                async with asyncio.timeout(10):
                    result = product_collection.query.fetch_objects(
                        filters=Filter.by_property("product_id").equal(product_id),
                        limit=1,
                    )

                if result.objects:
                    product = result.objects[0].properties
                    await get_redis_client().setex(safe_key, 3600, json.dumps(product))
                    return {"ok": True, "product": product}
                else:
                    return JSONResponse(
                        status_code=404,
                        content={"ok": False, "error": "Product not found"},
                    )

            if query:
                safe_query_key = f"query:{query_type}:{query}"
                cached = await get_redis_client().get(safe_query_key)
                if cached:
                    logger.info(f"Cache hit for query: {query}")
                    return {"ok": True, "products": json.loads(cached)}

                async with asyncio.timeout(10):
                    if query_type == "hybrid":
                        result = product_collection.query.hybrid(query=query, limit=24)
                    elif query_type == "keyword":
                        result = product_collection.query.bm25(query=query, limit=24)
                    else:
                        result = product_collection.query.near_text(
                            query=query, limit=24
                        )

                products = [obj.properties for obj in result.objects]
                await get_redis_client().setex(
                    safe_query_key, 3600, json.dumps(products)
                )
                return {"ok": True, "products": products}

            # No fallback: either 'query' or 'product_id' must be provided.
        except Exception as e:
            logger.error(f"Failed to fetch products: {str(e)}")
            return JSONResponse(
                status_code=500, content={"ok": False, "error": "Internal server error"}
            )
