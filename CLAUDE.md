# Data Copilot — AI Assistant That Talks to Your Databases, Files & the Web

## Project Overview
Data Copilot is an AI-powered assistant that lets teams query their SQL databases, explore spreadsheets and documents, and pull in web information — all through natural conversation. Instead of writing SQL, wrangling CSVs, or digging through file folders, users simply ask questions and get answers with full source attribution.

Built on the Model Context Protocol (MCP), Data Copilot connects LLMs to real data sources through a standardized, extensible server architecture.


## CRITICAL DESIGN PHILOSOPHY
**This project must read as a tool built to solve a real business problem — NOT as a technical demonstration or portfolio piece.** The story is: "Teams waste hours switching between databases, spreadsheets, and documents to answer simple business questions — Data Copilot eliminates that friction." The MCP architecture, tool routing, and LLM orchestration are the *means*, not the *purpose*. The mastery of these technologies is implicit and self-evident from the code — it should never be stated explicitly. Anyone reading this should think: "This person builds tools that solve real problems" — not "This person knows how MCP works."

## The Business Problem
Every data team deals with this: business stakeholders need answers that live across multiple systems. A sales question might require joining a SQL database with a CSV export from marketing, cross-referencing a policy document, and checking current market conditions online. Today, a data scientist manually bridges these gaps. Data Copilot automates that bridge.

## Architecture

### MCP Server (Python Backend)
The MCP server exposes multiple tool categories through the Model Context Protocol:

**1. SQL Database Tools**
- Connect to PostgreSQL, MySQL, or SQLite databases
- Natural language to SQL translation
- Schema introspection (tables, columns, types, relationships)
- Query execution with result formatting
- Query explanation and optimization suggestions
- Safety: read-only mode by default, parameterized queries, query size limits


**2. File System & Document Tools**
- Browse directory structures
- Read and parse multiple formats:
  - CSV/TSV → automatic column detection, summary statistics, filtering
  - Excel (.xlsx) → sheet selection, range reading
  - PDF → text extraction with page references
  - Markdown/TXT → full text reading
  - JSON → structure exploration and querying
- File search by name, type, or content
- Metadata extraction (size, dates, type)

**3. Web Search & Retrieval Tools**
- Web search for current information (via DuckDuckGo or similar free API)
- URL content fetching and summarization
- Useful for enriching internal data with external context (market data, competitor info, news)

**4. Data Analysis Tools**

- Basic statistical analysis on query results or CSV data

- Cross-source data joining (e.g., join SQL results with CSV data)
- Trend detection and summary generation
- Export results to CSV or formatted markdown tables


### Client Demo (TypeScript/React Frontend)
A simple but polished chat interface that demonstrates Data Copilot in action:
- Chat interface with streaming responses
- Data source connection panel (add databases, point to file directories)
- Result visualization (tables, basic charts for numeric data)
- Source attribution (shows which tool/source was used for each answer)
- Query history
- Export functionality


## Tech Stack

### Backend (Python)

- **Language**: Python 3.11+
- **MCP SDK**: `mcp` (official Model Context Protocol Python SDK)
- **Database**: `sqlalchemy` + `asyncpg` (PostgreSQL) / `aiosqlite` (SQLite)

- **Document Processing**: `pypdf`, `python-docx`, `openpyxl`, `pandas`
- **Web Search**: `duckduckgo-search` or `serpapi` (free tier)
- **Data Analysis**: `pandas`, `numpy`
- **Server**: `uvicorn` / `starlette` for HTTP transport, or stdio for direct MCP
- **Testing**: `pytest`, `pytest-asyncio`
- **Linting**: `ruff`

### Frontend (TypeScript/React)
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **UI Library**: Tailwind CSS + shadcn/ui (clean, professional look)
- **Chat Interface**: Custom chat component with markdown rendering
- **Data Display**: Simple table component, basic chart (recharts or chart.js)
- **MCP Client**: Connect to MCP server via SSE or HTTP transport
- **State Management**: React hooks (zustand if needed)

