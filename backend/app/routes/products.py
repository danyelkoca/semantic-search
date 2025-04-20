import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from weaviate.classes.query import Filter

from app.logger_setup import logger
from app.utils import get_product_collection, get_redis_client, rate_limit

router = APIRouter()


@router.get(
    "/products/{product_id}",
    summary="Get a Product by ID",
    description="Retrieve a single product from the database by its unique product_id."
    "Caches the response for performance.",
    response_description="Returns the product details if found.",
)
@rate_limit("60/minute")
async def get_product_by_id(product_id: int):
    """
    Fetch a product by its ID.

    - First checks Redis for cached result.
    - If not cached, queries Weaviate by filtering on 'product_id'.
    - Returns the matching product or appropriate error if not found.
    """
    logger.info(f"Received product_id lookup: {product_id}")

    if product_id <= 0:
        return JSONResponse(
            status_code=400, content={"ok": False, "error": "Invalid product_id"}
        )

    async with get_product_collection() as (client, product_collection):
        try:
            # Attempt to fetch from Redis cache
            safe_key = f"product_id:{product_id}"
            cached = await get_redis_client().get(safe_key)
            if cached:
                logger.info(f"Cache hit for product_id: {product_id}")
                return {"ok": True, "product": json.loads(cached)}

            # If not in cache, query Weaviate with timeout
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
        except Exception as e:
            logger.error(f"Failed to fetch product: {str(e)}")
            return JSONResponse(
                status_code=500, content={"ok": False, "error": "Internal server error"}
            )
