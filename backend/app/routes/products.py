import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from weaviate.classes.query import Filter

from app.logger_setup import logger
from app.utils import get_product_collection, get_redis_client, rate_limit

router = APIRouter()


@router.get("/products")
@rate_limit("60/minute")
async def get_products(request: Request, query: str = "", product_id: str = None):
    logger.info(f"Received query: {query}, product_id: {product_id}")
    try:
        product_id = int(product_id) if product_id else None
    except (ValueError, TypeError):
        return JSONResponse(
            status_code=400, content={"ok": False, "error": "Invalid product_id"}
        )

    async with get_product_collection() as (client, product_collection):
        if product_id is not None:
            cached = await get_redis_client().get(f"product_id:{product_id}")
            if cached:
                logger.info(f"Cache hit for product_id: {product_id}")
                return {"ok": True, "product": json.loads(cached)}

            result = product_collection.query.fetch_objects(
                filters=Filter.by_property("product_id").equal(product_id),
                limit=1,
            )
            if result.objects:
                product = result.objects[0].properties
                await get_redis_client().setex(
                    f"product_id:{product_id}", 3600, json.dumps(product)
                )
                return {"ok": True, "product": product}
            else:
                return JSONResponse(
                    status_code=404,
                    content={"ok": False, "error": "Product not found"},
                )

        if query:
            cached = await get_redis_client().get(f"query:{query}")
            if cached:
                logger.info(f"Cache hit for query: {query}")
                return {"ok": True, "products": json.loads(cached)}

            result = product_collection.query.near_text(query=query, limit=20)
            products = [obj.properties for obj in result.objects]
            await get_redis_client().setex(f"query:{query}", 3600, json.dumps(products))
            return {"ok": True, "products": products}

        result = product_collection.query.fetch_objects(limit=20)
        return {"ok": True, "products": [obj.properties for obj in result.objects]}
