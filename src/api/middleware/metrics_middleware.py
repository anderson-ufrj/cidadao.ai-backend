"""
Prometheus metrics middleware for automatic HTTP request tracking.

This middleware automatically records metrics for all HTTP requests,
including duration, status codes, and error rates.
"""

import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core import get_logger
from src.infrastructure.observability.metrics import metrics_manager

logger = get_logger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic Prometheus metrics collection."""

    def __init__(self, app):
        """Initialize metrics middleware."""
        super().__init__(app)
        self.logger = get_logger(__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with automatic metrics collection."""
        start_time = time.time()

        # Skip metrics endpoint to avoid recursion
        if request.url.path == "/api/v1/observability/metrics":
            return await call_next(request)

        # Extract path template (FastAPI route) for grouping
        path_template = self._get_path_template(request)
        method = request.method

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Record metrics
            self._record_request_metrics(
                method=method,
                path=path_template,
                status_code=response.status_code,
                duration=duration,
            )

            return response

        except Exception as exc:
            # Calculate duration even for errors
            duration = time.time() - start_time

            # Record error metrics
            self._record_request_metrics(
                method=method,
                path=path_template,
                status_code=500,  # Default error status
                duration=duration,
                error=True,
            )

            # Re-raise the exception
            raise exc

    def _get_path_template(self, request: Request) -> str:
        """
        Get the path template from FastAPI route.

        This extracts the route pattern (e.g., /users/{user_id})
        instead of the actual path (e.g., /users/123) to avoid
        high cardinality in metrics.
        """
        # Try to get route from request scope
        if hasattr(request, "scope") and "route" in request.scope:
            route = request.scope["route"]
            if hasattr(route, "path"):
                return route.path

        # Fallback to actual path, but try to generalize it
        path = request.url.path

        # Common patterns to generalize
        # Replace UUIDs
        import re

        path = re.sub(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "{uuid}",
            path,
            flags=re.IGNORECASE,
        )

        # Replace numeric IDs
        path = re.sub(r"/\d+", "/{id}", path)

        # Limit cardinality for unknown paths
        if path.count("/") > 5:
            path = "/unknown/deep/path"

        return path

    def _record_request_metrics(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        error: bool = False,
    ):
        """Record HTTP request metrics."""
        # HTTP request duration histogram
        metrics_manager.observe_histogram(
            "cidadao_ai_request_duration_seconds",
            duration,
            labels={
                "method": method.upper(),
                "endpoint": path,
                "status_code": str(status_code),
            },
        )

        # HTTP request counter
        metrics_manager.increment_counter(
            "cidadao_ai_http_requests_total",
            labels={
                "method": method.upper(),
                "endpoint": path,
                "status_code": str(status_code),
                "status": "error" if error or status_code >= 400 else "success",
            },
        )

        # Error rate tracking
        if error or status_code >= 400:
            metrics_manager.increment_counter(
                "cidadao_ai_http_errors_total",
                labels={
                    "method": method.upper(),
                    "endpoint": path,
                    "status_code": str(status_code),
                    "error_type": self._get_error_type(status_code),
                },
            )

        # Track slow requests
        if duration > 5.0:  # Requests taking more than 5 seconds
            metrics_manager.increment_counter(
                "cidadao_ai_slow_requests_total",
                labels={
                    "method": method.upper(),
                    "endpoint": path,
                    "duration_bucket": self._get_duration_bucket(duration),
                },
            )

        # Update concurrent requests gauge (simplified - in production use proper tracking)
        active_requests = getattr(self, "_active_requests", 0)
        metrics_manager.set_gauge(
            "cidadao_ai_http_requests_in_progress",
            active_requests,
            labels={"method": method.upper()},
        )

    def _get_error_type(self, status_code: int) -> str:
        """Categorize error types based on status code."""
        if 400 <= status_code < 500:
            return "client_error"
        elif 500 <= status_code < 600:
            return "server_error"
        else:
            return "unknown_error"

    def _get_duration_bucket(self, duration: float) -> str:
        """Categorize request duration into buckets."""
        if duration < 1:
            return "0-1s"
        elif duration < 5:
            return "1-5s"
        elif duration < 10:
            return "5-10s"
        elif duration < 30:
            return "10-30s"
        else:
            return "30s+"


def setup_http_metrics():
    """Setup HTTP-specific metrics if not already registered."""
    # HTTP requests total counter
    try:
        from src.infrastructure.observability.metrics import MetricConfig, MetricType

        metrics_manager.register_metric(
            MetricConfig(
                name="cidadao_ai_http_requests_total",
                description="Total HTTP requests received",
                labels=["method", "endpoint", "status_code", "status"],
            ),
            MetricType.COUNTER,
        )

        metrics_manager.register_metric(
            MetricConfig(
                name="cidadao_ai_http_errors_total",
                description="Total HTTP errors",
                labels=["method", "endpoint", "status_code", "error_type"],
            ),
            MetricType.COUNTER,
        )

        metrics_manager.register_metric(
            MetricConfig(
                name="cidadao_ai_slow_requests_total",
                description="Total slow HTTP requests",
                labels=["method", "endpoint", "duration_bucket"],
            ),
            MetricType.COUNTER,
        )

        metrics_manager.register_metric(
            MetricConfig(
                name="cidadao_ai_http_requests_in_progress",
                description="HTTP requests currently being processed",
                labels=["method"],
            ),
            MetricType.GAUGE,
        )

        logger.info("HTTP metrics initialized")
    except Exception as e:
        logger.warning(f"Some HTTP metrics may already be registered: {e}")
