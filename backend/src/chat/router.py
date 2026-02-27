"""Chat API router with SSE streaming."""

import json
import logging
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Request body for the chat endpoint.

    Attributes:
        messages: List of message dicts with 'role' and 'content'.
    """

    messages: list[dict[str, Any]]


@router.post("/chat")
async def chat(request: Request, body: ChatRequest) -> EventSourceResponse:
    """Stream a chat response with tool execution via SSE.

    The endpoint processes the conversation through the LLM orchestrator,
    executing any tool calls as needed, and streams events back to the client.

    Args:
        request: The FastAPI request object (provides app state).
        body: The chat request with conversation messages.

    Returns:
        An SSE stream of ChatEvent objects.
    """
    orchestrator = request.app.state.orchestrator

    async def event_generator():
        try:
            async for event in orchestrator.chat(body.messages):
                yield {
                    "event": event.type,
                    "data": json.dumps({
                        "type": event.type,
                        "content": event.content,
                        "tool_name": event.tool_name,
                        "tool_args": event.tool_args,
                        "sources": event.sources,
                    }),
                }
        except Exception as e:
            logger.error("Chat stream error: %s", e)
            yield {
                "event": "error",
                "data": json.dumps({
                    "type": "error",
                    "content": f"An unexpected error occurred: {e}",
                }),
            }

    return EventSourceResponse(event_generator())


@router.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Dict with status "ok".
    """
    return {"status": "ok"}


@router.get("/sources")
async def get_sources(request: Request) -> dict[str, Any]:
    """Return configured data sources and their connection status.

    Args:
        request: The FastAPI request object.

    Returns:
        Dict with list of data source info.
    """
    sources = getattr(request.app.state, "data_sources", [])
    return {"sources": sources}
