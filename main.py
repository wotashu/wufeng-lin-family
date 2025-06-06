import json
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

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
            member = FamilyMember.parse_obj(record)
            members.append(member)
        except Exception as e:
            print(f"Error parsing record: {record}\n{e}")
    return members


def get_member_key(member: FamilyMember) -> str:
    """
    Get a unique key for the member.
    Prefer name.english; if missing, use name.hanzi.
    Always return a string.
    """
    if member.name.english:
        return member.name.english
    if member.name.hanzi:
        return member.name.hanzi
    return "missing_name"


def create_family_graph(members):
    """
    Create an undirected graph from a list of FamilyMember instances.
    Nodes are keyed by the canonical family member name.
    Edges are added for both 'parents' and 'children' relationships.
    """
    G = nx.Graph()
    # Build a mapping from key -> member instance
    mapping = {}
    for member in members:
        key = get_member_key(member)
        mapping[key] = member
        # Add node with optional additional data
        G.add_node(key, label=key, data=member.dict())

    # For each member, connect to parents and children (undirected)
    for member in members:
        child_key = get_member_key(member)
        # Process parent's relationships
        for parent in member.parents:
            if isinstance(parent, str):
                parent_key = parent
            else:
                parent_key = get_member_key(parent)
            # Add edge if both nodes exist and avoid self-loop
            if parent_key in G.nodes and parent_key != child_key:
                G.add_edge(child_key, parent_key)
        # Process children relationships
        for child in member.children:
            if isinstance(child, str):
                ch_key = child
            else:
                ch_key = get_member_key(child)
            if ch_key in G.nodes and ch_key != child_key:
                G.add_edge(child_key, ch_key)
    return G


def main():
    json_path = Path("data/combined_houses.json")
    members = load_family_members(json_path)
    print(f"Loaded {len(members)} family members.")

    family_graph = create_family_graph(members)
    print(
        f"Graph has {family_graph.number_of_nodes()} nodes and {family_graph.number_of_edges()} edges."
    )

    # Optionally, display the graph using matplotlib
    pos = nx.spring_layout(family_graph)
    nx.draw(family_graph, pos, with_labels=True, node_size=500, font_size=8)
    plt.show()


if __name__ == "__main__":
    main()
