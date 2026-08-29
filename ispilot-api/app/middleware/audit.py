"""Audit logging middleware for request/response tracking."""

from __future__ import annotations

import logging
import os
import time
import traceback
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logging import get_structured_logger
from app.utils.metrics import get_metrics_client

logger = get_structured_logger(__name__)
metrics = get_metrics_client()


def _get_auth_method(request: Request) -> str:
    """Determine authentication method used."""
    if request.headers.get("Authorization", "").startswith("Bearer"):
        return "oauth2"
    elif request.headers.get("X-API-Key"):
        return "api_key"
    else:
        return "none"


def _get_http_status_text(status_code: int) -> str:
    """Get HTTP status text for a status code."""
    status_map = {
        200: "OK",
        201: "Created",
        204: "No Content",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
    }
    return status_map.get(status_code, "Unknown")


def _get_request_payload_summary(request: Request, body: bytes) -> str:
    """Extract request payload summary (first 500 chars)."""
    try:
        if not body:
            return ""
        decoded = body.decode("utf-8")
        return decoded[:500]
    except Exception:
        return f"[Binary data: {len(body)} bytes]"


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """
    Enhanced middleware to audit all requests and responses.
    
    Logs:
    - Request: method, path, user_id, session_id, payload summary, auth method
    - Response: status_code, status_text, duration_ms, cache headers
    - Error: error type, error message, stack trace (debug mode only)
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Log request/response lifecycle with enhanced context."""
        # Skip audit logging for health checks and swagger UI
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Extract context from request
        request_id = getattr(request.state, "request_id", "unknown")
        user_id = request.headers.get("X-User-ID", "anonymous")
        session_id = request.headers.get("X-Session-ID", "")
        auth_method = _get_auth_method(request)

        # Capture request body
        request_body = b""
        if request.method in ["POST", "PUT", "PATCH"]:
            request_body = await request.body()
            # Re-attach body to request for downstream processing
            async def receive():
                return {"type": "http.request", "body": request_body}
            request._receive = receive

        payload_summary = _get_request_payload_summary(request, request_body)
        content_type = request.headers.get("Content-Type", "unknown")

        # Record request start time
        start_time = time.time()

        # Log request with enhanced context
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "event": "request_start",
                "method": request.method,
                "path": request.url.path,
                "user_id": user_id,
                "session_id": session_id,
                "auth_method": auth_method,
                "content_type": content_type,
                "payload_summary": payload_summary,
                "client_ip": request.client.host if request.client else "unknown",
            },
        )

        try:
            # Call the next middleware/endpoint
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Extract cache headers
            cache_control = response.headers.get("Cache-Control", "")
            etag = response.headers.get("ETag", "")
            vary = response.headers.get("Vary", "")

            # Log successful response with enhanced context
            status_text = _get_http_status_text(response.status_code)
            logger.info(
                f"{request.method} {request.url.path} -> {response.status_code} {status_text}",
                extra={
                    "request_id": request_id,
                    "event": "request_complete",
                    "method": request.method,
                    "path": request.url.path,
                    "user_id": user_id,
                    "session_id": session_id,
                    "auth_method": auth_method,
                    "status_code": response.status_code,
                    "status_text": status_text,
                    "duration_ms": round(duration_ms, 2),
                    "response_content_type": response.headers.get("Content-Type", "unknown"),
                    "cache_control": cache_control if cache_control else None,
                    "etag": etag if etag else None,
                    "vary": vary if vary else None,
                },
            )

            # Record metrics to Cloud Monitoring
            metrics.record_api_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                auth_method=auth_method,
            )

            return response

        except Exception as exc:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log error with enhanced context
            log_extra = {
                "request_id": request_id,
                "event": "request_error",
                "method": request.method,
                "path": request.url.path,
                "user_id": user_id,
                "session_id": session_id,
                "auth_method": auth_method,
                "duration_ms": round(duration_ms, 2),
                "error_type": type(exc).__name__,
                "error_message": str(exc),
            }

            # Include stack trace in debug mode
            if os.environ.get("DEBUG") == "true":
                log_extra["stack_trace"] = traceback.format_exc()

            logger.error(
                f"{request.method} {request.url.path} raised {type(exc).__name__}",
                extra=log_extra,
            )

            raise