### Infrastructure
- **Containerization**: Docker + docker-compose (backend + frontend + sample PostgreSQL DB)
- **Sample Database**: Pre-loaded PostgreSQL with realistic business data (sales, customers, products)

## Project Structure
```
data-copilot/
├── CLAUDE.md
├── README.md
├── LICENSE                         # MIT License
├── docker-compose.yml              # All services: backend, frontend, sample DB
├── .env.example
├── .gitignore
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── src/
│   │   ├── __init__.py

│   │   ├── config.py               # Configuration (pydantic-settings)
│   │   ├── server.py               # MCP server initialization and tool registration
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── sql_tools.py        # Database query, schema, explain tools
│   │   │   ├── file_tools.py       # File browsing, reading, parsing tools
│   │   │   ├── web_tools.py        # Web search and URL fetching tools
│   │   │   └── analysis_tools.py   # Cross-source analysis and stats tools
│   │   ├── connectors/
│   │   │   ├── __init__.py

│   │   │   ├── database.py         # SQLAlchemy async database connector
│   │   │   ├── filesystem.py       # File system access layer
│   │   │   └── web.py              # Web search/fetch connector
│   │   ├── parsers/

│   │   │   ├── __init__.py
│   │   │   ├── csv_parser.py       # CSV/TSV intelligent parsing
│   │   │   ├── excel_parser.py     # Excel file parsing
│   │   │   ├── pdf_parser.py       # PDF text extraction
│   │   │   └── text_parser.py      # Markdown, TXT, JSON parsing
│   │   └── utils/

│   │       ├── __init__.py
│   │       ├── safety.py           # Query validation, sandboxing, rate limits
│   │       └── formatting.py       # Result formatting for LLM consumption
│   └── tests/
│       ├── test_sql_tools.py
│       ├── test_file_tools.py
│       ├── test_web_tools.py
│       ├── test_analysis_tools.py

│       └── test_integration.py
├── frontend/
│   ├── Dockerfile
│   ├── package.json

│   ├── tsconfig.json

│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── index.html
│   └── src/
│       ├── main.tsx
│       ├── App.tsx

│       ├── components/
│       │   ├── Chat/
│       │   │   ├── ChatWindow.tsx       # Main chat interface
│       │   │   ├── MessageBubble.tsx     # Individual message with source attribution
│       │   │   └── InputBar.tsx          # Message input with send
│       │   ├── DataSources/

│       │   │   ├── SourcePanel.tsx       # Data source connection manager
│       │   │   └── ConnectionForm.tsx    # Add new database/directory
│       │   ├── Results/
│       │   │   ├── DataTable.tsx         # Query result table display
│       │   │   └── SimpleChart.tsx       # Basic chart visualization
│       │   └── Layout/
│       │       ├── Sidebar.tsx           # Navigation and source list
│       │       └── Header.tsx
│       ├── hooks/
│       │   ├── useMCPClient.ts          # MCP client connection hook
│       │   └── useChat.ts               # Chat state management
│       ├── services/
│       │   └── mcpClient.ts             # MCP client implementation
│       └── types/

│           └── index.ts                 # TypeScript type definitions
├── sample-data/
│   ├── init.sql                         # PostgreSQL seed: sales, customers, products tables
│   ├── sample_csvs/
│   │   ├── marketing_campaigns.csv      # Marketing spend and performance
│   │   └── regional_targets.csv         # Quarterly targets by region
│   └── sample_docs/
│       ├── company_policies.md          # Sample internal document
│       └── market_report.pdf            # Sample external report (public domain)
└── docs/
    ├── architecture.md
    ├── setup.md
    └── images/
        └── demo_screenshot.png
```

## Sample Database Schema
Pre-loaded PostgreSQL with realistic (but synthetic) business data to make the demo compelling:


