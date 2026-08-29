"""Cloud Monitoring Dashboard Configuration and Metrics Definitions.

This module defines all the custom metrics that the IsPilot API publishes to
Google Cloud Monitoring. These metrics can be used to create dashboards,
set up alerts, and monitor application performance.

METRICS DEFINED:
1. api_request_duration_ms - Histogram of request durations
2. api_request_count - Counter of API requests
3. api_error_count - Counter of error responses
4. vertex_api_latency_ms - Histogram of Vertex AI call latencies
5. session_cache_operations - Counter of cache hits/misses
6. session_cache_latency_ms - Histogram of cache operation latencies
"""

from __future__ import annotations

from app.utils.logging import get_structured_logger

logger = get_structured_logger(__name__)


class MetricsDefinitions:
    """Defines all custom metrics for IsPilot API."""

    # API Request Duration Histogram
    API_REQUEST_DURATION = {
        "metric_type": "custom.googleapis.com/ispilot/api_request_duration_ms",
        "description": "Histogram of API request duration in milliseconds",
        "unit": "ms",
        "value_type": "DISTRIBUTION",
        "labels": [
            {"key": "method", "description": "HTTP method (GET, POST, etc.)"},
            {"key": "path", "description": "API endpoint path"},
            {"key": "status_code", "description": "HTTP response status code"},
        ],
        "display_name": "API Request Duration",
    }

    # API Request Count Counter
    API_REQUEST_COUNT = {
        "metric_type": "custom.googleapis.com/ispilot/api_request_count",
        "description": "Count of API requests by method, path, and status",
        "unit": "1",
        "value_type": "INT64",
        "labels": [
            {"key": "method", "description": "HTTP method"},
            {"key": "path", "description": "API endpoint path"},
            {"key": "status_code", "description": "HTTP response status code"},
            {"key": "auth_method", "description": "Authentication method used"},
        ],
        "display_name": "API Request Count",
    }

    # API Error Count Counter
    API_ERROR_COUNT = {
        "metric_type": "custom.googleapis.com/ispilot/api_error_count",
        "description": "Count of API errors (4xx and 5xx responses)",
        "unit": "1",
        "value_type": "INT64",
        "labels": [
            {"key": "method", "description": "HTTP method"},
            {"key": "path", "description": "API endpoint path"},
            {"key": "status_code", "description": "HTTP error status code"},
        ],
        "display_name": "API Error Count",
    }

    # Vertex AI Latency Histogram
    VERTEX_API_LATENCY = {
        "metric_type": "custom.googleapis.com/ispilot/vertex_api_latency_ms",
        "description": "Histogram of Vertex AI API call latency in milliseconds",
        "unit": "ms",
        "value_type": "DISTRIBUTION",
        "labels": [
            {"key": "success", "description": "Whether the call succeeded (true/false)"},
            {"key": "error_type", "description": "Type of error if failed"},
        ],
        "display_name": "Vertex AI API Latency",
    }

    # Session Cache Operations Counter
    SESSION_CACHE_OPS = {
        "metric_type": "custom.googleapis.com/ispilot/session_cache_operations",
        "description": "Count of session cache operations (hits and misses)",
        "unit": "1",
        "value_type": "INT64",
        "labels": [
            {"key": "result", "description": "Cache operation result (hit/miss)"},
        ],
        "display_name": "Session Cache Operations",
    }

    # Session Cache Latency Histogram
    SESSION_CACHE_LATENCY = {
        "metric_type": "custom.googleapis.com/ispilot/session_cache_latency_ms",
        "description": "Histogram of session cache operation latency in milliseconds",
        "unit": "ms",
        "value_type": "DISTRIBUTION",
        "labels": [
            {"key": "result", "description": "Cache operation result (hit/miss)"},
        ],
        "display_name": "Session Cache Latency",
    }

    @classmethod
    def get_all_metrics(cls) -> list[dict]:
        """Get all metric definitions."""
        return [
            cls.API_REQUEST_DURATION,
            cls.API_REQUEST_COUNT,
            cls.API_ERROR_COUNT,
            cls.VERTEX_API_LATENCY,
            cls.SESSION_CACHE_OPS,
            cls.SESSION_CACHE_LATENCY,
        ]

    @classmethod
    def log_metric_definitions(cls) -> None:
        """Log all metric definitions to structured logging."""
        logger.info(
            "IsPilot API Metrics Registered",
            extra={
                "event": "metrics_defined",
                "total_metrics": len(cls.get_all_metrics()),
                "metrics": [m["metric_type"] for m in cls.get_all_metrics()],
            },
        )


# Query examples for different use cases
MONITORING_QUERIES = {
    "p99_request_latency": """
        fetch api
        | metric 'custom.googleapis.com/ispilot/api_request_duration_ms'
        | filter resource.service == 'ispilot-api'
        | group_by [resource.service],
            [percentile_agg(.value, [0.99])]
    """,
    "error_rate": """
        fetch api
        | {
            metric 'custom.googleapis.com/ispilot/api_error_count'
            | filter resource.service == 'ispilot-api';
            metric 'custom.googleapis.com/ispilot/api_request_count'
            | filter resource.service == 'ispilot-api'
          }
        | join
        | value [val("1") / val("0") * 100]
        | window 5m
    """,
    "vertex_latency_by_status": """
        fetch api
        | metric 'custom.googleapis.com/ispilot/vertex_api_latency_ms'
        | filter resource.service == 'ispilot-api'
        | group_by [metric.success],
            [mean(.value)]
    """,
    "cache_hit_rate": """
        fetch api
        | {
            metric 'custom.googleapis.com/ispilot/session_cache_operations'
            | filter metric.result == 'hit';
            metric 'custom.googleapis.com/ispilot/session_cache_operations'
          }
        | join
        | value [val("0") / val("1") * 100]
        | window 5m
    """,
    "requests_by_endpoint": """
        fetch api
        | metric 'custom.googleapis.com/ispilot/api_request_count'
        | filter resource.service == 'ispilot-api'
        | group_by [metric.path, metric.method],
            [sum(.value)]
    """,
}


# Alert policy recommendations
ALERT_POLICIES = [
    {
        "name": "High API Latency",
        "description": "Alert when API request p99 latency exceeds 2000ms",
        "metric": "api_request_duration_ms",
        "threshold": 2000,
        "operator": "GREATER_THAN",
        "duration": 300,
    },
    {
        "name": "High Error Rate",
        "description": "Alert when error rate exceeds 5%",
        "metric": "api_error_count",
        "threshold": 5,
        "operator": "GREATER_THAN",
        "duration": 60,
    },
    {
        "name": "Vertex API Timeout",
        "description": "Alert when Vertex API latency exceeds 30 seconds",
        "metric": "vertex_api_latency_ms",
        "threshold": 30000,
        "operator": "GREATER_THAN",
        "duration": 60,
    },
    {
        "name": "Low Cache Hit Rate",
        "description": "Alert when session cache hit rate falls below 70%",
        "metric": "session_cache_operations",
        "threshold": 70,
        "operator": "LESS_THAN",
        "duration": 300,
    },
]
