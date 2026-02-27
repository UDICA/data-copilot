"""Integration tests for the full chat endpoint pipeline."""

import json
from unittest.mock import MagicMock

import httpx
import pytest
import respx
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.chat.orchestrator import ChatOrchestrator
from src.chat.router import router
from src.config import Settings
from src.connectors.database import DatabaseConnector
from src.connectors.filesystem import FilesystemConnector
from src.tools.file_tools import get_file_registry, init_file_tools
from src.tools.registry import ToolRegistry
from src.tools.sql_tools import get_sql_registry, init_sql_tools


def _build_registry() -> ToolRegistry:
    """Merge all available tool registries."""
    combined = ToolRegistry()
    for source_registry in [get_sql_registry(), get_file_registry()]:
        for name, meta in source_registry._tools.items():
            combined._tools[name] = meta
    return combined


@pytest.fixture
async def integration_app(tmp_path):
    """Create a fully wired FastAPI app with real connectors (SQLite + filesystem)."""
    # Set up SQLite database
    db_url = f"sqlite+aiosqlite:///{tmp_path}/integration.db"
    db = DatabaseConnector(db_url, read_only=True)
    await db.initialize()
    await db.execute_raw(
        "CREATE TABLE sales (id INTEGER PRIMARY KEY, product TEXT, amount REAL)"
    )
    await db.execute_raw(
        "INSERT INTO sales VALUES (1, 'Widget', 100.0), (2, 'Gadget', 250.0)"
    )
    init_sql_tools(db)

    # Set up filesystem
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "targets.csv").write_text("product,target\nWidget,500\nGadget,300\n")
    fs = FilesystemConnector(allowed_paths=[str(data_dir)])
    init_file_tools(fs)

    # Build registry and orchestrator
    registry = _build_registry()
    settings = Settings(
        openrouter_api_key="test-key",
        openrouter_base_url="https://openrouter.test/api/v1",
        openrouter_model="test-model",
        database_url=db_url,
    )
    orchestrator = ChatOrchestrator(settings, registry)

    app = FastAPI()
    app.include_router(router)
    app.state.orchestrator = orchestrator
    app.state.data_sources = []

    yield app

    await orchestrator.close()
    await db.close()


class TestIntegration:
    @respx.mock
    async def test_simple_chat_flow(self, integration_app):
        """End-to-end: user sends message, LLM responds with text."""
        respx.post("https://openrouter.test/api/v1/chat/completions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "message": {"role": "assistant", "content": "Hello! How can I help?"},
                            "finish_reason": "stop",
                        }
                    ]
                },
            )
        )

        client = TestClient(integration_app)
        response = client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Hi there"}]},
        )

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        assert "Hello! How can I help?" in response.text

    @respx.mock
    async def test_tool_call_flow(self, integration_app):
        """End-to-end: user asks a question, LLM calls query_database, then responds."""
        # First LLM call: model wants to use query_database
        tool_call_response = httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "call_1",
                                    "type": "function",
                                    "function": {
                                        "name": "query_database",
                                        "arguments": json.dumps({
                                            "query": "SELECT product, amount FROM sales ORDER BY amount DESC"
                                        }),
                                    },
                                }
                            ],
                        },
                        "finish_reason": "tool_calls",
                    }
                ]
            },
        )

        # Second LLM call: model produces final answer
        final_response = httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "Your top product is Gadget with $250 in sales.",
                        },
                        "finish_reason": "stop",
                    }
                ]
            },
        )

        route = respx.post("https://openrouter.test/api/v1/chat/completions")
        route.side_effect = [tool_call_response, final_response]

        client = TestClient(integration_app)
        response = client.post(
            "/api/chat",
            json={
                "messages": [
                    {"role": "user", "content": "What are my top products by sales?"}
                ]
            },
        )

        assert response.status_code == 200
        body = response.text

        # Verify tool execution happened
        assert "tool_start" in body
        assert "tool_result" in body
        assert "query_database" in body

        # Verify final response
        assert "Gadget" in body

    @respx.mock
    async def test_error_handling(self, integration_app):
        """End-to-end: LLM API error should produce error SSE event, not crash."""
        respx.post("https://openrouter.test/api/v1/chat/completions").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )

        client = TestClient(integration_app)
        response = client.post(
            "/api/chat",
            json={"messages": [{"role": "user", "content": "Hello"}]},
        )

        assert response.status_code == 200  # SSE stream is returned even on error
        assert "error" in response.text
