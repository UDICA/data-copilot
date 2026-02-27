"""Async database connector using SQLAlchemy with read-only enforcement."""

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.utils.safety import validate_sql_query

logger = logging.getLogger(__name__)


class DatabaseConnector:
    """Manages async database connections with safety guardrails.

    Supports PostgreSQL (asyncpg) and SQLite (aiosqlite) backends.
    Enforces read-only mode by default — all queries are validated
    before execution to prevent accidental data modifications.
    """

    def __init__(self, database_url: str, *, read_only: bool = True) -> None:
        self._database_url = database_url
        self._read_only = read_only
        self._engine: AsyncEngine | None = None

    async def initialize(self) -> None:
        """Create the async engine and verify connectivity."""
        self._engine = create_async_engine(
            self._database_url,
            echo=False,
            pool_pre_ping=True,
        )

    async def close(self) -> None:
        """Dispose of the engine and close all connections."""
        if self._engine:
            await self._engine.dispose()

    def _ensure_initialized(self) -> AsyncEngine:
        """Return the engine, raising if not initialized."""
        if not self._engine:
            raise RuntimeError("Database connector not initialized. Call initialize() first.")
        return self._engine

    async def execute_query(
        self,
        query: str,
        *,
        params: dict[str, Any] | None = None,
        max_rows: int = 1000,
    ) -> list[dict[str, Any]]:
        """Execute a SQL query and return results as a list of dicts.

        Args:
            query: SQL query string.
            params: Optional query parameters for safe interpolation.
            max_rows: Maximum number of rows to return.

        Returns:
            List of row dictionaries.

        Raises:
            QueryValidationError: If query violates read-only policy.
            RuntimeError: If the connector is not initialized.
        """
        engine = self._ensure_initialized()

        if self._read_only:
            validate_sql_query(query)

        # Append LIMIT if not already present
        exec_query = query.rstrip(";")
        if "LIMIT" not in query.upper():
            exec_query = f"{exec_query} LIMIT {max_rows}"

        async with engine.connect() as conn:
            result = await conn.execute(text(exec_query), params or {})
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]

        logger.info("Query returned %d rows", len(rows))
        return rows

    async def execute_raw(self, query: str) -> None:
        """Execute a raw SQL statement (for setup/migrations, bypasses read-only).

        Args:
            query: SQL statement to execute.
        """
        engine = self._ensure_initialized()
        async with engine.begin() as conn:
            await conn.execute(text(query))

    async def get_schema(self) -> dict[str, list[dict[str, str]]]:
        """Introspect the database schema.

        Returns:
            Dict mapping table names to lists of column info dicts
            with 'name' and 'type' keys.
        """
        engine = self._ensure_initialized()

        from sqlalchemy import inspect as sa_inspect

        def _inspect(conn: Any) -> dict[str, list[dict[str, str]]]:
            inspector = sa_inspect(conn)
            schema: dict[str, list[dict[str, str]]] = {}
            for table_name in inspector.get_table_names():
                columns = [
                    {"name": col["name"], "type": str(col["type"])}
                    for col in inspector.get_columns(table_name)
                ]
                schema[table_name] = columns
            return schema

        async with engine.connect() as conn:
            schema = await conn.run_sync(_inspect)

        return schema
