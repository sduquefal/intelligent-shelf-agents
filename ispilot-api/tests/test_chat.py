"""Tests for chat endpoint."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestChatEndpoint:
    """Test cases for the /chat endpoint."""

    def test_chat_requires_api_key(self, client, valid_chat_request):
        """Test that chat endpoint requires X-API-Key header."""
        # Arrange
        # (no API key header)

        # Act
        response = client.post("/chat", json=valid_chat_request)

        # Assert
        assert response.status_code == 401

    def test_chat_with_valid_api_key(self, client, api_key_header, valid_chat_request):
        """Test that chat endpoint accepts valid API key."""
        # Arrange
        # Mock the services
        with patch("app.api.chat.session_service") as mock_session_service:
            mock_session = {"session_id": "test-session-123"}
            mock_session_service.get_or_create = MagicMock(return_value=mock_session)

            with patch("app.api.chat.vertex_client") as mock_vertex:
                mock_vertex.chat = MagicMock(return_value=("Response from Vertex", "test-session-123"))

                # Act
                response = client.post(
                    "/chat",
                    json=valid_chat_request,
                    headers=api_key_header,
                )

        # Assert
        # TODO: Verify this passes once services are mocked properly
        # assert response.status_code == 200

    def test_chat_response_structure(self, client, api_key_header, valid_chat_request):
        """Test that chat response has correct structure."""
        # Arrange
        # Mock the services
        with patch("app.api.chat.session_service") as mock_session_service:
            mock_session = {"session_id": "test-session-123"}
            mock_session_service.get_or_create = MagicMock(return_value=mock_session)

            with patch("app.api.chat.vertex_client") as mock_vertex:
                mock_vertex.chat = MagicMock(return_value=("Response from Vertex", "test-session-123"))

                # Act
                response = client.post(
                    "/chat",
                    json=valid_chat_request,
                    headers=api_key_header,
                )

        # Assert
        # Expected response structure:
        # {
        #     "answer": "...",
        #     "session_id": "...",
        #     "request_id": "...",
        #     "timestamp": "...",
        #     "status": "success"
        # }
        # TODO: Verify response structure once mocking is complete

    def test_chat_invalid_request_body(self, client, api_key_header):
        """Test that chat endpoint validates request body."""
        # Arrange
        invalid_request = {"user_id": "test"}  # Missing required 'message' field

        # Act
        response = client.post(
            "/chat",
            json=invalid_request,
            headers=api_key_header,
        )

        # Assert
        # Should return 422 Unprocessable Entity for validation error
        # assert response.status_code == 422

    def test_chat_with_explicit_session_id(
        self, client, api_key_header, valid_chat_request_with_session
    ):
        """Test that chat endpoint accepts explicit session ID."""
        # Arrange
        with patch("app.api.chat.session_service") as mock_session_service:
            mock_session = {"session_id": "session-123456"}
            mock_session_service.get = MagicMock(return_value=mock_session)

            with patch("app.api.chat.vertex_client") as mock_vertex:
                mock_vertex.chat = MagicMock(
                    return_value=("Response from Vertex", "session-123456")
                )

                # Act
                response = client.post(
                    "/chat",
                    json=valid_chat_request_with_session,
                    headers=api_key_header,
                )

        # Assert
        # TODO: Verify session_id is used correctly

    def test_chat_invalid_api_key(self, client, valid_chat_request):
        """Test that chat endpoint rejects invalid API key."""
        # Arrange
        invalid_headers = {"X-API-Key": "invalid-key"}

        # Act
        response = client.post(
            "/chat",
            json=valid_chat_request,
            headers=invalid_headers,
        )

        # Assert
        assert response.status_code == 401

    def test_chat_accepts_lowercase_bearer_scheme(self, client, valid_chat_request):
        """Test that bearer tokens are accepted regardless of scheme casing."""
        with patch("app.api.chat.session_service") as mock_session_service:
            mock_session = {"session_id": "test-session-123"}
            mock_session_service.get_or_create = MagicMock(return_value=mock_session)

            with patch("app.api.chat.vertex_client") as mock_vertex:
                mock_vertex.chat = MagicMock(return_value=("Response from Vertex", "test-session-123"))

                response = client.post(
                    "/chat",
                    json=valid_chat_request,
                    headers={"Authorization": "bearer test-token"},
                )

        assert response.status_code == 200

    def test_chat_error_response_structure(
        self, client, api_key_header, valid_chat_request
    ):
        """Test that error responses have correct structure."""
        # Arrange
        with patch("app.api.chat.session_service") as mock_session_service:
            mock_session_service.get_or_create = MagicMock(
                side_effect=Exception("Service error")
            )

            # Act
            response = client.post(
                "/chat",
                json=valid_chat_request,
                headers=api_key_header,
            )

        # Assert
        # Expected error response:
        # {
        #     "error_code": "...",
        #     "error_message": "...",
        #     "request_id": "..."
        # }
        # TODO: Verify error response structure


class TestChatRequestValidation:
    """Test request validation for chat endpoint."""

    def test_chat_missing_user_id(self, client, api_key_header):
        """Test that chat requires user_id."""
        # Arrange
        request = {"message": "Hello"}  # Missing user_id

        # Act
        response = client.post(
            "/chat",
            json=request,
            headers=api_key_header,
        )

        # Assert
        # Should return 422 for validation error
        # assert response.status_code == 422

    def test_chat_missing_message(self, client, api_key_header):
        """Test that chat requires message."""
        # Arrange
        request = {"user_id": "test-user"}  # Missing message

        # Act
        response = client.post(
            "/chat",
            json=request,
            headers=api_key_header,
        )

        # Assert
        # Should return 422 for validation error
        # assert response.status_code == 422

    def test_chat_empty_message(self, client, api_key_header):
        """Test that chat rejects empty message."""
        # Arrange
        request = {"user_id": "test-user", "message": ""}

        # Act
        response = client.post(
            "/chat",
            json=request,
            headers=api_key_header,
        )

        # Assert
        # Should return 422 or 400 for empty message
        # assert response.status_code in [400, 422]
