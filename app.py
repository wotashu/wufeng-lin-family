from pathlib import Path

import streamlit as st

from src.graph_create import load_family_members
from src.graph_render import render_family_graph


def main():
    st.set_page_config(layout="wide")
    st.title("Family Graph Interactive App")
    st.write(
        "This application displays an interactive family graph based on unified relationships."
    )

    # Load members.
    json_path = Path("data")
    members = load_family_members(json_path)
    st.write(f"Loaded {len(members)} family members.")

    # Add a radio selector for the canonical key.
    cannon_key_selected = st.radio(
        "Select canonical key",
        ["None", "english", "pinyin", "hanzi", "kanji", "wade_giles", "katakana"],
    )
    cannon_key = None if cannon_key_selected == "None" else cannon_key_selected

    plot_height = st.slider(
        "Select plot height (px)", min_value=200, max_value=1000, value=700
    )

    # Render the graph using the helper function.
    render_family_graph(members, cannon_key=cannon_key, plot_height=plot_height)


if __name__ == "__main__":
    main()
