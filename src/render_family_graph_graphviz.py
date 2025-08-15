from collections import defaultdict

import graphviz
import streamlit as st

from src.graph_create import get_color_by_house, get_member_key


def render_family_graph_graphviz(
    members,
    relationships,
    name_language: str | None = None,
    plot_height: int = 1000,
):
    """
    Render a hierarchical family graph using Graphviz (top-down) with custom node colors.
    """

    orientation_selection = st.selectbox(
        "Select Graph Orientation",
        options=["TB (Top-Bottom)", "LR (Left-Right)"],
        index=0,
    )
    orientation = "TB"

    if orientation_selection == "LR (Left-Right)":
        orientation = "LR"

    dot = graphviz.Digraph(comment="Family Tree", format="png")
    dot.attr(rankdir=orientation)  # Top to Bottom
    dot.attr(
        size=f"{plot_height * 1000},{plot_height * 1000}"
    )  # Set size based on plot height

    # Add nodes with custom fill color
    for member in members:
        node_id = str(member.id)
        label = (
            member.name.english
            or member.name.hanzi
            or get_member_key(member, name_language)
        )
        # Use your color function (adjust as needed)
        house_branch = member.branch or member.house or "unknown"
        fillcolor = get_color_by_house(house_branch)
        dot.node(
            node_id,
            label,
            style="filled",
            fillcolor=fillcolor,
            fontcolor="black",
            color="white",  # border color
        )

    # Group nodes by generation for same-rank placement
    generation_groups = defaultdict(list)
    for member in members:
        node_id = str(member.id)
        generation = getattr(member, "generation", None)
        if generation is not None:
            generation_groups[generation].append(node_id)

    for generation, node_ids in generation_groups.items():
        with dot.subgraph() as s:  # type: ignore
            s.attr(rank="same")
            for node_id in node_ids:
                s.node(node_id)
    # Add edges using the relationships collection
    for rel in relationships:
        source_id = str(rel.source_id)
        target_id = str(rel.target)
        rel_type = rel.type
        dot.edge(source_id, target_id, label=rel_type)

    st.graphviz_chart(dot, use_container_width=True)

    st.info(
        "To save the graph as SVG, right-click the graph, choose 'Inspect', find the <svg> element, and save it as an SVG file. Direct SVG/PNG export is not available on this server."
    )
