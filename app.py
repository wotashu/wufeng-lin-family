import streamlit as st

from src.graph_display import display_page
from src.member_page import member_page
from src.relationship_page import add_relationship_page


def main():
    st.set_page_config(layout="wide")
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to", options=["Home", "Add / Update Document", "Add Relationship"]
    )

    if page == "Home":
        display_page()
    elif page == "Add / Update Document":
        member_page()
    elif page == "Add Relationship":
        add_relationship_page()


if __name__ == "__main__":
    main()
