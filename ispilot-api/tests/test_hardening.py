import pytest

from app.services.auth_service import AuthService
from app.services.session_service import SessionService
from app.services.vertex_client import VertexAgentClient


def test_vertex_empty_output_raises_value_error():
    client = VertexAgentClient()

    with pytest.raises(ValueError, match="no usable text output|empty output"):
        client._extract_text({"output": []})


def test_auth_service_rejects_invalid_key(monkeypatch):
    monkeypatch.setenv("ISPILOT_API_KEY", "secret-key")
    auth = AuthService(api_key="secret-key")

    assert auth.validate("secret-key") is True

    with pytest.raises(ValueError):
        auth.validate("wrong-key")


def test_session_service_tracks_user_session():
    store = {}
    session_service = SessionService(store=store)

    session_id = session_service.get_or_create("user-123", "session-1")

    assert session_id == "session-1"
    assert session_service.get_current("user-123") == "session-1"

    next_session = session_service.get_or_create("user-123", "session-2")
    assert next_session == "session-2"
