"""Tests for the PDF parser module."""

from pathlib import Path

import pytest

from src.parsers.pdf_parser import extract_pdf_text, get_pdf_info


@pytest.fixture
def pdf_path(tmp_path: Path) -> Path:
    """Create a minimal valid PDF for testing."""
    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    path = tmp_path / "test.pdf"
    with open(path, "wb") as f:
        writer.write(f)
    return path


class TestExtractPdfText:
    def test_extracts_text(self, pdf_path: Path) -> None:
        """extract_pdf_text returns a string without raising for a valid PDF."""
        result = extract_pdf_text(pdf_path)
        assert isinstance(result, str)

    def test_page_header_present(self, pdf_path: Path) -> None:
        """Extracted text includes the [Page N] header."""
        result = extract_pdf_text(pdf_path)
        assert "[Page 1]" in result

    def test_specific_pages(self, pdf_path: Path) -> None:
        """Passing pages=[1] extracts only the first page."""
        result = extract_pdf_text(pdf_path, pages=[1])
        assert "[Page 1]" in result

    def test_invalid_page_raises(self, pdf_path: Path) -> None:
        """Requesting a page beyond the document range raises ValueError."""
        with pytest.raises(ValueError, match="out of range"):
            extract_pdf_text(pdf_path, pages=[99])

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        """A missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            extract_pdf_text(tmp_path / "missing.pdf")


class TestGetPdfInfo:
    def test_returns_page_count(self, pdf_path: Path) -> None:
        """get_pdf_info returns a dict with pages >= 1."""
        info = get_pdf_info(pdf_path)
        assert isinstance(info, dict)
        assert "pages" in info
        assert info["pages"] >= 1

    def test_contains_metadata_keys(self, pdf_path: Path) -> None:
        """Result dict contains title and author keys."""
        info = get_pdf_info(pdf_path)
        assert "title" in info
        assert "author" in info

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        """A missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            get_pdf_info(tmp_path / "missing.pdf")
