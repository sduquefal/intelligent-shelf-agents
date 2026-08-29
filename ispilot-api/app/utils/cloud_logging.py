"""Google Cloud Logging integration with structured logging support."""

from __future__ import annotations

import json
import logging
import sys
from typing import Any

try:
    from google.cloud import logging as cloud_logging
    GOOGLE_CLOUD_LOGGING_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_LOGGING_AVAILABLE = False


class CloudLoggingFormatter(logging.Formatter):
    """Formatter that outputs JSON logs compatible with Google Cloud Logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


def setup_cloud_logging() -> logging.Logger | None:
    """
    Initialize Google Cloud Logging client.
    
    Returns None if google-cloud-logging is not available.
    Logs will fall back to console output.
    """
    if not GOOGLE_CLOUD_LOGGING_AVAILABLE:
        return None

    try:
        client = cloud_logging.Client()
        client.setup_logging()
        return logging.getLogger()
    except Exception as e:
        # If Cloud Logging setup fails, log to stderr and continue
        print(f"Warning: Failed to setup Google Cloud Logging: {e}", file=sys.stderr)
        return None


def get_cloud_logger(
    name: str,
    use_cloud_logging: bool = True,
) -> logging.Logger:
    """
    Get a logger that outputs structured JSON logs.
    
    Args:
        name: Logger name (typically __name__)
        use_cloud_logging: If True and available, use Google Cloud Logging
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # Use Cloud Logging formatter
    formatter = CloudLoggingFormatter()
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


class CloudLogger(logging.LoggerAdapter):
    """
    Extended logger adapter that supports structured fields.
    
    Usage:
        logger = CloudLogger(logging.getLogger(__name__), {})
        logger.info("Message", extra={"user_id": "123", "request_id": "abc"})
    """

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """Process log message and add extra fields."""
        # Initialize extra fields
        if "extra" not in kwargs:
            kwargs["extra"] = {}

        # Ensure extra_fields for formatter
        if "extra_fields" not in kwargs["extra"]:
            kwargs["extra"]["extra_fields"] = {}

        # Merge context with extra
        context_extra = self.extra.copy() if self.extra else {}
        context_extra.update(kwargs["extra"].get("extra_fields", {}))

        kwargs["extra"]["extra_fields"] = context_extra

        return msg, kwargs
