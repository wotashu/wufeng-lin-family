import json

import networkx as nx
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

from src.models import FamilyMember

with open("data/combined_houses.json", "r", encoding="utf-8") as infile:
    family_json = json.load(infile)

for item in family_json:
    FamilyMember(item)

# Initialize a directed graph
family_graph = nx.DiGraph()

# Add nodes and relationships to the graph
for person, details in family_data.items():
    # Add the person as a node
    family_graph.add_node(person, note=details.get("note", ""))

    # Add spouse relationship as an undirected edge
    if "spouse" in details and details["spouse"]:
        family_graph.add_edge(person, details["spouse"], relationship="spouse")
        family_graph.add_node(details["spouse"])  # Ensure spouse is also a node

    # Add former spouse relationship
    if "former_spouse" in details and details["former_spouse"]:
        family_graph.add_edge(
            person, details["former_spouse"], relationship="former_spouse"
        )
        family_graph.add_node(
            details["former_spouse"]
        )  # Ensure former spouse is also a node

    # Add parent-child relationships
    for child in details.get("children", []):
        family_graph.add_node(child)  # Ensure child is a node
        family_graph.add_edge(person, child, relationship="parent")

# Convert NetworkX graph to Pyvis Network
net = Network(height="750px", width="100%", directed=True)
net.from_nx(family_graph)

# Customize node and edge appearance
for node, data in family_graph.nodes(data=True):
    net.get_node(node)["title"] = data.get("note", "")  # Add hover text
    net.get_node(node)["color"] = "lightblue"  # Set node color

for edge in family_graph.edges(data=True):
    if edge[2]["relationship"] == "spouse":
        net.add_edge(edge[0], edge[1], color="green")
    elif edge[2]["relationship"] == "former_spouse":
        net.add_edge(edge[0], edge[1], color="red")
    elif edge[2]["relationship"] == "parent":
        net.add_edge(edge[0], edge[1], color="blue")

# Save the graph as an HTML file
try:
    path = "/tmp"
    net.save_graph(f"{path}/family_tree.html")
    HtmlFile = open(f"{path}/family_tree.html", "r", encoding="utf-8")

except FileNotFoundError:
    path = "/html_files"
    net.save_graph(f"{path}/family_tree.html")
    HtmlFile = open(f"{path}/family_tree.html", "r", encoding="utf-8")

# Streamlit app
st.title("Family Tree Visualization")

components.html(open(f"{path}/family_tree.html", "r").read(), height=750)
