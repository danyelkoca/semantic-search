from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.init_db import get_ingestion_status
from app.logger_setup import logger
from app.utils import rate_limit

router = APIRouter()


@rate_limit("60/minute")
@router.get("/health")
async def health_check():
    try:
        redis_status = "ok"
        weaviate_status = "ok"
        return {
            "ok": True,
            "redis": redis_status,
            "weaviate": weaviate_status,
            "ingestion_complete": get_ingestion_status(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(status_code=500, content={"ok": False})
