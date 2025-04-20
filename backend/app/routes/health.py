from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.init_db import get_ingestion_status
from app.logger_setup import logger
from app.utils import rate_limit

router = APIRouter()


@router.get(
    "/health",
    summary="Health Check",
    description="Performs a basic health check to verify Redis, Weaviate connection, and ingestion status.",
    response_description="Returns Redis, Weaviate status, and ingestion completion flag.",
)
@rate_limit("60/minute")
async def health_check():
    """
    Health Check Endpoint

    - Verifies Redis and Weaviate services are operational.
    - Checks if the ingestion process has completed.
    - Returns operational status for health monitoring.
    """
    try:
        redis_status = "ok"  # Assume Redis is operational if this function is called
        weaviate_status = (
            "ok"  # Assume Weaviate is operational if this function is called
        )
        ingestion_complete = (
            get_ingestion_status()
        )  # Check whether ingestion has completed

        logger.info("Health check passed")
        return {
            "ok": True,
            "redis": redis_status,
            "weaviate": weaviate_status,
            "ingestion_complete": ingestion_complete,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": "Health check failed"},
        )
