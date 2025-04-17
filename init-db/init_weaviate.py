import os
import dotenv
import gzip
import json

# Load environment variables from .env
dotenv.load_dotenv()

import time
import logging
import weaviate
from weaviate.classes.config import Configure, Property, DataType

logging.basicConfig(level=logging.INFO)

client = weaviate.connect_to_custom(
    http_host="weaviate",  # docker-compose service name
    http_port=8080,
    http_secure=False,
    grpc_host="weaviate",
    grpc_port=50051,
    grpc_secure=False,
)
print("✅ Connected to Weaviate.")


def wait_for_schema_ready(client, retries=30, delay=2):
    for i in range(retries):
        try:
            client.collections.list_all()
            print("✅ Weaviate schema is available.")
            return
        except weaviate.exceptions.InsufficientPermissionsError as e:
            logging.warning(
                f"⏳ Weaviate not ready (leader not elected): attempt {i+1}/{retries}"
            )
            time.sleep(delay)
    raise RuntimeError("❌ Weaviate never became ready to read schema.")


wait_for_schema_ready(client)

# Example logic
print("Creating schema...")

if "Product" not in client.collections.list_all():
    collection = client.collections.create(
        name="Product",
        properties=[
            Property(
                name="title",
                data_type=DataType.TEXT,
                module_config={
                    "text2vec-openai": {
                        "skip": False,
                        "vectorizePropertyName": True,
                    }
                },
            ),
            Property(
                name="average_rating",
                data_type=DataType.NUMBER,
                module_config={"text2vec-openai": {"skip": True}},
            ),
            Property(
                name="rating_number",
                data_type=DataType.INT,
                module_config={"text2vec-openai": {"skip": True}},
            ),
            Property(
                name="features",
                data_type=DataType.TEXT_ARRAY,
                module_config={
                    "text2vec-openai": {
                        "skip": False,
                        "vectorizePropertyName": True,
                    }
                },
            ),
            Property(
                name="description",
                data_type=DataType.TEXT,
                module_config={
                    "text2vec-openai": {
                        "skip": False,
                        "vectorizePropertyName": True,
                    }
                },
            ),
            Property(
                name="price",
                data_type=DataType.NUMBER,
                module_config={"text2vec-openai": {"skip": True}},
            ),
            Property(
                name="store",
                data_type=DataType.TEXT,
                module_config={
                    "text2vec-openai": {
                        "skip": False,
                        "vectorizePropertyName": True,
                    }
                },
            ),
            Property(
                name="details",
                data_type=DataType.TEXT,
                module_config={
                    "text2vec-openai": {
                        "skip": False,
                        "vectorizePropertyName": True,
                    }
                },
            ),
            Property(
                name="main_hi_res_image",
                data_type=DataType.TEXT,
                module_config={"text2vec-openai": {"skip": True}},
            ),
        ],
        vectorizer_config=Configure.Vectorizer.text2vec_openai(),
    )
    logging.info("✅ Created 'Product' schema; beginning line-by-line ingestion.")
    # Stream and ingest records directly from raw JSONL
    RAW_PATH = os.getenv("RAW_PATH", "/data/meta_Amazon_Fashion.jsonl.gz")
    with gzip.open(RAW_PATH, "rt", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            rec = json.loads(line)
            props = {
                "title": rec.get("title", ""),
                "description": (
                    " ".join(rec.get("description", []))
                    if isinstance(rec.get("description"), list)
                    else rec.get("description", "")
                ),
                "average_rating": float(rec.get("average_rating", -1)),
                "rating_number": int(rec.get("rating_number", -1)),
                "features": rec.get("features", []),
                "price": float(rec.get("price", -1)),
                "store": rec.get("store", ""),
                "details": json.dumps(rec.get("details", {})),
                "main_hi_res_image": rec.get("main_hi_res_image", ""),
            }
            collection.data.insert(props)
            if i % 1000 == 0:
                logging.info(f"Ingested {i} products")
    logging.info("✅ Products ingested and DB initialized.")
else:
    collection = client.collections.get("Product")
    logging.info("✅ Found existing 'Product' collection; skipping ingestion.")

if client:
    client.close()
    logging.info("✅ Client connection closed.")
    # Keep the container alive so init-db service remains healthy
    logging.info("Entering idle sleep to maintain service healthy status.")
