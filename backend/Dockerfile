FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies for asyncpg
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .

# Install Python dependencies
RUN pip install --no-cache-dir . && \
    apt-get purge -y --auto-remove gcc

COPY src/ src/

EXPOSE 8000

CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
