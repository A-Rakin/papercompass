"""
===============================================================================
PaperCompass
Author      : Your Name
Project     : PaperCompass - AI Research Paper Assistant
File        : app.py

Description
-----------
Main Streamlit application entry point.

Responsibilities
----------------
1. Configure Streamlit application.
2. Manage session state.
3. Handle PDF uploads.
4. Initialize RAG pipeline.
5. Connect UI components.

===============================================================================
"""


import streamlit as st
from pathlib import Path
import tempfile
from utils import load_css



from pdf_loader import PDFLoader
from chunker import TextChunker
from embeddings import EmbeddingEngine
from search import SemanticSearcher
from llm import PaperCompassLLM


# UI Components
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.chat import render_chat



# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="PaperCompass",
    page_icon="📚",
    layout="wide"
)



# =============================================================================
# Session State Initialization
# =============================================================================

def initialize_session():

    defaults = {

        "papers": [],

        "chunks": [],

        "embedding_engine": None,

        "engine": None,

        "searcher": None,

        "llm": None,

        "processed": False,

        "processing": False,

        "chat_history": []

    }


    for key, value in defaults.items():

        if key not in st.session_state:

            st.session_state[key] = value




# =============================================================================
# Document Processing Pipeline
# =============================================================================

def process_documents(uploaded_files):

    try:

        st.session_state.processing = True


        progress = st.progress(
            0
        )


        status = st.empty()



        # ---------------------------------------------------------
        # Save Uploaded PDFs
        # ---------------------------------------------------------

        status.info(
            "Saving uploaded papers..."
        )


        temp_dir = Path(
            tempfile.mkdtemp()
        )


        saved_files = []


        for file in uploaded_files:


            file_path = temp_dir / file.name


            with open(
                file_path,
                "wb"
            ) as f:

                f.write(
                    file.getbuffer()
                )


            saved_files.append(
                file_path
            )


        progress.progress(
            20
        )



        # ---------------------------------------------------------
        # PDF Loading
        # ---------------------------------------------------------

        status.info(
            "Extracting text from PDFs..."
        )


        loader = PDFLoader()


        papers = loader.load_papers(
            saved_files
        )


        progress.progress(
            40
        )



        # ---------------------------------------------------------
        # Chunking
        # ---------------------------------------------------------

        status.info(
            "Creating text chunks..."
        )


        chunker = TextChunker()


        chunks = chunker.chunk_all_papers(
            papers
        )


        progress.progress(
            60
        )



        # ---------------------------------------------------------
        # Embeddings + FAISS
        # ---------------------------------------------------------

        status.info(
            "Generating embeddings..."
        )


        engine = EmbeddingEngine()


        embeddings = engine.create_embeddings(
            chunks
        )


        engine.build_index(
            embeddings
        )


        progress.progress(
            85
        )



        # ---------------------------------------------------------
        # Search + LLM
        # ---------------------------------------------------------

        status.info(
            "Initializing AI assistant..."
        )


        searcher = SemanticSearcher(
            engine
        )


        llm = PaperCompassLLM()


        progress.progress(
            100
        )



        # ---------------------------------------------------------
        # Store Session Data
        # ---------------------------------------------------------

        st.session_state.papers = papers

        st.session_state.chunks = chunks

        st.session_state.embedding_engine = engine

        st.session_state.engine = engine

        st.session_state.searcher = searcher

        st.session_state.llm = llm

        st.session_state.processed = True

        st.session_state.processing = False



        status.success(
            "Paper processing completed successfully!"
        )


    except Exception as e:


        st.session_state.processing = False


        st.error(
            f"Processing failed: {str(e)}"
        )




# =============================================================================
# Main Application
# =============================================================================

def main():


    initialize_session()

    load_css("styles/style.css")



    # Sidebar

    uploaded_files = render_sidebar()



    # Process Button

    if uploaded_files:


        if st.button(
            "🚀 Process Papers",
            use_container_width=True
        ):


            process_documents(
                uploaded_files
            )



    # Before Processing

    if not st.session_state.processed:


        st.markdown(
            """
            <div class="welcome-banner">
                <h2>📚 Welcome to PaperCompass</h2>
                <p>Your AI-powered research assistant. To get started, please follow these steps:</p>
                <ol style="margin-left: 20px; color: #CBD5E1; font-size: 15px; line-height: 1.8; margin-top: 10px;">
                    <li>Upload your research papers (PDFs) or choose <strong>Use Demo Papers</strong> in the sidebar.</li>
                    <li>Click the green <strong>🚀 Build Knowledge Base</strong> button at the bottom of the sidebar.</li>
                    <li>The dashboard and chatbot will instantly appear here to answer your questions!</li>
                </ol>
            </div>
            """,
            unsafe_allow_html=True
        )


        return



    # Dashboard Section

    render_dashboard(

        st.session_state.papers,

        st.session_state.chunks

    )



    st.divider()



    # Chat Section

    render_chat(

        st.session_state.searcher,

        st.session_state.llm

    )




# =============================================================================
# Run Application
# =============================================================================

if __name__ == "__main__":

    main()