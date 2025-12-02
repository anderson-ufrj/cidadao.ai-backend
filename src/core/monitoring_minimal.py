"""
Minimal monitoring system for HuggingFace deployment.
Uses only prometheus_client without complex OpenTelemetry dependencies.
"""

import asyncio
import functools
import time
from collections import defaultdict, deque
from collections.abc import Callable
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

import psutil
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from src.core import get_logger
from src.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()

# Create a custom registry to avoid conflicts
_metrics_registry = CollectorRegistry()
_metrics_cache = {}


def get_or_create_metric(metric_type, name, description, labels=None, **kwargs):
    """Get existing metric or create new one using custom registry."""
    # Check if metric already exists in our cache
    if name in _metrics_cache:
        return _metrics_cache[name]

    # Create new metric with custom registry
    if metric_type == Counter:
        metric = Counter(
            name, description, labels or [], registry=_metrics_registry, **kwargs
        )
    elif metric_type == Histogram:
        metric = Histogram(
            name, description, labels or [], registry=_metrics_registry, **kwargs
        )
    elif metric_type == Gauge:
        metric = Gauge(
            name, description, labels or [], registry=_metrics_registry, **kwargs
        )
    else:
        raise ValueError(f"Unknown metric type: {metric_type}")

    _metrics_cache[name] = metric
    return metric


# Prometheus metrics - with duplicate checking
request_count = get_or_create_metric(
    Counter,
    "cidadao_ai_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

request_duration = get_or_create_metric(
    Histogram,
    "cidadao_ai_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
)

active_requests = get_or_create_metric(
    Gauge, "cidadao_ai_http_requests_active", "Active HTTP requests"
)

agent_tasks_total = get_or_create_metric(
    Counter,
    "cidadao_ai_agent_tasks_total",
    "Total agent tasks executed",
    ["agent", "status"],
)

agent_task_duration = get_or_create_metric(
    Histogram,
    "cidadao_ai_agent_task_duration_seconds",
    "Agent task execution time",
    ["agent", "task_type"],
)

cache_operations = get_or_create_metric(
    Counter,
    "cidadao_ai_cache_operations_total",
    "Cache operations",
    ["operation", "status"],
)

cache_hit_ratio = get_or_create_metric(
    Gauge, "cidadao_ai_cache_hit_ratio", "Cache hit ratio"
)

# System metrics
system_cpu = get_or_create_metric(
    Gauge, "cidadao_ai_system_cpu_percent", "System CPU usage"
)
system_memory = get_or_create_metric(
    Gauge, "cidadao_ai_system_memory_percent", "System memory usage"
)
system_disk = get_or_create_metric(
    Gauge, "cidadao_ai_system_disk_percent", "System disk usage"
)


class MockTracer:
    """Mock tracer for minimal deployment."""

    def start_as_current_span(self, name: str, **kwargs):
        """Mock span context manager."""

        class MockSpan:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

            def set_attribute(self, key: str, value: Any):
                pass

            def set_status(self, status: Any):
                pass

            def add_event(self, name: str, attributes: dict | None = None):
                pass

        return MockSpan()


class MetricsCollector:
    """Simplified metrics collector."""

    def __init__(self):
        self.metrics_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._tracer = MockTracer()
        self._last_system_check = 0
        self._system_check_interval = 60  # seconds

    async def initialize(self):
        """Initialize metrics collector."""
        logger.info("Initializing minimal metrics collector")
        # Start system metrics collection
        asyncio.create_task(self._collect_system_metrics())

    async def shutdown(self):
        """Shutdown metrics collector."""
        logger.info("Shutting down minimal metrics collector")

    def get_tracer(self):
        """Get tracer instance."""
        return self._tracer

    async def _collect_system_metrics(self):
        """Collect system metrics periodically."""
        while True:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                system_cpu.set(cpu_percent)

                # Memory usage
                memory = psutil.virtual_memory()
                system_memory.set(memory.percent)

                # Disk usage
                disk = psutil.disk_usage("/")
                system_disk.set(disk.percent)

                await asyncio.sleep(self._system_check_interval)
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(self._system_check_interval)

    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics."""
        request_count.labels(method=method, endpoint=endpoint, status=str(status)).inc()
        request_duration.labels(method=method, endpoint=endpoint).observe(duration)

    def record_agent_task(
        self, agent: str, task_type: str, status: str, duration: float
    ):
        """Record agent task metrics."""
        agent_tasks_total.labels(agent=agent, status=status).inc()
        agent_task_duration.labels(agent=agent, task_type=task_type).observe(duration)

    def record_cache_operation(self, operation: str, status: str):
        """Record cache operation metrics."""
        cache_operations.labels(operation=operation, status=status).inc()

    def update_cache_hit_ratio(self, ratio: float):
        """Update cache hit ratio."""
        cache_hit_ratio.set(ratio)

    @asynccontextmanager
    async def trace_operation(
        self, operation_name: str, attributes: dict | None = None
    ):
        """Context manager for tracing operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            logger.debug(f"Operation {operation_name} completed in {duration:.3f}s")

    def get_metrics(self) -> str:
        """Get Prometheus metrics."""
        return generate_latest(_metrics_registry)


# Global metrics collector instance
_metrics_collector = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def trace_method(span_name: str | None = None) -> Callable:
    """Decorator for tracing methods - simplified version."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            operation_name = span_name or f"{self.__class__.__name__}.{func.__name__}"
            collector = get_metrics_collector()
            async with collector.trace_operation(operation_name):
                return await func(self, *args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            operation_name = span_name or f"{self.__class__.__name__}.{func.__name__}"
            start_time = time.time()
            try:
                return func(self, *args, **kwargs)
            finally:
                duration = time.time() - start_time
                logger.debug(f"Operation {operation_name} completed in {duration:.3f}s")

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


class HealthMonitor:
    """Simplified health monitoring."""

    def __init__(self):
        self.checks: dict[str, dict[str, Any]] = {}
        self._last_check_time: dict[str, float] = {}

    def register_check(self, name: str, check_func: Callable, critical: bool = False):
        """Register a health check."""
        self.checks[name] = {
            "func": check_func,
            "critical": critical,
            "last_status": None,
            "last_error": None,
        }

    async def check_health(self) -> dict[str, Any]:
        """Run all health checks."""
        results = {}
        overall_healthy = True

        for name, check_info in self.checks.items():
            try:
                if asyncio.iscoroutinefunction(check_info["func"]):
                    result = await check_info["func"]()
                else:
                    result = check_info["func"]()

                results[name] = {
                    "status": "healthy" if result else "unhealthy",
                    "critical": check_info["critical"],
                }

                if not result and check_info["critical"]:
                    overall_healthy = False

            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                results[name] = {
                    "status": "error",
                    "error": str(e),
                    "critical": check_info["critical"],
                }
                if check_info["critical"]:
                    overall_healthy = False

        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "checks": results,
            "timestamp": datetime.now(UTC).isoformat(),
        }


# Export minimal monitoring components
__all__ = [
    "MetricsCollector",
    "get_metrics_collector",
    "trace_method",
    "HealthMonitor",
    "request_count",
    "request_duration",
    "active_requests",
    "agent_tasks_total",
    "agent_task_duration",
    "cache_operations",
    "cache_hit_ratio",
    "system_cpu",
    "system_memory",
    "system_disk",
    "CONTENT_TYPE_LATEST",
]
