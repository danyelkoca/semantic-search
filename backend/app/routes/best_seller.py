import json
import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from weaviate.classes.query import Sort

from app.utils import get_redis_client, product_collection, rate_limit

router = APIRouter()
logger = logging.getLogger("semantic-search")


@router.get("/products/best-seller")
@rate_limit("60/minute")
async def get_best_seller_products(request: Request):
    logger.info("Fetching best-seller products")
    cached = await get_redis_client().get("best_seller_products")
    if cached:
        logger.info("Cache hit for best-seller products")
        return {"ok": True, "products": json.loads(cached)}

    try:
        result = product_collection.query.fetch_objects(
            limit=200,
            sort=Sort.by_property(name="sales_volume", ascending=False),
        )
        if not result.objects:
            return {"ok": False, "error": "No products found"}

        top_20 = sorted(
            [obj.properties for obj in result.objects],
            key=lambda x: x.get("sales_volume", 0),
            reverse=True,
        )[:20]
        await get_redis_client().setex("best_seller_products", 3600, json.dumps(top_20))
        return {"ok": True, "products": top_20}
    except Exception as e:
        logger.error(f"Error fetching best-seller products: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})
