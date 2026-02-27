# Development Setup

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker and Docker Compose (for the full stack)
- An [OpenRouter](https://openrouter.ai) API key

## Quick Start (Docker)

The fastest way to run everything:

```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

docker-compose up --build
```

Open http://localhost:3000 and start asking questions.

## Local Development

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e ".[dev]"

# Set environment variables
export OPENROUTER_API_KEY=your-key
export DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname
export ALLOWED_FILE_PATHS='["/path/to/files"]'

# Run the server
uvicorn src.server:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

npm install
npm run dev
```

The dev server runs on http://localhost:3000 and proxies `/api` requests to the backend at port 8000.

### Running Tests

```bash
cd backend
pytest -v
```

Tests use SQLite and mocked external services — no PostgreSQL or API keys required.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | (required) | Your OpenRouter API key |
| `OPENROUTER_MODEL` | `openai/gpt-4o-mini` | LLM model identifier |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Database connection string |
| `DB_READ_ONLY` | `true` | Enforce read-only database access |
| `ALLOWED_FILE_PATHS` | `["/app/sample-data"]` | JSON array of allowed file directories |
| `MAX_QUERY_ROWS` | `1000` | Maximum rows returned per query |
| `QUERY_TIMEOUT_SECONDS` | `30` | SQL query timeout |
| `MAX_FILE_SIZE_MB` | `50` | Maximum file size to read |
| `LOG_LEVEL` | `INFO` | Logging level |

## Project Structure

```
data-copilot/
├── backend/           # Python FastAPI backend
│   ├── src/
│   │   ├── chat/      # Chat orchestrator and API router
│   │   ├── connectors/# Database, filesystem, web connectors
│   │   ├── parsers/   # CSV, Excel, PDF, text parsers
│   │   ├── tools/     # MCP tool implementations
│   │   └── utils/     # Safety, formatting utilities
│   └── tests/         # pytest test suite
├── frontend/          # React TypeScript frontend
│   └── src/
│       ├── components/# UI components
│       ├── hooks/     # React hooks
│       └── services/  # API client
├── sample-data/       # Demo data (SQL seed, CSVs, documents)
└── docs/              # Documentation
```
