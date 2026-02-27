"""Tests for the tool registry."""

import pytest

from src.tools.registry import ToolRegistry, tool

_registry = ToolRegistry()


@tool(_registry, description="Add two numbers")
async def add_numbers(a: int, b: int) -> str:
    """Add two numbers together."""
    return str(a + b)


@tool(_registry, description="Greet someone", name="greet")
async def greet_person(name: str, formal: bool = False) -> str:
    """Generate a greeting."""
    if formal:
        return f"Good day, {name}."
    return f"Hi, {name}!"


class TestToolRegistry:
    def test_registers_tool(self):
        assert "add_numbers" in _registry.list_tools()

    def test_registers_with_custom_name(self):
        assert "greet" in _registry.list_tools()

    def test_tool_has_description(self):
        tools = _registry.list_tools()
        assert tools["add_numbers"]["description"] == "Add two numbers"

    async def test_execute_tool(self):
        result = await _registry.execute("add_numbers", {"a": 2, "b": 3})
        assert result == "5"

    async def test_execute_with_defaults(self):
        result = await _registry.execute("greet", {"name": "Alice"})
        assert result == "Hi, Alice!"

    async def test_unknown_tool_raises(self):
        with pytest.raises(KeyError):
            await _registry.execute("nonexistent", {})

    def test_openai_function_schema(self):
        schemas = _registry.to_openai_tools()
        assert len(schemas) >= 2
        add_schema = next(s for s in schemas if s["function"]["name"] == "add_numbers")
        assert add_schema["type"] == "function"
        assert "parameters" in add_schema["function"]
        assert "a" in add_schema["function"]["parameters"]["properties"]

    def test_required_params(self):
        tools = _registry.list_tools()
        assert "a" in tools["add_numbers"]["parameters"]["required"]
        assert "b" in tools["add_numbers"]["parameters"]["required"]

    def test_optional_params_not_required(self):
        tools = _registry.list_tools()
        assert "formal" not in tools["greet"]["parameters"]["required"]
