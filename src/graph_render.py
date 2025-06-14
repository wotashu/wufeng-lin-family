from pathlib import Path

import streamlit as st
from pyvis.network import Network
from streamlit.components import v1 as components

from .graph_create import create_family_graph  # import any necessary functions
from .models import FamilyMember


def render_family_graph(
    members: list[FamilyMember], cannon_key: str | None = None, plot_height: int = 600
):
    graph = create_family_graph(members, cannon_key)

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
        net.set_options("""
        var options = {
            "layout": {
                "hierarchical": {
                    "enabled": true,
                    "levelSeparation": 150,
                    "nodeSpacing": 100,
                    "treeSpacing": 200,
                    "direction": "UD",
                    "sortMethod": "hubsize"
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
