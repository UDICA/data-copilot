"""Shared test fixtures for the Data Copilot test suite."""

import os
from pathlib import Path

import pytest

# Set test environment variables before any config imports
os.environ.setdefault("OPENROUTER_API_KEY", "test-key-not-real")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///")
os.environ.setdefault("ALLOWED_FILE_PATHS", '["tests/fixtures"]')


@pytest.fixture
def fixtures_dir() -> Path:
    """Return the path to the test fixtures directory."""
    return Path(__file__).parent / "fixtures"
