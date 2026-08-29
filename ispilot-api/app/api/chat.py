from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.config.settings import settings
from app.models.responses import ChatResponse, ErrorResponse
from app.services.session_service import SessionService
from app.services.vertex_client import VertexAgentClient
from app.utils.logging import get_request_id

router = APIRouter(prefix="", tags=["chat"])
session_service = SessionService(session_timeout_hours=settings.session_timeout_hours)
vertex_client = VertexAgentClient()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """Request model for chat endpoint.
    
    This model represents a user's message request to the IsPilot agent.
    Sessions are automatically managed based on user_id and optional session_id.
    """
    
    user_id: str = Field(
        ..., 
        description="Unique identifier for the user sending the message",
        example="user@example.com"
    )
    message: str = Field(
        ..., 
        description="The user's message or query to the IsPilot agent",
        example="What is the inventory status for SKU 12345?"
    )
    session_id: str | None = Field(
        None,
        description="Optional session ID to maintain conversation context. If not provided, a new session is created.",
        example="session_550e8400-e29b-41d4-a716-446655440000"
    )

    class Config:
        """Configuration for the ChatRequest model."""
        json_schema_extra = {
            "example": {
                "user_id": "user@example.com",
                "message": "What is the inventory status for SKU 12345?",
                "session_id": None
            }
        }


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Send a message to the IsPilot agent",
    description="Submit a user message to the IsPilot agent and receive a response. "
                "Sessions are automatically created or reused based on the provided user_id and session_id.",
    responses={
        200: {
            "description": "Successful response from the agent",
            "content": {
                "application/json": {
                    "example": {
                        "answer": "The inventory status for SKU 12345 is: In Stock (250 units)",
                        "session_id": "session_550e8400-e29b-41d4-a716-446655440000",
                        "request_id": "req_550e8400-e29b-41d4-a716-446655440000",
                        "timestamp": "2026-08-29T03:38:06.750012",
                        "status": "ok"
                    }
                }
            }
        },
        400: {
            "description": "Validation error in request body",
            "content": {
                "application/json": {
                    "example": {
                        "error_code": "VALIDATION_ERROR",
                        "error_message": "field required",
                        "request_id": "req_550e8400-e29b-41d4-a716-446655440000",
                        "timestamp": "2026-08-29T03:38:06.750012",
                        "details": None
                    }
                }
            }
        },
        401: {
            "description": "Authentication error (missing or invalid API key)",
            "content": {
                "application/json": {
                    "example": {
                        "error_code": "INVALID_API_KEY",
                        "error_message": "Invalid API key provided",
                        "request_id": "req_550e8400-e29b-41d4-a716-446655440000",
                        "timestamp": "2026-08-29T03:38:06.750012",
                        "details": None
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "error_code": "INTERNAL_SERVER_ERROR",
                        "error_message": "Internal server error",
                        "request_id": "req_550e8400-e29b-41d4-a716-446655440000",
                        "timestamp": "2026-08-29T03:38:06.750012",
                        "details": {"exception_type": "RuntimeError"}
                    }
                }
            }
        }
    }
)
async def chat(request: ChatRequest, http_request: Request) -> ChatResponse:
    """
    Chat endpoint that uses SessionService for session management.
    
    **Features:**
    - Manages user sessions with timeout expiration
    - Automatically creates new sessions or reuses existing ones
    - Returns structured ChatResponse with request_id and timestamp
    - Logs all interactions with structured JSON logging
    - Integrates with Vertex AI agent for intelligent responses
    
    **Request Headers:**
    - `X-API-Key`: Required for authentication
    - `X-Request-ID`: Optional, auto-generated if not provided
    - `X-User-ID`: Optional, captured in audit logs
    - `X-Session-ID`: Optional, captured in audit logs
    
    **Response:**
    - `answer`: The agent's response to the user's message
    - `session_id`: The session ID for this conversation
    - `request_id`: Unique identifier for tracking this request
    - `timestamp`: ISO-8601 timestamp of the response
    - `status`: Status of the request ("ok" for success)
    """
    request_id = get_request_id()
    user_id = request.user_id
    session_id = request.session_id
    
    try:
        logger.info(
            "Chat request received",
            extra={
                "user_id": user_id,
                "has_session": session_id is not None,
                "request_id": request_id,
            },
        )
        
        # Use existing session or create new one
        effective_session = session_service.get_or_create(
            user_id=user_id,
            session_id=session_id,
        )

        # Execute chat via Vertex
        answer, confirmed_session = vertex_client.chat(
            user_id=user_id,
            message=request.message,
            session_id=effective_session,
        )
        
        response = ChatResponse(
            answer=answer,
            session_id=confirmed_session,
            request_id=request_id,
            timestamp=datetime.utcnow(),
            status="ok",
        )
        
        logger.info(
            "Chat response sent",
            extra={
                "user_id": user_id,
                "session_id": confirmed_session,
                "request_id": request_id,
                "answer_length": len(answer),
            },
        )
        
        return response
        
    except ValueError as exc:
        logger.error(
            f"Validation error in chat: {str(exc)}",
            extra={
                "user_id": user_id,
                "request_id": request_id,
                "error": str(exc),
            },
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - API protection layer
        logger.error(
            f"Unhandled error in chat: {type(exc).__name__}",
            extra={
                "user_id": user_id,
                "request_id": request_id,
                "error": str(exc),
                "exception_type": type(exc).__name__,
            },
        )
        raise HTTPException(status_code=500, detail=f"Internal error: {exc}") from exc
