import streamlit as st

from .database import load_documents
from .graph_create import load_family_members, load_relationships
from .graph_render import render_family_graph
from .render_family_graph_graphviz import render_family_graph_graphviz


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

    pyvis_tab, graphviz_tab = st.tabs(
        ["Pyvis (Interactive)", "Graphviz (Hierarchical)"]
    )

    with pyvis_tab:
        name_pyvis_select = st.radio(
            "Select canonical name key",
            ["None", "English", "Pinyin", "簡体字", "Wade-Giles", "漢字", "カタカナ"],
            horizontal=True,
        )

        name_language_map = {
            "None": None,
            "English": "english",
            "Pinyin": "pinyin",
            "簡体字": "hanzi",
            "Wade-Giles": "wade_giles",
            "漢字": "kanji",
            "カタカナ": "katakana",
        }

        name_lang = name_language_map.get(name_pyvis_select, None)

        plot_height = st.slider(
            "Select plot height (px)", min_value=200, max_value=1000, value=700
        )

        render_family_graph(members, relationships, name_lang, plot_height=plot_height)

    with graphviz_tab:
        render_family_graph_graphviz(members, relationships)
