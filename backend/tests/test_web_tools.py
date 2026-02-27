"""Tests for web tools — search and URL fetching."""

import pytest

from src.connectors.web import WebConnector
from src.tools.web_tools import (
    init_web_tools,
    web_search,
    fetch_url,
)


@pytest.fixture
def web_connector(monkeypatch):
    """Create a WebConnector with mocked search and fetch methods."""
    connector = WebConnector()

    async def mock_search(query, *, max_results=5):
        return [
            {"title": "First Result", "url": "https://example.com/1", "snippet": "First snippet"},
            {"title": "Second Result", "url": "https://example.com/2", "snippet": "Second snippet"},
        ]

    async def mock_fetch_url(url, *, max_length=50_000):
        return {
            "url": url,
            "status_code": 200,
            "content": "Page content for testing",
            "content_type": "text/html",
        }

    monkeypatch.setattr(connector, "search", mock_search)
    monkeypatch.setattr(connector, "fetch_url", mock_fetch_url)
    init_web_tools(connector)
    return connector


class TestWebSearch:
    async def test_returns_formatted_results(self, web_connector):
        """web_search should return a numbered list with titles, URLs, and snippets."""
        result = await web_search("test query")

        assert "First Result" in result
        assert "Second Result" in result
        assert "https://example.com/1" in result
        assert "https://example.com/2" in result
        assert "First snippet" in result
        # Source attribution
        assert "web_search" in result
        assert "Web Search" in result

    async def test_empty_results(self, web_connector, monkeypatch):
        """web_search should return a 'no results' message when the connector returns nothing."""

        async def mock_empty_search(query, *, max_results=5):
            return []

        monkeypatch.setattr(web_connector, "search", mock_empty_search)

        result = await web_search("obscure query")
        assert "No results found" in result

    async def test_connector_failure_returns_error(self, web_connector, monkeypatch):
        """web_search should return a formatted error when the connector raises."""

        async def mock_failing_search(query, *, max_results=5):
            raise ConnectionError("Network unreachable")

        monkeypatch.setattr(web_connector, "search", mock_failing_search)

        result = await web_search("will fail")
        assert "[Error in web_search]" in result
        assert "Network unreachable" in result


class TestFetchUrl:
    async def test_returns_page_content(self, web_connector):
        """fetch_url should return the page text with source attribution."""
        result = await fetch_url("https://example.com/page")

        assert "Page content for testing" in result
        # Source attribution includes the URL
        assert "https://example.com/page" in result
        assert "fetch_url" in result

    async def test_connector_failure_returns_error(self, web_connector, monkeypatch):
        """fetch_url should return a formatted error when the connector raises."""

        async def mock_failing_fetch(url, *, max_length=50_000):
            raise ConnectionError("Connection refused")

        monkeypatch.setattr(web_connector, "fetch_url", mock_failing_fetch)

        result = await fetch_url("https://bad-url.example.com")
        assert "[Error in fetch_url]" in result
        assert "Connection refused" in result
