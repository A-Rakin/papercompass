"""
===============================================================================
PaperCompass
AI Research Paper Assistant

Author : Your Name

Description
-----------
PaperCompass is a Retrieval-Augmented Generation (RAG) application that allows
researchers to upload one or more research papers and ask natural language
questions.

Main Responsibilities
---------------------
1. Upload PDFs
2. Build embeddings
3. Semantic search
4. Question answering using Groq
5. Beautiful Streamlit UI
===============================================================================
"""

import os
from pathlib import Path

import streamlit as st

from pdf_loader import PDFLoader
from chunker import TextChunker
from embeddings import EmbeddingEngine
from search import SemanticSearcher
from llm import PaperCompassLLM

###############################################################################
# PAGE CONFIGURATION
###############################################################################

st.set_page_config(
    page_title="PaperCompass",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

###############################################################################
# CUSTOM CSS
###############################################################################

st.markdown(
    """
<style>

/* ---------------------------------------------------------- */
/* Hide Streamlit Branding */
/* ---------------------------------------------------------- */

#MainMenu {
    visibility:hidden;
}

footer{
    visibility:hidden;
}

header{
    visibility:hidden;
}

/* ---------------------------------------------------------- */
/* Main background */
/* ---------------------------------------------------------- */

.stApp{

    background:#F4F7FC;

}

/* ---------------------------------------------------------- */
/* Main title */
/* ---------------------------------------------------------- */

.main-title{

    font-size:42px;

    font-weight:700;

    color:#1E3A8A;

    margin-bottom:5px;

}

/* ---------------------------------------------------------- */

.subtitle{

    color:#5B6475;

    font-size:18px;

    margin-bottom:25px;

}

/* ---------------------------------------------------------- */
/* Paper Card */
/* ---------------------------------------------------------- */

.paper-card{

    background:white;

    padding:18px;

    border-radius:12px;

    box-shadow:0px 2px 12px rgba(0,0,0,0.08);

    margin-bottom:15px;

}

/* ---------------------------------------------------------- */
/* Answer Card */
/* ---------------------------------------------------------- */

.answer-box{

    background:white;

    border-left:6px solid #2563EB;

    padding:20px;

    border-radius:12px;

    box-shadow:0px 3px 15px rgba(0,0,0,.08);

}

/* ---------------------------------------------------------- */

.metric-box{

    background:white;

    border-radius:12px;

    padding:15px;

    text-align:center;

    box-shadow:0px 3px 12px rgba(0,0,0,.08);

}

/* ---------------------------------------------------------- */

.source-box{

    background:#EEF4FF;

    border-radius:10px;

    padding:15px;

}

/* ---------------------------------------------------------- */

.chat-user{

    background:#DCF8C6;

    padding:15px;

    border-radius:10px;

}

.chat-ai{

    background:white;

    padding:15px;

    border-radius:10px;

}

</style>
""",
    unsafe_allow_html=True,
)

###############################################################################
# SESSION STATE
###############################################################################

if "messages" not in st.session_state:
    st.session_state.messages = []

if "engine" not in st.session_state:
    st.session_state.engine = None

if "searcher" not in st.session_state:
    st.session_state.searcher = None

if "llm" not in st.session_state:
    st.session_state.llm = None

if "papers" not in st.session_state:
    st.session_state.papers = []

if "chunks" not in st.session_state:
    st.session_state.chunks = []

###############################################################################
# HEADER
###############################################################################

st.markdown(
    """
<div class="main-title">

📚 PaperCompass

</div>

<div class="subtitle">

An Intelligent Research Paper Assistant powered by
Semantic Search, FAISS and Groq LLM.

</div>
""",
    unsafe_allow_html=True,
)

###############################################################################
# TWO COLUMN LAYOUT
###############################################################################

left_col, right_col = st.columns([1, 2], gap="large")

###############################################################################
# LEFT PANEL
###############################################################################

with left_col:

    st.subheader("📂 Upload Research Papers")

    uploaded_files = st.file_uploader(
        label="Select one or more PDF papers",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload research papers in PDF format."
    )

    st.divider()

    ###########################################################################
    # Save Uploaded Files
    ###########################################################################

    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    if uploaded_files:

        for uploaded_file in uploaded_files:

            save_path = upload_dir / uploaded_file.name

            with open(save_path, "wb") as file:
                file.write(uploaded_file.getbuffer())

    ###########################################################################
    # Build Knowledge Base Button
    ###########################################################################

    if st.button(
        "🚀 Build Knowledge Base",
        use_container_width=True,
        type="primary"
    ):

        with st.spinner("Reading research papers..."):

            loader = PDFLoader()

            papers = loader.load_papers()

            st.session_state.papers = papers

        with st.spinner("Chunking papers..."):

            chunker = TextChunker(
                chunk_size=300,
                overlap=50
            )

            chunks = chunker.chunk_all_papers(papers)

            st.session_state.chunks = chunks

        with st.spinner("Generating embeddings..."):

            engine = EmbeddingEngine()

            embeddings = engine.create_embeddings(chunks)

            engine.build_index(embeddings)

        with st.spinner("Preparing semantic search..."):

            searcher = SemanticSearcher(engine)

            llm = PaperCompassLLM()

        st.session_state.engine = engine
        st.session_state.searcher = searcher
        st.session_state.llm = llm

        st.success("Knowledge Base Ready!")

    ###########################################################################
    # Statistics
    ###########################################################################

    st.divider()

    st.subheader("📊 Statistics")

    total_papers = len(st.session_state.papers)

    total_chunks = len(st.session_state.chunks)

    total_pages = sum(
        paper["metadata"]["pages"]
        for paper in st.session_state.papers
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            label="Papers",
            value=total_papers
        )

    with col2:

        st.metric(
            label="Chunks",
            value=total_chunks
        )

    st.metric(
        label="Pages Indexed",
        value=total_pages
    )

    ###########################################################################
    # Uploaded Papers
    ###########################################################################

    st.divider()

    st.subheader("📚 Uploaded Papers")

    if len(st.session_state.papers) == 0:

        st.info("No papers indexed yet.")

    else:

        for paper in st.session_state.papers:

            metadata = paper["metadata"]

            with st.expander(
                f"📄 {metadata['filename']}",
                expanded=False
            ):

                st.write(
                    f"**Title:** {metadata['title']}"
                )

                st.write(
                    f"**Author:** {metadata['author']}"
                )

                st.write(
                    f"**Pages:** {metadata['pages']}"
                )

    ###########################################################################
    # Clear Conversation
    ###########################################################################

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.success("Conversation cleared.")

    ###########################################################################
    # Footer
    ###########################################################################

    st.divider()

    st.caption("📚 PaperCompass v1.0")

    st.caption("Powered by Streamlit + FAISS + Groq")

###############################################################################
# RIGHT PANEL
###############################################################################

with right_col:

    st.subheader("💬 Chat with Your Research Papers")

    # -----------------------------------------------------------------------
    # Welcome Screen
    # -----------------------------------------------------------------------

    if st.session_state.searcher is None:

        st.info(
            """
            👋 Welcome to **PaperCompass**

            **Getting Started**

            1. Upload one or more research papers.
            2. Click **Build Knowledge Base**.
            3. Ask questions in natural language.

            Example Questions:

            • What dataset was used?

            • Summarize the methodology.

            • What optimizer was used?

            • What are the limitations?

            • What accuracy was achieved?

            • What are the future works?
            """
        )

    # -----------------------------------------------------------------------
    # Display Chat History
    # -----------------------------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            # Show source cards for assistant responses
            if (
                message["role"] == "assistant"
                and "sources" in message
            ):

                with st.expander("📚 Sources"):

                    for source in message["sources"]:

                        st.markdown(
                            f"""
**Paper**

{source['paper']}

**Chunk**

{source['chunk_id']}

**Similarity**

{source['score']:.3f}
"""
                        )

            # Show retrieved context
            if (
                message["role"] == "assistant"
                and "context" in message
            ):

                with st.expander("🔍 Retrieved Context"):

                    st.write(message["context"])

    # -----------------------------------------------------------------------
    # Chat Input
    # -----------------------------------------------------------------------

    question = st.chat_input(
        "Ask anything about the uploaded papers..."
    )

    # -----------------------------------------------------------------------
    # User Asked Question
    # -----------------------------------------------------------------------

    if question:

        # Show user message immediately

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message("user"):

            st.markdown(question)

        # ---------------------------------------------------------------

        with st.chat_message("assistant"):

            if st.session_state.searcher is None:

                st.error(
                    "Please build the Knowledge Base first."
                )

            else:

                with st.spinner("Searching research papers..."):

                    retrieval = (
                        st.session_state.searcher.retrieve(
                            question=question,
                            top_k=3
                        )
                    )

                if not retrieval["found"]:

                    answer = (
                        "I couldn't find relevant information "
                        "in the uploaded papers."
                    )

                    st.warning(answer)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )

                else:

                    with st.spinner("Generating answer..."):

                        answer = (
                            st.session_state.llm.generate(
                                question=question,
                                context=retrieval["context"]
                            )
                        )

                    # ---------------------------------------------------

                    st.markdown(answer)

                    # ---------------------------------------------------
                    # Similarity
                    # ---------------------------------------------------

                    st.success(
                        f"Highest Similarity: "
                        f"{retrieval['similarity']:.3f}"
                    )

                    # ---------------------------------------------------
                    # Sources
                    # ---------------------------------------------------

                    with st.expander(
                        "📚 Source Papers",
                        expanded=False
                    ):

                        for source in retrieval["sources"]:

                            st.markdown(
                                f"""
### 📄 {source['paper']}

**Chunk:** {source['chunk_id']}

**Similarity:** {source['score']:.3f}

**Title:** {source['title']}

**Author:** {source['author']}
"""
                            )

                    # ---------------------------------------------------
                    # Retrieved Context
                    # ---------------------------------------------------

                    with st.expander(
                        "🔍 Retrieved Context"
                    ):

                        st.write(retrieval["context"])

                    # ---------------------------------------------------
                    # Save Assistant Response
                    # ---------------------------------------------------

                    st.session_state.messages.append(

                        {
                            "role": "assistant",

                            "content": answer,

                            "sources": retrieval["sources"],

                            "context": retrieval["context"]
                        }

                    )

