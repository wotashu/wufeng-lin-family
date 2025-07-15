import base64
from typing import Any

import networkx as nx
from unidecode import unidecode

from src.models import FamilyMember, Relationship


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
        "Before Wu-feng": "#1976d2",  # Deep Blue
        "Taiping Branch": "#c62828",  # Strong Red
        "Single House": "#00897b",  # Teal
        "Lower House": "#43a047",  # Green
        "Wencha Branch": "#fbc02d",  # Yellow (dark enough for white text)
        "Wenming Branch": "#7b1fa2",  # Purple
        "Upper House": "#f57c00",  # Orange
        "Wenfeng Branch": "#d81b60",  # Pink
        "Xiantang Branch": "#455a64",  # Slate
        "Yunlong Branch": "#5e35b1",  # Indigo
    }
    return house_branch_color_map.get(house, "#8a8a8a")


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
    try:
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
        # Change the MIME type if needed (e.g. image/jpeg)
        return f"data:image/jpeg;base64,{encoded}"
    except FileNotFoundError:
        print(f"Image file not found: {image_path}")
        return ""


def create_family_graph(
    members: list[FamilyMember],
    relationships: list[Relationship],
    name_display_type: str | None = None,
) -> nx.DiGraph:
    """
    Create a NetworkX graph using the unified relationships model.
    Nodes are keyed by stringified ObjectId (member.id).
    """
    G = nx.DiGraph()
    spouse_edges = set()

    # Add nodes
    for member in members:
        node_id = str(member.id)
        house = member.house or "unknown house"
        branch = member.branch or "unknown branch"
        house_branch = member.branch or member.house or "unknown"
        generation = member.generation if member.generation is not None else 0
        color = get_color_by_house(house_branch)
        gender = member.gender if member.gender else "Male"
        shape = get_shape_by_gender(gender)
        model_data = member.model_dump()
        model_data["id"] = node_id
        image_url = model_data.get("image", None)
        if image_url and not image_url.startswith("http"):
            image_url = encode_local_image(image_url)
            shape = "image"
        note = (
            f"note: {member.note}"
            if getattr(member, "note", None)
            else getattr(member, "historical_significance", None)
            if getattr(member, "historical_significance", None)
            else "No additional note"
        )
        birth_date = getattr(member, "birth_year", "") or ""
        end_date = getattr(member, "death_year", "") or ""
        life_span = (
            f"dates: ({birth_date} - {end_date})"
            if birth_date or end_date
            else "unknown dates"
        )

        label = get_member_key(member, name_display_type)

        title = f"{label}\n{house}\n{branch}\n{life_span}\n{note}"
        G.add_node(
            node_id,
            label=label,
            color={
                "background": color,
                "border": "#FFFFFF",
                "highlight": {"background": color, "border": "#FFD700"},
            },
            title=title,
            generation=generation,
            data=model_data,
            shape=shape,
            use_physics=False,
            image=image_url if image_url else "",
        )

    # Add edges using the relationships collection
    for rel in relationships:
        source_id = str(rel.source_id)
        target_id = str(rel.target)
        rel_type = rel.type

        # Only add edge if both nodes exist
        if source_id not in G.nodes or target_id not in G.nodes:
            print(
                f"Skipping edge: missing node for source_id={source_id} or target_id={target_id}"
            )
            continue

        if rel_type == "child":
            parent_branch = G.nodes[source_id]["data"].get("branch", None)
            if parent_branch is None:
                parent_branch = G.nodes[source_id]["data"].get("house", "unknown")
            parent_color = get_color_by_house(parent_branch)
            G.add_edge(
                target_id,
                source_id,
                width=4,
                arrows={"from": {"enabled": True}},
                color=parent_color,
            )
        elif rel_type in ["spouse", "concubine", "former_spouse"]:
            edge = tuple(sorted([source_id, target_id]))
            if edge not in spouse_edges:
                spouse_edges.add(edge)
                G.add_edge(
                    target_id,
                    source_id,
                    color="white",
                    weight=0.1,
                    dashes=True,
                    arrows={"to": {"enabled": False}},
                )
        else:
            G.add_edge(
                target_id,
                source_id,
                width=2,
                dashes=True,
                arrows={"to": {"enabled": False}},
            )
    return G


def load_family_members(member_docs: list[dict[Any, Any]]):
    """
    Load all family member JSON files from the data directory.
    Returns a list of FamilyMember instances.
    """
    members = []
    for record in member_docs:
        member = FamilyMember.model_validate(record)
        members.append(member)
    return members


def load_relationships(relationship_docs: list[dict[Any, Any]]):
    """Load all relationship JSON files from the data directory.
    Returns a list of Relationship instances.
    """
    relationships = []
    for record in relationship_docs:
        relationship = Relationship.model_validate(record)
        relationships.append(relationship)

    return relationships
