import json
from pathlib import Path

import networkx as nx
import streamlit as st
from pyvis.network import Network
from streamlit.components import v1 as components
from unidecode import unidecode

from src.models import FamilyMember


def load_family_members(json_path: Path):
    """
    Load the JSON list file and convert each record into a FamilyMember instance.
    """
    with open(json_path, "r", encoding="utf-8") as infile:
        data = json.load(infile)

    members = []
    for record in data:
        try:
            member = FamilyMember.model_validate(record)
            members.append(member)
        except Exception as e:
            st.write(f"Error parsing record: {record}\n{e}")
    return members


def get_member_key(member: FamilyMember) -> str:
    """
    Get a unique canonical key for the member.
    Prefer name.english; if missing, use pinyin (ascii) then hanzi.
    """
    if member.name.english:
        return member.name.english
    if member.name.pinyin:
        return unidecode(member.name.pinyin)
    if member.name.hanzi:
        return member.name.hanzi
    return "missing_name"


def get_alternate_keys(member: FamilyMember) -> set:
    """
    Return a set of possible key names for the member.
    This includes english, ascii pinyin, and hanzi (if available).
    """
    keys = set()
    if member.name.english:
        keys.add(member.name.english)
    if member.name.pinyin:
        keys.add(unidecode(member.name.pinyin))
    if member.name.hanzi:
        keys.add(member.name.hanzi)
    return keys


def get_color_by_house(house: str) -> str:
    """
    Return a color code based on the house name.
    """

    house_color_map = {
        "Whole family (before split)": "#0000FF",  # Blue
        "Whole family (before split, settled in Wu-feng)": "#00CCFF",  # Blue
        "Upper House": "#B700FF",  # Red
        "Lower House": "#00FF15",  # Green
        "Overseas House": "#FF0000",  # Orange
    }
    return house_color_map.get(house, "#000000")  # Default black if not found


def get_shape_by_gender(gender: str) -> str:
    """
    Return a shape based on the gender.
    """
    gender_shape_map = {
        "Male": "dot",
        "Female": "triangle",
    }
    return gender_shape_map.get(gender, "square")  # Default to square if not found


def create_family_graph(members: list[FamilyMember]):
    """
    Create an undirected NetworkX graph from a list of FamilyMember instances.
    Nodes are keyed by canonical name and color-coded by house.
    Parent, child, spouse, former_spouse, concubine, and concubine_of relationships
    are matched using alternate names.
    On hover, nodes display full metadata.
    """
    G = nx.Graph()

    # Build an alternate name mapping: alternate name -> canonical key.
    alt_mapping = {}
    for member in members:
        canon = get_member_key(member)
        for key in get_alternate_keys(member):
            alt_mapping[key] = canon

    # Add nodes using canonical keys.
    for member in members:
        key = get_member_key(member)
        house = member.house if member.house else "unknown"
        color = get_color_by_house(house)
        gender = member.gender if member.gender else "Male"
        gender = get_shape_by_gender(gender)
        generation = member.generation if member.generation else -1
        y_position = 1000 - (
            generation * 100
        )  # Adjust vertical position based on generation
        # Prepare metadata as pretty JSON for hover tooltip.
        use_physics = True if member.generation is None else False
        metadata = json.dumps(member.model_dump(), ensure_ascii=False, indent=2)
        G.add_node(
            key,
            label=key,
            color=color,
            title=metadata,
            data=member.model_dump(),
            shape=gender,
            x=y_position,
            use_physics=use_physics,
        )

    # Connect relationships using alternate mapping.
    for member in members:
        child_key = get_member_key(member)
        # Process parent's relationships.
        for parent in member.parents:
            parent_key = parent
            if parent_key not in G.nodes:
                parent_key = alt_mapping.get(parent, parent)
            if parent_key in G.nodes and parent_key != child_key:
                G.add_edge(child_key, parent_key, width=4)
        # Process children relationships.
        for child in member.children:
            ch_key = child
            if ch_key not in G.nodes:
                ch_key = alt_mapping.get(child, child)
            if ch_key in G.nodes and ch_key != child_key:
                G.add_edge(child_key, ch_key, width=4)
        # Process spouse relationship.
        if member.spouse:
            if isinstance(member.spouse, str):
                sp_key = member.spouse
            else:
                sp_key = get_member_key(member.spouse)
            if sp_key not in G.nodes:
                sp_key = alt_mapping.get(member.spouse, sp_key)
            if sp_key in G.nodes and sp_key != child_key:
                G.add_edge(child_key, sp_key, width=2, dashes=True)
        # Process former_spouses relationships.
        if member.former_spouses:
            for former in member.former_spouses:
                if isinstance(former, str):
                    fs_key = former
                else:
                    fs_key = get_member_key(former)
                if fs_key not in G.nodes:
                    fs_key = alt_mapping.get(former, fs_key)
                if fs_key in G.nodes and fs_key != child_key:
                    G.add_edge(child_key, fs_key, width=2, color="black", dashes=True)
        # Process concubines relationships.
        if hasattr(member, "concubines") and member.concubines:
            # Expecting concubines to be a list.
            for concubine in member.concubines:
                if isinstance(concubine, str):
                    c_key = concubine
                else:
                    c_key = get_member_key(concubine)
                if c_key not in G.nodes:
                    c_key = alt_mapping.get(concubine, c_key)
                if c_key in G.nodes and c_key != child_key:
                    G.add_edge(child_key, c_key, width=2, dashes=True)
        # Process concubine_of relationship.
        if hasattr(member, "concubine_of") and member.concubine_of:
            if isinstance(member.concubine_of, str):
                co_key = member.concubine_of
            else:
                co_key = get_member_key(member.concubine_of)
            if co_key not in G.nodes:
                co_key = alt_mapping.get(member.concubine_of, co_key)
            if co_key in G.nodes and co_key != child_key:
                G.add_edge(child_key, co_key, width=2, dashes=True)
    return G


def main():
    st.title("Family Graph Interactive App")
    st.write(
        "This application displays an interactive family graph, color-coded by house."
    )

    # Set the path for the updated combined JSON file.
    json_path = Path("data/combined_houses_updated.json")
    members = load_family_members(json_path)
    st.write(f"Loaded {len(members)} family members.")

    # Create the family graph from the loaded members.
    family_graph = create_family_graph(members)
    st.write(
        f"Graph has {family_graph.number_of_nodes()} nodes and {family_graph.number_of_edges()} edges."
    )

    # Build an interactive graph using Pyvis.
    net = Network(notebook=True, height="700px", width="100%", directed=False)
    net.from_nx(family_graph)
    net.set_options(
        """
    {
        "nodes": {
            "font": {
                "size": 16,
                "face": "arial"
            }
        },
        "physics": {
            "enabled": true,
            "hierarchicalRepulsion": {
                "centralGravity": 0,
                "springLength": 100,
                "springConstant": 0.01,
                "nodeDistance": 120,
                "damping": 0.09
            },
            "minVelocity": 0.75
        }
    }
    """
    )

    # Save the interactive graph as HTML.
    net.save_graph("family_graph_interactive.html")

    # Read and embed the HTML file in the Streamlit app.
    html_file = Path("family_graph_interactive.html")
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()
        components.html(html_content, height=750, scrolling=True)
    else:
        st.write("Interactive graph file not found.")


if __name__ == "__main__":
    main()
