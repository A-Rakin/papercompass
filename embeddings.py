"""
===============================================================================
PaperCompass
Author      : Your Name
Project     : PaperCompass - AI Research Paper Assistant
File        : embeddings.py

Description
-----------
This module generates semantic embeddings for research paper chunks using
Sentence Transformers and builds a FAISS vector index for efficient retrieval.

Responsibilities
----------------
1. Load a SentenceTransformer model.
2. Convert text chunks into dense vector embeddings.
3. Normalize embeddings.
4. Build a FAISS index.
5. Perform semantic similarity search.

===============================================================================
"""

from typing import List, Dict, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingEngine:
    """
    Embedding engine for semantic search.

    Parameters
    ----------
    model_name : str
        Name of the SentenceTransformer model.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2"
    ) -> None:

        print("Loading embedding model...")

        self.model = SentenceTransformer(model_name)

        self.index = None

        self.chunks = []

    # ------------------------------------------------------------------ #
    # Generate Embeddings
    # ------------------------------------------------------------------ #

    def create_embeddings(
        self,
        chunks: List[Dict]
    ) -> np.ndarray:
        """
        Generate embeddings for every text chunk.

        Parameters
        ----------
        chunks : list

        Returns
        -------
        np.ndarray
        """

        self.chunks = chunks

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return embeddings.astype(np.float32)

    # ------------------------------------------------------------------ #
    # Build FAISS Index
    # ------------------------------------------------------------------ #

    def build_index(
        self,
        embeddings: np.ndarray
    ) -> None:
        """
        Build FAISS index.

        Parameters
        ----------
        embeddings : np.ndarray
        """

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)

        print(f"Indexed {self.index.ntotal} chunks.")

    # ------------------------------------------------------------------ #
    # Search
    # ------------------------------------------------------------------ #

    def search(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Tuple[float, Dict]]:
        """
        Search the vector database.

        Parameters
        ----------
        query : str

        top_k : int

        Returns
        -------
        List[(score, chunk)]
        """

        if self.index is None:
            raise RuntimeError(
                "FAISS index has not been created."
            )

        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype(np.float32)

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        for score, idx in zip(scores[0], indices[0]):

            if idx == -1:
                continue

            results.append(
                (
                    float(score),
                    self.chunks[idx]
                )
            )

        return results


# =============================================================================
# Testing
# =============================================================================

if __name__ == "__main__":

    from pdf_loader import PDFLoader
    from chunker import TextChunker

    # Load papers
    loader = PDFLoader()

    papers = loader.load_papers()

    # Chunk papers
    chunker = TextChunker()

    chunks = chunker.chunk_all_papers(papers)

    # Create embeddings
    engine = EmbeddingEngine()

    embeddings = engine.create_embeddings(chunks)

    engine.build_index(embeddings)

    print("\n")

    while True:

        question = input("Ask a question (exit to quit): ")

        if question.lower() == "exit":
            break

        results = engine.search(question)

        print("\nTop Results")
        print("=" * 80)

        for rank, (score, chunk) in enumerate(results, start=1):

            print(f"\nResult #{rank}")

            print(f"Similarity : {score:.4f}")

            print(f"Paper      : {chunk['metadata']['filename']}")

            print(f"Chunk ID   : {chunk['chunk_id']}")

            print("-" * 80)

            print(chunk["text"][:500])

            print("\n")