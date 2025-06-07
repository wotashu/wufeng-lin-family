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
        "Female": "square",
    }
    return gender_shape_map.get(gender, "square")  # Default to square if not found


def create_family_graph(members: list[FamilyMember]):
    """
    Create a NetworkX graph using the new unified relationships model.
    Nodes are added as before, and edges are created by iterating over the
    relationships array, using the "type" field to customize edge attributes.
    """
    G = nx.DiGraph()  # Use a directed graph if you want arrows for parent-child

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
        generation = member.generation if member.generation is not None else -1
        # Use generation for vertical positioning (or you can ignore it if using a layout)
        y_position = 1000 - (generation * 100)
        metadata = json.dumps(member.model_dump(), ensure_ascii=False, indent=2)
        G.add_node(
            key,
            label=key,
            color=color,
            title=metadata,
            data=member.model_dump(),  # contains generation, etc.
            shape=gender,
            x=y_position,
            use_physics=True if member.generation is None else False,
        )

    # Process relationships from the unified "relationships" field.
    for member in members:
        source_key = get_member_key(member)
        # Check if the member has the 'relationships' field
        rels = member.model_dump().get("relationships", [])
        for rel in rels:
            rel_type = rel.get("type")
            target = rel.get("target")
            # Resolve target using alternate mapping if needed.
            target_key = target
            if target_key not in G.nodes:
                target_key = alt_mapping.get(target, target)
            if target_key in G.nodes and target_key != source_key:
                # Parent-child edges: arrow from parent to child.
                if rel_type in ["parent", "child_of"]:
                    # If relationship type is "parent" (from child's perspective),
                    # add edge from target (parent) to source (child).
                    G.add_edge(target_key, source_key, width=4, arrows="to")
                # Child edges: arrow disabled (if desired to keep consistency).
                elif rel_type == "child":
                    G.add_edge(
                        source_key,
                        target_key,
                        width=4,
                        arrows={"to": {"enabled": False}},
                    )
                # For spouse, former_spouse, concubine, etc., disable arrows.
                else:
                    G.add_edge(
                        source_key,
                        target_key,
                        width=2,
                        dashes=True,
                        arrows={"to": {"enabled": False}},
                    )
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
    net = Network(notebook=True, height="700px", width="100%", directed=True)
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
