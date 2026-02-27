"""Web tools — search the web and fetch URL content."""

import logging

from src.tools.registry import ToolRegistry, tool
from src.connectors.web import WebConnector
from src.utils.formatting import format_tool_result, format_error

logger = logging.getLogger(__name__)

registry = ToolRegistry()

_connector: WebConnector | None = None


def init_web_tools(connector: WebConnector) -> None:
    """Wire the web tools to a live WebConnector instance.

    Args:
        connector: An initialized WebConnector instance.
    """
    global _connector
    _connector = connector


def get_web_registry() -> ToolRegistry:
    """Return the web tool registry for server registration.

    Returns:
        The module-level ToolRegistry containing all web tools.
    """
    return registry


def _ensure_connector() -> WebConnector:
    """Return the active connector or raise a clear error.

    Returns:
        The initialized WebConnector.

    Raises:
        RuntimeError: If no connector has been set via init_web_tools.
    """
    if _connector is None:
        raise RuntimeError(
            "No web connector configured. Call init_web_tools() first."
        )
    return _connector


@tool(
    registry,
    description="Search the web for current information. Returns titles, URLs, and snippets.",
)
async def web_search(query: str) -> str:
    """Search the web and return a numbered list of results.

    Args:
        query: The search query string.

    Returns:
        A numbered list of results with title, URL, and snippet,
        wrapped with source attribution, or a user-friendly error
        message if the search fails.
    """
    try:
        connector = _ensure_connector()
        results = await connector.search(query)

        if not results:
            return format_tool_result(
                "_No results found._", "web_search", source="Web Search"
            )

        lines: list[str] = []
        for i, result in enumerate(results, start=1):
            title = result.get("title", "Untitled")
            url = result.get("url", "")
            snippet = result.get("snippet", "")
            lines.append(f"{i}. **{title}**\n   {url}\n   {snippet}")

        text = "\n\n".join(lines)
        return format_tool_result(text, "web_search", source="Web Search")
    except Exception as exc:
        logger.exception("web_search failed")
        return format_error(str(exc), "web_search")


@tool(
    registry,
    description="Fetch and read the content of a web page URL.",
)
async def fetch_url(url: str) -> str:
    """Fetch a web page and return its text content.

    Args:
        url: The URL to fetch.

    Returns:
        The page text content wrapped with source attribution,
        or a user-friendly error message if fetching fails.
    """
    try:
        connector = _ensure_connector()
        result = await connector.fetch_url(url)
        content = result.get("content", "")
        return format_tool_result(content, "fetch_url", source=url)
    except Exception as exc:
        logger.exception("fetch_url failed")
        return format_error(str(exc), "fetch_url")
