"""File system browsing, reading, and search tools.

Exposes MCP-compatible tools that let an LLM explore directories, read files
in multiple formats (CSV, Excel, PDF, JSON, Markdown, plain text), and search
for files by glob pattern — all within the sandboxed paths configured for the
FilesystemConnector.
"""

import json
import logging
from pathlib import Path

from src.connectors.filesystem import FilesystemConnector
from src.parsers.csv_parser import get_csv_summary, parse_csv
from src.parsers.excel_parser import list_sheets, parse_excel
from src.parsers.pdf_parser import extract_pdf_text
from src.parsers.text_parser import parse_json_file, read_text_file
from src.tools.registry import ToolRegistry, tool
from src.utils.formatting import format_as_markdown_table, format_error, format_tool_result

logger = logging.getLogger(__name__)

registry = ToolRegistry()
_connector: FilesystemConnector | None = None


def init_file_tools(connector: FilesystemConnector) -> None:
    """Bind the file tools to a configured filesystem connector.

    Must be called once at startup before any tool execution.

    Args:
        connector: A FilesystemConnector instance with allowed paths set.
    """
    global _connector
    _connector = connector
    logger.info("File tools initialized")


def get_file_registry() -> ToolRegistry:
    """Return the tool registry containing the file tools.

    Returns:
        The module-level ToolRegistry with all file tools registered.
    """
    return registry


def _humanize_size(size_bytes: int | None) -> str:
    """Format a byte count into a human-readable string.

    Args:
        size_bytes: File size in bytes, or None for directories.

    Returns:
        Formatted size string (e.g. "1.2 KB") or "-" for None.
    """
    if size_bytes is None:
        return "-"
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.0f} {unit}" if unit == "B" else f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def _get_connector() -> FilesystemConnector:
    """Return the active connector or raise if not initialized.

    Returns:
        The FilesystemConnector bound via init_file_tools.

    Raises:
        RuntimeError: If init_file_tools has not been called.
    """
    if _connector is None:
        raise RuntimeError("File tools not initialized — call init_file_tools() first")
    return _connector


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@tool(registry, description="List files and directories at the given path.")
async def list_files(directory: str) -> str:
    """List files and directories at the given path.

    Returns a formatted listing with entry type, name, size, and file
    extension for each item in the directory.

    Args:
        directory: Absolute path to the directory to list.

    Returns:
        Formatted directory listing string with source attribution,
        or an error message if the operation fails.
    """
    try:
        connector = _get_connector()
        entries = connector.list_directory(directory)

        if not entries:
            return format_tool_result(
                "_Directory is empty._",
                "list_files",
                directory,
            )

        lines: list[str] = []
        for entry in entries:
            icon = "/" if entry["type"] == "directory" else " "
            size = _humanize_size(entry.get("size_bytes"))
            ext = entry.get("extension") or ""
            lines.append(f"  {icon} {entry['name']:<40} {size:>10}  {ext}")

        header = f"Contents of {directory}  ({len(entries)} items)\n"
        body = header + "\n".join(lines)
        return format_tool_result(body, "list_files", directory)

    except Exception as exc:
        logger.exception("list_files failed for %s", directory)
        return format_error(str(exc), "list_files")


@tool(
    registry,
    description=(
        "Read and parse a file. Automatically detects format "
        "(CSV, Excel, PDF, JSON, Markdown, text) and returns appropriate content."
    ),
)
async def read_file(file_path: str) -> str:
    """Read and parse a file, auto-detecting its format.

    Supported formats and behaviour:
    - **CSV/TSV** — returns a structural summary plus the first 10 rows as a
      markdown table.
    - **Excel (.xlsx)** — lists sheet names and renders the first sheet as a
      markdown table.
    - **PDF** — extracts full text with page-number annotations.
    - **JSON** — parses and pretty-prints the JSON structure.
    - **Markdown / plain text / other** — returns the raw text content.

    Args:
        file_path: Absolute path to the file to read.

    Returns:
        Parsed file content string with source attribution,
        or an error message if the operation fails.
    """
    try:
        connector = _get_connector()
        path = Path(file_path)
        suffix = path.suffix.lower()

        # CSV / TSV -----------------------------------------------------------
        if suffix in (".csv", ".tsv", ".tab"):
            # Use the connector's access check first (validates sandbox)
            connector.read_file(file_path)

            summary = get_csv_summary(file_path)
            df = parse_csv(file_path, max_rows=10)
            rows = df.to_dict(orient="records")
            table = format_as_markdown_table(rows)

            parts = [
                f"**{summary['rows']} rows x {summary['columns']} columns**",
                f"Columns: {', '.join(summary['column_names'])}",
                "",
                table,
            ]
            return format_tool_result("\n".join(parts), "read_file", file_path)

        # Excel ---------------------------------------------------------------
        if suffix in (".xlsx", ".xls"):
            connector.read_file(file_path)

            sheets = list_sheets(path)
            df = parse_excel(path, max_rows=50)
            rows = df.to_dict(orient="records")
            table = format_as_markdown_table(rows)

            parts = [
                f"Sheets: {', '.join(sheets)}",
                f"Showing first sheet: **{sheets[0]}**",
                "",
                table,
            ]
            return format_tool_result("\n".join(parts), "read_file", file_path)

        # PDF -----------------------------------------------------------------
        if suffix == ".pdf":
            connector.read_file(file_path)

            text = extract_pdf_text(path)
            return format_tool_result(text, "read_file", file_path)

        # JSON ----------------------------------------------------------------
        if suffix == ".json":
            connector.read_file(file_path)

            data = parse_json_file(file_path)
            pretty = json.dumps(data, indent=2, default=str)
            return format_tool_result(pretty, "read_file", file_path)

        # Markdown, plain text, and everything else ---------------------------
        content = connector.read_file(file_path)
        return format_tool_result(content, "read_file", file_path)

    except Exception as exc:
        logger.exception("read_file failed for %s", file_path)
        return format_error(str(exc), "read_file")


@tool(registry, description="Search for files matching a pattern in a directory.")
async def search_files(directory: str, pattern: str) -> str:
    """Search for files matching a glob pattern within a directory.

    The search is recursive by default, descending into all subdirectories.

    Args:
        directory: Absolute path to the root directory for the search.
        pattern: Glob pattern to match (e.g. ``"*.csv"``, ``"report*"``).

    Returns:
        Formatted search results with file names, paths, and sizes,
        or an error message if the operation fails.
    """
    try:
        connector = _get_connector()
        results = connector.search_files(directory, pattern=pattern)

        if not results:
            return format_tool_result(
                f"No files matching `{pattern}` found in {directory}.",
                "search_files",
                f"{directory} (pattern: {pattern})",
            )

        lines: list[str] = []
        for entry in results:
            size = _humanize_size(entry.get("size_bytes"))
            lines.append(f"  {entry['path']:<60} {size:>10}")

        header = f"Found {len(results)} file(s) matching `{pattern}`:\n"
        body = header + "\n".join(lines)
        return format_tool_result(body, "search_files", f"{directory} (pattern: {pattern})")

    except Exception as exc:
        logger.exception("search_files failed for %s with pattern %s", directory, pattern)
        return format_error(str(exc), "search_files")
