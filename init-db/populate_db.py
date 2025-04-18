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
# Suppress verbose HTTPX and Weaviate client INFO logs during ingestion
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("weaviate").setLevel(logging.WARNING)

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


# Check if FORCE_REFRESH_DB is set to true in the environment variables
force_refresh_db = os.getenv("FORCE_REFRESH_DB", "false").lower() == "true"

if force_refresh_db and "Product" in client.collections.list_all():
    client.collections.delete("Product")
    logging.info("✅ Deleted 'Product' schema due to FORCE_REFRESH_DB being enabled.")
    logging.info("✅ Will re-ingest data.")

if "Product" not in client.collections.list_all():
    collection = client.collections.create(
        name="Product",
        # properties=[
        #     Property(
        #         name="title",
        #         data_type=DataType.TEXT,
        #         module_config={
        #             "text2vec-openai": {
        #                 "skip": False,
        #                 "vectorizePropertyName": True,
        #             }
        #         },
        #     ),
        #     Property(
        #         name="average_rating",
        #         data_type=DataType.NUMBER,
        #         module_config={"text2vec-openai": {"skip": True}},
        #     ),
        #     Property(
        #         name="rating_number",
        #         data_type=DataType.INT,
        #         module_config={"text2vec-openai": {"skip": True}},
        #     ),
        #     Property(
        #         name="features",
        #         data_type=DataType.TEXT_ARRAY,
        #         module_config={
        #             "text2vec-openai": {
        #                 "skip": False,
        #                 "vectorizePropertyName": True,
        #             }
        #         },
        #     ),
        #     Property(
        #         name="description",
        #         data_type=DataType.TEXT,
        #         module_config={
        #             "text2vec-openai": {
        #                 "skip": False,
        #                 "vectorizePropertyName": True,
        #             }
        #         },
        #     ),
        #     Property(
        #         name="price",
        #         data_type=DataType.NUMBER,
        #         module_config={"text2vec-openai": {"skip": True}},
        #     ),
        #     Property(
        #         name="store",
        #         data_type=DataType.TEXT,
        #         module_config={
        #             "text2vec-openai": {
        #                 "skip": False,
        #                 "vectorizePropertyName": True,
        #             }
        #         },
        #     ),
        #     Property(
        #         name="details",
        #         data_type=DataType.TEXT,
        #         module_config={
        #             "text2vec-openai": {
        #                 "skip": False,
        #                 "vectorizePropertyName": True,
        #             }
        #         },
        #     ),
        #     Property(
        #         name="main_hi_res_image",
        #         data_type=DataType.TEXT,
        #         module_config={"text2vec-openai": {"skip": True}},
        #     ),
        # ],
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
        # vectorizer_config=Configure.Vectorizer.text2vec_openai(),
    )

    logging.info("✅ Created 'Product' schema; beginning line-by-line ingestion.")
    # Stream and ingest records directly from raw JSONL
    RAW_PATH = os.getenv("RAW_PATH", "/data/meta_Amazon_Fashion.jsonl.gz")
    with gzip.open(RAW_PATH, "rt", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):

            if os.getenv("NO_OF_PRODUCTS") and i > int(os.getenv("NO_OF_PRODUCTS")):
                break

            rec = json.loads(line)

            props = {
                # Assign unique ID
                "product_id": i,
                # Keep title and store as is (str)
                "title": rec.get("title", ""),
                "store": rec.get("store", ""),
                # Convert description array into string
                "description": (
                    " ".join(rec["description"])
                    if isinstance(rec.get("description", []), list)
                    else rec.get("description", "")
                ),
                # Keep features as array of strings
                "features": rec.get("features", []),
                # Convert average_rating, rating_number, and price to float/int
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
                # details is a dict; convert to JSON string
                "details": json.dumps(rec.get("details", {})),
                # Extract main_hi_res_image from images and remove URL prefix
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
    logging.info("✅ Products ingested and DB initialized.")
else:
    collection = client.collections.get("Product")
    logging.info("✅ Found existing 'Product' collection; skipping ingestion.")

if client:
    client.close()
    logging.info("✅ Client connection closed.")
    # Keep the container alive so init-db service remains healthy
    logging.info("Entering idle sleep to maintain service healthy status.")
