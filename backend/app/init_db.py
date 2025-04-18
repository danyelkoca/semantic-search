import gzip
import json
import logging
import os

import dotenv
import requests
import weaviate
from weaviate.classes.config import Configure, DataType, Property

from app.logger_setup import logger  # Import your logger cleanly

# Load environment variables
dotenv.load_dotenv()

# Silence noisy libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("weaviate").setLevel(logging.WARNING)

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

    force_initialize = os.getenv("FORCE_INITIALIZE_DB", "false").lower() == "true"

    if force_initialize and "Product" in client.collections.list_all():
        client.collections.delete("Product")
        logger.info(
            "✅ Deleted 'Product' collection as requested by FORCE_INITIALIZE_DB"
        )

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
        if collection.aggregate.over_all(total_count=True).total_count == 0:
            logger.info(
                "✅ Found existing 'Product' collection with zero objects; populating."
            )
            populate_collection(collection)
        else:
            logger.info("DB already initialized; skipping ingestion.")
            set_ingestion_complete()

    client.close()
    logger.info("✅ Weaviate client closed.")


def populate_collection(collection):
    raw_url = os.getenv("RAW_URL")
    if not raw_url:
        raise ValueError("RAW_URL is not set in environment variables.")

    no_of_products = os.getenv("NO_OF_PRODUCTS")
    no_of_products = int(no_of_products) if no_of_products else None

    logger.info(f"🔗 Starting download and ingestion from {raw_url}")

    resp = requests.get(raw_url, stream=True)
    resp.raise_for_status()
    logger.info("✅ Successfully downloaded and opened raw gzip file.")

    if no_of_products:
        logger.info(f"🔢 Will ingest up to {no_of_products} products as configured.")
    else:
        logger.info("🔢 Will ingest all available products.")

    # Full download is necessary to read the lines, but ingestion is limited by no_of_products
    inserted_products = 0
    batch = []
    with gzip.GzipFile(fileobj=resp.raw) as gz:
        for i, line in enumerate(gz, start=1):
            if no_of_products is not None and i > no_of_products:
                break
            rec = json.loads(line.decode("utf-8"))

            props = {
                "product_id": i,
                "title": rec.get("title", ""),
                "store": rec.get("store", ""),
                "description": (
                    " ".join(rec["description"])
                    if isinstance(rec.get("description", []), list)
                    else rec.get("description", "")
                ),
                "features": rec.get("features", []),
                "average_rating": (
                    float(rec.get("average_rating"))
                    if rec.get("average_rating") is not None
                    else -1.0
                ),
                "rating_number": (
                    int(rec.get("rating_number"))
                    if rec.get("rating_number") is not None
                    else -1
                ),
                "price": (
                    float(rec.get("price")) if rec.get("price") is not None else -1.0
                ),
                "details": json.dumps(rec.get("details", {})),
                "main_hi_res_image": (
                    next(
                        (
                            (img.get("hi_res") or "").replace(
                                "https://m.media-amazon.com/images/I/", ""
                            )
                            for img in rec.get("images", [])
                            if img.get("variant", "").lower() == "main"
                        ),
                        "",
                    )
                    if isinstance(rec.get("images", []), list)
                    else ""
                ),
            }
            batch.append(props)
            if len(batch) == 50:
                collection.data.insert_many(batch)
                inserted_products += len(batch)
                batch.clear()
                if inserted_products % 1000 == 0:
                    logger.info(f"Ingested {inserted_products} products")

    if batch:
        collection.data.insert_many(batch)
        inserted_products += len(batch)

    logger.info(f"✅ Finished ingestion. Total products inserted: {inserted_products}")
    set_ingestion_complete()
