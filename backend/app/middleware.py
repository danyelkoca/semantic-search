import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler,
)
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.init_db import initialize_database
from app.logger_setup import logger
from app.utils import get_redis_client, get_weaviate_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = get_redis_client()
    try:
        await client.flushdb()
        logger.info("Cache cleared successfully at startup")

        await asyncio.gather(
            asyncio.to_thread(initialize_database),
        )
    except Exception as e:
        logger.error(f"Error clearing Redis cache on startup: {e}")
    yield
    try:
        client = get_weaviate_client()
        yield client
    finally:
        client.close()
        logger.info("Weaviate client closed successfully")


async def log_slow_requests(request: Request, call_next):
    from time import time

    start_time = time()
    response = await call_next(request)
    duration = time() - start_time
    if duration > 1.0:
        logger.warning(
            f"Slow request: {request.method} {request.url} took {duration:.2f}s"
        )
    return response


async def log_error_responses(request: Request, call_next):
    response = await call_next(request)
    if response.status_code >= 500:
        logger.error(
            f"Server error {response.status_code} on {request.method} {request.url}"
        )
    elif response.status_code >= 400:
        logger.warning(
            f"Client error {response.status_code} on {request.method} {request.url}"
        )
    return response


async def custom_http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP Exception: {exc.detail} on {request.url}")
    return await http_exception_handler(request, exc)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()} on {request.url}")
    return await request_validation_exception_handler(request, exc)


async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error: {str(exc)} on {request.url}", exc_info=True)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"ok": False, "error": "Internal server error"},
    )
