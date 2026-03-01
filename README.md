# Data Copilot

**Ask questions across your databases, spreadsheets, and documents — get answers in plain English.**

Every data team knows the pain: a stakeholder asks "how did our enterprise accounts in the North region perform last quarter compared to our targets?" The answer lives across a SQL database, a CSV from marketing, and a policy document. A data scientist spends 30 minutes pulling it together. Data Copilot does it in seconds.

## What It Does

Data Copilot is a conversational AI assistant that connects to your existing data sources and answers questions naturally. No SQL required, no CSV wrangling, no switching between tools.

- **SQL Databases** — Query PostgreSQL, MySQL, or SQLite through conversation. Schema introspection, query execution, and result formatting happen automatically.
- **Files & Documents** — Read and analyze CSV, Excel, PDF, Markdown, JSON, and plain text files. Get summaries, filter data, and search across directories.
- **Web Search** — Pull in current information from the web to enrich your analysis with market data, competitor info, or industry context.
- **Cross-Source Analysis** — The real power: join SQL results with CSV data, compare database metrics against spreadsheet targets, and reference policy documents — all in one conversation.

Every response includes **source attribution**, so you always know where the data came from.

## Quick Start

```bash
git clone https://github.com/yourusername/data-copilot.git
cd data-copilot

# Configure your API key
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# Start everything
docker compose up --build

# Open http://localhost:3000
```

The sample PostgreSQL database, CSV files, and documents are pre-loaded. Start asking questions immediately.

## Example Conversations

**1. "What were our top 5 products by revenue last quarter?"**

Data Copilot queries the database, calculates revenue by product, and returns a formatted table with rankings.

**2. "Compare that with the regional targets in the CSV."**

Cross-references SQL results with `regional_targets.csv`, highlighting which regions hit their targets and which fell short.

**3. "Are there any trends in customer orders by segment?"**

Analyzes order patterns across Enterprise, SMB, Startup, and Individual segments. Identifies that Enterprise accounts show 23% higher average order values with seasonal peaks in Q4.

**4. "What's the current market outlook for our top product category?"**

Searches the web for current market intelligence, then summarizes relevant trends and competitive dynamics.

**5. "Summarize the company policy on returns and refunds."**

Reads the internal policy document and provides a concise summary with key details (30-day window, processing time, conditions).

## Connecting Your Data

### Adding a Database

Set the `DATABASE_URL` environment variable to your connection string:

```bash
# PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname

# SQLite
DATABASE_URL=sqlite+aiosqlite:///path/to/database.db
```

### Adding File Directories

Add paths to the `ALLOWED_FILE_PATHS` environment variable:

```bash
ALLOWED_FILE_PATHS=["/path/to/reports", "/path/to/exports"]
```

Data Copilot will be able to browse, read, and analyze files in those directories.

## Architecture

```
User  ─▶  React Frontend  ─▶  FastAPI Backend  ─▶  OpenRouter LLM
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
               SQL Tools       File Tools       Web Tools
                    │                │                │
              PostgreSQL      File System      DuckDuckGo
```

The backend orchestrates everything: it receives chat messages, forwards them to the LLM with available tool definitions, executes any tool calls the LLM requests, and streams the final response back. The frontend is a pure chat UI.

Built on the [Model Context Protocol](https://modelcontextprotocol.io) (MCP), so the tools can also be used by any MCP-compatible client.

## Supported Data Sources

| Source | Formats | Capabilities |
|--------|---------|-------------|
| SQL Database | PostgreSQL, MySQL, SQLite | Query, schema inspection, explain plans |
| Spreadsheets | CSV, TSV, Excel (.xlsx) | Read, filter, summary statistics |
| Documents | PDF, Markdown, TXT | Full text extraction, search |
| Structured Data | JSON | Parse, query nested paths |
| Web | Any URL | Search, fetch, content extraction |

## Configuration

See [docs/setup.md](docs/setup.md) for the full environment variable reference.

Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | (required) | API key for LLM access |
| `OPENROUTER_MODEL` | `openai/gpt-4o-mini` | Which model to use |
| `DATABASE_URL` | — | Database connection string |
| `DB_READ_ONLY` | `true` | Enforce read-only queries |
| `ALLOWED_FILE_PATHS` | `["/app/sample-data"]` | Accessible file directories |

## Security

- **Read-only by default** — Database queries are validated before execution. Write operations are rejected unless explicitly enabled.
- **Path sandboxing** — File access is restricted to configured directories. Path traversal attacks are blocked.
- **Query limits** — Results capped at 1,000 rows, 30-second timeout.
- **No credential exposure** — API keys and database passwords stay server-side. The frontend never sees them.

## Tech Stack

**Backend**: Python 3.11+ · FastAPI · SQLAlchemy · pandas · MCP SDK · OpenRouter

**Frontend**: React 18 · TypeScript · Vite · Tailwind CSS · Recharts

**Infrastructure**: Docker Compose · PostgreSQL 16 · Nginx

## Development

```bash
# Backend
cd backend
pip install -e ".[dev]"
pytest -v                    # 119 tests
uvicorn src.server:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

See [docs/setup.md](docs/setup.md) for detailed setup instructions and [docs/architecture.md](docs/architecture.md) for system design.

## License

MIT — see [LICENSE](LICENSE).
