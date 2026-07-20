"""
===============================================================================
PaperCompass
Sidebar Component

Responsibilities
----------------
1. Upload research papers
2. Load demo papers
3. Build vector database
4. Display statistics
5. Show uploaded papers
===============================================================================
"""

from pathlib import Path
import shutil

import streamlit as st

from pdf_loader import PDFLoader
from chunker import TextChunker
from embeddings import EmbeddingEngine
from search import SemanticSearcher
from llm import PaperCompassLLM


UPLOAD_DIR = Path("uploads")
DEMO_DIR = Path("demo_papers")


def save_uploaded_files(uploaded_files):
    """
    Save uploaded PDFs into uploads folder.
    """

    UPLOAD_DIR.mkdir(exist_ok=True)

    saved = []

    for file in uploaded_files:

        destination = UPLOAD_DIR / file.name

        with open(destination, "wb") as f:
            f.write(file.getbuffer())

        saved.append(destination)

    return saved


def load_demo_papers():

    """
    Copy demo papers into uploads folder.
    """

    UPLOAD_DIR.mkdir(exist_ok=True)

    copied = 0

    for pdf in DEMO_DIR.glob("*.pdf"):

        shutil.copy(pdf, UPLOAD_DIR / pdf.name)

        copied += 1

    return copied


def build_knowledge_base():

    """
    Build the RAG pipeline.
    """

    with st.spinner("Reading papers..."):

        loader = PDFLoader()

        papers = loader.load_papers()

    with st.spinner("Chunking papers..."):

        chunker = TextChunker()

        chunks = chunker.chunk_all_papers(papers)

    with st.spinner("Generating embeddings..."):

        engine = EmbeddingEngine()

        embeddings = engine.create_embeddings(chunks)

        engine.build_index(embeddings)

    with st.spinner("Preparing search engine..."):

        searcher = SemanticSearcher(engine)

        llm = PaperCompassLLM()

    st.session_state.papers = papers
    st.session_state.chunks = chunks
    st.session_state.engine = engine
    st.session_state.searcher = searcher
    st.session_state.llm = llm

    st.success("Knowledge Base Ready!")


def render_sidebar():

    """
    Render the left sidebar.
    """

    with st.sidebar:

        st.title("📚 PaperCompass")

        st.caption("AI Research Workspace")

        st.divider()

        ###################################################################
        # Mode
        ###################################################################

        mode = st.radio(

            "Choose Mode",

            [

                "Upload Your Papers",

                "Use Demo Papers"

            ]

        )

        ###################################################################
        # Upload
        ###################################################################

        if mode == "Upload Your Papers":

            uploaded_files = st.file_uploader(

                "Upload PDFs",

                type=["pdf"],

                accept_multiple_files=True

            )

            if uploaded_files:

                save_uploaded_files(uploaded_files)

                st.success(

                    f"{len(uploaded_files)} paper(s) uploaded."

                )

        ###################################################################
        # Demo
        ###################################################################

        else:

            if st.button(

                "Load Demo Papers",

                use_container_width=True

            ):

                count = load_demo_papers()

                st.success(

                    f"{count} demo papers loaded."

                )

        ###################################################################
        # Build
        ###################################################################

        st.divider()

        if st.button(

            "🚀 Build Knowledge Base",

            use_container_width=True,

            type="primary"

        ):

            build_knowledge_base()

        ###################################################################
        # Statistics
        ###################################################################

        st.divider()

        st.subheader("Statistics")

        papers = len(st.session_state.get("papers", []))

        chunks = len(st.session_state.get("chunks", []))

        pages = sum(

            paper["metadata"]["pages"]

            for paper in st.session_state.get("papers", [])

        )

        st.metric(

            "Papers",

            papers

        )

        st.metric(

            "Pages",

            pages

        )

        st.metric(

            "Chunks",

            chunks

        )

        ###################################################################
        # Uploaded Papers
        ###################################################################

        st.divider()

        st.subheader("Uploaded Papers")

        if papers == 0:

            st.info(

                "No papers indexed."

            )

        else:

            for paper in st.session_state["papers"]:

                metadata = paper["metadata"]

                with st.expander(

                    metadata["filename"]

                ):

                    st.write(

                        f"**Author:** {metadata['author']}"

                    )

                    st.write(

                        f"**Pages:** {metadata['pages']}"

                    )

        ###################################################################
        # Conversation
        ###################################################################

        st.divider()

        if st.button(

            "🗑 Clear Conversation",

            use_container_width=True

        ):

            st.session_state.messages = []

            st.success(

                "Conversation cleared."

            )

        st.divider()

        st.caption("Version 1.0")