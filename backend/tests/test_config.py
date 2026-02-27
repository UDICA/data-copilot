"""Tests for application configuration."""

from src.config import Settings


def test_settings_loads_defaults():
    """Settings should load with sensible defaults when env vars are minimal."""
    settings = Settings(openrouter_api_key="test-key")
    assert settings.openrouter_api_key == "test-key"
    assert settings.db_read_only is True
    assert settings.max_query_rows == 1000
    assert settings.query_timeout_seconds == 30


def test_settings_override_from_env(monkeypatch):
    """Settings should pick up values from environment variables."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "env-key")
    monkeypatch.setenv("MAX_QUERY_ROWS", "500")
    monkeypatch.setenv("DB_READ_ONLY", "false")
    settings = Settings()
    assert settings.openrouter_api_key == "env-key"
    assert settings.max_query_rows == 500
    assert settings.db_read_only is False
