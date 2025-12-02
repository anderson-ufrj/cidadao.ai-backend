"""
Prometheus metrics for Federal API clients.

Provides comprehensive metrics for monitoring IBGE, DataSUS, and INEP API clients
including request performance, retry behavior, cache efficiency, and error rates.

Author: Anderson Henrique da Silva
Created: 2025-10-12 18:35:24 -03
License: Proprietary - All rights reserved
"""

import asyncio
import time
from functools import wraps

from src.core import get_logger
from src.infrastructure.observability.metrics import (
    MetricConfig,
    MetricType,
    metrics_manager,
)

logger = get_logger(__name__)


# Register Federal API specific metrics
def register_federal_api_metrics():
    """Register all Federal API client metrics."""

    # Request duration metrics with detailed buckets for API calls
    metrics_manager.register_metric(
        MetricConfig(
            name="federal_api_request_duration_seconds",
            description="Duration of Federal API requests",
            labels=["api_name", "method", "endpoint", "status"],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
        ),
        MetricType.HISTOGRAM,
    )

    # Request counter
    metrics_manager.register_metric(
        MetricConfig(
            name="federal_api_requests_total",
            description="Total Federal API requests",
            labels=["api_name", "method", "endpoint", "status_code"],
        ),
        MetricType.COUNTER,
    )

    # Retry metrics
    metrics_manager.register_metric(
        MetricConfig(
            name="federal_api_retries_total",
            description="Total retry attempts for Federal API requests",
            labels=["api_name", "method", "reason"],
        ),
        MetricType.COUNTER,
    )

    metrics_manager.register_metric(
        MetricConfig(
            name="federal_api_retry_attempts",
            description="Number of retry attempts per request",
            labels=["api_name", "method"],
            buckets=[0, 1, 2, 3, 4, 5],
        ),
        MetricType.HISTOGRAM,
    )

    # Cache metrics
    metrics_manager.register_metric(
        MetricConfig(
            name="federal_api_cache_operations_total",
            description="Total cache operations for Federal APIs",
            labels=["api_name", "operation", "result"],
        ),
        MetricType.COUNTER,
    )

    metrics_manager.register_metric(
        MetricConfig(
            name="federal_api_cache_size",
            description="Current size of Federal API cache",
            labels=["api_name", "cache_type"],
        ),
        MetricType.GAUGE,
    )

    # Error metrics
    metrics_manager.register_metric(
        MetricConfig(
            name="federal_api_errors_total",
            description="Total errors from Federal APIs",
            labels=["api_name", "error_type", "retryable"],
        ),
        MetricType.COUNTER,
    )

    # Data volume metrics
    metrics_manager.register_metric(
        MetricConfig(
            name="federal_api_records_fetched_total",
            description="Total records fetched from Federal APIs",
            labels=["api_name", "data_type"],
        ),
        MetricType.COUNTER,
    )

    # Response size metrics
    metrics_manager.register_metric(
        MetricConfig(
            name="federal_api_response_size_bytes",
            description="Size of Federal API responses",
            labels=["api_name", "endpoint"],
            buckets=[100, 1000, 10000, 100000, 1000000, 10000000],
        ),
        MetricType.HISTOGRAM,
    )

    # Timeout metrics
    metrics_manager.register_metric(
        MetricConfig(
            name="federal_api_timeouts_total",
            description="Total timeout errors from Federal APIs",
            labels=["api_name", "method", "timeout_seconds"],
        ),
        MetricType.COUNTER,
    )

    # Rate limit metrics
    metrics_manager.register_metric(
        MetricConfig(
            name="federal_api_rate_limits_total",
            description="Total rate limit errors from Federal APIs",
            labels=["api_name", "retry_after"],
        ),
        MetricType.COUNTER,
    )

    # Active requests gauge
    metrics_manager.register_metric(
        MetricConfig(
            name="federal_api_active_requests",
            description="Currently active requests to Federal APIs",
            labels=["api_name"],
        ),
        MetricType.GAUGE,
    )

    logger.info("Federal API metrics registered successfully")


