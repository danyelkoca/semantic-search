import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from weaviate.classes.query import Sort

from app.logger_setup import logger
from app.utils import get_product_collection, get_redis_client, rate_limit

router = APIRouter()


@router.get(
    "/trending",
    summary="Get Trending Products",
    description="Fetches a curated list of trending products based on high ratings and review counts. "
    "Results are cached for performance.",
    response_description="Returns a list of trending products.",
)
@rate_limit("60/minute")
async def get_trending():
    """
    Fetch trending products based on rating and popularity.

    - Prioritizes high average ratings and number of reviews.
    - Caches results in Redis for 1 hour.
    - Returns top 12 trending products.
    """
    logger.info("Fetching trending products")
    try:
        # Check Redis cache first
        cached = await get_redis_client().get("trending_products")
        if cached:
            logger.info("Cache hit for trending products")
            return {"ok": True, "products": json.loads(cached)}

        # Fetch from Weaviate if not cached
        async with get_product_collection() as (client, product_collection):
            async with asyncio.timeout(10):
                result = product_collection.query.fetch_objects(
                    limit=200,
                    sort=Sort.by_property(name="average_rating", ascending=False),
                )

            if not result.objects:
                logger.error("No trending products found")
                return JSONResponse(
                    status_code=404,
                    content={"ok": False, "error": "No trending products found"},
                )

            # Sort by number of ratings and take top 12 products
            top = sorted(
                (obj.properties for obj in result.objects),
                key=lambda x: x.get("rating_number", 0),
                reverse=True,
            )[:12]

            # Cache the result
            await get_redis_client().setex("trending_products", 3600, json.dumps(top))
            return {"ok": True, "products": top}
    except Exception as e:
        logger.error(f"Failed to fetch trending products: {str(e)}")
        return JSONResponse(
            status_code=500, content={"ok": False, "error": "Internal server error"}
        )
