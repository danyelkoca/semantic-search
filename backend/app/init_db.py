import gzip
import json
import logging
import os

import dotenv
import weaviate
from weaviate.classes.config import Configure, DataType
from weaviate.collections.classes.config import Property

from app.logger_setup import logger  # Import your logger cleanly

# Load environment variables
dotenv.load_dotenv()

# Silence noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("weaviate").setLevel(logging.WARNING)
logging.getLogger("grafana").setLevel(logging.WARNING)

ingestion_complete = False


def set_ingestion_complete():
    global ingestion_complete
    ingestion_complete = True


def reset_ingestion_status():
    global ingestion_complete
    ingestion_complete = False


def get_ingestion_status():
    return ingestion_complete


def wait_for_schema_ready(client, retries=30, delay=2):
    import time

    for i in range(retries):
        try:
            client.collections.list_all()
            logger.info("✅ Weaviate schema is available.")
            return
        except weaviate.exceptions.InsufficientPermissionsError:
            logger.warning(f"⏳ Weaviate not ready (attempt {i+1}/{retries})")
            time.sleep(delay)
    raise RuntimeError("❌ Weaviate never became ready.")


def initialize_database():
    client = weaviate.connect_to_custom(
        http_host="weaviate",
        http_port=8080,
        http_secure=False,
        grpc_host="weaviate",
        grpc_port=50051,
        grpc_secure=False,
    )

    wait_for_schema_ready(client)

    # TODO: DELETE THIS LINE AFTER TESTING
    client.collections.delete("Product")
    logger.info("✅ Removed Product collection.")

    if "Product" not in client.collections.list_all():
        collection = client.collections.create(
            name="Product",
            properties=[
                Property(
                    name="product_id",
                    data_type=DataType.INT,
                    module_config={"text2vec-openai": {"skip": True}},
                ),
                Property(
                    name="title",
                    data_type=DataType.TEXT,
                    module_config={"text2vec-openai": {"vectorize": True}},
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
                    module_config={"text2vec-openai": {"skip": True}},
                ),
                Property(
                    name="description",
                    data_type=DataType.TEXT,
                    module_config={"text2vec-openai": {"vectorize": True}},
                ),
                Property(
                    name="price",
                    data_type=DataType.NUMBER,
                    module_config={"text2vec-openai": {"skip": True}},
                ),
                Property(
                    name="store",
                    data_type=DataType.TEXT,
                    module_config={"text2vec-openai": {"skip": True}},
                ),
                Property(
                    name="details",
                    data_type=DataType.TEXT,
                    module_config={"text2vec-openai": {"skip": True}},
                ),
                Property(
                    name="main_hi_res_image",
                    data_type=DataType.TEXT,
                    module_config={"text2vec-openai": {"skip": True}},
                ),
            ],
            vectorizer_config=Configure.Vectorizer.text2vec_openai(
                model="text-embedding-3-small"
            ),
        )
        logger.info("✅ Created 'Product' schema.")
        populate_collection(collection)
    else:
        collection = client.collections.get("Product")
        total_count = collection.aggregate.over_all(total_count=True).total_count
        logger.info(
            f"📦 Found {total_count} products in existing 'Product' collection."
        )
        if total_count == 0:
            logger.info(
                "✅ Found existing 'Product' collection with zero objects; populating."
            )
            populate_collection(collection)
        else:
            logger.info(
                "DB already initialized with existing data; skipping ingestion."
            )
            set_ingestion_complete()

    client.close()
    logger.info("✅ Weaviate client closed.")


def populate_collection(collection):
    local_path = "./data/products.jsonl.gz"
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Dataset file not found at {local_path}")

    logger.info(f"🔍 Reading data from local {local_path}")

    with gzip.open(local_path, "rt", encoding="utf-8") as gz:
        records = [json.loads(line) for line in gz]

    logger.info(f"📦 Found {len(records)} products available for ingestion.")

    batch_size = 50
    batch = []
    inserted_products = 0

    for i, rec in enumerate(records, start=1):
        props = {
            "product_id": i,
            "title": rec.get("title", ""),
            "store": rec.get("store", ""),
            "description": rec.get("description", ""),
            "features": rec.get("features", []),
            "average_rating": float(rec.get("average_rating", -1.0)),
            "rating_number": int(rec.get("rating_number", -1)),
            "price": float(rec.get("price", -1.0)),
            "details": rec.get("details", "{}"),
            "main_hi_res_image": rec.get("main_hi_res_image", ""),
        }
        batch.append(props)

        if len(batch) == batch_size:
            collection.data.insert_many(batch)
            inserted_products += len(batch)
            logger.info(f"✅ Inserted {inserted_products} products so far...")
            batch = []

    if batch:
        collection.data.insert_many(batch)
        inserted_products += len(batch)
        logger.info(f"✅ Inserted {inserted_products} products in total.")

    logger.info(f"✅ Finished ingestion. Total products inserted: {inserted_products}")
    set_ingestion_complete()
