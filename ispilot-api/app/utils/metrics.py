"""Cloud Monitoring metrics collection and reporting."""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from app.utils.logging import get_structured_logger

logger = get_structured_logger(__name__)

# Try to import monitoring client, but make it optional
try:
    from google.cloud import monitoring_v3
    HAS_MONITORING = True
except ImportError:
    HAS_MONITORING = False
    logger.debug("google-cloud-monitoring not installed, metrics disabled")


class MetricsClient:
    """Client for publishing metrics to Google Cloud Monitoring."""

    def __init__(self):
        """Initialize metrics client."""
        self.enabled = False
        self.project_id = os.environ.get("GCP_PROJECT_ID", "")
        
        if not HAS_MONITORING:
            logger.debug("Cloud Monitoring client disabled (package not installed)")
            return
        
        try:
            if self.project_id:
                self.client = monitoring_v3.MetricServiceClient()
                self.enabled = True
                logger.info("Cloud Monitoring client initialized", extra={
                    "event": "metrics_initialized",
                    "project_id": self.project_id,
                })
        except Exception as e:
            logger.warning(
                "Failed to initialize Cloud Monitoring client",
                extra={
                    "event": "metrics_init_failed",
                    "error": str(e),
                }
            )
            self.enabled = False

    def record_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        auth_method: str = "unknown",
    ) -> None:
        """Record API request metrics.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            status_code: HTTP status code
            duration_ms: Request duration in milliseconds
            auth_method: Authentication method used
        """
        if not self.enabled:
            return

        try:
            project_name = f"projects/{self.project_id}"
            
            # Record request duration
            self._write_time_series(
                metric_type="custom.googleapis.com/ispilot/api_request_duration_ms",
                value=duration_ms,
                labels={
                    "method": method,
                    "path": path,
                    "status_code": str(status_code),
                },
            )
            
            # Record request count
            self._write_time_series(
                metric_type="custom.googleapis.com/ispilot/api_request_count",
                value=1,
                labels={
                    "method": method,
                    "path": path,
                    "status_code": str(status_code),
                    "auth_method": auth_method,
                },
            )

            # Record error rate for non-2xx responses
            if status_code >= 400:
                self._write_time_series(
                    metric_type="custom.googleapis.com/ispilot/api_error_count",
                    value=1,
                    labels={
                        "method": method,
                        "path": path,
                        "status_code": str(status_code),
                    },
                )

        except Exception as e:
            logger.debug(
                "Failed to record API metrics",
                extra={
                    "event": "metrics_record_failed",
                    "error": str(e),
                }
            )

    def record_vertex_latency(
        self,
        latency_ms: float,
        success: bool = True,
        error_type: Optional[str] = None,
    ) -> None:
        """Record Vertex AI API latency.
        
        Args:
            latency_ms: API call latency in milliseconds
            success: Whether the call succeeded
            error_type: Type of error if failed
        """
        if not self.enabled:
            return

        try:
            self._write_time_series(
                metric_type="custom.googleapis.com/ispilot/vertex_api_latency_ms",
                value=latency_ms,
                labels={
                    "success": "true" if success else "false",
                    "error_type": error_type or "none",
                },
            )
        except Exception as e:
            logger.debug(
                "Failed to record Vertex latency metrics",
                extra={
                    "event": "vertex_metrics_failed",
                    "error": str(e),
                }
            )

    def record_session_cache(
        self,
        hit: bool,
        duration_ms: float,
    ) -> None:
        """Record session cache statistics.
        
        Args:
            hit: Whether the cache was hit (True) or miss (False)
            duration_ms: Duration of cache operation
        """
        if not self.enabled:
            return

        try:
            cache_result = "hit" if hit else "miss"
            self._write_time_series(
                metric_type="custom.googleapis.com/ispilot/session_cache_operations",
                value=1,
                labels={
                    "result": cache_result,
                },
            )
            
            self._write_time_series(
                metric_type="custom.googleapis.com/ispilot/session_cache_latency_ms",
                value=duration_ms,
                labels={
                    "result": cache_result,
                },
            )
        except Exception as e:
            logger.debug(
                "Failed to record session cache metrics",
                extra={
                    "event": "cache_metrics_failed",
                    "error": str(e),
                }
            )

    def _write_time_series(
        self,
        metric_type: str,
        value: float,
        labels: dict[str, str],
    ) -> None:
        """Write a time series metric to Cloud Monitoring.
        
        Args:
            metric_type: Full metric type name
            value: Metric value
            labels: Metric labels
        """
        if not self.enabled or not HAS_MONITORING:
            return

        try:
            project_name = f"projects/{self.project_id}"
            
            series = monitoring_v3.TimeSeries()
            series.metric.type = metric_type
            
            # Set labels
            for key, val in labels.items():
                series.metric.labels[key] = val

            # Set resource
            series.resource.type = "global"
            series.resource.labels["project_id"] = self.project_id

            # Create data point
            now = datetime.utcnow()
            seconds = int(now.timestamp())
            nanos = int((now.timestamp() - seconds) * 1e9)
            interval = monitoring_v3.TimeInterval(
                {"end_time": {"seconds": seconds, "nanos": nanos}}
            )
            point = monitoring_v3.Point(
                {"interval": interval, "value": {"double_value": value}}
            )
            series.points = [point]

            # Write time series
            self.client.create_time_series(
                name=project_name,
                time_series=[series],
            )

        except Exception as e:
            logger.debug(
                f"Failed to write time series {metric_type}",
                extra={
                    "event": "time_series_write_failed",
                    "metric_type": metric_type,
                    "error": str(e),
                }
            )


# Global metrics client instance
_metrics_client: Optional[MetricsClient] = None


def get_metrics_client() -> MetricsClient:
    """Get or create the global metrics client."""
    global _metrics_client
    if _metrics_client is None:
        _metrics_client = MetricsClient()
    return _metrics_client
