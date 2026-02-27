"""LLM orchestrator — manages the conversation loop with OpenRouter and tool execution."""

import json
import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any

import httpx

from src.config import Settings
from src.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

# Safety limit to prevent infinite tool-call loops
MAX_TOOL_ITERATIONS = 10


@dataclass
class ChatEvent:
    """A streaming event produced during chat orchestration.

    Attributes:
        type: One of "token", "tool_start", "tool_result", "done", "error".
        content: Text content (token text, tool result, error message).
        tool_name: Name of the tool being called (for tool_start/tool_result).
        tool_args: Arguments passed to the tool (for tool_start).
        sources: List of source descriptions accumulated during the response.
    """

    type: str
    content: str = ""
    tool_name: str | None = None
    tool_args: dict[str, Any] | None = None
    sources: list[str] = field(default_factory=list)


class ChatOrchestrator:
    """Orchestrates conversations between the user, LLM, and tools.

    Sends messages to OpenRouter, interprets tool calls, executes them
    via the tool registry, and loops until the model produces a final
    text response.
    """

    def __init__(self, settings: Settings, registry: ToolRegistry) -> None:
        self._settings = settings
        self._registry = registry
        self._client = httpx.AsyncClient(
            base_url=settings.openrouter_base_url,
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            timeout=60,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def chat(
        self,
        messages: list[dict[str, Any]],
    ) -> AsyncGenerator[ChatEvent, None]:
        """Process a chat conversation with tool execution.

        Sends messages to the LLM, handles tool calls, and yields events
        as they occur. Supports multi-turn tool execution loops.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.

        Yields:
            ChatEvent objects representing tokens, tool activity, or completion.
        """
        tools = self._registry.to_openai_tools()
        sources: list[str] = []

        # Build working copy of messages for the tool loop
        working_messages = list(messages)

        for iteration in range(MAX_TOOL_ITERATIONS):
            try:
                response = await self._call_llm(working_messages, tools)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    yield ChatEvent(type="error", content="Rate limit reached. Please try again.")
                    return
                yield ChatEvent(
                    type="error",
                    content=f"LLM request failed: {e.response.status_code}",
                )
                return
            except Exception as e:
                yield ChatEvent(type="error", content=f"LLM request failed: {e}")
                return

            choice = response.get("choices", [{}])[0]
            message = choice.get("message", {})
            finish_reason = choice.get("finish_reason", "")

            # If the model wants to call tools
            tool_calls = message.get("tool_calls", [])
            if tool_calls:
                # Add assistant message with tool calls to history
                working_messages.append(message)

                for tc in tool_calls:
                    func = tc.get("function", {})
                    tool_name = func.get("name", "unknown")
                    tool_args_str = func.get("arguments", "{}")
                    tool_call_id = tc.get("id", "")

                    try:
                        tool_args = json.loads(tool_args_str)
                    except json.JSONDecodeError:
                        tool_args = {}

                    yield ChatEvent(
                        type="tool_start",
                        tool_name=tool_name,
                        tool_args=tool_args,
                    )

                    # Execute the tool
                    try:
                        result = await self._registry.execute(tool_name, tool_args)
                        sources.append(tool_name)
                    except Exception as e:
                        result = f"Tool error: {e}"
                        logger.error("Tool %s failed: %s", tool_name, e)

                    yield ChatEvent(
                        type="tool_result",
                        content=result,
                        tool_name=tool_name,
                    )

                    # Add tool result to messages
                    working_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": result,
                    })

                # Continue the loop — send tool results back to LLM
                continue

            # No tool calls — this is the final text response
            content = message.get("content", "")
            if content:
                yield ChatEvent(type="token", content=content, sources=sources)

            yield ChatEvent(type="done", sources=sources)
            return

        # Safety: exceeded max iterations
        yield ChatEvent(
            type="error",
            content="Reached maximum tool call iterations. Please simplify your request.",
        )

    async def _call_llm(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Make a single call to the OpenRouter API.

        Args:
            messages: Conversation messages.
            tools: Tool definitions in OpenAI format.

        Returns:
            Parsed JSON response from the API.

        Raises:
            httpx.HTTPStatusError: On non-2xx responses.
        """
        payload: dict[str, Any] = {
            "model": self._settings.openrouter_model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        response = await self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        return response.json()
