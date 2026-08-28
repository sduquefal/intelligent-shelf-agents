"""Pytest configuration and fixtures for IsPilot API tests."""

import importlib
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    test_env = {
        "GOOGLE_CLOUD_PROJECT": "test-project",
        "GOOGLE_CLOUD_LOCATION": "us-central1",
        "VERTEX_PROJECT_ID": "test-project",
        "VERTEX_LOCATION": "us-central1",
        "VERTEX_ENGINE_ID": "test-engine-id",
        "ISPILOT_API_KEY": "test-api-key",
        "SESSION_TIMEOUT_HOURS": "8",
        "FIRESTORE_COLLECTION": "user_sessions",
    }
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)
    return test_env


@pytest.fixture
def client():
    """FastAPI test client."""
    import app.main
    import app.api.chat
    importlib.reload(app.api.chat)
    importlib.reload(app.main)
    from app.main import app
    return TestClient(app)


@pytest.fixture
def mock_firestore_client(monkeypatch):
    """Mock Firestore client."""
    mock_client = MagicMock()
    mock_client.save_session = AsyncMock()
    mock_client.get_session = AsyncMock()
    return mock_client


@pytest.fixture
def mock_vertex_client(monkeypatch):
    """Mock Vertex AI client."""
    mock_client = MagicMock()
    mock_client.create_session = AsyncMock()
    mock_client.send_message = AsyncMock(return_value="Mock response from Vertex")
    return mock_client


@pytest.fixture
def api_key_header():
    """Default API key header for requests."""
    return {"X-API-Key": "test-api-key"}


@pytest.fixture
def user_id():
    """Default test user ID."""
    return "test-user-123"


@pytest.fixture
def session_id():
    """Default test session ID."""
    return "session-123456"


@pytest.fixture
def valid_chat_request():
    """Valid chat request payload."""
    return {
        "user_id": "test-user-123",
        "message": "What is the inventory status?",
    }


@pytest.fixture
def valid_chat_request_with_session(session_id):
    """Valid chat request with explicit session ID."""
    return {
        "user_id": "test-user-123",
        "message": "What is the inventory status?",
        "session_id": session_id,
    }
