"""Tests for the text, Markdown, and JSON parser."""

from pathlib import Path

import pytest

from src.parsers.text_parser import parse_json_file, read_text_file


class TestReadTextFile:
    def test_reads_markdown(self, fixtures_dir: Path) -> None:
        content = read_text_file(fixtures_dir / "sample.md")
        assert "Company Policy" in content
        assert "Returns" in content

    def test_nonexistent(self, fixtures_dir: Path) -> None:
        with pytest.raises(FileNotFoundError):
            read_text_file(fixtures_dir / "does_not_exist.txt")


class TestParseJsonFile:
    def test_parses_json(self, fixtures_dir: Path) -> None:
        data = parse_json_file(fixtures_dir / "sample.json")
        assert data["company"] == "Acme Corp"
        assert len(data["departments"]) == 2

    def test_json_query_path(self, fixtures_dir: Path) -> None:
        departments = parse_json_file(fixtures_dir / "sample.json", json_path="departments")
        assert isinstance(departments, list)
        assert len(departments) == 2
        assert departments[0]["name"] == "Sales"
