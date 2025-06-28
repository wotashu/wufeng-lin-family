import streamlit as st
from bson import ObjectId

from .database import (  # You need to implement add_relationship
    add_relationship,
    load_documents,
)


def add_relationship_page():
    st.title("Add Relationship")

    # Load members
    member_docs, _ = load_documents()
    # Choose preferred language for display
    lang = st.selectbox(
        "Display names in:",
        ["english", "hanzi", "pinyin", "kanji", "wade_giles", "katakana"],
        index=0,
    )

    # Build display names and mapping to ObjectId
    def get_display_name(doc):
        name = doc.get("name", {})
        return (
            name.get(lang)
            or name.get("english")
            or name.get("hanzi")
            or str(doc["_id"])
        )

    member_choices = [(get_display_name(doc), str(doc["_id"])) for doc in member_docs]
    member_choices.sort(key=lambda x: x[0])

    # Select source and target
    source_display = st.selectbox(
        "Select first member (source)", [name for name, _id in member_choices]
    )
    target_display = st.selectbox(
        "Select second member (target)", [name for name, _id in member_choices]
    )

    # Relationship type
    rel_type = st.selectbox(
        "Relationship type",
        ["child", "spouse", "concubine", "former_spouse", "other"],
    )

    # Optional fields
    start_date = st.text_input("Start date (optional)")
    end_date = st.text_input("End date (optional)")

    if st.button("Add Relationship"):
        # Map display names back to ObjectIds
        source_id = ObjectId(dict(member_choices)[source_display])
        target_id = ObjectId(dict(member_choices)[target_display])

        if source_id == target_id:
            st.error("Source and target cannot be the same member.")
            return

        rel_doc = {
            "source_id": source_id,
            "target": target_id,
            "type": rel_type,
            "start_date": start_date or None,
            "end_date": end_date or None,
        }
        add_relationship(rel_doc)
        st.success("Relationship added successfully!")
