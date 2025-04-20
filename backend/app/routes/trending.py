import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from weaviate.classes.query import Sort

from app.logger_setup import logger
from app.utils import get_product_collection, get_redis_client, rate_limit

router = APIRouter()


@router.get("/trending")
@rate_limit("60/minute")
async def get_trending(request: Request):
    logger.info("Fetching trending products")
    try:
        cached = await get_redis_client().get("trending_products")
        if cached:
            logger.info("Cache hit for trending products")
            return {"ok": True, "products": json.loads(cached)}

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

            top = sorted(
                (obj.properties for obj in result.objects),
                key=lambda x: x.get("rating_number", 0),
                reverse=True,
            )[:12]

            await get_redis_client().setex("trending_products", 3600, json.dumps(top))
            return {"ok": True, "products": top}
    except Exception as e:
        logger.error(f"Failed to fetch trending products: {str(e)}")
        return JSONResponse(
            status_code=500, content={"ok": False, "error": "Internal server error"}
        )
