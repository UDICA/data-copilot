"""Tests for the async database connector."""

import pytest

from src.connectors.database import DatabaseConnector
from src.utils.safety import QueryValidationError


@pytest.fixture
async def db_connector(tmp_path):
    """Create a SQLite-based connector for testing."""
    db_url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    connector = DatabaseConnector(db_url, read_only=True)
    await connector.initialize()
    await connector.execute_raw(
        "CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL)"
    )
    await connector.execute_raw(
        "INSERT INTO products VALUES (1, 'Widget', 9.99), (2, 'Gadget', 19.99)"
    )
    yield connector
    await connector.close()


class TestDatabaseConnector:
    async def test_execute_query(self, db_connector):
        rows = await db_connector.execute_query("SELECT * FROM products")
        assert len(rows) == 2
        assert rows[0]["name"] == "Widget"

    async def test_get_schema(self, db_connector):
        schema = await db_connector.get_schema()
        assert "products" in schema
        assert any(col["name"] == "name" for col in schema["products"])

    async def test_read_only_blocks_writes(self, db_connector):
        with pytest.raises(QueryValidationError):
            await db_connector.execute_query("DROP TABLE products")

    async def test_row_limit(self, db_connector):
        rows = await db_connector.execute_query("SELECT * FROM products", max_rows=1)
        assert len(rows) == 1

    async def test_parameterized_query(self, db_connector):
        rows = await db_connector.execute_query(
            "SELECT * FROM products WHERE name = :name",
            params={"name": "Widget"},
        )
        assert len(rows) == 1
        assert rows[0]["price"] == 9.99

    async def test_not_initialized_raises(self):
        connector = DatabaseConnector("sqlite+aiosqlite:///", read_only=True)
        with pytest.raises(RuntimeError, match="not initialized"):
            await connector.execute_query("SELECT 1")
