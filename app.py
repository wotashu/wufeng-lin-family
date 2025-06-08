import base64
import json
from pathlib import Path

import networkx as nx
import streamlit as st
from pyvis.network import Network
from streamlit.components import v1 as components
from unidecode import unidecode

from src.models import FamilyMember


def encode_local_image(image_path: str) -> str:
    """Encode image file as a Base64 data URI."""
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")
    # Change the MIME type if needed (e.g. image/jpeg)
    return f"data:image/jpeg;base64,{encoded}"


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
    Prefer name.english; if missing, use pinyin then hanzi.
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
    This includes english, ascii pinyin, and hanzi.
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
        "Whole family (before split)": "#1f77b4",
        "Whole family (before split, settled in Wu-feng)": "#ff7f0e",
        "Lower House": "#2ca02c",
        "Upper House": "#d62728",
        "Overseas House": "#9467bd",
    }
    return house_color_map.get(house, "#8c564b")


def get_shape_by_gender(gender: str) -> str:
    """
    Return a shape based on the gender.
    """
    gender_shape_map = {
        "Male": "dot",
        "Female": "square",
    }
    return gender_shape_map.get(gender, "square")


def create_family_graph(members: list[FamilyMember]):
    """
    Create a NetworkX graph using the new unified relationships model.
    Nodes are added with visual properties reflecting house, gender, generation, and optionally an image.
    """
    G = nx.DiGraph()  # directed graph so we can show arrows for parent -> child

    # Build alternate key mapping: alternate name -> canonical key.
    alt_mapping = {}
    for member in members:
        canon = get_member_key(member)
        for key in get_alternate_keys(member):
            alt_mapping[key] = canon

    # Add nodes.
    for member in members:
        key = get_member_key(member)
        house = member.house if member.house else "unknown"
        generation = member.generation if member.generation is not None else 0
        color = get_color_by_house(house)
        gender = member.gender if member.gender else "Male"
        # Default shape from gender.
        shape = get_shape_by_gender(gender)

        # Check if the member has an image (adjust the attribute name as needed)
        model_data = member.model_dump()
        image_url = model_data.get("image", None)
        if image_url:
            # If the path is local, encode it.
            if image_url.startswith("http") is False:
                image_url = encode_local_image(image_url)
            shape = "image"  # switch to image node shape

        metadata = json.dumps(model_data, ensure_ascii=False, indent=2)
        G.add_node(
            key,
            label=key,
            color={
                "background": color,
                "border": "#FFFFFF",
                "highlight": {"background": color, "border": "#FFD700"},
            },
            title=metadata,
            generation=generation,
            data=model_data,  # Contains generation and other info.
            shape=shape,
            use_physics=False,
            image=image_url if image_url else "",
        )

    # Process relationships from the unified "relationships" field.
    for member in members:
        source_key = get_member_key(member)
        rels = member.model_dump().get("relationships", [])
        for rel in rels:
            rel_type = rel.get("type")
            target = rel.get("target")
            target_key = target
            # Use alt_mapping if needed.
            if target_key not in G.nodes:
                target_key = alt_mapping.get(target, target)
            if target_key in G.nodes and target_key != source_key:
                if rel_type in ["parent", "child_of"]:
                    parent_house = G.nodes[target_key]["data"].get("house", "unknown")
                    parent_color = get_color_by_house(parent_house)
                    G.add_edge(
                        target_key, source_key, width=4, arrows="to", color=parent_color
                    )
                elif rel_type == "child":
                    parent_house = G.nodes[target_key]["data"].get("house", "unknown")
                    parent_color = get_color_by_house(parent_house)
                    G.add_edge(
                        source_key,
                        target_key,
                        width=4,
                        arrows={"to": {"enabled": False}},
                        color=parent_color,
                    )
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
    st.set_page_config(layout="wide")
    st.title("Family Graph Interactive App")
    st.write(
        "This application displays an interactive family graph based on unified relationships."
    )

    # Load members.
    json_path = Path("data/cleaned_data.json")
    members = load_family_members(json_path)
    st.write(f"Loaded {len(members)} family members.")

    # Create the family graph.
    family_graph = create_family_graph(members)
    st.write(
        f"Graph has {family_graph.number_of_nodes()} nodes and {family_graph.number_of_edges()} edges."
    )

    # Build Pyvis network.
    net = Network(
        notebook=True,
        height="700px",
        width="100%",
        directed=True,
        bgcolor="#222222",
    )
    net.from_nx(family_graph)

    # Disable physics since layout is precomputed.
    net.set_options(
        """
    {
        "nodes": {
            "font": {
                "size": 16,
                "face": "arial",
                "color": "#ffffff"
            }
        },
        "edges": {
            "color": { "inherit": true }
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

    # Save and embed the graph.
    net.save_graph("family_graph_interactive.html")
    html_file = Path("family_graph_interactive.html")
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Inject custom CSS to override the frame styles.
        custom_css = """
        <style>
            /* Adjust the pyvis network container */
            #mynetwork {
                border: 2px solid #222222;  /* dark border */
                background-color: #222222;  /* dark background */
            }
            body {
                background-color: #222222;  /* ensure outer background is also dark */
            }
        </style>
        """
        # Insert the CSS block right before the closing </head> tag.
        html_content = html_content.replace("</head>", custom_css + "</head>")

        components.html(html_content, height=750, scrolling=True)
    else:
        st.write("Interactive graph file not found.")


if __name__ == "__main__":
    main()
