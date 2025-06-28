import streamlit as st

from .database import load_documents
from .graph_create import load_family_members, load_relationships
from .graph_render import render_family_graph, render_family_graph_graphviz


def display_page():
    """
    Display the main page of the Streamlit app.
    This function sets up the page configuration, title, and description.
    It also loads family members and renders the family graph.
    """
    st.title("Wufeng Lin Family Graph Interactive App")
    st.write(
        "This application displays an interactive family graph based on unified relationships."
    )

    member_docs, relationship_docs = load_documents()
    members = load_family_members(member_docs)
    relationships = load_relationships(relationship_docs)

    # Add a radio selector for the canonical key.
    name_lang_selection = st.selectbox(
        "Select canonical name key",
        ["None", "english", "pinyin", "hanzi", "kanji", "wade_giles", "katakana"],
    )
    name_lang = None if name_lang_selection == "None" else name_lang_selection

    layout_type = st.selectbox(
        "Select Graph Layout",
        options=["Pyvis (Interactive)", "Graphviz (Hierarchical)"],
    )
    plot_height = st.slider(
        "Select plot height (px)", min_value=200, max_value=1000, value=700
    )
    if layout_type == "Pyvis (Interactive)":
        render_family_graph(members, relationships, name_lang, plot_height=plot_height)
    elif layout_type == "Graphviz (Hierarchical)":
        render_family_graph_graphviz(
            members, relationships, name_lang, plot_height=plot_height
        )