```sql
-- Core business tables
customers (id, name, email, segment, region, created_at)
products (id, name, category, price, cost, status)
orders (id, customer_id, order_date, total_amount, status)
order_items (id, order_id, product_id, quantity, unit_price)

sales_reps (id, name, region, hire_date)

-- ~10K rows of realistic synthetic data
-- Enough to show meaningful queries and patterns
```

## Demo Scenarios
The README should include example conversations that show real business value:

1. **"What were our top 5 products by revenue last quarter?"** → SQL query, formatted table
2. **"Compare that with the regional targets in the CSV"** → Cross-source: SQL results + CSV data
3. **"Are there any trends in customer churn by segment?"** → Analysis tool with SQL data
4. **"What's the current market outlook for our top product category?"** → Web search enrichment
5. **"Summarize the company policy on returns"** → Document reading tool


These scenarios demonstrate the real power: seamlessly combining multiple data sources in a single conversation.


## README Requirements
The README must tell a story about the problem being solved:

1. **Opening**: Describe the pain point (data scattered across systems, stakeholders waiting for analysts)
2. **What Data Copilot Does**: Clear, non-technical explanation with a screenshot/GIF
3. **Quick Start**: `docker-compose up` and go
4. **Example Conversations**: Show 3-5 real business scenarios with actual outputs
5. **Connecting Your Data**: How to point it at your own database/files
6. **Architecture Overview**: Brief, with diagram — explains MCP at a high level for the curious
7. **Supported Data Sources**: Table of what's supported
8. **Configuration**: Environment variables, connection strings
9. **Security Considerations**: Read-only mode, query limits, no credential exposure
10. **Tech Stack**: Badges and versions
11. **Contributing & License**

## Code Quality Standards
- Type hints on all functions (Python and TypeScript)

- Docstrings on all public methods (Google style for Python, JSDoc for TypeScript)
- Pydantic models for configuration and data validation
- Abstract base classes for connectors (easy to add new data sources)
- Comprehensive error handling with user-friendly error messages
- Logging with structured output
- All secrets via environment variables
- SQL injection prevention (parameterized queries, read-only connections)
- Input validation on all tool inputs

## Key Design Decisions to Highlight
These demonstrate senior-level, business-aware thinking:
1. **Read-only database access by default** — shows security consciousness
2. **Cross-source analysis** — the killer feature; joining SQL + CSV in conversation
3. **Source attribution in every response** — shows awareness of trust/transparency in AI tools
4. **Extensible connector architecture** — easy to add new data sources without modifying core
5. **Safety guardrails** — query size limits, timeout handling, input sanitization
6. **Sample data that tells a business story** — realistic scenarios, not lorem ipsum

## Demo Mode

Must work out-of-the-box:
```bash
git clone <repo>
cd data-copilot
docker-compose up
# Open http://localhost:3000
# Sample PostgreSQL DB, CSV files, and documents are pre-loaded
# Works with Ollama (local, free) — no API keys needed for basic demo
```

## LLM Configuration
- **Default**: Ollama (local, free) for zero-setup demo
- **Optional**: OpenAI, Anthropic via environment variables
- The MCP server itself is LLM-agnostic — it exposes tools, any MCP-compatible client can use them

## What NOT to Include
- No proprietary data or company-specific code

- No API keys or secrets (even in git history)
- No overly complex abstractions — keep it readable
- **CRITICAL: Do NOT mention, reference, or hint anywhere in the codebase (code, comments, README, docs, commit messages, or any file) that this project was built using Claude Code, any AI coding assistant, or any AI tool. The code must read as if it was written entirely by the developer.**
- **CRITICAL: Do NOT mention, reference, or hint anywhere in the codebase that this project is intended as a portfolio piece, job application material, or meant to be evaluated by recruiters. It must read as a genuine tool built to solve a real business problem.**

## Tone
The whole project should read as: "I had this problem at work, so I built a tool to fix it." Professional, practical, zero fluff. Code comments explain *why* business decisions were made, not just technical *what*. The README speaks to potential users, not evaluators.
