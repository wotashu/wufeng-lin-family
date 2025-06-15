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


def add_document(document: dict[Any, Any]):
    # Get the MongoDB URI from your secrets.toml file
    mongodb_uri = st.secrets["mongodb"]["uri"]

    # Create a MongoClient instance
    client = MongoClient(mongodb_uri)

    # Specify the database and collection names.
    db = client["wufeng"]
    collection = db["members"]

    # Insert the document into the collection
    result = collection.insert_one(document)

    st.write(f"Document inserted with ID: {result.inserted_id}")


def update_document(document_id: str, updated_data: dict[Any, Any]):
    # Get the MongoDB URI from your secrets.toml file
    mongodb_uri = st.secrets["mongodb"]["uri"]

    # Create a MongoClient instance
    client = MongoClient(mongodb_uri)

    # Specify the database and collection names.
    db = client["wufeng"]
    collection = db["members"]

    # Update the document with the specified ID
    result = collection.update_one({"_id": document_id}, {"$set": updated_data})

    if result.modified_count > 0:
        st.write(f"Document with ID {document_id} updated successfully.")
    else:
        st.write(f"No document found with ID {document_id}.")


def delete_document(document_id: str):
    # Get the MongoDB URI from your secrets.toml file
    mongodb_uri = st.secrets["mongodb"]["uri"]

    # Create a MongoClient instance
    client = MongoClient(mongodb_uri)

    # Specify the database and collection names.
    db = client["wufeng"]
    collection = db["members"]

    # Delete the document with the specified ID
    result = collection.delete_one({"_id": document_id})

    if result.deleted_count > 0:
        st.write(f"Document with ID {document_id} deleted successfully.")
    else:
        st.write(f"No document found with ID {document_id}.")
