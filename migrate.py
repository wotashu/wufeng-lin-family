import json
from pathlib import Path

import streamlit as st
from pymongo import MongoClient


def merge_json_files(data_dir: Path) -> list:
    """
    Recursively merge all JSON files within data_dir into a single list.
    """
    merged_data = []
    for json_file in data_dir.rglob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    merged_data.extend(data)
                else:
                    merged_data.append(data)
        except Exception as error:
            print(f"Error reading {json_file}: {error}")
    return merged_data


def migrate_data_to_mongodb(data_dir: Path):
    merged_data = merge_json_files(data_dir)
    print(f"Merged {len(merged_data)} records from JSON files.")

    # Use your MongoDB Atlas connection string from Streamlit secrets.
    mongodb_uri = st.secrets["mongodb"]["uri"]
    client = MongoClient(mongodb_uri)

    # Specify the new database name; it will be created on first insert if it doesn't exist.
    db = client["wufeng"]
    # Also specify the collection name.
    collection = db["members"]

    if merged_data:
        result = collection.insert_many(merged_data)
        print(f"Inserted {len(result.inserted_ids)} documents.")
    else:
        print("No data to insert.")


if __name__ == "__main__":
    data_dir = Path("data")
    migrate_data_to_mongodb(data_dir)
