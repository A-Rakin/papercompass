"""
===============================================================================
PaperCompass
Author      : Your Name
Project     : PaperCompass - AI Research Paper Assistant
File        : search.py

Description
-----------
This module performs semantic retrieval over indexed research paper chunks.

Responsibilities
----------------
1. Accept a user question.
2. Retrieve the most relevant chunks from FAISS.
3. Filter irrelevant chunks.
4. Combine retrieved chunks into a single context.
5. Return context and metadata for the LLM.

===============================================================================
"""

from typing import Dict, List

from embeddings import EmbeddingEngine


class SemanticSearcher:
    """
    Performs semantic retrieval over indexed research papers.

    Parameters
    ----------
    embedding_engine : EmbeddingEngine
        Initialized embedding engine containing
        the FAISS index.
    """

    def __init__(self, embedding_engine: EmbeddingEngine):

        self.engine = embedding_engine

    # ------------------------------------------------------------------ #
    # Retrieve Context
    # ------------------------------------------------------------------ #

    def retrieve(
        self,
        question: str,
        top_k: int = 3,
        similarity_threshold: float = 0.40
    ) -> Dict:
        """
        Retrieve relevant context for the LLM.

        Parameters
        ----------
        question : str

        top_k : int

        similarity_threshold : float

        Returns
        -------
        dict
        """

        search_results = self.engine.search(
            query=question,
            top_k=top_k
        )

        if len(search_results) == 0:

            return {
                "found": False,
                "context": "",
                "sources": [],
                "similarity": 0.0
            }

        context_parts = []

        sources = []

        similarities = []

        for score, chunk in search_results:

            if score < similarity_threshold:
                continue

            context_parts.append(chunk["text"])

            similarities.append(score)

            sources.append(
                {
                    "paper": chunk["metadata"]["filename"],
                    "chunk_id": chunk["chunk_id"],
                    "score": score,
                    "title": chunk["metadata"]["title"],
                    "author": chunk["metadata"]["author"]
                }
            )

        if len(context_parts) == 0:

            return {
                "found": False,
                "context": "",
                "sources": [],
                "similarity": 0.0
            }

        return {
            "found": True,

            "context": "\n\n".join(context_parts),

            "sources": sources,

            "similarity": max(similarities)
        }


# =============================================================================
# Testing
# =============================================================================

if __name__ == "__main__":

    from pdf_loader import PDFLoader
    from chunker import TextChunker
    from embeddings import EmbeddingEngine

    # -------------------------------------------------------------

    loader = PDFLoader()

    papers = loader.load_papers()

    chunker = TextChunker()

    chunks = chunker.chunk_all_papers(papers)

    engine = EmbeddingEngine()

    embeddings = engine.create_embeddings(chunks)

    engine.build_index(embeddings)

    searcher = SemanticSearcher(engine)

    # -------------------------------------------------------------

    while True:

        question = input("\nAsk a question (exit to quit): ")

        if question.lower() == "exit":
            break

        result = searcher.retrieve(question)

        print("\n")

        if not result["found"]:

            print("No relevant information found.")

            continue

        print("=" * 80)

        print("Similarity :", round(result["similarity"], 3))

        print("\nSources")

        print("-" * 80)

        for source in result["sources"]:

            print(
                f"{source['paper']} "
                f"(Chunk {source['chunk_id']}) "
                f"Score={source['score']:.3f}"
            )

        print("\n")

        print("=" * 80)

        print("Retrieved Context")

        print("=" * 80)

        print(result["context"][:1200])

        print("\n")