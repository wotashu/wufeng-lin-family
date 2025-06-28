import streamlit as st
from pymongo import MongoClient

mongodb_uri = st.secrets["mongodb"]["uri"]
client = MongoClient(mongodb_uri)
db = client["wufeng"]
members_col = db["members"]
relationships_col = db["relationships"]

# Get all member IDs as strings
all_member_ids = {str(doc["_id"]) for doc in members_col.find({}, {"_id": 1})}

# Get all source and target IDs from relationships as strings
source_ids = {
    str(rel.get("source_id")) for rel in relationships_col.find({}, {"source_id": 1})
}
target_ids = {
    str(rel.get("target")) for rel in relationships_col.find({}, {"target": 1})
}

# Nodes with any edge
connected_ids = source_ids | target_ids

# Nodes with no edges
isolated_ids = all_member_ids - connected_ids

print(f"Found {len(isolated_ids)} isolated nodes (no edges):")
for node_id in isolated_ids:
    print(node_id)
