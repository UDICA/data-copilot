# Architecture

## System Overview

Data Copilot connects users to their data through natural conversation. The system has three main components:

```
┌─────────────┐     ┌──────────────────────────────────┐     ┌──────────┐
│   Frontend   │────▶│           Backend                │────▶│ OpenRouter│
│  (React UI)  │◀────│  FastAPI + Tool Registry         │◀────│   LLM    │
└─────────────┘     │                                  │     └──────────┘
                    │  ┌──────────┐ ┌──────────────┐   │
                    │  │ SQL Tools│ │  File Tools   │   │
                    │  └────┬─────┘ └──────┬───────┘   │
                    │       │              │           │
                    │  ┌────▼─────┐ ┌──────▼───────┐   │
                    │  │PostgreSQL│ │  File System  │   │
                    │  └──────────┘ └──────────────┘   │
                    │                                  │
                    │  ┌──────────┐ ┌──────────────┐   │
                    │  │Web Tools │ │Analysis Tools│   │
                    │  └────┬─────┘ └──────────────┘   │
                    │       │                          │
                    │  ┌────▼──────┐                    │
                    │  │DuckDuckGo │                    │
                    │  └───────────┘                    │
                    └──────────────────────────────────┘
```

## Request Flow

1. User types a question in the chat interface
2. Frontend sends the message to `POST /api/chat`
3. Backend forwards the conversation to OpenRouter with tool definitions
4. If the LLM decides to use a tool, the backend:
   - Executes the tool (SQL query, file read, web search, etc.)
   - Sends the tool result back to the LLM
   - Repeats until the LLM produces a final text response
5. The final response streams back to the frontend as Server-Sent Events (SSE)
6. The frontend renders the response with source attribution badges

## Backend Architecture

The backend uses a **tool registry** pattern: all tools are defined as decorated async functions in separate modules. Each module has its own registry, and the server merges them into a single combined registry at startup.

This design means tools can be:
- Used directly by the chat orchestrator (fast, in-process)
- Exposed as a standalone MCP server for external clients
- Tested independently with mocked connectors

### Layers

| Layer | Purpose | Examples |
|-------|---------|---------|
| **Tools** | Business logic for each capability | `query_database`, `read_file`, `web_search` |
| **Connectors** | Abstracted access to external systems | `DatabaseConnector`, `FilesystemConnector`, `WebConnector` |
| **Parsers** | File format handling | CSV, Excel, PDF, JSON/Markdown parsing |
| **Utilities** | Cross-cutting concerns | Query validation, path sandboxing, result formatting |

### Safety Guardrails

- **Read-only database access**: All SQL queries are validated before execution. Write operations (INSERT, UPDATE, DELETE, DROP) are rejected.
- **Path sandboxing**: File access is restricted to explicitly configured directories. Path traversal attacks are blocked.
- **Query limits**: Results are capped at 1,000 rows. Queries time out after 30 seconds.
- **Input sanitization**: All tool inputs are validated before processing.

## Adding New Data Sources

To add a new data source connector:

1. Create a connector class in `backend/src/connectors/` that handles the connection lifecycle
2. Create a tool module in `backend/src/tools/` with functions registered via `@tool`
3. Initialize the connector and wire the tools in `backend/src/server.py`
4. The tools automatically appear in the LLM's available tool set

## Frontend Architecture

The frontend is a standard React application with no MCP client logic. It communicates exclusively through the backend's REST API:

- `POST /api/chat` — Send messages, receive SSE stream
- `GET /api/sources` — List connected data sources
- `GET /api/health` — Health check

State management uses React hooks only (`useChat`, `useDataSources`).
