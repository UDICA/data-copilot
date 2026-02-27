"""PDF text extraction and metadata retrieval.

Uses pypdf to read PDF files, extract page text with page-number prefixes,
and surface basic document metadata (page count, title, author).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pypdf import PdfReader


def extract_pdf_text(path: Path, *, pages: list[int] | None = None) -> str:
    """Extract text content from a PDF file.

    Each page's text is prefixed with a ``[Page N]`` header (1-based) so
    downstream consumers can attribute information to specific pages.

    Args:
        path: Filesystem path to the PDF file.
        pages: Optional list of 1-based page numbers to extract.  When
            *None*, every page in the document is extracted.

    Returns:
        Concatenated text of the requested pages, separated by newlines.

    Raises:
        FileNotFoundError: If *path* does not point to an existing file.
        ValueError: If any requested page number is out of range.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    reader = PdfReader(path)
    total_pages = len(reader.pages)

    if pages is None:
        target_pages = list(range(1, total_pages + 1))
    else:
        for p in pages:
            if p < 1 or p > total_pages:
                raise ValueError(
                    f"Page {p} is out of range. Document has {total_pages} page(s)."
                )
        target_pages = pages

    sections: list[str] = []
    for page_num in target_pages:
        page = reader.pages[page_num - 1]
        text = page.extract_text() or ""
        sections.append(f"[Page {page_num}]\n{text}")

    return "\n\n".join(sections)


def get_pdf_info(path: Path) -> dict[str, Any]:
    """Return basic metadata about a PDF file.

    Args:
        path: Filesystem path to the PDF file.

    Returns:
        A dictionary with the keys:
            - **pages** (*int*): Total number of pages.
            - **title** (*str | None*): Document title from PDF metadata.
            - **author** (*str | None*): Document author from PDF metadata.

    Raises:
        FileNotFoundError: If *path* does not point to an existing file.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    reader = PdfReader(path)
    meta = reader.metadata

    return {
        "pages": len(reader.pages),
        "title": meta.title if meta else None,
        "author": meta.author if meta else None,
    }
