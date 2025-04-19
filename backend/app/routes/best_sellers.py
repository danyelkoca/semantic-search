import json
import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from weaviate.classes.query import Sort

from app.utils import get_product_collection, get_redis_client, rate_limit

router = APIRouter()
logger = logging.getLogger("semantic-search")


@router.get("/best-sellers")
@rate_limit("60/minute")
async def get_best_sellers(request: Request):
    logger.info("Fetching best-sellers")
    cached = await get_redis_client().get("best_sellers")
    if cached:
        logger.info("Cache hit for best-sellers")
        return {"ok": True, "products": json.loads(cached)}

    async with get_product_collection() as (client, product_collection):
        try:
            result = product_collection.query.fetch_objects(
                limit=200,
                sort=Sort.by_property(name="rating_number", ascending=False),
            )
            if not result.objects:
                return {"ok": False, "error": "No products found"}

            top_20 = sorted(
                [obj.properties for obj in result.objects],
                key=lambda x: x.get("average_rating", 0),
                reverse=True,
            )[:20]
            await get_redis_client().setex("best_sellers", 3600, json.dumps(top_20))
            return {"ok": True, "products": top_20}
        except Exception as e:
            logger.error(f"Error fetching best-sellers: {e}")
            return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})
