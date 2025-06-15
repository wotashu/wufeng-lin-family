from typing import Any

import streamlit as st
from pymongo import MongoClient


def load_documents():
    # Load members.
    # Get the MongoDB URI from your secrets.toml file
    mongodb_uri = st.secrets["mongodb"]["uri"]

    # Create a MongoClient instance
    client = MongoClient(mongodb_uri)

    # Specify the database and collection names.
    # These will be created on the first write if they don't exist.
    db = client["wufeng"]
    collection = db["members"]

    # Retrieve all documents from the collection
    documents: list[dict[Any, Any]] = list(collection.find({}))

    # Now you can use the retrieved documents as needed.
    st.write(f"Retrieved {len(documents)} records from MongoDB.")

    return documents
