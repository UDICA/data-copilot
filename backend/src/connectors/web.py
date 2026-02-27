"""Web search and URL content fetching."""

import logging
import re
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")


def _html_to_text(html: str) -> str:
    """Strip HTML tags and collapse whitespace into readable text."""
    text = _TAG_RE.sub(" ", html)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


class WebConnector:
    """Provides web search and URL content fetching capabilities.

    Uses DuckDuckGo for search and httpx for page fetching. All requests
    have reasonable timeouts to avoid blocking the event loop.
    """

    def __init__(self, *, timeout: int = 15) -> None:
        self._timeout = timeout

    async def search(
        self,
        query: str,
        *,
        max_results: int = 5,
    ) -> list[dict[str, str]]:
        """Search the web using DuckDuckGo.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.

        Returns:
            List of dicts with title, url, and snippet.
        """
        return await self._search(query, max_results)

    async def _search(
        self,
        query: str,
        max_results: int,
    ) -> list[dict[str, str]]:
        """Internal search implementation using duckduckgo-search."""
        try:
            from duckduckgo_search import AsyncDDGS

            async with AsyncDDGS() as ddgs:
                raw_results = await ddgs.atext(query, max_results=max_results)

            return [
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", r.get("link", "")),
                    "snippet": r.get("body", r.get("snippet", "")),
                }
                for r in raw_results
            ]
        except Exception as e:
            logger.error("Web search failed: %s", e)
            return []

    async def fetch_url(
        self,
        url: str,
        *,
        max_length: int = 50_000,
    ) -> dict[str, Any]:
        """Fetch content from a URL and extract readable text.

        Args:
            url: The URL to fetch.
            max_length: Maximum character length of extracted text.

        Returns:
            Dict with url, status_code, content (text), and content_type.
        """
        async with httpx.AsyncClient(
            timeout=self._timeout, follow_redirects=True
        ) as client:
            response = await client.get(url)

        content_type = response.headers.get("content-type", "")
        raw = response.text

        if "html" in content_type:
            text = _html_to_text(raw)
        else:
            text = raw

        if len(text) > max_length:
            text = text[:max_length] + "\n\n[Content truncated]"

        return {
            "url": str(response.url),
            "status_code": response.status_code,
            "content": text,
            "content_type": content_type,
        }