class FederalAPIMetrics:
    """Helper class for recording Federal API metrics."""

    @staticmethod
    def record_request(
        api_name: str,
        method: str,
        endpoint: str,
        status_code: int,
        duration_seconds: float,
        status: str = "success",
    ):
        """
        Record a Federal API request.

        Args:
            api_name: Name of the API (IBGE, DataSUS, INEP)
            method: HTTP method (GET, POST)
            endpoint: API endpoint called
            status_code: HTTP status code
            duration_seconds: Request duration
            status: Request status (success, error, timeout)
        """
        # Record duration
        metrics_manager.observe_histogram(
            "federal_api_request_duration_seconds",
            duration_seconds,
            {
                "api_name": api_name,
                "method": method,
                "endpoint": endpoint,
                "status": status,
            },
        )

        # Record request count
        metrics_manager.increment_counter(
            "federal_api_requests_total",
            {
                "api_name": api_name,
                "method": method,
                "endpoint": endpoint,
                "status_code": str(status_code),
            },
        )

    @staticmethod
    def record_retry(api_name: str, method: str, reason: str, attempt_number: int):
        """
        Record a retry attempt.

        Args:
            api_name: Name of the API
            method: HTTP method
            reason: Reason for retry (network_error, timeout, server_error)
            attempt_number: Current retry attempt number
        """
        metrics_manager.increment_counter(
            "federal_api_retries_total",
            {"api_name": api_name, "method": method, "reason": reason},
        )

        metrics_manager.observe_histogram(
            "federal_api_retry_attempts",
            attempt_number,
            {"api_name": api_name, "method": method},
        )

    @staticmethod
    def record_cache_operation(api_name: str, operation: str, result: str):
        """
        Record a cache operation.

        Args:
            api_name: Name of the API
            operation: Operation type (read, write, delete)
            result: Operation result (hit, miss, success, error)
        """
        metrics_manager.increment_counter(
            "federal_api_cache_operations_total",
            {"api_name": api_name, "operation": operation, "result": result},
        )

    @staticmethod
    def update_cache_size(api_name: str, cache_type: str, size: int):
        """
        Update cache size gauge.

        Args:
            api_name: Name of the API
            cache_type: Type of cache (memory, redis)
            size: Current cache size
        """
        metrics_manager.set_gauge(
            "federal_api_cache_size",
            size,
            {"api_name": api_name, "cache_type": cache_type},
        )

    @staticmethod
    def record_error(api_name: str, error_type: str, retryable: bool):
        """
        Record an API error.

        Args:
            api_name: Name of the API
            error_type: Type of error (NetworkError, TimeoutError, etc)
            retryable: Whether the error is retryable
        """
        metrics_manager.increment_counter(
            "federal_api_errors_total",
            {
                "api_name": api_name,
                "error_type": error_type,
                "retryable": str(retryable).lower(),
            },
        )

    @staticmethod
    def record_data_fetched(api_name: str, data_type: str, record_count: int):
        """
        Record data fetched from API.

        Args:
            api_name: Name of the API
            data_type: Type of data (states, municipalities, health_facilities, etc)
            record_count: Number of records fetched
        """
        metrics_manager.increment_counter(
            "federal_api_records_fetched_total",
            {"api_name": api_name, "data_type": data_type},
            amount=record_count,
        )

    @staticmethod
    def record_response_size(api_name: str, endpoint: str, size_bytes: int):
        """
        Record response size.

        Args:
            api_name: Name of the API
            endpoint: API endpoint
            size_bytes: Response size in bytes
        """
        metrics_manager.observe_histogram(
            "federal_api_response_size_bytes",
            size_bytes,
            {"api_name": api_name, "endpoint": endpoint},
        )

    @staticmethod
    def record_timeout(api_name: str, method: str, timeout_seconds: float):
        """
        Record a timeout error.

        Args:
            api_name: Name of the API
            method: HTTP method
            timeout_seconds: Timeout duration
        """
        metrics_manager.increment_counter(
            "federal_api_timeouts_total",
            {
                "api_name": api_name,
                "method": method,
                "timeout_seconds": str(int(timeout_seconds)),
            },
        )

    @staticmethod
    def record_rate_limit(api_name: str, retry_after: int | None = None):
        """
        Record a rate limit error.

        Args:
            api_name: Name of the API
            retry_after: Retry-After header value (seconds)
        """
        metrics_manager.increment_counter(
            "federal_api_rate_limits_total",
            {
                "api_name": api_name,
                "retry_after": str(retry_after) if retry_after else "unknown",
            },
        )

    @staticmethod
    def increment_active_requests(api_name: str):
        """Increment active requests gauge."""
        metric = metrics_manager.get_metric("federal_api_active_requests")
        if metric:
            metric.labels(api_name=api_name).inc()

    @staticmethod
    def decrement_active_requests(api_name: str):
        """Decrement active requests gauge."""
        metric = metrics_manager.get_metric("federal_api_active_requests")
        if metric:
            metric.labels(api_name=api_name).dec()


def track_federal_api_call(api_name: str):
    """
    Decorator to track Federal API calls with comprehensive metrics.

    Args:
        api_name: Name of the API (IBGE, DataSUS, INEP)

    Usage:
        @track_federal_api_call("IBGE")
        async def get_states(self):
            ...
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Increment active requests
            FederalAPIMetrics.increment_active_requests(api_name)

            start_time = time.time()
            method = "GET"  # Default
            endpoint = func.__name__
            status = "success"
            status_code = 200

            try:
                # Execute function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                return result

            except Exception as e:
                status = "error"
                status_code = getattr(e, "status_code", 500)

                # Record error
                FederalAPIMetrics.record_error(
                    api_name,
                    type(e).__name__,
                    retryable=hasattr(e, "__class__")
                    and "Retryable" in str(e.__class__.__mro__),
                )

                raise

            finally:
                # Always record metrics
                duration = time.time() - start_time

                FederalAPIMetrics.record_request(
                    api_name, method, endpoint, status_code, duration, status
                )

                # Decrement active requests
                FederalAPIMetrics.decrement_active_requests(api_name)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            FederalAPIMetrics.increment_active_requests(api_name)

            start_time = time.time()
            method = "GET"
            endpoint = func.__name__
            status = "success"
            status_code = 200

            try:
                result = func(*args, **kwargs)
                return result

            except Exception as e:
                status = "error"
                status_code = getattr(e, "status_code", 500)

                FederalAPIMetrics.record_error(
                    api_name, type(e).__name__, retryable=False
                )

                raise

            finally:
                duration = time.time() - start_time

                FederalAPIMetrics.record_request(
                    api_name, method, endpoint, status_code, duration, status
                )

                FederalAPIMetrics.decrement_active_requests(api_name)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Auto-register metrics on module import
register_federal_api_metrics()
