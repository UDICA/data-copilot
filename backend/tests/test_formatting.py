"""Tests for result formatting utilities."""

from src.utils.formatting import (
    format_as_markdown_table,
    format_error,
    format_tool_result,
)


class TestFormatAsMarkdownTable:
    def test_basic_table(self):
        rows = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = format_as_markdown_table(rows)
        assert "| name | age |" in result
        assert "| Alice | 30 |" in result
        assert "| Bob | 25 |" in result

    def test_empty_rows(self):
        result = format_as_markdown_table([])
        assert result == "_No results_"

    def test_single_column(self):
        rows = [{"count": 42}]
        result = format_as_markdown_table(rows)
        assert "| count |" in result
        assert "| 42 |" in result


class TestFormatToolResult:
    def test_includes_source(self):
        result = format_tool_result(
            content="Some data here",
            tool_name="query_database",
            source="PostgreSQL: orders table",
        )
        assert "query_database" in result
        assert "PostgreSQL" in result

    def test_includes_content(self):
        result = format_tool_result(
            content="42 rows returned",
            tool_name="query_database",
            source="db",
        )
        assert "42 rows returned" in result


class TestFormatError:
    def test_error_message(self):
        result = format_error("Connection refused", tool_name="query_database")
        assert "Connection refused" in result
        assert "query_database" in result
