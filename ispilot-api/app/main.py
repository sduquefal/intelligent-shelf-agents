from __future__ import annotations

import logging
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.chat import router as chat_router
from app.config.settings import settings
from app.middleware.auth import APIKeyValidationMiddleware
from app.models.responses import HealthResponse
from app.utils.logging import generate_request_id, get_structured_logger, set_request_id

# Setup structured logging
logger = get_structured_logger(__name__)

app = FastAPI(
    title="IsPilot API",
    version="0.2.0",
    description="API facade for Vertex-hosted IsPilot agent",
)

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
    return JSONResponse(
        status_code=400,
        content={
            "error_code": "VALIDATION_ERROR",
            "error_message": str(exc),
            "request_id": request_id,
        },
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
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_ERROR",
            "error_message": "Internal server error",
            "request_id": request_id,
        },
    )


app.include_router(chat_router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
    )
