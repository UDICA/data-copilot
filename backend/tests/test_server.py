"""Tests for the FastAPI server setup."""

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from src.server import create_app


class TestServer:
    def test_app_creation(self):
        """App should be created with correct metadata."""
        app = create_app()
        assert app.title == "Data Copilot"

    def test_cors_configured(self):
        """App should have CORS middleware."""
        app = create_app()
        middleware_classes = [m.cls.__name__ for m in app.user_middleware]
        assert "CORSMiddleware" in middleware_classes

    def test_health_endpoint_available(self):
        """Health endpoint should be registered on the app."""
        app = create_app()
        routes = [r.path for r in app.routes]
        assert "/api/health" in routes

    def test_chat_endpoint_available(self):
        """Chat endpoint should be registered on the app."""
        app = create_app()
        routes = [r.path for r in app.routes]
        assert "/api/chat" in routes
