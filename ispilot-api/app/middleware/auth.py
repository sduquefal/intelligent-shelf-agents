from __future__ import annotations

import logging
import os
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.logging import get_structured_logger

logger = get_structured_logger(__name__)


class APIKeyValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate API key from X-API-Key header."""

    def __init__(self, app: Callable, api_key: str | None = None) -> None:
        super().__init__(app)
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """Validate API key and extract user_id."""
        # Refresh from runtime environment so app startup does not lock in stale config values.
        self.api_key = self.api_key or os.getenv("ISPILOT_API_KEY")

        # Skip auth for health endpoint
        if request.url.path == "/health":
            return await call_next(request)

        # Extract API key from header
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            self.logger.warning(
                "Unauthorized request: missing API key",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client": request.client.host if request.client else "unknown",
                },
            )
            return Response(
                content='{"error_code": "MISSING_API_KEY", "error_message": "X-API-Key header required"}',
                status_code=401,
                media_type="application/json",
            )

        if not self.api_key:
            self.logger.error(
                "API server misconfiguration: missing ISPILOT_API_KEY",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client": request.client.host if request.client else "unknown",
                },
            )
            return Response(
                content='{"error_code": "SERVER_CONFIG_ERROR", "error_message": "API key is not configured on the server"}',
                status_code=500,
                media_type="application/json",
            )

        # Validate API key
        if api_key != self.api_key:
            self.logger.warning(
                "Unauthorized request: invalid API key",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "client": request.client.host if request.client else "unknown",
                },
            )
            return Response(
                content='{"error_code": "INVALID_API_KEY", "error_message": "Invalid API key"}',
                status_code=401,
                media_type="application/json",
            )

        # Extract user_id from header if provided
        user_id = request.headers.get("X-User-ID")
        if user_id:
            request.state.user_id = user_id

        # Add request_id from context if available
        if hasattr(request.state, "request_id"):
            self.logger.info(
                "API request authenticated",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "request_id": request.state.request_id,
                    "user_id": user_id,
                },
            )

        return await call_next(request)
