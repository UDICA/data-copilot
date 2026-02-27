"""Central tool registry — tools defined once, used by both chat orchestrator and MCP server."""

import inspect
import logging
from typing import Any, Callable, Coroutine, get_type_hints

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Stores tool functions and their metadata.

    Tools are registered via the @tool decorator. The registry can export
    tool definitions in OpenAI function-calling format or MCP format,
    and execute tools by name.
    """

    def __init__(self) -> None:
        self._tools: dict[str, dict[str, Any]] = {}

    def register(
        self,
        func: Callable[..., Coroutine],
        *,
        name: str | None = None,
        description: str,
    ) -> None:
        """Register an async function as a tool.

        Args:
            func: The async tool function.
            name: Optional override for the tool name (defaults to func.__name__).
            description: Human-readable description of what the tool does.
        """
        tool_name = name or func.__name__
        hints = get_type_hints(func)
        sig = inspect.signature(func)

        parameters: dict[str, Any] = {
            "type": "object",
            "properties": {},
            "required": [],
        }

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            hint = hints.get(param_name, str)
            prop = _type_to_json_schema(hint)

            if param.default is not inspect.Parameter.empty:
                prop["default"] = param.default
            else:
                parameters["required"].append(param_name)

            parameters["properties"][param_name] = prop

        self._tools[tool_name] = {
            "function": func,
            "description": description,
            "parameters": parameters,
        }
        logger.info("Registered tool: %s", tool_name)

    def list_tools(self) -> dict[str, dict[str, Any]]:
        """Return metadata for all registered tools (without the callable).

        Returns:
            Dict mapping tool names to their description and parameter schema.
        """
        return {
            name: {"description": t["description"], "parameters": t["parameters"]}
            for name, t in self._tools.items()
        }

    async def execute(self, name: str, arguments: dict[str, Any]) -> str:
        """Execute a registered tool by name.

        Args:
            name: The tool name.
            arguments: Dict of argument name to value.

        Returns:
            Tool result as a string.

        Raises:
            KeyError: If the tool is not registered.
        """
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")

        func = self._tools[name]["function"]
        result = await func(**arguments)
        return result if isinstance(result, str) else str(result)

    def to_openai_tools(self) -> list[dict[str, Any]]:
        """Export tool definitions in OpenAI function-calling format.

        Returns:
            List of OpenAI tool definition dicts.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": t["description"],
                    "parameters": t["parameters"],
                },
            }
            for name, t in self._tools.items()
        ]


def _type_to_json_schema(python_type: type) -> dict[str, Any]:
    """Convert a Python type hint to a JSON Schema property."""
    type_map: dict[type, dict[str, Any]] = {
        str: {"type": "string"},
        int: {"type": "integer"},
        float: {"type": "number"},
        bool: {"type": "boolean"},
    }

    origin = getattr(python_type, "__origin__", None)
    if origin is list:
        args = getattr(python_type, "__args__", (str,))
        return {"type": "array", "items": _type_to_json_schema(args[0])}

    return type_map.get(python_type, {"type": "string"})


def tool(
    registry: ToolRegistry,
    *,
    description: str,
    name: str | None = None,
) -> Callable:
    """Decorator to register a function as a tool.

    Args:
        registry: The ToolRegistry to register with.
        description: Human-readable description.
        name: Optional name override.

    Returns:
        Decorator function.
    """

    def decorator(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        registry.register(func, name=name, description=description)
        return func

    return decorator
