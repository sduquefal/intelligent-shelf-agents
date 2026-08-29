from __future__ import annotations

import logging
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.chat import router as chat_router
from app.config.settings import settings
from app.middleware.audit import AuditLoggingMiddleware
from app.middleware.auth import APIKeyValidationMiddleware
from app.models.errors import ErrorResponse
from app.models.responses import HealthResponse
from app.utils.logging import generate_request_id, get_structured_logger, set_request_id

# Setup structured logging
logger = get_structured_logger(__name__)

app = FastAPI(
    title="IsPilot API",
    version="0.2.0",
    description="""
    **IsPilot Agent API** - API facade for Vertex-hosted Intelligent Shelf (IsPilot) agent
    
    This API provides a unified interface for:
    - **Chat Interface**: Send messages to the IsPilot agent for inventory and shelf analysis
    - **Session Management**: Automatic session creation and management across requests
    - **Security**: OAuth 2.0 Bearer token and API Key authentication
    - **Observability**: Structured JSON logging, request tracking, and audit logs
    
    ## Authentication
    All endpoints (except `/health` and `/docs`) require authentication via:
    - **Production**: OAuth 2.0 Bearer token in `Authorization: Bearer <token>` header
    - **Development**: API Key in `X-API-Key: <key>` header
    
    ## Request Headers
    - `X-API-Key`: Required for development/local testing
    - `X-Request-ID`: Optional, auto-generated if not provided. Use for request tracking.
    - `X-User-ID`: Optional, captured in audit logs
    - `X-Session-ID`: Optional, captured in audit logs
    
    ## Error Handling
    All errors follow a standard ErrorResponse format:
    ```json
    {
        "error_code": "ERROR_TYPE",
        "error_message": "Human readable description",
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "timestamp": "2026-08-29T03:38:06.750012",
        "details": null
    }
    ```
    
    ## API Endpoints
    - `GET /health` - Health check
    - `POST /chat` - Send message to IsPilot agent
    - `GET /docs` - OpenAPI/Swagger documentation
    - `GET /openapi.json` - OpenAPI schema
    
    ## Supported Error Codes
    - `MISSING_API_KEY` - Authentication header is missing
    - `INVALID_API_KEY` - Invalid or expired API key
    - `AUTH_FAILED` - Authentication failed
    - `VALIDATION_ERROR` - Request validation failed
    - `VERTEX_TIMEOUT` - Vertex AI request timeout
    - `VERTEX_ERROR` - Vertex AI backend error
    - `FIRESTORE_UNAVAILABLE` - Session storage unavailable
    - `SESSION_NOT_FOUND` - Session expired or not found
    - `INTERNAL_SERVER_ERROR` - Unexpected server error
    
    ## Contact & Support
    For issues or support, contact: team@example.com
    """,
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url="/redoc",
)

# Audit logging middleware (must be added first to capture all requests)
app.add_middleware(AuditLoggingMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key validation middleware
app.add_middleware(
    APIKeyValidationMiddleware,
    api_key=settings.api_key,
)


@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Add request_id to each request."""
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        f"Validation error: {str(exc)}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "error": str(exc),
        },
    )
    error_response = ErrorResponse(
        error_code="VALIDATION_ERROR",
        error_message=str(exc),
        request_id=request_id,
    )
    return JSONResponse(
        status_code=400,
        content=error_response.model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "error": str(exc),
            "exception_type": type(exc).__name__,
        },
    )
    error_response = ErrorResponse(
        error_code="INTERNAL_SERVER_ERROR",
        error_message="Internal server error",
        request_id=request_id,
        details={"exception_type": type(exc).__name__} if settings.debug else None,
    )
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump(),
    )


app.include_router(chat_router)


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Verify that the API is running and responding normally. "
                "Returns the current timestamp to validate timezone synchronization.",
    tags=["Health"]
)
def health() -> HealthResponse:
    """
    Health check endpoint.
    
    **Purpose**: Used by load balancers, monitoring systems, and health checks.
    
    **Returns**:
    - `status`: "healthy" if the API is running normally
    - `timestamp`: ISO-8601 timestamp for timezone verification
    
    **No authentication required** - This endpoint is excluded from auth checks.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
    )
