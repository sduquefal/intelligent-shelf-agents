from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """
    Response model for chat endpoint.
    
    Represents a successful response from the IsPilot agent to a user's message.
    Includes session management, request tracking, and timestamp information.
    """
    
    answer: str = Field(
        ...,
        description="The agent's response to the user's message",
        example="The inventory status for SKU 12345 is: In Stock (250 units)"
    )
    session_id: str = Field(
        ...,
        description="Session ID for maintaining conversation context across multiple requests",
        example="session_550e8400-e29b-41d4-a716-446655440000"
    )
    request_id: str = Field(
        ...,
        description="Unique identifier for this request, useful for debugging and audit logs",
        example="req_550e8400-e29b-41d4-a716-446655440000"
    )
    timestamp: datetime = Field(
        ...,
        description="ISO-8601 timestamp of when this response was generated",
        example="2026-08-29T03:38:06.750012"
    )
    status: str = Field(
        ...,
        description="Status of the request (ok for success, error for failures)",
        example="ok"
    )

    class Config:
        """Configuration for the ChatResponse model."""
        json_schema_extra = {
            "example": {
                "answer": "The inventory status for SKU 12345 is: In Stock (250 units)",
                "session_id": "session_550e8400-e29b-41d4-a716-446655440000",
                "request_id": "req_550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2026-08-29T03:38:06.750012",
                "status": "ok"
            }
        }


class ErrorResponse(BaseModel):
    """
    Response model for errors.
    
    Standardized error response returned by the API for all error conditions.
    Includes error code for programmatic handling and request tracking for debugging.
    """
    
    error_code: str = Field(
        ...,
        description="Machine-readable error code for programmatic handling",
        example="INVALID_API_KEY"
    )
    error_message: str = Field(
        ...,
        description="Human-readable error message",
        example="Invalid API key provided"
    )
    request_id: str = Field(
        ...,
        description="Unique identifier for this request, useful for debugging and support",
        example="req_550e8400-e29b-41d4-a716-446655440000"
    )
    timestamp: str = Field(
        ...,
        description="ISO-8601 timestamp of when this error occurred",
        example="2026-08-29T03:38:06.750012"
    )
    details: dict | None = Field(
        None,
        description="Additional debug details, only present when debug mode is enabled",
        example={"exception_type": "ValueError"}
    )

    class Config:
        """Configuration for the ErrorResponse model."""
        json_schema_extra = {
            "example": {
                "error_code": "INVALID_API_KEY",
                "error_message": "Invalid API key provided",
                "request_id": "req_550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2026-08-29T03:38:06.750012",
                "details": None
            }
        }


class HealthResponse(BaseModel):
    """
    Response model for health endpoint.
    
    Used to verify that the API is running and responding normally.
    Useful for load balancers and monitoring systems.
    """
    
    status: str = Field(
        ...,
        description="Health status of the API (healthy for running properly)",
        example="healthy"
    )
    timestamp: datetime = Field(
        ...,
        description="ISO-8601 timestamp of when this health check was performed",
        example="2026-08-29T03:38:06.750012"
    )

    class Config:
        """Configuration for the HealthResponse model."""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-08-29T03:38:06.750012"
            }
        }
