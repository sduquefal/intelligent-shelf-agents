from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

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
    """Request model for chat endpoint."""
    
    user_id: str
    message: str
    session_id: str | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request) -> ChatResponse:
    """
    Chat endpoint that uses SessionService for session management.
    
    - Manages user sessions with timeout expiration
    - Returns structured ChatResponse with request_id and timestamp
    - Logs all interactions with structured logging
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
