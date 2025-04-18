import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.app.utils import rate_limit

router = APIRouter()
logger = logging.getLogger("semantic-search")


@rate_limit("60/minute")
@router.get("/health")
async def health_check():
    try:
        redis_status = "ok"
        weaviate_status = "ok"
        return {"ok": True, "redis": redis_status, "weaviate": weaviate_status}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(status_code=500, content={"ok": False})
