from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    
    answer: str
    session_id: str
    request_id: str
    timestamp: datetime
    status: str  # "ok" or "error"


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    error_code: str
    error_message: str
    request_id: str


class HealthResponse(BaseModel):
    """Response model for health endpoint."""
    
    status: str
    timestamp: datetime
