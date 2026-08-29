"""Audit logging middleware for request/response tracking."""

from __future__ import annotations

import logging
import time
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logging import get_structured_logger

logger = get_structured_logger(__name__)


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to audit all requests and responses.
    
    Logs:
    - Request: timestamp, method, path, user_id, session_id
    - Response: duration_ms, status_code, error_code (if applicable)
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Log request/response lifecycle."""
        # Skip audit logging for health checks
        if request.url.path == "/health":
            return await call_next(request)

        # Extract context from request
        request_id = getattr(request.state, "request_id", "unknown")
        user_id = request.headers.get("X-User-ID", "anonymous")
        session_id = request.headers.get("X-Session-ID", "")

        # Record request start time
        start_time = time.time()

        # Log request
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "event": "request_start",
                "method": request.method,
                "path": request.url.path,
                "user_id": user_id,
                "session_id": session_id,
                "client_ip": request.client.host if request.client else "unknown",
            },
        )

        try:
            # Call the next middleware/endpoint
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log successful response
            logger.info(
                f"{request.method} {request.url.path} -> {response.status_code}",
                extra={
                    "request_id": request_id,
                    "event": "request_complete",
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                    "user_id": user_id,
                    "session_id": session_id,
                },
            )

            return response

        except Exception as exc:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            logger.error(
                f"{request.method} {request.url.path} raised {type(exc).__name__}",
                extra={
                    "request_id": request_id,
                    "event": "request_error",
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "user_id": user_id,
                    "session_id": session_id,
                },
            )

            raise
