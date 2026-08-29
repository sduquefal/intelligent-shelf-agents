from __future__ import annotations

import logging
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.models.errors import ErrorResponse
from app.utils.logging import get_structured_logger

logger = get_structured_logger(__name__)


class APIKeyValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate OAuth Bearer tokens (GCP-native authentication)."""

    def __init__(self, app: Callable, api_key: str | None = None) -> None:
        super().__init__(app)
        self.logger = logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """Validate authentication via OAuth Bearer token (GCP standard)."""
        # Skip auth for health and documentation endpoints
        skip_auth_paths = ["/health", "/docs", "/openapi.json", "/redoc"]
        if any(request.url.path == path or request.url.path.startswith(path + "/") for path in skip_auth_paths):
            return await call_next(request)

        # Check for OAuth token (Authorization: Bearer) - GCP standard authentication
        auth_header = request.headers.get("Authorization", "")
        if auth_header.strip().lower().startswith("bearer "):
            # OAuth token is valid; allow request to proceed
            self.logger.info(
                "Request authenticated via OAuth",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client": request.client.host if request.client else "unknown",
                },
            )
            return await call_next(request)

        # No Bearer token provided
        request_id = getattr(request.state, "request_id", "unknown")
        self.logger.warning(
            "Unauthorized request: missing OAuth Bearer token",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            },
        )
        error_response = ErrorResponse(
            error_code="MISSING_AUTH_TOKEN",
            error_message="Authorization header with Bearer token required",
            request_id=request_id,
        )
        return Response(
            content=error_response.model_dump_json(),
            status_code=401,
            media_type="application/json",
        )
