# Data Copilot — Architecture Design

## Overview

Data Copilot is an AI-powered assistant that lets teams query SQL databases, explore
spreadsheets and documents, and pull in web information through natural conversation.
Built on the Model Context Protocol (MCP) with a FastAPI backend and React frontend.

## Architecture Decision: Backend Orchestration

The backend handles all LLM orchestration. The frontend is a pure chat UI.

```
User -> Frontend -> POST /api/chat -> Backend -> OpenRouter API
                                        |             |
                                        |    <-- tool calls -->
                                        |             |
                                        +-- MCP Tools (SQL, Files, Web, Analysis)
                                        |
                                 SSE stream back to Frontend
```

**Why**: API key stays server-side, simpler frontend, single point of control,
easier to add rate limiting and logging.

## Backend Structure

Single FastAPI application with MCP tools as a reusable library:

- **Dual entry point**: FastAPI app for the chat endpoint + MCP server for external clients
- **Tool registry**: Tools defined once as decorated async functions, usable by both
- **Orchestrator**: Calls OpenRouter (OpenAI-compatible API), interprets tool calls,
  executes them via the registry, loops until final text response

### Modules

| Module | Purpose |
|--------|---------|
| `config.py` | Pydantic Settings — DB URL, OpenRouter key, file paths, limits |
| `server.py` | FastAPI app + MCP server dual entry point |
| `chat/router.py` | POST /api/chat (SSE streaming), GET /api/chat/history |
| `chat/orchestrator.py` | OpenRouter client, tool-call loop, conversation state |
| `tools/registry.py` | Central tool registry (shared by chat + MCP server) |
| `tools/sql_tools.py` | query_database, get_schema, explain_query |
| `tools/file_tools.py` | list_files, read_file, search_files |
| `tools/web_tools.py` | web_search, fetch_url |
| `tools/analysis_tools.py` | describe_data, cross_join, export_csv |
| `connectors/database.py` | SQLAlchemy async engine pool, read-only enforcement |
| `connectors/filesystem.py` | Sandboxed file access (stays within allowed dirs) |
| `connectors/web.py` | DuckDuckGo search + httpx URL fetch |
| `parsers/*.py` | CSV, Excel, PDF, text/JSON parsing |
| `utils/safety.py` | Query validation, size limits, timeout, input sanitization |
| `utils/formatting.py` | Result formatting for LLM consumption |

### LLM Integration (OpenRouter)

- Uses OpenAI-compatible chat completions API via OpenRouter
- Tool definitions sent as OpenAI function calling format
- Supports streaming responses via SSE
- Retry with exponential backoff (max 3 retries) for rate limits/timeouts
- Environment variable: `OPENROUTER_API_KEY`

## Frontend Structure

React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui.

No MCP client in the frontend — it's a pure chat interface that calls the backend.

### Components

| Component | Purpose |
|-----------|---------|
| `ChatWindow.tsx` | Scrollable message list with auto-scroll |
| `MessageBubble.tsx` | Renders markdown, tables, charts, source badges |
| `InputBar.tsx` | Text input + send + keyboard submit |
| `SourcePanel.tsx` | Lists connected data sources with status |
| `ConnectionForm.tsx` | Form to add DB connection or file directory |
| `DataTable.tsx` | Sortable table for query results |
| `SimpleChart.tsx` | Bar/line chart using recharts |
| `Sidebar.tsx` | Navigation, source list, history |
| `Header.tsx` | App title + settings |

### State Management

React hooks only (useChat, useDataSources). No external state library.

### Streaming

SSE connection per chat request. Tokens rendered as they arrive.

### Source Attribution

Each message includes metadata about which tools were used, displayed as colored
badges (SQL, File, Web, Analysis).

## Infrastructure

### Docker Compose (3 services)

1. **`db`** — PostgreSQL 16, initialized with `sample-data/init.sql`
2. **`backend`** — Python 3.11, FastAPI on port 8000
3. **`frontend`** — Node 20, Vite dev server on port 3000

### Sample Data

- `init.sql` — ~10K rows across 5 tables (customers, products, orders, order_items, sales_reps)
- `marketing_campaigns.csv` — 50 rows of campaign data
- `regional_targets.csv` — 20 rows of quarterly targets by region
- `company_policies.md` — return/refund policy document
- `market_report.md` — market analysis document

### Security

- Read-only PostgreSQL role for queries
- File access sandboxed to configured directories
- Query limits: max 1000 rows, 30s timeout
- Input sanitization on all tool inputs
- API key server-side only

## Error Handling

- Connectors raise typed exceptions (DatabaseConnectionError, FileNotFoundError, etc.)
- Tools catch connector errors and return user-friendly messages
- Orchestrator retries OpenRouter errors (exponential backoff, max 3)
- Chat endpoint always returns valid SSE stream, even for errors

## Testing

- Unit tests per tool module (mocked connectors)
- Unit tests for parsers (fixture files)
- Integration tests for orchestrator (mocked OpenRouter)
- Integration tests for chat endpoint (full cycle, mocked LLM)
- SQLite for SQL tool tests (no PostgreSQL dependency in tests)
- `pytest` + `pytest-asyncio`
