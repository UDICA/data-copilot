"""SQL database tools — query execution, schema introspection, and query explanation."""

import logging
from typing import Any

from src.tools.registry import ToolRegistry, tool
from src.connectors.database import DatabaseConnector
from src.utils.formatting import format_as_markdown_table, format_tool_result, format_error

logger = logging.getLogger(__name__)

registry = ToolRegistry()

_connector: DatabaseConnector | None = None


def init_sql_tools(connector: DatabaseConnector) -> None:
    """Wire the SQL tools to a live database connector.

    Args:
        connector: An initialized DatabaseConnector instance.
    """
    global _connector
    _connector = connector


def get_sql_registry() -> ToolRegistry:
    """Return the SQL tool registry for server registration.

    Returns:
        The module-level ToolRegistry containing all SQL tools.
    """
    return registry


def _ensure_connector() -> DatabaseConnector:
    """Return the active connector or raise a clear error.

    Returns:
        The initialized DatabaseConnector.

    Raises:
        RuntimeError: If no connector has been set via init_sql_tools.
    """
    if _connector is None:
        raise RuntimeError(
            "No database connector configured. Call init_sql_tools() first."
        )
    return _connector


@tool(
    registry,
    description=(
        "Execute a SQL query against the connected database. "
        "Returns results as a formatted markdown table."
    ),
)
async def query_database(query: str) -> str:
    """Execute a read-only SQL query and return the results.

    Args:
        query: A SQL SELECT query to run against the connected database.

    Returns:
        A markdown-formatted table of results with source attribution,
        or a user-friendly error message if execution fails.
    """
    try:
        connector = _ensure_connector()
        rows: list[dict[str, Any]] = await connector.execute_query(query)
        table = format_as_markdown_table(rows)
        return format_tool_result(table, "query_database", f"SQL query: {query}")
    except Exception as exc:
        logger.exception("query_database failed")
        return format_error(str(exc), "query_database")


@tool(
    registry,
    description="Get the database schema — lists all tables and their columns with types.",
)
async def get_database_schema() -> str:
    """Retrieve the full database schema as human-readable text.

    Returns:
        A text listing of every table and its columns with data types,
        or a user-friendly error message if introspection fails.
    """
    try:
        connector = _ensure_connector()
        schema = await connector.get_schema()

        if not schema:
            return format_tool_result(
                "_No tables found in the database._",
                "get_database_schema",
                "database schema",
            )

        lines: list[str] = []
        for table_name, columns in schema.items():
            lines.append(f"Table: {table_name}")
            for col in columns:
                lines.append(f"  - {col['name']} ({col['type']})")
            lines.append("")  # blank line between tables

        text = "\n".join(lines).rstrip()
        return format_tool_result(text, "get_database_schema", "database schema")
    except Exception as exc:
        logger.exception("get_database_schema failed")
        return format_error(str(exc), "get_database_schema")


@tool(
    registry,
    description="Explain a SQL query — shows the execution plan without running the query.",
)
async def explain_query(query: str) -> str:
    """Show the execution plan for a SQL query without executing it.

    Args:
        query: The SQL query whose execution plan should be returned.

    Returns:
        The EXPLAIN output formatted as a markdown table with source
        attribution, or a user-friendly error message on failure.
    """
    try:
        connector = _ensure_connector()
        explain_sql = f"EXPLAIN {query}"
        rows: list[dict[str, Any]] = await connector.execute_query(explain_sql)
        table = format_as_markdown_table(rows)
        return format_tool_result(table, "explain_query", f"EXPLAIN plan for: {query}")
    except Exception as exc:
        logger.exception("explain_query failed")
        return format_error(str(exc), "explain_query")
