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
    Load all family member JSON files from the data directory.
    Returns a list of FamilyMember instances.
    """
    data_dir = Path(json_path)
    members = []
    for json_file in data_dir.rglob("*.json"):
        if json_file.name == "cleaned_data.json":
            continue  # Skip the main cleaned file
        try:
            with open(json_file, "r", encoding="utf-8") as infile:
                data = json.load(infile)
            for record in data:
                member = FamilyMember.model_validate(record)
                members.append(member)
        except Exception as e:
            st.write(f"Error parsing {json_file.name}: {e}")
    return members


def get_member_key(member: FamilyMember, cannon_key: str | None = None) -> str:
    """
    Get a unique canonical key for the member.
    Prefer name.english; if missing, use pinyin then hanzi.
    If cannon_key is provided, use that as the primary key.
    If no names are available, return "missing_name".
    """
    if cannon_key:
        names = member.name.model_dump()
        if cannon_key in names:
            cannonical_name = names.get(cannon_key, None)
            if cannonical_name is not None:
                return cannonical_name

    # Fallback to the best available name.
    if member.name.english:
        return member.name.english
    if member.name.pinyin:
        return unidecode(member.name.pinyin)
    if member.name.hanzi:
        return member.name.hanzi
    if member.name.wade_giles:
        return member.name.wade_giles
    if member.name.kanji:
        return member.name.kanji
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
    house_branch_color_map = {
        "Before Wu-feng": "#1f77b4",
        "Taiping Branch": "#FBFF00",
        "Single House": "#0084ff",
        "Lower House": "#2ca02c",
        "Wencha Branch": "#bbff00",
        "Wenming Branch": "#00ffc8",
        "Upper House": "#d62728",
        "Wenfeng Branch": "#ff7b00",
        "Xiantang Branch": "#f700a5",
        "Yunlong Branch": "#c688ff",
    }
    return house_branch_color_map.get(house, "#cacaca")


def get_shape_by_gender(gender: str) -> str:
    """
    Return a shape based on the gender.
    """
    gender_shape_map = {
        "Male": "dot",
        "Female": "square",
    }
    return gender_shape_map.get(gender, "square")


def create_family_graph(
    members: list[FamilyMember], cannon_key: str | None = None
) -> nx.DiGraph:
    """
    Create a NetworkX graph using the new unified relationships model.
    Nodes are added with visual properties reflecting house, gender, generation, and optionally an image.
    """
    G = nx.DiGraph()  # directed graph so we can show arrows for parent -> child

    # Build alternate key mapping: alternate name -> canonical key.
    alt_mapping = {}
    for member in members:
        canon = get_member_key(member, cannon_key)
        for key in get_alternate_keys(member):
            alt_mapping[key] = canon

    # Add nodes.
    for member in members:
        key = get_member_key(member, cannon_key)
        house = member.house or "unknown"
        house_branch = member.branch or member.house or "unknown"
        generation = member.generation if member.generation is not None else 0
        color = get_color_by_house(house_branch)
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

        note = (
            f"note: {member.note}"
            if member.note
            else member.historical_significance
            if member.historical_significance
            else "No additional note"
        )
        birth_date = member.birth_year if member.birth_year else ""
        end_date = member.death_year if member.death_year else ""
        life_span = (
            f"dates: ({birth_date} - {end_date})"
            if birth_date or end_date
            else "unknown dates"
        )
        G.add_node(
            key,
            label=key,
            color={
                "background": color,
                "border": "#FFFFFF",
                "highlight": {"background": color, "border": "#FFD700"},
            },
            title=f"{house}\n{life_span}\n{note}",
            generation=generation,
            data=model_data,  # Contains generation and other info.
            shape=shape,
            use_physics=False,
            image=image_url if image_url else "",
        )

    # Process relationships from the unified "relationships" field.
    for member in members:
        source_key = get_member_key(member, cannon_key)
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
                    parent_branch = G.nodes[source_key]["data"].get("branch", None)
                    if parent_branch is None:
                        parent_branch = G.nodes[source_key]["data"].get(
                            "house", "unknown"
                        )
                    parent_color = get_color_by_house(parent_branch)
                    G.add_edge(
                        target_key, source_key, width=4, arrows="to", color=parent_color
                    )
                elif rel_type == "child":
                    parent_branch = G.nodes[source_key]["data"].get("branch", None)
                    if parent_branch is None:
                        parent_branch = G.nodes[source_key]["data"].get(
                            "house", "unknown"
                        )
                    parent_color = get_color_by_house(parent_branch)
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
    json_path = Path("data")
    members = load_family_members(json_path)
    st.write(f"Loaded {len(members)} family members.")

    # Add a radio selector for the canonical key.
    cannon_key_selected = st.radio(
        "Select canonical key",
        ["None", "english", "pinyin", "hanzi", "kanji", "wade_giles", "katakana"],
    )
    cannon_key = None if cannon_key_selected == "None" else cannon_key_selected

    # Create the family graph with the cannon_key.
    family_graph = create_family_graph(members, cannon_key=cannon_key)
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
