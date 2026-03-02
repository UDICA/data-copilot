"""Application configuration loaded from environment variables."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for Data Copilot."""

    # OpenRouter LLM
    openrouter_api_key: str = Field(description="OpenRouter API key for LLM access")
    openrouter_model: str = Field(
        default="anthropic/claude-haiku-4.5",
        description="Model identifier on OpenRouter",
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter API base URL",
    )

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://datacopilot:datacopilot@localhost:5432/datacopilot",
        description="SQLAlchemy async database URL",
    )
    db_read_only: bool = Field(
        default=True,
        description="Enforce read-only database access",
    )

    # File system
    allowed_file_paths: list[str] = Field(
        default_factory=lambda: ["/app/sample-data"],
        description="Directories the file tools are allowed to access",
    )

    # Safety limits
    max_query_rows: int = Field(default=1000, description="Maximum rows returned per query")
    query_timeout_seconds: int = Field(default=30, description="SQL query timeout in seconds")
    max_file_size_mb: int = Field(default=50, description="Maximum file size to read in MB")

    # Server
    host: str = Field(default="0.0.0.0", description="Server bind host")
    port: int = Field(default=8000, description="Server bind port")
    log_level: str = Field(default="INFO", description="Logging level")

    model_config = {"env_prefix": "", "env_file": ".env", "extra": "ignore"}


def get_settings() -> Settings:
    """Return a Settings instance."""
    return Settings()
