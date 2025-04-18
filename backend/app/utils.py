import dotenv
import os
import weaviate

# Load environment variables
dotenv.load_dotenv()

# Lazy Redis connection
redis_client = None


def get_redis_client():
    global redis_client
    if redis_client is None:
        import redis.asyncio as aioredis

        redis_client = aioredis.from_url("redis://redis:6379/0", decode_responses=True)
    return redis_client


# Setup Weaviate client
weaviate_client = weaviate.connect_to_custom(
    http_host="weaviate",
    http_port=8080,
    http_secure=False,
    grpc_host="weaviate",
    grpc_port=50051,
    grpc_secure=False,
)

product_collection = weaviate_client.collections.get("Product")
