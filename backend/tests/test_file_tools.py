"""Tests for the file system tools (list, read, search)."""

from pathlib import Path

import pytest

from src.connectors.filesystem import FilesystemConnector
from src.tools.file_tools import (
    init_file_tools,
    list_files,
    read_file,
    search_files,
)


@pytest.fixture
def sample_dir(tmp_path: Path) -> Path:
    """Create a temporary directory tree with assorted test files."""
    # CSV
    (tmp_path / "sales.csv").write_text(
        "product,region,revenue\n"
        "Widget,North,1200\n"
        "Gadget,South,3400\n"
        "Widget,South,900\n"
    )

    # Markdown
    (tmp_path / "readme.md").write_text(
        "# Project README\n\nThis is a sample document.\n"
    )

    # JSON
    (tmp_path / "config.json").write_text(
        '{"database": "postgres", "port": 5432}\n'
    )

    # Subdirectory with a nested file
    sub = tmp_path / "reports"
    sub.mkdir()
    (sub / "q1.txt").write_text("Q1 results look strong.\n")

    return tmp_path


@pytest.fixture(autouse=True)
def _init_tools(sample_dir: Path) -> None:
    """Initialize file tools with the temporary sample directory."""
    connector = FilesystemConnector(allowed_paths=[str(sample_dir)])
    init_file_tools(connector)


class TestListFiles:
    @pytest.mark.asyncio
    async def test_returns_file_names(self, sample_dir: Path) -> None:
        result = await list_files(str(sample_dir))
        assert "sales.csv" in result
        assert "readme.md" in result
        assert "config.json" in result
        assert "reports" in result

    @pytest.mark.asyncio
    async def test_shows_item_count(self, sample_dir: Path) -> None:
        result = await list_files(str(sample_dir))
        assert "4 items" in result

    @pytest.mark.asyncio
    async def test_source_attribution(self, sample_dir: Path) -> None:
        result = await list_files(str(sample_dir))
        assert "[Source: list_files" in result


class TestReadFile:
    @pytest.mark.asyncio
    async def test_csv_returns_table(self, sample_dir: Path) -> None:
        result = await read_file(str(sample_dir / "sales.csv"))
        # Should contain column names in a markdown table
        assert "product" in result
        assert "region" in result
        assert "revenue" in result
        # Should show row/column summary
        assert "3 rows" in result
        assert "3 columns" in result

    @pytest.mark.asyncio
    async def test_markdown_returns_text(self, sample_dir: Path) -> None:
        result = await read_file(str(sample_dir / "readme.md"))
        assert "# Project README" in result
        assert "sample document" in result

    @pytest.mark.asyncio
    async def test_json_returns_pretty_printed(self, sample_dir: Path) -> None:
        result = await read_file(str(sample_dir / "config.json"))
        assert '"database"' in result
        assert '"postgres"' in result
        assert '"port"' in result

    @pytest.mark.asyncio
    async def test_plain_text_returns_content(self, sample_dir: Path) -> None:
        result = await read_file(str(sample_dir / "reports" / "q1.txt"))
        assert "Q1 results" in result

    @pytest.mark.asyncio
    async def test_nonexistent_file_returns_error(self, sample_dir: Path) -> None:
        result = await read_file(str(sample_dir / "does_not_exist.csv"))
        assert "[Error in read_file]" in result

    @pytest.mark.asyncio
    async def test_source_attribution(self, sample_dir: Path) -> None:
        result = await read_file(str(sample_dir / "readme.md"))
        assert "[Source: read_file" in result


class TestSearchFiles:
    @pytest.mark.asyncio
    async def test_finds_csv_files(self, sample_dir: Path) -> None:
        result = await search_files(str(sample_dir), "*.csv")
        assert "sales.csv" in result

    @pytest.mark.asyncio
    async def test_finds_files_recursively(self, sample_dir: Path) -> None:
        result = await search_files(str(sample_dir), "*.txt")
        assert "q1.txt" in result

    @pytest.mark.asyncio
    async def test_no_matches_returns_message(self, sample_dir: Path) -> None:
        result = await search_files(str(sample_dir), "*.xlsx")
        assert "No files matching" in result

    @pytest.mark.asyncio
    async def test_source_attribution(self, sample_dir: Path) -> None:
        result = await search_files(str(sample_dir), "*.json")
        assert "[Source: search_files" in result
