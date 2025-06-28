import streamlit as st
from bson import ObjectId

from .database import add_document, load_documents, update_document
from .graph_create import get_member_key, load_family_members


def member_form(
    existing_member: dict | None = None, form_key: str = "member_form"
) -> dict:
    """Render a form for adding or editing a family member."""
    with st.form(key=form_key):
        english_name = st.text_input(
            "English Name (identifier)",
            value=existing_member.get("name", {}).get("english", "")
            if existing_member
            else "",
        )
        hanzi_name = st.text_input(
            "Hanzi Name",
            value=existing_member.get("name", {}).get("hanzi", "")
            if existing_member
            else "",
        )
        pinyin_name = st.text_input(
            "Pinyin Name",
            value=existing_member.get("name", {}).get("pinyin", "")
            if existing_member
            else "",
        )
        kanji_name = st.text_input(
            "Kanji Name",
            value=existing_member.get("name", {}).get("kanji", "")
            if existing_member
            else "",
        )
        wade_giles_name = st.text_input(
            "Wade-Giles Name",
            value=existing_member.get("name", {}).get("wade_giles", "")
            if existing_member
            else "",
        )
        katakana_name = st.text_input(
            "Katakana Name",
            value=existing_member.get("name", {}).get("katakana", "")
            if existing_member
            else "",
        )
        house = st.text_input(
            "House", value=existing_member.get("house", "") if existing_member else ""
        )
        branch = st.text_input(
            "Branch",
            value=existing_member.get("branch", "") if existing_member else None,
        )
        generation = st.number_input(
            "Generation",
            value=existing_member.get("generation", 1) if existing_member else 1,
            min_value=1,
        )
        gender = st.selectbox("Gender", options=["Male", "Female", "Other"])
        birth_year = st.number_input(
            "Birth Year",
            min_value=0,
            max_value=2100,
            value=existing_member.get("birth_year", None) if existing_member else None,
        )
        death_year = st.number_input(
            "Death Year",
            min_value=0,
            max_value=2100,
            value=existing_member.get("death_year", None) if existing_member else None,
        )

        historical_significance = st.text_input(
            "Historical Significance (optional)",
            value=existing_member.get("historical_significance", "")
            if existing_member
            else "",
        )
        image = st.text_input(
            "Image URL (optional)",
            placeholder="URL or path to image",
            value=existing_member.get("image", "") if existing_member else "",
        )
        links = st.text_input(
            "Links (optional, comma-separated URLs)",
            placeholder="https://example.com, https://another-example.com",
            value=existing_member.get("links", []) if existing_member else [],
        )
        if links:
            links = [link.strip() for link in links.split(",") if link.strip()]
        else:
            links = []
        note = st.text_area(
            "Note (optional)",
            height=100,
            value=existing_member.get("note", "") if existing_member else "",
        )
        submitted = st.form_submit_button(form_key.replace("_", " ").title())
        if submitted:
            return {
                "name": {
                    "english": english_name,
                    "hanzi": hanzi_name,
                    "pinyin": pinyin_name,
                    "kanji": kanji_name,
                    "wade_giles": wade_giles_name,
                    "katakana": katakana_name,
                },
                "house": house,
                "branch": branch,
                "generation": generation,
                "gender": gender,
                "birth_year": birth_year,
                "death_year": death_year,
                "historical_significance": historical_significance,
                "image": image,
                "links": links,
                "note": note,
            }

    return {}


def member_page():
    st.title("Family Member Details")
    st.write(
        "This page will display detailed information about a selected family member."
    )
    member_docs, _ = load_documents()
    st.write(f"Object ID for the first member: {member_docs[0]['_id']}")

    # 1. Extract unique house values
    all_houses = sorted(
        {doc.get("house", "Unknown") for doc in member_docs if doc.get("house")}
    )
    house_filter = st.selectbox("Filter by House", options=["All"] + all_houses)

    ids = [doc["_id"] for doc in member_docs]
    members = load_family_members(member_docs)

    # Add a radio selector for the canonical key.
    cannon_key_selected = st.selectbox(
        "Select canonical name key",
        ["None", "english", "pinyin", "hanzi", "kanji", "wade_giles", "katakana"],
    )
    cannon_key = None if cannon_key_selected == "None" else cannon_key_selected

    # 2. Filter members by house
    if house_filter != "All":
        filtered_members = [
            m for m in members if getattr(m, "house", None) == house_filter
        ]
        filtered_ids = [
            doc["_id"] for doc in member_docs if doc.get("house") == house_filter
        ]
    else:
        filtered_members = members
        filtered_ids = ids

    # Pair each name with its corresponding ID
    name_id_pairs = list(
        zip(
            [get_member_key(member, cannon_key) for member in filtered_members],
            filtered_ids,
        )
    )

    # Sort the pairs by name
    name_id_pairs.sort(key=lambda x: x[0])

    # Unpack the sorted names and ids
    sorted_names = [name for name, _id in name_id_pairs]
    sorted_ids = [_id for name, _id in name_id_pairs]

    selected_member = st.selectbox(
        "Select a family member",
        options=["None", "Add Member"] + sorted_names,
        key="member_selector",
    )

    if selected_member == "None":
        st.warning("Please select a family member to view details.")
        return
    if selected_member == "Add Member":
        st.write("You can add a new member here.")
        new_member = member_form(existing_member=None, form_key="add_member_form")
        if not new_member:
            st.warning("Please fill out the form to add a new member.")
            return
        add_document(new_member)
        st.success("New member added successfully!")
        return

    selected_index = sorted_names.index(selected_member)
    selected_id = sorted_ids[selected_index]
    st.write(f"Selected member name: {selected_member}")
    st.write(f"Selected member id: {selected_id}")

    if selected_member:
        member = next(
            (
                m
                for m in filtered_members
                if get_member_key(m, cannon_key) == selected_member
            ),
            None,
        )
        if member:
            st.write(f"Details for {selected_member}:")
            existing_member = member.model_dump()
            st.write("You can edit the member details below:")
            updated_member = member_form(
                existing_member=existing_member,
                form_key=f"update_member_form_{selected_id}",
            )
            if updated_member:
                updated_member["_id"] = ObjectId(selected_id)
                update_document(selected_id, updated_member)
                st.success("Changes saved successfully!")
                st.json(updated_member)
            st.write("You can edit the JSON document above and save changes.")
        else:
            st.warning("Member not found.")
