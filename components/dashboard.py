"""
===============================================================================
PaperCompass
Dashboard Component

Description:
    This module renders the dashboard section of PaperCompass.
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

    def __init__(self) -> None:
        self.papers = st.session_state.get("papers", [])
        self.chunks = st.session_state.get("chunks", [])
        self.engine = st.session_state.get("engine")
        self.searcher = st.session_state.get("searcher")
        self.llm = st.session_state.get("llm")

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

    def render_statistics(self) -> None:
        """Display dashboard metrics using custom HTML cards."""
        total_papers = len(self.papers)
        total_chunks = len(self.chunks)
        total_pages = sum(
            paper["metadata"]["pages"]
            for paper in self.papers
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.markdown(
                f"""
                <div class="custom-metric-card">
                    <div class="metric-val">{total_papers}</div>
                    <div class="metric-lbl">📄 Papers</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c2:
            st.markdown(
                f"""
                <div class="custom-metric-card">
                    <div class="metric-val">{total_pages}</div>
                    <div class="metric-lbl">📑 Pages</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c3:
            st.markdown(
                f"""
                <div class="custom-metric-card">
                    <div class="metric-val">{total_chunks}</div>
                    <div class="metric-lbl">🧩 Chunks</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with c4:
            embed_model = "MiniLM" if self.engine is not None else "Not Ready"
            st.markdown(
                f"""
                <div class="custom-metric-card">
                    <div class="metric-val">{embed_model}</div>
                    <div class="metric-lbl">🤖 Embedding</div>
                </div>
                """,
                unsafe_allow_html=True
            )

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

    def render_paper_cards(self) -> None:
        """Render uploaded paper cards using custom HTML glassmorphic designs."""
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

            st.markdown(
                f"""
                <div class="custom-paper-card">
                    <h3>📄 {metadata['filename']}</h3>
                    <div class="meta-grid">
                        <div class="meta-item"><span class="meta-label">Title:</span> {metadata.get('title', 'Unknown')}</div>
                        <div class="meta-item"><span class="meta-label">Author:</span> {metadata.get('author', 'Unknown')}</div>
                        <div class="meta-item"><span class="meta-label">Pages:</span> {metadata.get('pages', 0)}</div>
                        <div class="meta-item"><span class="meta-label">Chunks:</span> {chunk_count}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
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
