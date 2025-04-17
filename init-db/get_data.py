#!/usr/bin/env python3

import os
import requests
import pandas as pd
import json
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

# URL to download dataset from
URL = "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/meta_categories/meta_Amazon_Fashion.jsonl.gz"

# Local paths for the dataset
RAW_PATH = os.getenv("RAW_PATH", "/data/meta_Amazon_Fashion.jsonl.gz")
OUTPUT_ZIP = os.getenv("OUTPUT_ZIP", "/data/products.zip")


def download_dataset(url: str, path: str) -> None:
    """Download the dataset if it doesn't already exist on disk."""
    logging.info(f"Checking for existing dataset at {path}")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
        logging.info(f"Downloading dataset from {url}...")
        with open(path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        logging.info(f"Downloaded dataset to {path}")
    else:
        logging.info(f"Dataset already exists at {path}")


def process_data(raw_path: str) -> pd.DataFrame:
    """
    Load and process the raw JSONL dataset.
    - Converts 'details' dict to JSON string.
    - Joins list-valued 'description' entries into space-separated text.
    - Drops unneeded columns to reduce size.
    """
    logging.info(f"Loading data from {raw_path}")
    # 1. Load the gzipped JSONL into a DataFrame
    df = pd.read_json(raw_path, lines=True, compression="gzip")
    logging.info(f"Loaded {len(df)} records")

    # 2. Convert 'details' (dict) to a JSON-formatted string
    if "details" in df.columns:
        df["details"] = df["details"].apply(
            lambda d: json.dumps(d) if isinstance(d, dict) else ""
        )
        logging.info("Converted 'details' column to JSON strings")

    # 3. Flatten 'description' lists into strings
    if "description" in df.columns:
        df["description"] = df["description"].apply(
            lambda x: " ".join(x) if isinstance(x, list) else (x or "")
        )
        logging.info("Flattened 'description' lists into strings")

    # 4. Drop intermediate or unneeded columns
    for col in ["parent_asin", "details_keys", "description_length"]:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)
    logging.info("Dropped unneeded columns")

    return df


def save_data(df: pd.DataFrame, output_zip: str) -> None:
    """Save the processed DataFrame to a zipped CSV."""
    logging.info(f"Saving processed data to {output_zip}")
    df.to_csv(output_zip, index=False, compression="zip")
    size_mb = os.path.getsize(output_zip) / (1024 * 1024)
    logging.info(f"Saved processed data to {output_zip} ({size_mb:.2f} MB)")


def main():
    """Main function to orchestrate the data processing pipeline."""
    download_dataset(URL, RAW_PATH)
    df = process_data(RAW_PATH)
    save_data(df, OUTPUT_ZIP)
    logging.info("Data processing pipeline completed successfully")


if __name__ == "__main__":
    main()
