import base64
from typing import Any

import networkx as nx
from unidecode import unidecode

from src.models import FamilyMember


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
    if member.name.katakana:
        return member.name.katakana
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


def encode_local_image(image_path: str) -> str:
    """Encode image file as a Base64 data URI."""
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")
    # Change the MIME type if needed (e.g. image/jpeg)
    return f"data:image/jpeg;base64,{encoded}"


def create_family_graph(
    members: list[FamilyMember], cannon_key: str | None = None
) -> nx.DiGraph:
    """
    Create a NetworkX graph using the new unified relationships model.
    Nodes are added with visual properties reflecting house, gender, generation, and optionally an image.
    """
    G = nx.DiGraph()  # directed graph so we can show arrows for parent -> child
    spouse_edges = set()  # to track unique spouse relationships

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
        title = f"{house}\n{life_span}\n{note}"
        G.add_node(
            key,
            label=key,
            color={
                "background": color,
                "border": "#FFFFFF",
                "highlight": {"background": color, "border": "#FFD700"},
            },
            title=title,
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
                elif rel_type in ["spouse", "concubine", "former_spouse"]:
                    edge = tuple(sorted([source_key, target_key]))
                    if edge not in spouse_edges:
                        spouse_edges.add(edge)
                        G.add_edge(
                            source_key,
                            target_key,
                            label="spouse",
                            color="white",
                            weight=0.1,
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


def load_family_members(documents: list[dict[Any, Any]]):
    """
    Load all family member JSON files from the data directory.
    Returns a list of FamilyMember instances.
    """
    members = []
    for record in documents:
        member = FamilyMember.model_validate(record)
        members.append(member)
    return members
