"""FastAPI application entry point with tool initialization."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.chat.orchestrator import ChatOrchestrator
from src.chat.router import router as chat_router
from src.config import Settings, get_settings
from src.connectors.database import DatabaseConnector
from src.connectors.filesystem import FilesystemConnector
from src.connectors.web import WebConnector
from src.tools.analysis_tools import get_analysis_registry
from src.tools.file_tools import get_file_registry, init_file_tools
from src.tools.registry import ToolRegistry
from src.tools.sql_tools import get_sql_registry, init_sql_tools
from src.tools.web_tools import get_web_registry, init_web_tools

logger = structlog.get_logger()


def _build_registry() -> ToolRegistry:
    """Merge all tool registries into a single registry.

    Returns:
        A ToolRegistry containing all tools from every module.
    """
    combined = ToolRegistry()
    for source_registry in [
        get_sql_registry(),
        get_file_registry(),
        get_web_registry(),
        get_analysis_registry(),
    ]:
        for name, meta in source_registry._tools.items():
            combined._tools[name] = meta
    return combined


async def _build_system_prompt(
    db_connector: DatabaseConnector,
    fs_connector: FilesystemConnector,
    settings: Settings,
) -> str:
    """Build a system prompt that tells the LLM about available data.

    Dynamically fetches the database schema and lists files in the
    allowed paths so the LLM knows exactly what data it can access.

    Args:
        db_connector: Initialized database connector for schema introspection.
        fs_connector: Initialized filesystem connector for directory listing.
        settings: Application settings with file path configuration.

    Returns:
        A multi-line system prompt string.
    """
    parts: list[str] = [
        "You are Data Copilot, an AI assistant that helps users query databases, "
        "explore files, and search the web. Answer concisely and always use the "
        "appropriate tool for the job.",
        "",
        "## Tool Selection Guide",
        "- For questions about business data (orders, customers, products, sales): "
        "use `query_database` or `get_database_schema`.",
        "- For questions about local files, documents, CSVs, or company policies: "
        "use `list_files`, `read_file`, or `search_files`.",
        "- For questions about current events, market data, or external information: "
        "use `web_search` or `fetch_url`.",
        "- For statistical analysis on data you've already retrieved: "
        "use `describe_data`, `cross_join_data`, or `export_to_csv`.",
        "",
    ]

    # Database schema
    try:
        schema: dict[str, list[dict[str, Any]]] = await db_connector.get_schema()
        if schema:
            parts.append("## Database Schema")
            parts.append("The connected PostgreSQL database contains the following tables:")
            parts.append("")
            for table_name, columns in schema.items():
                col_list = ", ".join(f"{c['name']} ({c['type']})" for c in columns)
                parts.append(f"- **{table_name}**: {col_list}")
            parts.append("")
            parts.append(
                "The database has ~500 customers, ~5000 orders, ~30 products, "
                "~12000 order_items, and 20 sales reps."
            )
            parts.append("")
            parts.append("### Table Relationships")
            parts.append(
                "- orders.customer_id → customers.id\n"
                "- order_items.order_id → orders.id\n"
                "- order_items.product_id → products.id\n"
                "- To get revenue per product, JOIN order_items with products and "
                "orders, then SUM(order_items.quantity * order_items.unit_price).\n"
                "- The orders.total_amount is the order-level total, NOT per product."
            )
            parts.append("")
            parts.append("### Date Range")
            parts.append(
                "CRITICAL: All order data spans 2023-01-01 to 2024-12-31. There is "
                "NO data after December 2024. Interpret time references relative to "
                "this range:\n"
                "- 'last quarter' → Q4 2024 (2024-10-01 to 2024-12-31)\n"
                "- 'this year' or 'last year' → 2024\n"
                "- 'previous year' → 2023\n"
                "Do NOT use today's date for filtering — the data ends in Dec 2024."
            )
            parts.append("")
    except Exception:
        logger.warning("Could not fetch database schema for system prompt")

    # Available files — show full absolute paths so the LLM can use them directly
    try:
        file_sections: list[str] = []
        for allowed_path in settings.allowed_file_paths:
            entries = fs_connector.list_directory(allowed_path)
            if entries:
                for entry in entries:
                    full_path = str(Path(allowed_path) / entry["name"])
                    if entry["type"] == "directory":
                        file_sections.append(f"- Directory: `{full_path}/`")
                        try:
                            sub_entries = fs_connector.list_directory(full_path)
                            for sub in sub_entries:
                                sub_full = str(Path(full_path) / sub["name"])
                                file_sections.append(f"  - `{sub_full}`")
                        except Exception:
                            pass
                    else:
                        file_sections.append(f"- `{full_path}`")

        if file_sections:
            parts.append("## Available Local Files")
            parts.append(
                "The following files are available locally. Always use file tools "
                "(read_file, list_files, search_files) to access them — NEVER use "
                "web_search for local content. Use the FULL PATH shown below when "
                "calling read_file."
            )
            parts.append("")
            parts.extend(file_sections)
            parts.append("")
            parts.append(
                "**Important:** The sample_docs directory contains company policies "
                "(returns, refunds, warranty, data handling) and an enterprise "
                "technology market report. Check these local files FIRST before "
                "using web_search for company or market questions."
            )
            parts.append("")
    except Exception:
        logger.warning("Could not list files for system prompt")

    parts.append(
        "## Response Guidelines\n"
        "- Always cite which tool and source you used.\n"
        "- Format query results as markdown tables.\n"
        "- If a tool returns an error, explain it clearly and suggest alternatives.\n"
        "- When asked for 'top N' results, make sure the SQL query uses LIMIT N."
    )

    return "\n".join(parts)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle.

    Initializes database, filesystem, and web connectors, wires up
    tool modules, and creates the chat orchestrator. Cleans up on shutdown.
    """
    settings = get_settings()

    # Configure logging
    logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))

    # Initialize connectors
    db_connector = DatabaseConnector(
        settings.database_url, read_only=settings.db_read_only
    )
    await db_connector.initialize()

    fs_connector = FilesystemConnector(allowed_paths=settings.allowed_file_paths)
    web_connector = WebConnector()

    # Wire tool modules to their connectors
    init_sql_tools(db_connector)
    init_file_tools(fs_connector)
    init_web_tools(web_connector)

    # Build combined registry, system prompt, and orchestrator
    registry = _build_registry()
    system_prompt = await _build_system_prompt(db_connector, fs_connector, settings)
    orchestrator = ChatOrchestrator(settings, registry, system_prompt=system_prompt)

    # Store on app state for access in request handlers
    app.state.orchestrator = orchestrator
    app.state.data_sources = [
        {
            "id": "default-db",
            "name": "Sample Database",
            "type": "database",
            "status": "connected",
            "details": "PostgreSQL with sample business data",
        },
        {
            "id": "default-files",
            "name": "Sample Files",
            "type": "directory",
            "status": "connected",
            "details": ", ".join(settings.allowed_file_paths),
        },
    ]

    logger.info(
        "server.started",
        tools=list(registry.list_tools().keys()),
        db_read_only=settings.db_read_only,
    )

    yield

    # Cleanup
    await orchestrator.close()
    await db_connector.close()
    logger.info("server.shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app with CORS, routers, and lifespan.
    """
    app = FastAPI(
        title="Data Copilot",
        description="AI assistant that talks to your databases, files, and the web",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(chat_router)

    return app


app = create_app()
