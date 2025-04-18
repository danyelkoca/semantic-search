import json
import logging
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from .utils import get_redis_client, product_collection
from weaviate.classes.query import Filter, Sort

router = APIRouter()
logger = logging.getLogger("semantic-search")

limiter = Limiter(key_func=get_remote_address)


@router.get("/products")
@limiter.limit("60/minute")
async def get_products(request: Request, query: str = "", product_id: str = None):
    logger.info(f"Received query: {query}, product_id: {product_id}")
    try:
        product_id = int(product_id) if product_id else None
    except (ValueError, TypeError):
        return JSONResponse(
            status_code=400, content={"ok": False, "error": "Invalid product_id"}
        )

    if product_id is not None:
        cached = await get_redis_client().get(f"product_id:{product_id}")
        if cached:
            logger.info(f"Cache hit for product_id: {product_id}")
            return {"ok": True, "product": json.loads(cached)}
        try:
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
                    status_code=404, content={"ok": False, "error": "Product not found"}
                )
        except Exception as e:
            logger.error(f"Error fetching product by ID: {e}")
            return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

    if query:
        cached = await get_redis_client().get(f"query:{query}")
        if cached:
            logger.info(f"Cache hit for query: {query}")
            return {"ok": True, "products": json.loads(cached)}
        try:
            result = product_collection.query.bm25(query=query, limit=20)
            products = [obj.properties for obj in result.objects]
            await get_redis_client().setex(f"query:{query}", 3600, json.dumps(products))
            return {"ok": True, "products": products}
        except Exception as e:
            logger.error(f"Error during BM25 search: {e}")
            return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})

    try:
        result = product_collection.query.fetch_objects(limit=20)
        return {"ok": True, "products": [obj.properties for obj in result.objects]}
    except Exception as e:
        logger.error(f"Error fetching default products: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@router.get("/products/popular")
@limiter.limit("10/minute")
async def get_popular_products(request: Request):
    logger.info("Fetching popular products")
    cached = await get_redis_client().get("popular_products")
    if cached:
        logger.info("Cache hit for popular products")
        return {"ok": True, "products": json.loads(cached)}

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
        await get_redis_client().setex("popular_products", 3600, json.dumps(top_20))
        return {"ok": True, "products": top_20}
    except Exception as e:
        logger.error(f"Error fetching popular products: {e}")
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


@router.get("/health")
async def health_check():
    try:
        redis_status = "ok"
        weaviate_status = "ok"
        return {"ok": True, "redis": redis_status, "weaviate": weaviate_status}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(status_code=500, content={"ok": False})
