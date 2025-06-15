import json

import streamlit as st
from bson import ObjectId

from .database import add_document, load_documents, update_document
from .graph_create import get_member_key, load_family_members


def member_page():
    st.title("Family Member Details")
    st.write(
        "This page will display detailed information about a selected family member."
    )
    documents = load_documents()
    st.write(f"Object ID for the first member: {documents[0]['_id']}")

    ids = [doc["_id"] for doc in documents]
    members = load_family_members(documents)

    # Add a radio selector for the canonical key.
    cannon_key_selected = st.selectbox(
        "Select canonical name key",
        ["None", "english", "pinyin", "hanzi", "kanji", "wade_giles", "katakana"],
    )
    cannon_key = None if cannon_key_selected == "None" else cannon_key_selected

    names = [get_member_key(member, cannon_key) for member in members]

    selected_member = st.selectbox(
        "Select a family member",
        options=["None", "Add Member"] + names,
        key="member_selector",
    )

    if selected_member == "None":
        st.warning("Please select a family member to view details.")
        return
    if selected_member == "Add Member":
        st.write("You can add a new member here.")
        with st.form("create_member_form"):
            english_name = st.text_input("English Name (identifier)")
            hanzi_name = st.text_input("Hanzi Name")
            pinyin_name = st.text_input("Pinyin Name")
            house = st.text_input("House")
            branch = st.text_input("Branch")
            generation = st.number_input("Generation", value=1)
            gender = st.selectbox("Gender", options=["Male", "Female", "Other"])
            birth_year = st.number_input(
                "Birth Year", min_value=0, max_value=2100, value=0
            )
            death_year = st.number_input(
                "Death Year", min_value=0, max_value=2100, value=0
            )
            if death_year < birth_year:
                st.error("Death year cannot be earlier than birth year.")
            historical_significance = st.text_input(
                "Historical Significance (optional)"
            )
            notes = st.text_area("Notes", height=100)
            relationships = st.text_area(
                "Relationships (JSON format)",
                height=100,
                placeholder='[{"type": "parent", "target": "unkown"}]',
            )
            submitted = st.form_submit_button("Save New Document")
            if submitted:
                new_doc = {
                    "name": {
                        "english": english_name,
                        "hanzi": hanzi_name,
                        "pinyin": pinyin_name,
                    },
                    "house": house,
                    "branch": branch,
                    "generation": generation,
                    "gender": gender,
                    "birth_year": birth_year if birth_year > 0 else None,
                    "death_year": death_year if death_year > 0 else None,
                    "historical_significance": historical_significance,
                    "notes": notes,
                    "relationships": json.loads(relationships)
                    if relationships
                    else [{"type": "parent", "target": "unkown"}],
                }
                add_document(new_doc)
                st.success("New member added successfully!")
        return

    selected_index = names.index(selected_member)
    selected_id = ids[selected_index]
    st.write(f"Selected member name: {selected_member}")
    st.write(f"Selected member id: {selected_id}")

    if selected_member:
        # Find the member object based on the selected name
        member = next(
            (m for m in members if get_member_key(m, cannon_key) == selected_member),
            None,
        )
        if member:
            st.write(f"Details for {selected_member}:")
            st.json(member.model_dump())

            document_json = json.dumps(
                member.model_dump(), indent=2, default=str, ensure_ascii=False
            )
            edited_json = st.text_area(
                "Edit JSON Document",
                value=document_json,
                height=300,
            )
            if st.button("Save Changes"):
                updated_document = json.loads(edited_json)
                # Ensure the _id field is preserved and converted to ObjectId.
                updated_document["_id"] = ObjectId(selected_id)

                update_document(selected_id, updated_document)
                # For now, we just display a message
                st.success("Changes saved successfully!")
                st.json(edited_json)
            st.write("You can edit the JSON document above and save changes.")
        else:
            st.warning("Member not found.")
