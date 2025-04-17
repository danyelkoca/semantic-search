#!/usr/bin/env python3

import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging for the script
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

# URL to download the dataset from
URL = "https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/meta_categories/meta_Amazon_Fashion.jsonl.gz"

# Local path to save the downloaded dataset
RAW_PATH = os.getenv("RAW_PATH", "/data/products.jsonl.gz")


def download_dataset(url: str, path: str) -> None:
    """
    Download the dataset from the given URL if it doesn't already exist locally.

    Args:
        url (str): The URL to download the dataset from.
        path (str): The local file path to save the dataset.
    """
    logging.info(f"Checking for existing dataset at {path}")
    if not os.path.exists(path):  # Check if the file already exists
        os.makedirs(
            os.path.dirname(path), exist_ok=True
        )  # Create directories if needed
        resp = requests.get(
            url, stream=True
        )  # Stream the download to handle large files
        resp.raise_for_status()  # Raise an error if the request fails
        logging.info(f"Downloading dataset from {url}...")
        with open(path, "wb") as f:  # Write the file in binary mode
            for chunk in resp.iter_content(chunk_size=8192):  # Download in chunks
                f.write(chunk)
        logging.info(f"Downloaded dataset to {path}")
    else:
        logging.info(f"Dataset already exists at {path}")


def main():
    """
    Main function to orchestrate the dataset download process.
    """
    download_dataset(URL, RAW_PATH)
    logging.info("Dataset download completed successfully")


if __name__ == "__main__":
    main()
