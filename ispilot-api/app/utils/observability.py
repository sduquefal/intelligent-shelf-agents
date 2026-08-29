"""Observability utilities for tracking Vertex AI metrics.

This module provides decorators and context managers for tracking
performance metrics from Vertex AI API calls.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Optional

from app.utils.logging import get_structured_logger
from app.utils.metrics import get_metrics_client

logger = get_structured_logger(__name__)
metrics = get_metrics_client()


@contextmanager
def track_vertex_latency(operation_name: str, error_type: Optional[str] = None):
    """Context manager to track Vertex AI operation latency.
    
    Args:
        operation_name: Name of the operation being tracked
        error_type: Type of error if the operation fails
        
    Yields:
        None
        
    Example:
        with track_vertex_latency("generate_response"):
            response = vertex_client.generate_text(...)
    """
    start_time = time.time()
    success = True
    caught_error = None
    
    try:
        yield
    except Exception as e:
        success = False
        caught_error = e
        error_type = type(e).__name__
        raise
    finally:
        latency_ms = (time.time() - start_time) * 1000
        
        # Log the operation
        if success:
            logger.info(
                f"Vertex AI operation completed: {operation_name}",
                extra={
                    "event": "vertex_operation_complete",
                    "operation": operation_name,
                    "latency_ms": round(latency_ms, 2),
                    "success": True,
                },
            )
        else:
            logger.warning(
                f"Vertex AI operation failed: {operation_name}",
                extra={
                    "event": "vertex_operation_failed",
                    "operation": operation_name,
                    "latency_ms": round(latency_ms, 2),
                    "success": False,
                    "error_type": error_type,
                    "error_message": str(caught_error),
                },
            )
        
        # Record metrics
        metrics.record_vertex_latency(
            latency_ms=latency_ms,
            success=success,
            error_type=error_type if not success else None,
        )


def track_cache_operation(hit: bool):
    """Context manager to track session cache operation latency.
    
    Args:
        hit: Whether this is a cache hit (True) or miss (False)
        
    Yields:
        None
        
    Example:
        with track_cache_operation(hit=True):
            session = cache.get(session_id)
    """
    @contextmanager
    def _track():
        start_time = time.time()
        try:
            yield
        finally:
            latency_ms = (time.time() - start_time) * 1000
            
            # Log the operation
            operation_type = "cache_hit" if hit else "cache_miss"
            logger.debug(
                f"Session cache {operation_type}",
                extra={
                    "event": f"session_{operation_type}",
                    "latency_ms": round(latency_ms, 2),
                },
            )
            
            # Record metrics
            metrics.record_session_cache(hit=hit, duration_ms=latency_ms)
    
    return _track()


def observability_decorator(func: Callable) -> Callable:
    """Decorator to add observability to async functions.
    
    Tracks execution time and logs start/end events.
    
    Args:
        func: Async function to decorate
        
    Returns:
        Decorated function with observability
        
    Example:
        @observability_decorator
        async def process_request(request):
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        func_name = func.__name__
        start_time = time.time()
        
        logger.info(
            f"Starting {func_name}",
            extra={
                "event": f"{func_name}_start",
                "function": func_name,
            },
        )
        
        try:
            result = await func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            logger.info(
                f"Completed {func_name}",
                extra={
                    "event": f"{func_name}_complete",
                    "function": func_name,
                    "duration_ms": round(duration_ms, 2),
                },
            )
            
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error(
                f"Failed {func_name}: {type(e).__name__}",
                extra={
                    "event": f"{func_name}_error",
                    "function": func_name,
                    "duration_ms": round(duration_ms, 2),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
            )
            
            raise
    
    return wrapper
