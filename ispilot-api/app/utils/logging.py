from __future__ import annotations

import json
import logging
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any

# Context variable to store request_id across async operations
request_id_context: ContextVar[str] = ContextVar("request_id", default="")


def generate_request_id() -> str:
    """Generate a unique request ID."""
    return str(uuid.uuid4())


def get_request_id() -> str:
    """Get the current request ID from context."""
    return request_id_context.get()


def set_request_id(request_id: str) -> None:
    """Set the request ID in context."""
    request_id_context.set(request_id)


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add request_id if available
        if request_id := get_request_id():
            log_data["request_id"] = request_id

        # Add extra fields from record
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def get_structured_logger(name: str) -> logging.Logger:
    """Get a structured logger with JSON formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    # Create and set formatter
    formatter = StructuredFormatter()
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


class StructuredLogger(logging.LoggerAdapter):
    """Extended logger with structured fields support."""

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Process log message and add context."""
        # Merge extra fields
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        
        # Add context variables
        if request_id := get_request_id():
            kwargs["extra"]["request_id"] = request_id

        return msg, kwargs
