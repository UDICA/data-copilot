"""Tests for the chat orchestrator."""

import json

import httpx
import pytest
import respx

from src.chat.orchestrator import ChatOrchestrator
from src.config import Settings
from src.tools.registry import ToolRegistry, tool


@pytest.fixture
def settings():
    return Settings(
        openrouter_api_key="test-key",
        openrouter_model="test-model",
        openrouter_base_url="https://openrouter.test/api/v1",
    )


@pytest.fixture
def registry():
    reg = ToolRegistry()

    @tool(reg, description="Add two numbers")
    async def add_numbers(a: int, b: int) -> str:
        return str(a + b)

    return reg


@pytest.fixture
def orchestrator(settings, registry):
    return ChatOrchestrator(settings, registry)


class TestChatOrchestrator:
    @respx.mock
    async def test_simple_text_response(self, orchestrator):
        """LLM returns a plain text response with no tool calls."""
        respx.post("https://openrouter.test/api/v1/chat/completions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "choices": [
                        {
                            "message": {"role": "assistant", "content": "Hello!"},
                            "finish_reason": "stop",
                        }
                    ]
                },
            )
        )

        events = []
        async for event in orchestrator.chat([{"role": "user", "content": "Hi"}]):
            events.append(event)

        assert any(e.type == "token" and "Hello!" in e.content for e in events)
        assert events[-1].type == "done"

    @respx.mock
    async def test_tool_call_then_response(self, orchestrator):
        """LLM calls a tool, gets result, then produces final text."""
        # First call: LLM wants to call add_numbers
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
                                        "name": "add_numbers",
                                        "arguments": json.dumps({"a": 2, "b": 3}),
                                    },
                                }
                            ],
                        },
                        "finish_reason": "tool_calls",
                    }
                ]
            },
        )

        # Second call: LLM produces final text
        final_response = httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {"role": "assistant", "content": "The sum is 5."},
                        "finish_reason": "stop",
                    }
                ]
            },
        )

        route = respx.post("https://openrouter.test/api/v1/chat/completions")
        route.side_effect = [tool_call_response, final_response]

        events = []
        async for event in orchestrator.chat(
            [{"role": "user", "content": "What is 2 + 3?"}]
        ):
            events.append(event)

        types = [e.type for e in events]
        assert "tool_start" in types
        assert "tool_result" in types
        assert "token" in types
        assert "done" in types

        tool_result = next(e for e in events if e.type == "tool_result")
        assert "5" in tool_result.content

    @respx.mock
    async def test_api_error_yields_error_event(self, orchestrator):
        """API error should yield an error event, not raise."""
        respx.post("https://openrouter.test/api/v1/chat/completions").mock(
            return_value=httpx.Response(500, text="Internal Server Error")
        )

        events = []
        async for event in orchestrator.chat([{"role": "user", "content": "Hi"}]):
            events.append(event)

        assert any(e.type == "error" for e in events)

    @respx.mock
    async def test_rate_limit_yields_error(self, orchestrator):
        """429 should yield a rate limit error event."""
        respx.post("https://openrouter.test/api/v1/chat/completions").mock(
            return_value=httpx.Response(429, text="Too Many Requests")
        )

        events = []
        async for event in orchestrator.chat([{"role": "user", "content": "Hi"}]):
            events.append(event)

        assert any(e.type == "error" and "Rate limit" in e.content for e in events)
