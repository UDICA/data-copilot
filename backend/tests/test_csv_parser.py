"""Tests for the CSV/TSV parser module."""

from pathlib import Path

import pytest

from src.parsers.csv_parser import get_csv_summary, parse_csv


class TestParseCsv:
    """Tests for parse_csv."""

    def test_reads_csv(self, fixtures_dir: Path) -> None:
        """parse_csv returns the correct DataFrame for a standard CSV."""
        df = parse_csv(fixtures_dir / "sample.csv")
        assert len(df) == 4
        assert list(df.columns) == ["name", "region", "revenue", "quarter"]

    def test_reads_tsv(self, fixtures_dir: Path) -> None:
        """parse_csv correctly handles tab-separated files."""
        df = parse_csv(fixtures_dir / "sample.tsv")
        assert len(df) == 4
        assert list(df.columns) == ["name", "region", "revenue", "quarter"]

    def test_with_filter(self, fixtures_dir: Path) -> None:
        """Filtering by region='North' returns only matching rows."""
        df = parse_csv(fixtures_dir / "sample.csv", filters={"region": "North"})
        assert len(df) == 2
        assert set(df["name"]) == {"Alice", "Carol"}

    def test_nonexistent_file(self, fixtures_dir: Path) -> None:
        """A missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            parse_csv(fixtures_dir / "does_not_exist.csv")


class TestGetCsvSummary:
    """Tests for get_csv_summary."""

    def test_summary_shape(self, fixtures_dir: Path) -> None:
        """Summary reports the correct row and column counts."""
        summary = get_csv_summary(fixtures_dir / "sample.csv")
        assert summary["rows"] == 4
        assert summary["columns"] == 4
        assert summary["column_names"] == ["name", "region", "revenue", "quarter"]

    def test_summary_includes_dtypes(self, fixtures_dir: Path) -> None:
        """Summary contains a column_types mapping with dtype strings."""
        summary = get_csv_summary(fixtures_dir / "sample.csv")
        assert isinstance(summary["column_types"], dict)
        assert "revenue" in summary["column_types"]
        # revenue should be parsed as an integer type
        assert "int" in summary["column_types"]["revenue"]
