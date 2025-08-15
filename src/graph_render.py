import json
from pathlib import Path

import streamlit as st
from pyvis.network import Network
from streamlit.components import v1 as components

from .graph_create import create_family_graph
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
        direction = st.selectbox("Select direction", options=["UD", "LR"])
        net.from_nx(graph)

        # Use the generation attribute to set the hierarchical level
        for node in net.nodes:
            # Each node should have a "generation" attribute if provided
            node["shape"] = "box"  # or "ellipse"
            if "generation" in node:
                # Assign the generation value to a "level" property.
                node["level"] = node["generation"]

            # --- Add this block to assign a group based on house/branch ---
            # The 'data' attribute comes from your create_family_graph function
            if "data" in node and "house" in node["data"]:
                # You can group by house, or get more specific by grouping by branch
                group_key = node["data"].get("branch") or node["data"].get("house")
                if group_key:
                    node["group"] = group_key
            # --- End of new block ---

        options = {
            "layout": {
                "hierarchical": {
                    "enabled": True,
                    "levelSeparation": 150,
                    "nodeSpacing": 200,
                    "treeSpacing": 200,
                    "direction": direction,
                    "sortMethod": "hubsize",
                    "parentCentralization": True,
                }
            },
            "physics": {"enabled": False},
            "nodes": {"shape": "box"},
        }

        net.set_options(f"var options = {json.dumps(options)}")
    else:
        # Default (force-directed) layout
        net.from_nx(graph)

        options = {
            "nodes": {"font": {"size": 16, "face": "arial", "color": "#ffffff"}},
            "edges": {"color": {"inherit": True}},
            "physics": {
                "enabled": True,
                "hierarchicalRepulsion": {
                    "centralGravity": 0,
                    "springLength": 100,
                    "springConstant": 0.01,
                    "nodeDistance": 120,
                    "damping": 0.09,
                },
                "minVelocity": 0.75,
            },
        }
        net.set_options(f"var options = {json.dumps(options)}")

    for node in net.nodes:
        # Use the node's main color for the label text color.
        node["font"] = {"color": "#FFFFFFFF"}

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
