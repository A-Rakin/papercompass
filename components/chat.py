"""
===============================================================================
PaperCompass
Chat Component

Description
-----------
This module handles the complete chat interface, including semantic retrieval,
LLM integration (via Groq), citation badges, copy boxes, download exports,
and conversation statistics.
===============================================================================
"""

from __future__ import annotations
import streamlit as st
import time
import json
from datetime import datetime


class ChatUI:

    def __init__(self, searcher=None, llm=None):
        self.searcher = searcher if searcher is not None else st.session_state.get("searcher")
        self.llm = llm if llm is not None else st.session_state.get("llm")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        if "current_question" not in st.session_state:
            st.session_state.current_question = None

    def render_welcome(self):
        st.markdown("## 💬 Chat with Your Research Papers")
        if len(st.session_state.messages) > 0:
            return

        st.info(
            """
### 👋 Welcome to PaperCompass

Upload research papers and ask questions naturally.

Example:

• Summarize the paper.

• What dataset was used?

• Explain methodology.

• What optimizer was used?

• Compare experiments.

• What are the future works?
"""
        )

    def render_history(self):
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "time" in message:
                    st.caption(f"🕒 {message['time']}")

    def render_suggestions(self):
        st.markdown("### 💡 Quick Questions")

        suggestions = [
            "Summarize this paper",
            "What dataset was used?",
            "Explain the methodology",
            "What are the future works?"
        ]

        cols = st.columns(2)

        for index, question in enumerate(suggestions):
            with cols[index % 2]:
                if st.button(
                    question,
                    key=f"chat_{index}",
                    use_container_width=True
                ):
                    st.session_state.current_question = question

    def get_user_question(self):
        user_question = st.chat_input(
            "Ask anything about your research papers..."
        )

        if user_question:
            return user_question

        if st.session_state.current_question:
            question = st.session_state.current_question
            st.session_state.current_question = None
            return question

        return None

    def get_timestamp(self) -> str:
        return datetime.now().strftime("%I:%M %p")

    def save_message(self, role: str, content: str, sources=None, context: str = ""):
        st.session_state.messages.append(
            {
                "role": role,
                "content": content,
                "sources": sources if sources else [],
                "context": context,
                "time": self.get_timestamp()
            }
        )

    def render_user_message(self, question: str):
        with st.chat_message("user"):
            st.markdown(question)

    def retrieve_context(self, question: str):
        if self.searcher is None:
            return None

        return self.searcher.retrieve(
            question=question,
            top_k=3
        )

    def generate_answer(self, question: str, context: str):
        if self.llm is None:
            return "LLM is not initialized."

        return self.llm.generate(
            question=question,
            context=context
        )

    def render_similarity(self, retrieval):
        similarity = retrieval.get("similarity", 0.0)
        st.markdown("### 📈 Semantic Similarity")
        progress = max(0.0, min(float(similarity), 1.0))
        st.progress(progress)
        st.caption(f"Similarity Score : {progress:.2%}")

    def render_citation_badges(self, retrieval):
        sources = retrieval.get("sources", [])
        if not sources:
            return
        st.markdown("### 🏷 Referenced Papers")
        cols = st.columns(min(4, len(sources)))
        for i, source in enumerate(sources):
            with cols[i]:
                st.info(
                    f"[{i+1}] {source.get('paper','Unknown')}"
                )

    def render_sources(self, retrieval):
        sources = retrieval.get("sources", [])
        if not sources:
            return

        st.markdown("### 📚 Source Papers")
        for source in sources:
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(
                        f"#### 📄 {source.get('paper','Unknown')}"
                    )
                    st.write(
                        f"**Title:** {source.get('title','Unknown')}"
                    )
                    st.write(
                        f"**Author:** {source.get('author','Unknown')}"
                    )
                with col2:
                    st.metric(
                        "Chunk",
                        source.get("chunk_id", "-")
                    )
                    st.metric(
                        "Score",
                        f"{source.get('score', 0):.2f}"
                    )

    def render_context(self, retrieval):
        context = retrieval.get("context", "")
        with st.expander("🔍 Retrieved Context", expanded=False):
            st.code(context, language="text")

    def render_copy_box(self, answer):
        with st.expander("📋 Copy Answer"):
            st.text_area(
                "Answer",
                value=answer,
                height=220
            )

    def render_copy_button(self, answer):
        st.markdown("### 📋 Copy Answer")
        st.code(answer, language="text")

    def render_feedback(self):
        st.markdown("### ⭐ Was this answer helpful?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button(
                "👍 Helpful",
                use_container_width=True,
                key="feedback_yes"
            ):
                st.success("Thanks for your feedback!")
        with c2:
            if st.button(
                "👎 Needs Improvement",
                use_container_width=True,
                key="feedback_no"
            ):
                st.info("Feedback recorded.")

    def export_chat_txt(self):
        conversation = ""
        for message in st.session_state.messages:
            role = message["role"].upper()
            content = message["content"]
            conversation += f"{role}\n"
            conversation += "-" * 50 + "\n"
            conversation += content
            conversation += "\n\n"
        filename = f"papercompass_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        return conversation, filename

    def export_chat_json(self):
        filename = f"papercompass_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        data = json.dumps(
            st.session_state.messages,
            indent=4,
            ensure_ascii=False
        )
        return data, filename

    def render_export_buttons(self):
        st.markdown("### 📤 Export Conversation")
        txt_data, txt_name = self.export_chat_txt()
        json_data, json_name = self.export_chat_json()

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📄 Export TXT",
                data=txt_data,
                file_name=txt_name,
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            st.download_button(
                label="📦 Export JSON",
                data=json_data,
                file_name=json_name,
                mime="application/json",
                use_container_width=True
            )

    def render_chat_statistics(self):
        """Render chat statistics using custom HTML cards."""
        st.markdown("### 📊 Conversation Statistics")
        total_messages = len(st.session_state.messages)
        user_questions = len([m for m in st.session_state.messages if m["role"] == "user"])
        ai_answers = len([m for m in st.session_state.messages if m["role"] == "assistant"])

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f"""
                <div class="custom-metric-card">
                    <div class="metric-val">{total_messages}</div>
                    <div class="metric-lbl">💬 Messages</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                f"""
                <div class="custom-metric-card">
                    <div class="metric-val">{user_questions}</div>
                    <div class="metric-lbl">👤 Questions</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c3:
            st.markdown(
                f"""
                <div class="custom-metric-card">
                    <div class="metric-val">{ai_answers}</div>
                    <div class="metric-lbl">🤖 Answers</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    def render_markdown_help(self):
        with st.expander("📝 Markdown Supported"):
            st.markdown(
                """
You can ask for

- Tables

- Bullet Lists

- Equations

- Python Code

- Algorithms

- Literature Review

- Summary

- Comparison
"""
            )

    def stream_text(self, text: str, speed: float = 0.015) -> str:
        placeholder = st.empty()
        streamed_text = ""
        words = text.split()
        for word in words:
            streamed_text += word + " "
            placeholder.markdown(streamed_text + "▌")
            time.sleep(speed)
        placeholder.markdown(streamed_text)
        return streamed_text

    def thinking_animation(self):
        placeholder = st.empty()
        messages = [
            "🔍 Searching papers...",
            "📚 Retrieving relevant chunks...",
            "🧠 Understanding your question...",
            "🤖 Generating answer..."
        ]
        for msg in messages:
            placeholder.info(msg)
            time.sleep(0.35)
        placeholder.empty()

    def render_streaming_answer(self, answer, retrieval):
        with st.chat_message("assistant"):
            self.thinking_animation()
            final_answer = self.stream_text(answer)
            st.divider()
            self.render_similarity(retrieval)
            self.render_citation_badges(retrieval)
            self.render_sources(retrieval)
            self.render_context(retrieval)
            self.render_copy_box(final_answer)
            self.render_copy_button(final_answer)
            self.render_feedback()
            self.render_export_buttons()
            self.render_chat_statistics()
            self.render_markdown_help()

    def process_question(self, question: str):
        if self.searcher is None:
            st.error("Please build the Knowledge Base first.")
            return

        with st.spinner("Searching relevant papers..."):
            retrieval = self.retrieve_context(question)

        if retrieval is None:
            st.error("Search Engine not available.")
            return

        if not retrieval["found"]:
            answer = (
                "I could not find any relevant information "
                "inside the uploaded papers."
            )
            with st.chat_message("assistant"):
                st.warning(answer)

            self.save_message(
                "assistant",
                answer,
                [],
                ""
            )
            return

        with st.spinner("Generating answer..."):
            answer = self.generate_answer(
                question,
                retrieval["context"]
            )

        self.render_streaming_answer(
            answer,
            retrieval
        )

        self.save_message(
            "assistant",
            answer,
            retrieval.get("sources", []),
            retrieval.get("context", "")
        )

    def render(self):
        self.render_welcome()
        self.render_history()
        self.render_suggestions()
        self.render_markdown_help()

        question = self.get_user_question()
        if question is None:
            return

        # Render user message immediately
        self.render_user_message(question)
        
        # Save user message to session state
        self.save_message("user", question)
        
        # Process the question (searches, streams response, and saves assistant response)
        self.process_question(question)
        
        # Rerun to clear input and update history
        st.rerun()


def render_chat(searcher=None, llm=None):
    """
    Module level entry point for rendering the Chat interface.
    """
    chat_ui = ChatUI(searcher=searcher, llm=llm)
    chat_ui.render()
