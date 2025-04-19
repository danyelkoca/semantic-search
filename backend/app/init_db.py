import gzip
import json
import logging
import os

import dotenv
import requests
import weaviate
from weaviate.classes.config import DataType, Property

# Load environment variables
dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("weaviate").setLevel(logging.WARNING)


def wait_for_schema_ready(client, retries=30, delay=2):
    import time

    for i in range(retries):
        try:
            client.collections.list_all()
            logging.info("✅ Weaviate schema is available.")
            return
        except weaviate.exceptions.InsufficientPermissionsError:
            logging.warning(f"⏳ Weaviate not ready (attempt {i+1}/{retries})")
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

    if "Product" not in client.collections.list_all():
        collection = client.collections.create(
            name="Product",
            properties=[
                Property(name="product_id", data_type=DataType.INT),
                Property(name="title", data_type=DataType.TEXT),
                Property(name="average_rating", data_type=DataType.NUMBER),
                Property(name="rating_number", data_type=DataType.INT),
                Property(name="features", data_type=DataType.TEXT_ARRAY),
                Property(name="description", data_type=DataType.TEXT),
                Property(name="price", data_type=DataType.NUMBER),
                Property(name="store", data_type=DataType.TEXT),
                Property(name="details", data_type=DataType.TEXT),
                Property(name="main_hi_res_image", data_type=DataType.TEXT),
            ],
        )
        logging.info("✅ Created 'Product' schema.")
        populate_collection(collection)
    else:
        collection = client.collections.get("Product")
        if collection.aggregate.over_all(total_count=True).total_count == 0:
            logging.info(
                "✅ Found existing 'Product' collection with zero objects; populating."
            )
            populate_collection(collection)
        else:
            logging.info("DB already initialized; skipping ingestion.")

    client.close()
    logging.info("✅ Weaviate client closed.")


def populate_collection(collection):
    raw_url = os.getenv("RAW_URL")
    if not raw_url:
        raise ValueError("RAW_URL is not set in environment variables.")

    logging.info(f"🔗 Starting download and ingestion from {raw_url}")

    resp = requests.get(raw_url, stream=True)
    resp.raise_for_status()

    with gzip.GzipFile(fileobj=resp.raw) as gz:
        for i, line in enumerate(gz, start=1):
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
            collection.data.insert(props)
            if i % 1000 == 0:
                logging.info(f"Ingested {i} products")

    logging.info("✅ Finished ingestion.")
