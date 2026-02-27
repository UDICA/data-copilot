"""Tests for the filesystem connector."""

from pathlib import Path

import pytest

from src.connectors.filesystem import FilesystemConnector


@pytest.fixture
def fs_connector(tmp_path: Path) -> FilesystemConnector:
    """Create a connector with test files in a temporary directory."""
    (tmp_path / "data.csv").write_text("a,b\n1,2\n")
    (tmp_path / "notes.md").write_text("# Notes\nSome text\n")
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "deep.json").write_text('{"key": "value"}')
    return FilesystemConnector(allowed_paths=[str(tmp_path)])


class TestFilesystemConnector:
    def test_list_directory(self, fs_connector, tmp_path):
        entries = fs_connector.list_directory(str(tmp_path))
        names = [e["name"] for e in entries]
        assert "data.csv" in names
        assert "notes.md" in names
        assert "subdir" in names

    def test_list_directory_types(self, fs_connector, tmp_path):
        entries = fs_connector.list_directory(str(tmp_path))
        file_entry = next(e for e in entries if e["name"] == "data.csv")
        dir_entry = next(e for e in entries if e["name"] == "subdir")
        assert file_entry["type"] == "file"
        assert dir_entry["type"] == "directory"

    def test_read_file(self, fs_connector, tmp_path):
        content = fs_connector.read_file(str(tmp_path / "notes.md"))
        assert "# Notes" in content

    def test_get_file_info(self, fs_connector, tmp_path):
        info = fs_connector.get_file_info(str(tmp_path / "data.csv"))
        assert info["name"] == "data.csv"
        assert info["size_bytes"] > 0
        assert info["extension"] == ".csv"

    def test_blocks_path_outside_allowed(self, fs_connector):
        with pytest.raises(PermissionError):
            fs_connector.read_file("/etc/passwd")

    def test_search_files(self, fs_connector, tmp_path):
        results = fs_connector.search_files(str(tmp_path), pattern="*.csv")
        assert len(results) == 1
        assert results[0]["name"] == "data.csv"

    def test_search_files_recursive(self, fs_connector, tmp_path):
        results = fs_connector.search_files(str(tmp_path), pattern="*.json")
        assert len(results) == 1
        assert results[0]["name"] == "deep.json"
