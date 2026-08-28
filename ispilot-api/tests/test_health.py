"""Tests for health check endpoint."""

import pytest


class TestHealth:
    """Test cases for the /health endpoint."""

    def test_health_check_returns_200(self, client):
        """Test that health endpoint returns 200 OK."""
        # Arrange
        # (no setup needed - public endpoint)

        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200

    def test_health_check_response_structure(self, client):
        """Test that health response has correct structure."""
        # Arrange
        # (no setup needed - public endpoint)

        # Act
        response = client.get("/health")
        data = response.json()

        # Assert
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"

    def test_health_check_response_content_type(self, client):
        """Test that health endpoint returns JSON content type."""
        # Arrange
        # (no setup needed - public endpoint)

        # Act
        response = client.get("/health")

        # Assert
        assert response.headers["content-type"] == "application/json"

    def test_health_check_timestamp_format(self, client):
        """Test that health endpoint timestamp is valid ISO format."""
        # Arrange
        # (no setup needed - public endpoint)

        # Act
        response = client.get("/health")
        data = response.json()

        # Assert
        timestamp = data["timestamp"]
        # Should be ISO format string
        assert isinstance(timestamp, str)
        assert "T" in timestamp or "+" in timestamp or "Z" in timestamp
