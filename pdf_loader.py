"""
===============================================================================
PaperCompass
Author      : Your Name
Project     : PaperCompass - AI Research Paper Assistant
File        : pdf_loader.py

Description
-----------
This module is responsible for reading uploaded PDF research papers,
extracting their text, and collecting basic metadata.

Responsibilities
----------------
1. Read one or multiple PDF files.
2. Extract text from every page.
3. Store extracted text.
4. Extract basic metadata.
5. Return structured information for downstream modules.

Dependencies
------------
- PyPDF2
- pathlib
===============================================================================
"""

from pathlib import Path
from typing import Dict, List
from PyPDF2 import PdfReader


class PDFLoader:
    """
    Handles loading and parsing PDF research papers.

    Parameters
    ----------
    upload_folder : str
        Directory containing uploaded PDF files.

    Example
    -------
    >>> loader = PDFLoader("uploads")
    >>> papers = loader.load_papers()
    """

    def __init__(self, upload_folder: str = "uploads") -> None:
        self.upload_folder = Path(upload_folder)

    # ------------------------------------------------------------------ #
    # Private Methods
    # ------------------------------------------------------------------ #

    def _extract_text(self, pdf_path: Path) -> str:
        """
        Extract all text from a PDF.

        Parameters
        ----------
        pdf_path : Path

        Returns
        -------
        str
            Complete extracted text.
        """

        reader = PdfReader(str(pdf_path))

        pages = []

        for page in reader.pages:

            text = page.extract_text()

            if text:
                pages.append(text)

        return "\n".join(pages)

    def _extract_metadata(self, pdf_path: Path) -> Dict:
        """
        Extract metadata from the PDF.

        Parameters
        ----------
        pdf_path : Path

        Returns
        -------
        dict
        """

        reader = PdfReader(str(pdf_path))

        metadata = reader.metadata or {}

        return {
            "title": metadata.get("/Title", "Unknown"),
            "author": metadata.get("/Author", "Unknown"),
            "creator": metadata.get("/Creator", "Unknown"),
            "producer": metadata.get("/Producer", "Unknown"),
            "pages": len(reader.pages),
            "filename": pdf_path.name,
            "filepath": str(pdf_path),
        }

    # ------------------------------------------------------------------ #
    # Public Method
    # ------------------------------------------------------------------ #

    def load_papers(self, pdf_files: List[Path] = None) -> List[Dict]:
        """
        Load every PDF inside the upload folder or the provided list of files.

        Returns
        -------
        list

        Example
        -------
        [
            {
                "metadata": {...},
                "text": "...entire paper..."
            }
        ]
        """

        papers = []

        if pdf_files is None:
            if not self.upload_folder.exists():
                raise FileNotFoundError(
                    f"Upload folder '{self.upload_folder}' does not exist."
                )
            pdf_files = sorted(self.upload_folder.glob("*.pdf"))

        if len(pdf_files) == 0:
            raise ValueError(
                "No PDF files were found or provided."
            )

        for pdf in pdf_files:

            try:

                metadata = self._extract_metadata(pdf)

                text = self._extract_text(pdf)

                papers.append(
                    {
                        "metadata": metadata,
                        "text": text,
                    }
                )

            except Exception as e:

                print(f"Failed to load {pdf.name}")

                print(e)

        return papers


# =============================================================================
# Testing
# =============================================================================

if __name__ == "__main__":

    loader = PDFLoader()

    papers = loader.load_papers()

    print("=" * 80)
    print(f"Loaded {len(papers)} paper(s)")
    print("=" * 80)

    for paper in papers:

        print("\nFilename :", paper["metadata"]["filename"])
        print("Title    :", paper["metadata"]["title"])
        print("Author   :", paper["metadata"]["author"])
        print("Pages    :", paper["metadata"]["pages"])

        print("-" * 80)

        print(paper["text"][:600])

        print("\n")