"""FastAPI application entry point with tool initialization."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

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

    # Build combined registry and orchestrator
    registry = _build_registry()
    orchestrator = ChatOrchestrator(settings, registry)

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
