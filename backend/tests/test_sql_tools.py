"""Tests for SQL database tools — query, schema, and explain."""

import pytest

from src.connectors.database import DatabaseConnector
from src.tools.sql_tools import (
    init_sql_tools,
    query_database,
    get_database_schema,
    explain_query,
)


@pytest.fixture
async def db_connector(tmp_path):
    """Create a SQLite connector with sample data and wire it into sql_tools."""
    db_url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    connector = DatabaseConnector(db_url, read_only=True)
    await connector.initialize()
    await connector.execute_raw(
        "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)"
    )
    await connector.execute_raw(
        "INSERT INTO products VALUES (1, 'Widget', 9.99), (2, 'Gadget', 19.99)"
    )
    init_sql_tools(connector)
    yield connector
    await connector.close()


class TestQueryDatabase:
    async def test_returns_markdown_table(self, db_connector):
        """query_database should return a markdown table containing the queried data."""
        result = await query_database("SELECT name, price FROM products ORDER BY id")

        assert "Widget" in result
        assert "Gadget" in result
        # Markdown table separators
        assert "---" in result
        assert "|" in result
        # Source attribution
        assert "query_database" in result

    async def test_invalid_sql_returns_error(self, db_connector):
        """Invalid SQL should produce an error string, not raise an exception."""
        result = await query_database("SELECT * FROM nonexistent_table")

        assert "[Error in query_database]" in result

    async def test_write_query_returns_error(self, db_connector):
        """Write operations should be rejected and return an error about read-only mode."""
        result = await query_database("DROP TABLE products")

        assert "[Error in query_database]" in result
        assert "read-only" in result.lower()


class TestGetDatabaseSchema:
    async def test_schema_lists_products_table(self, db_connector):
        """get_database_schema should return text mentioning the products table."""
        result = await get_database_schema()

        assert "products" in result
        assert "name" in result
        assert "price" in result


class TestExplainQuery:
    async def test_explain_returns_plan(self, db_connector):
        """explain_query should return an execution plan without executing the query."""
        result = await explain_query("SELECT * FROM products")

        # SQLite EXPLAIN produces output containing SCAN or detail columns
        assert "explain_query" in result
        # Should not raise and should contain some tabular output
        assert "|" in result
