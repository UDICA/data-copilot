"""Tests for the chat API router."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.chat.orchestrator import ChatEvent
from src.chat.router import router


def _create_test_app(events: list[ChatEvent]) -> FastAPI:
    """Create a FastAPI app with a mocked orchestrator."""
    app = FastAPI()
    app.include_router(router)

    mock_orchestrator = MagicMock()

    async def mock_chat(messages):
        for event in events:
            yield event

    mock_orchestrator.chat = mock_chat
    app.state.orchestrator = mock_orchestrator
    app.state.data_sources = [
        {"id": "1", "name": "Sample DB", "type": "database", "status": "connected"}
    ]
    return app


class TestChatRouter:
    def test_health_check(self):
        app = _create_test_app([])
        client = TestClient(app)
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_sources_endpoint(self):
        app = _create_test_app([])
        client = TestClient(app)
        response = client.get("/api/sources")
        assert response.status_code == 200
        data = response.json()
        assert len(data["sources"]) == 1
        assert data["sources"][0]["name"] == "Sample DB"

    def test_chat_endpoint_returns_sse(self):
        events = [
            ChatEvent(type="token", content="Hello!"),
            ChatEvent(type="done"),
        ]
        app = _create_test_app(events)
        client = TestClient(app)

        response = client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Hi"}]},
        )
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

        # Parse SSE events
        body = response.text
        assert "token" in body
        assert "Hello!" in body

    def test_chat_endpoint_with_tool_events(self):
        events = [
            ChatEvent(type="tool_start", tool_name="query_database", tool_args={"query": "SELECT 1"}),
            ChatEvent(type="tool_result", content="1", tool_name="query_database"),
            ChatEvent(type="token", content="The result is 1.", sources=["query_database"]),
            ChatEvent(type="done", sources=["query_database"]),
        ]
        app = _create_test_app(events)
        client = TestClient(app)

        response = client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Run SELECT 1"}]},
        )
        assert response.status_code == 200
        body = response.text
        assert "tool_start" in body
        assert "tool_result" in body
