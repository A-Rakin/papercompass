from pathlib import Path


UPLOAD_DIR = Path("uploads")

DEMO_DIR = Path("demo_papers")


def create_directories():

    UPLOAD_DIR.mkdir(exist_ok=True)

    DEMO_DIR.mkdir(exist_ok=True)


def load_css(file_path: str) -> None:
    """
    Inject a custom CSS file into the Streamlit session.
    """
    import streamlit as st
    path = Path(file_path)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)