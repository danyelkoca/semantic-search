import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from weaviate.classes.query import Sort

from app.logger_setup import logger
from app.utils import get_product_collection, get_redis_client, rate_limit

router = APIRouter()


@router.get("/best-sellers")
@rate_limit("60/minute")
async def get_best_sellers(request: Request):
    logger.info("Fetching best-sellers")
    try:
        cached = await get_redis_client().get("best_sellers")
        if cached:
            logger.info("Cache hit for best-sellers")
            return {"ok": True, "products": json.loads(cached)}

        async with get_product_collection() as (client, product_collection):
            async with asyncio.timeout(10):
                result = product_collection.query.fetch_objects(
                    limit=200,
                    sort=Sort.by_property(name="rating_number", ascending=False),
                )

            if not result.objects:
                logger.error("No products found while fetching best-sellers")
                return JSONResponse(
                    status_code=404, content={"ok": False, "error": "No products found"}
                )

            top = sorted(
                [obj.properties for obj in result.objects],
                key=lambda x: x.get("average_rating", 0),
                reverse=True,
            )[:12]

            await get_redis_client().setex("best_sellers", 3600, json.dumps(top))
            return {"ok": True, "products": top}
    except Exception as e:
        logger.error(f"Failed to fetch best-sellers: {str(e)}")
        return JSONResponse(
            status_code=500, content={"ok": False, "error": "Internal server error"}
        )
