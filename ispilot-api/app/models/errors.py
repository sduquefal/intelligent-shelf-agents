"""Standardized error models for API responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """
    Standard error response contract used across all API endpoints.
    
    All API errors return this consistent structure for easy programmatic handling
    and debugging. The error_code field allows clients to handle specific error types,
    while error_message provides a user-friendly description.
    """

    error_code: str = Field(
        description="Machine-readable error code (e.g., VERTEX_TIMEOUT, AUTH_FAILED). "
                    "Use this for programmatic error handling and routing.",
        example="VERTEX_TIMEOUT"
    )
    error_message: str = Field(
        description="Human-readable error message suitable for displaying to users",
        example="Request to Vertex AI timed out. Please retry."
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for this request. Use this when reporting issues to support.",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO-8601 timestamp of when this error occurred",
        example="2026-08-28T10:30:45.123456"
    )
    details: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional error context and debug information. Only present when debug mode is enabled.",
        example={"exception_type": "TimeoutError", "retry_after_seconds": 5}
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": "VERTEX_TIMEOUT",
                "error_message": "Request to Vertex AI timed out. Please retry.",
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2026-08-28T10:30:45.123456",
                "details": None
            }
        }


class ValidationErrorResponse(ErrorResponse):
    """Validation error response for malformed requests."""

    error_code: str = "VALIDATION_ERROR"
    details: Optional[dict[str, Any]] = Field(
        default=None,
        description="Field validation errors with paths and descriptions",
        example={"field_errors": {"message": "field required"}}
    )


class AuthenticationErrorResponse(ErrorResponse):
    """Authentication error response for auth failures."""

    error_code: str = "AUTH_FAILED"


class NotFoundErrorResponse(ErrorResponse):
    """Resource not found error response."""

    error_code: str = "NOT_FOUND"


class ServerErrorResponse(ErrorResponse):
    """Server error response for internal failures."""

    error_code: str = "INTERNAL_SERVER_ERROR"


# Standard error codes used across the API
# Each code has a description for documentation purposes
ERROR_CODES = {
    "MISSING_API_KEY": "Authorization header or X-API-Key header is required for this endpoint",
    "INVALID_API_KEY": "Invalid or expired API key provided",
    "AUTH_FAILED": "Authentication failed. Please check your credentials.",
    "SERVER_CONFIG_ERROR": "API server misconfiguration. Contact support if this persists.",
    "VERTEX_TIMEOUT": "Request to Vertex AI timed out. Please retry.",
    "VERTEX_ERROR": "Error communicating with Vertex AI backend",
    "FIRESTORE_UNAVAILABLE": "Session storage temporarily unavailable",
    "SESSION_NOT_FOUND": "Session not found or expired",
    "VALIDATION_ERROR": "Request validation failed. Check request body format.",
    "NOT_FOUND": "Requested resource not found",
    "INTERNAL_SERVER_ERROR": "Unexpected server error. Contact support if this persists.",
    "RATE_LIMIT_EXCEEDED": "Rate limit exceeded. Please retry after some time.",
}
