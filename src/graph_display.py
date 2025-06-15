import streamlit as st

from .database import load_documents
from .graph_create import load_family_members
from .graph_render import render_family_graph


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

    documents = load_documents()
    members = load_family_members(documents)

    # Add a radio selector for the canonical key.
    cannon_key_selected = st.selectbox(
        "Select canonical name key",
        ["None", "english", "pinyin", "hanzi", "kanji", "wade_giles", "katakana"],
    )
    cannon_key = None if cannon_key_selected == "None" else cannon_key_selected

    plot_height = st.slider(
        "Select plot height (px)", min_value=200, max_value=1000, value=700
    )

    # Render the graph using the helper function.
    render_family_graph(members, cannon_key=cannon_key, plot_height=plot_height)
