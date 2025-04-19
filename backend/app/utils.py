from contextlib import asynccontextmanager
from typing import Callable

import dotenv
import redis.asyncio as aioredis
import weaviate

# Load environment variables
dotenv.load_dotenv()

# Lazy Redis connection
redis_client = None


def get_redis_client():
    """
    Lazily initializes and returns a Redis client.
    """
    global redis_client
    if redis_client is None:
        redis_client = aioredis.from_url("redis://redis:6379/0", decode_responses=True)
    return redis_client


def get_weaviate_client():
    return weaviate.connect_to_custom(
        http_host="weaviate",
        http_port=8080,
        http_secure=False,
        grpc_host="weaviate",
        grpc_port=50051,
        grpc_secure=False,
    )


@asynccontextmanager
async def get_product_collection():
    client = None
    try:
        client = get_weaviate_client()
        collection = client.collections.get("Product")
        yield client, collection
    finally:
        if client:
            client.close()


def rate_limit(limit_string: str):
    """
    Decorator to attach rate limit information to a function.
    """

    def decorator(func: Callable):
        func.__rate_limit__ = limit_string
        return func

    return decorator
