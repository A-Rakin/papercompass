"""
===============================================================================
PaperCompass
Dashboard Component

Author:
    Your Name

Description:
    This module renders the dashboard section of PaperCompass.

Responsibilities:
    • Dashboard Header
    • Statistics Cards
    • Knowledge Base Status
    • Model Information
    • Empty State
===============================================================================
"""

from __future__ import annotations

import streamlit as st


class Dashboard:
    """
    Dashboard Component

    Displays:
        - Statistics
        - Knowledge Base Status
        - Model Information
        - Empty State
    """

    ###########################################################################
    # Constructor
    ###########################################################################

    def __init__(self) -> None:

        self.papers = st.session_state.get("papers", [])

        self.chunks = st.session_state.get("chunks", [])

        self.engine = st.session_state.get("engine")

        self.searcher = st.session_state.get("searcher")

        self.llm = st.session_state.get("llm")

    ###########################################################################
    # Header
    ###########################################################################

    def render_header(self) -> None:
        """Render dashboard title."""

        st.markdown(
            """
            ## 📊 Dashboard

            Welcome to **PaperCompass AI Research Workspace**.

            Upload papers, build a semantic knowledge base,
            and chat naturally with your research documents.
            """
        )

    ###########################################################################
    # Statistics
    ###########################################################################

    def render_statistics(self) -> None:
        """Display dashboard metrics."""

        total_papers = len(self.papers)

        total_chunks = len(self.chunks)

        total_pages = sum(

            paper["metadata"]["pages"]

            for paper in self.papers

        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(

                label="📄 Papers",

                value=total_papers

            )

        with c2:

            st.metric(

                label="📑 Pages",

                value=total_pages

            )

        with c3:

            st.metric(

                label="🧩 Chunks",

                value=total_chunks

            )

        with c4:

            if self.engine is None:

                st.metric(

                    label="🤖 Embedding",

                    value="Not Ready"

                )

            else:

                st.metric(

                    label="🤖 Embedding",

                    value="MiniLM"

                )

    ###########################################################################
    # Knowledge Base Status
    ###########################################################################

    def render_kb_status(self) -> None:

        st.subheader("Knowledge Base")

        if self.engine is None:

            st.warning(
                """
                No Knowledge Base detected.

                Please upload one or more research papers
                and build the vector database.
                """
            )

            return

        st.success("Knowledge Base Ready")

        col1, col2 = st.columns(2)

        with col1:

            st.write("**Semantic Search**")

            st.success("Available")

        with col2:

            st.write("**LLM**")

            st.success("Connected")

    ###########################################################################
    # Model Information
    ###########################################################################

    def render_model_information(self) -> None:

        st.subheader("AI Models")

        col1, col2 = st.columns(2)

        with col1:

            st.info(
                """
                **Embedding Model**

                all-MiniLM-L6-v2
                """
            )

        with col2:

            st.info(
                """
                **Large Language Model**

                Llama 3
                (Groq)
                """
            )

    ###########################################################################
    # Empty State
    ###########################################################################

    def render_empty_state(self) -> bool:
        """
        Returns
        -------
        bool
            True if dashboard should stop rendering.
        """

        if len(self.papers) != 0:

            return False

        st.divider()

        st.info(
            """
            ## 👋 Welcome to PaperCompass

            To get started:

            1. Upload one or more research papers.

            2. Click **Build Knowledge Base**.

            3. Ask questions naturally.

            Example:

            • Summarize the methodology.

            • What dataset was used?

            • What are the limitations?

            • Compare the experiments.
            """
        )

        return True

    ###########################################################################
    # Paper Cards
    ###########################################################################

    def render_paper_cards(self) -> None:
        """Render uploaded paper cards."""

        st.subheader("📚 Indexed Research Papers")

        for index, paper in enumerate(self.papers, start=1):
            metadata = paper["metadata"]

            chunk_count = len(
                [
                    chunk
                    for chunk in self.chunks
                    if chunk["metadata"]["filename"] == metadata["filename"]
                ]
            )

            with st.container(border=True):
                col1, col2 = st.columns([5, 1])

                with col1:
                    st.markdown(f"### 📄 {metadata['filename']}")

                    st.write(f"**Title:** {metadata.get('title', 'Unknown')}")

                    st.write(f"**Author:** {metadata.get('author', 'Unknown')}")

                    st.write(f"**Pages:** {metadata.get('pages', 0)}")

                with col2:
                    st.metric(
                        label="Chunks",
                        value=chunk_count
                    )

                with st.expander("📖 Preview Metadata"):
                    st.json(metadata)

    def render_dataset_analytics(self) -> None:
        st.subheader("📈 Collection Analytics")

        total_words = sum(
            len(chunk["text"].split())
            for chunk in self.chunks
        )

        average_chunk = 0

        if len(self.chunks):
            average_chunk = round(
                total_words / len(self.chunks)
            )

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Total Words",
                f"{total_words:,}"
            )

        with col2:
            st.metric(
                "Average Words / Chunk",
                average_chunk
            )

    def render_recent_activity(self) -> None:
        st.subheader("⚡ Recent Activity")

        if len(self.papers) == 0:
            st.info("No activity found.")
            return

        for paper in reversed(self.papers):
            filename = paper["metadata"]["filename"]
            pages = paper["metadata"]["pages"]

            st.success(
                f"Indexed **{filename}** ({pages} pages)"
            )

    def render_suggestions(self) -> None:
        st.subheader("💡 Suggested Questions")

        suggestions = [
            "Summarize this paper",
            "What dataset was used?",
            "Explain the methodology",
            "What optimizer was used?",
            "What are the limitations?",
            "What are the future works?",
            "Compare the experimental results",
            "What is the main contribution?"
        ]

        cols = st.columns(2)

        for i, question in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(
                    question,
                    key=f"suggestion_{i}",
                    use_container_width=True
                ):
                    st.session_state.current_question = question
                    st.rerun()

    def render_footer(self) -> None:
        st.divider()
        st.caption("📚 PaperCompass v1.0")
        st.caption("Powered by Streamlit • FAISS • SentenceTransformers • Groq")

    def render(self) -> None:
        self.render_header()

        st.divider()

        self.render_statistics()

        st.divider()

        self.render_kb_status()

        st.divider()

        self.render_model_information()

        if self.render_empty_state():
            return

        st.divider()

        self.render_paper_cards()

        st.divider()

        self.render_dataset_analytics()

        st.divider()

        self.render_recent_activity()

        st.divider()

        self.render_suggestions()

        self.render_footer()


def render_dashboard(papers=None, chunks=None):
    """
    Module level entry point for rendering the Dashboard.
    """
    dashboard = Dashboard()
    dashboard.render()