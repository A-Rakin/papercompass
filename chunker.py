"""
===============================================================================
PaperCompass
Author      : Your Name
Project     : PaperCompass - AI Research Paper Assistant
File        : chunker.py

Description
-----------
This module splits extracted research paper text into smaller overlapping chunks.

Why Chunking?
-------------
Large Language Models (LLMs) have context length limitations. Instead of sending
an entire paper, we divide it into manageable pieces ("chunks"). During retrieval,
only the most relevant chunk(s) are passed to the LLM.

Chunking Strategy
-----------------
- Word-based chunking
- Configurable chunk size
- Configurable overlap
- Preserves document metadata
===============================================================================
"""

from typing import List, Dict


class TextChunker:
    """
    Splits research papers into overlapping chunks.

    Parameters
    ----------
    chunk_size : int
        Number of words in each chunk.

    overlap : int
        Number of overlapping words between consecutive chunks.
    """

    def __init__(
        self,
        chunk_size: int = 300,
        overlap: int = 50
    ) -> None:

        if overlap >= chunk_size:
            raise ValueError(
                "Overlap must be smaller than chunk size."
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    # ---------------------------------------------------------------------- #
    # Private Helper
    # ---------------------------------------------------------------------- #

    def _split_words(self, text: str) -> List[str]:
        """
        Split text into words.

        Parameters
        ----------
        text : str

        Returns
        -------
        list
            List of words.
        """

        return text.split()

    # ---------------------------------------------------------------------- #
    # Chunk a Single Paper
    # ---------------------------------------------------------------------- #

    def chunk_paper(self, paper: Dict) -> List[Dict]:
        """
        Split one paper into overlapping chunks.

        Parameters
        ----------
        paper : dict

        Returns
        -------
        list
            List of chunk dictionaries.
        """

        words = self._split_words(paper["text"])

        chunks = []

        start = 0
        chunk_id = 1

        while start < len(words):

            end = start + self.chunk_size

            chunk_words = words[start:end]

            chunk_text = " ".join(chunk_words)

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "metadata": paper["metadata"],
                }
            )

            chunk_id += 1

            start += self.chunk_size - self.overlap

        return chunks

    # ---------------------------------------------------------------------- #
    # Chunk Multiple Papers
    # ---------------------------------------------------------------------- #

    def chunk_all_papers(
        self,
        papers: List[Dict]
    ) -> List[Dict]:
        """
        Chunk every uploaded paper.

        Parameters
        ----------
        papers : list

        Returns
        -------
        list
            Flattened list of all chunks.
        """

        all_chunks = []

        for paper in papers:

            paper_chunks = self.chunk_paper(paper)

            all_chunks.extend(paper_chunks)

        return all_chunks


# =============================================================================
# Testing
# =============================================================================

if __name__ == "__main__":

    from pdf_loader import PDFLoader

    loader = PDFLoader()

    papers = loader.load_papers()

    chunker = TextChunker(
        chunk_size=300,
        overlap=50
    )

    chunks = chunker.chunk_all_papers(papers)

    print("=" * 80)
    print(f"Generated {len(chunks)} chunks")
    print("=" * 80)

    for chunk in chunks[:3]:

        print("\nChunk ID :", chunk["chunk_id"])
        print("Paper    :", chunk["metadata"]["filename"])

        print("-" * 80)

        print(chunk["text"][:500])

        print("\n")