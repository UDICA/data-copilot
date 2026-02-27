"""Tests for the web search and fetch connector."""

import httpx
import pytest
import respx

from src.connectors.web import WebConnector


@pytest.fixture
def web_connector() -> WebConnector:
    return WebConnector()


class TestWebConnector:
    @respx.mock
    async def test_fetch_url(self, web_connector):
        respx.get("https://example.com/page").mock(
            return_value=httpx.Response(
                200,
                text="<html><body>Hello World</body></html>",
                headers={"content-type": "text/html"},
            )
        )
        result = await web_connector.fetch_url("https://example.com/page")
        assert "Hello World" in result["content"]
        assert result["status_code"] == 200

    @respx.mock
    async def test_fetch_url_error_status(self, web_connector):
        respx.get("https://example.com/404").mock(
            return_value=httpx.Response(404, text="Not Found")
        )
        result = await web_connector.fetch_url("https://example.com/404")
        assert result["status_code"] == 404

    @respx.mock
    async def test_fetch_url_truncates_long_content(self, web_connector):
        long_text = "x" * 60_000
        respx.get("https://example.com/long").mock(
            return_value=httpx.Response(200, text=long_text)
        )
        result = await web_connector.fetch_url("https://example.com/long")
        assert "[Content truncated]" in result["content"]

    async def test_search_returns_list(self, web_connector, monkeypatch):
        async def mock_search(query, max_results):
            return [
                {"title": "Result 1", "href": "https://a.com", "body": "First result"},
                {"title": "Result 2", "href": "https://b.com", "body": "Second result"},
            ]

        monkeypatch.setattr(web_connector, "_search", mock_search)
        results = await web_connector.search("test query", max_results=2)
        assert len(results) == 2
        assert results[0]["title"] == "Result 1"
