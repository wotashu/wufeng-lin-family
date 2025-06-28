from pathlib import Path

import graphviz
import streamlit as st
from pyvis.network import Network
from streamlit.components import v1 as components

from .graph_create import create_family_graph, get_member_key
from .models import FamilyMember, Relationship


def render_family_graph(
    members: list[FamilyMember],
    relationships: list[Relationship],
    name_display_type: str | None = None,
    plot_height: int = 600,
):
    graph = create_family_graph(
        members, relationships, name_display_type=name_display_type
    )

    # Let the user select a layout
    layout_option = st.selectbox(
        "Select Graph Layout", options=["default", "hierarchical"]
    )

    # Create a Pyvis Network with a fixed height if desired
    net = Network(
        height=f"{plot_height}px", width="100%", directed=True, bgcolor="#222222"
    )

    # Apply layout options.
    if layout_option == "hierarchical":
        net.from_nx(graph)

        # Use the generation attribute to set the hierarchical level
        for node in net.nodes:
            # Each node should have a "generation" attribute if provided
            if "generation" in node:
                # Assign the generation value to a "level" property.
                node["level"] = node["generation"]

        net.set_options("""
        var options = {
            "layout": {
                "hierarchical": {
                    "enabled": true,
                    "levelSeparation": 150,
                    "nodeSpacing": 100,
                    "treeSpacing": 200,
                    "direction": "UD",
                    "sortMethod": "hubsize",
                    "parentCentralization": true
                }
            },
            "physics": {
                "enabled": false
            }
        }
        """)
    else:
        # Default (force-directed) layout
        net.from_nx(graph)
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

    for node in net.nodes:
        # Use the node's main color for the label text color.
        node["font"] = {"color": "#FFFFFF"}

    # Re-generate the interactive HTML to include layout changes.
    net.write_html("family_graph_interactive.html", notebook=False)

    html_file = Path("family_graph_interactive.html")
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Inject custom CSS to override the frame styles.
        custom_css = """
        <style>
            /* Adjust the pyvis network container */
            #mynetwork {
                border: 2px solid #222222;
                background-color: #222222;
                margin: 0 auto;
            }
            body {
                background-color: #222222;
            }
        </style>
        """
        # Insert the CSS block right before the closing </head> tag.
        html_content = html_content.replace("</head>", custom_css + "</head>")

        components.html(html_content, height=plot_height + 10, scrolling=True)
    else:
        st.write("Interactive graph file not found.")


def render_family_graph_graphviz(
    members, relationships, name_language: str | None = None, plot_height: int = 600
):
    """
    Render a hierarchical family graph using Graphviz (top-down).
    """
    dot = graphviz.Digraph(comment="Family Tree", format="png")
    dot.attr(rankdir="LR")  # Top to Bottom
    dot.attr(
        size=f"{plot_height * 1000},{plot_height * 1000}"
    )  # Set size based on plot height

    # Add nodes
    for member in members:
        node_id = str(member.id)
        label = (
            member.name.english
            or member.name.hanzi
            or get_member_key(member, name_language)
        )
        dot.node(node_id, label)

    # Add edges using the relationships collection
    for rel in relationships:
        source_id = str(rel.source_id)
        target_id = str(rel.target)
        rel_type = rel.type

        # Only add edge if both nodes exist
        # (optional, but prevents errors if data is incomplete)
        # You can build a set of node_ids for efficiency if needed
        dot.edge(source_id, target_id, label=rel_type)

    st.graphviz_chart(dot, use_container_width=True)
