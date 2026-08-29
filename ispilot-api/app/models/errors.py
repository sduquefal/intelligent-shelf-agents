"""Standardized error models for API responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response contract."""

    error_code: str = Field(
        description="Machine-readable error code (e.g., VERTEX_TIMEOUT, AUTH_FAILED)"
    )
    error_message: str = Field(description="Human-readable error message")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracing")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Error timestamp (ISO-8601)",
    )
    details: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional error context (development only)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "VERTEX_TIMEOUT",
                "error_message": "Request to Vertex AI timed out. Please retry.",
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2026-08-28T10:30:45.123456",
            }
        }


class ValidationErrorResponse(ErrorResponse):
    """Validation error response."""

    error_code: str = "VALIDATION_ERROR"
    details: Optional[dict[str, Any]] = Field(
        default=None,
        description="Field validation errors",
    )


class AuthenticationErrorResponse(ErrorResponse):
    """Authentication error response."""

    error_code: str = "AUTH_FAILED"


class NotFoundErrorResponse(ErrorResponse):
    """Resource not found error response."""

    error_code: str = "NOT_FOUND"


class ServerErrorResponse(ErrorResponse):
    """Server error response."""

    error_code: str = "INTERNAL_SERVER_ERROR"


# Standard error codes used across the API
ERROR_CODES = {
    "MISSING_API_KEY": "Authorization header or X-API-Key header required",
    "INVALID_API_KEY": "Invalid API key provided",
    "AUTH_FAILED": "Authentication failed",
    "SERVER_CONFIG_ERROR": "API server misconfiguration",
    "VERTEX_TIMEOUT": "Request to Vertex AI timed out. Please retry.",
    "VERTEX_ERROR": "Error communicating with Vertex AI",
    "FIRESTORE_UNAVAILABLE": "Session storage temporarily unavailable",
    "SESSION_NOT_FOUND": "Session not found or expired",
    "VALIDATION_ERROR": "Request validation failed",
    "NOT_FOUND": "Requested resource not found",
    "INTERNAL_SERVER_ERROR": "Unexpected server error",
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded. Please retry later.",
}
