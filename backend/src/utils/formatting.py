"""Result formatting utilities for LLM-friendly output."""

from typing import Any


def format_as_markdown_table(rows: list[dict[str, Any]]) -> str:
    """Format a list of row dicts as a markdown table.

    Args:
        rows: List of dictionaries, each representing a row.

    Returns:
        Markdown-formatted table string, or "_No results_" if empty.
    """
    if not rows:
        return "_No results_"

    headers = list(rows[0].keys())
    header_row = "| " + " | ".join(str(h) for h in headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    data_rows = [
        "| " + " | ".join(str(row.get(h, "")) for h in headers) + " |"
        for row in rows
    ]
    return "\n".join([header_row, separator, *data_rows])


def format_tool_result(content: str, tool_name: str, source: str) -> str:
    """Wrap tool output with source attribution metadata.

    Args:
        content: The tool's text output.
        tool_name: Name of the tool that produced the result.
        source: Human-readable source description.

    Returns:
        Formatted string with source attribution header.
    """
    return f"[Source: {tool_name} — {source}]\n\n{content}"


def format_error(message: str, tool_name: str) -> str:
    """Format a tool error for user-friendly display.

    Args:
        message: The error message.
        tool_name: Name of the tool that produced the error.

    Returns:
        Formatted error string.
    """
    return f"[Error in {tool_name}] {message}"
