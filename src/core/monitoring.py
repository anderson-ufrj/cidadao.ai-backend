"""
Comprehensive monitoring and observability system.
Provides metrics collection, distributed tracing, and health monitoring.
"""

import asyncio
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from typing import Any

import psutil
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# Try to import OpenTelemetry, fallback to minimal if not available
try:
    from opentelemetry import baggage, trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False

from src.core import get_logger
from src.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


def get_or_create_metric(metric_type, name, description, labels=None, **kwargs):
    """Get existing metric or create new one."""
    # Check if metric already exists in the default registry
    for collector in REGISTRY._collector_to_names:
        if hasattr(collector, "_name") and collector._name == name:
            return collector

    # Create new metric
    if metric_type == Counter:
        return Counter(name, description, labels or [], **kwargs)
    if metric_type == Histogram:
        return Histogram(name, description, labels or [], **kwargs)
    if metric_type == Gauge:
        return Gauge(name, description, labels or [], **kwargs)
    raise ValueError(f"Unknown metric type: {metric_type}")


# Prometheus Metrics - with duplicate checking
REQUEST_COUNT = get_or_create_metric(
    Counter,
    "cidadao_ai_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status_code"],
)

REQUEST_DURATION = get_or_create_metric(
    Histogram,
    "cidadao_ai_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
)

AGENT_TASK_COUNT = get_or_create_metric(
    Counter,
    "cidadao_ai_agent_tasks_total",
    "Total number of agent tasks",
    ["agent_type", "task_type", "status"],
)

AGENT_TASK_DURATION = get_or_create_metric(
    Histogram,
    "cidadao_ai_agent_task_duration_seconds",
    "Agent task duration in seconds",
    ["agent_type", "task_type"],
)

DATABASE_QUERIES = get_or_create_metric(
    Counter,
    "cidadao_ai_database_queries_total",
    "Total number of database queries",
    ["operation", "table"],
)

DATABASE_QUERY_DURATION = get_or_create_metric(
    Histogram,
    "cidadao_ai_database_query_duration_seconds",
    "Database query duration in seconds",
    ["operation", "table"],
)

TRANSPARENCY_API_CALLS = get_or_create_metric(
    Counter,
    "cidadao_ai_transparency_api_calls_total",
    "Total calls to transparency API",
    ["endpoint", "status"],
)

TRANSPARENCY_API_DURATION = get_or_create_metric(
    Histogram,
    "cidadao_ai_transparency_api_duration_seconds",
    "Transparency API call duration",
    ["endpoint"],
)

SYSTEM_CPU_USAGE = get_or_create_metric(
    Gauge, "cidadao_ai_system_cpu_percent", "System CPU usage percentage"
)

SYSTEM_MEMORY_USAGE = get_or_create_metric(
    Gauge, "cidadao_ai_system_memory_percent", "System memory usage percentage"
)

REDIS_OPERATIONS = get_or_create_metric(
    Counter,
    "cidadao_ai_redis_operations_total",
    "Total Redis operations",
    ["operation", "status"],
)

ACTIVE_CONNECTIONS = get_or_create_metric(
    Gauge,
    "cidadao_ai_active_connections",
    "Number of active connections",
    ["connection_type"],
)

# Investigation and Anomaly Detection Metrics
INVESTIGATIONS_TOTAL = get_or_create_metric(
    Counter,
    "cidadao_ai_investigations_total",
    "Total number of investigations started",
    ["agent_type", "investigation_type", "status"],
)

ANOMALIES_DETECTED = get_or_create_metric(
    Counter,
    "cidadao_ai_anomalies_detected_total",
    "Total number of anomalies detected",
    ["anomaly_type", "severity", "agent"],
)

INVESTIGATION_DURATION = get_or_create_metric(
    Histogram,
    "cidadao_ai_investigation_duration_seconds",
    "Time taken for investigations",
    ["agent_type", "investigation_type"],
)

DATA_RECORDS_PROCESSED = get_or_create_metric(
    Counter,
    "cidadao_ai_data_records_processed_total",
    "Total number of data records processed",
    ["data_source", "agent", "operation"],
)

TRANSPARENCY_API_DATA_FETCHED = get_or_create_metric(
    Counter,
    "cidadao_ai_transparency_data_fetched_total",
    "Total data fetched from transparency API",
    ["endpoint", "organization", "status"],
)


class PerformanceMetrics:
    """System performance metrics collector."""

    def __init__(self):
        """Initialize performance metrics collector."""
        self.metrics_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._system_metrics_task: asyncio.Task | None = None
        self._last_update = time.time()
        self._update_interval = 60  # Update every 60 seconds

    async def start_collection(self):
        """Start collecting system metrics."""
        if self._system_metrics_task is None:
            self._system_metrics_task = asyncio.create_task(
                self._collect_system_metrics()
            )
            logger.info("Started system metrics collection")

    async def stop_collection(self):
        """Stop collecting system metrics."""
        if self._system_metrics_task:
            self._system_metrics_task.cancel()
            try:
                await self._system_metrics_task
            except asyncio.CancelledError:
                pass
            self._system_metrics_task = None
            logger.info("Stopped system metrics collection")

    async def _collect_system_metrics(self):
        """Collect system metrics periodically."""
        while True:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                SYSTEM_CPU_USAGE.set(cpu_percent)
                self.metrics_history["cpu"].append(
                    {"timestamp": datetime.now(UTC), "value": cpu_percent}
                )

                # Memory usage
                memory = psutil.virtual_memory()
                SYSTEM_MEMORY_USAGE.set(memory.percent)
                self.metrics_history["memory"].append(
                    {"timestamp": datetime.now(UTC), "value": memory.percent}
                )

                # Disk usage
                disk = psutil.disk_usage("/")
                self.metrics_history["disk"].append(
                    {"timestamp": datetime.now(UTC), "value": disk.percent}
                )

                # Network I/O
                net_io = psutil.net_io_counters()
                self.metrics_history["network"].append(
                    {
                        "timestamp": datetime.now(UTC),
                        "bytes_sent": net_io.bytes_sent,
                        "bytes_recv": net_io.bytes_recv,
                    }
                )

                await asyncio.sleep(self._update_interval)

            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(self._update_interval)

    def get_current_metrics(self) -> dict[str, Any]:
        """Get current system metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "available": psutil.virtual_memory().available,
                "total": psutil.virtual_memory().total,
            },
            "disk": {
                "percent": psutil.disk_usage("/").percent,
                "free": psutil.disk_usage("/").free,
                "total": psutil.disk_usage("/").total,
            },
            "network": {
                "connections": len(psutil.net_connections()),
                "io_counters": (
                    psutil.net_io_counters()._asdict()
                    if psutil.net_io_counters()
                    else {}
                ),
            },
        }

    def get_metrics_history(
        self, metric_type: str, duration_minutes: int = 60
    ) -> list[dict[str, Any]]:
        """Get metrics history for a specific duration."""
        if metric_type not in self.metrics_history:
            return []

        cutoff_time = datetime.now(UTC) - timedelta(minutes=duration_minutes)
        return [
            metric
            for metric in self.metrics_history[metric_type]
            if metric.get("timestamp", datetime.min) > cutoff_time
        ]


# Global performance metrics instance
performance_metrics = PerformanceMetrics()


class TracingManager:
    """Manages distributed tracing configuration."""

    def __init__(self):
        """Initialize tracing manager."""
        self.tracer = None
        self._initialized = False

    def initialize(self):
        """Initialize OpenTelemetry tracing."""
        if not OPENTELEMETRY_AVAILABLE or self._initialized:
            return

        try:
            # Configure tracer provider
            trace.set_tracer_provider(
                TracerProvider(
                    resource=trace.Resource.create(
                        {
                            "service.name": "cidadao.ai.backend",
                            "service.version": settings.VERSION,
                        }
                    )
                )
            )

            # Add Jaeger exporter if configured
            if settings.JAEGER_ENABLED and settings.JAEGER_ENDPOINT:
                jaeger_exporter = JaegerExporter(
                    agent_host_name=settings.JAEGER_ENDPOINT.split(":")[0],
                    agent_port=(
                        int(settings.JAEGER_ENDPOINT.split(":")[1])
                        if ":" in settings.JAEGER_ENDPOINT
                        else 6831
                    ),
                )
                trace.get_tracer_provider().add_span_processor(
                    BatchSpanProcessor(jaeger_exporter)
                )

            self.tracer = trace.get_tracer(__name__)
            self._initialized = True
            logger.info("OpenTelemetry tracing initialized")

        except Exception as e:
            logger.error(f"Failed to initialize tracing: {e}")

    @asynccontextmanager
    async def trace_operation(
        self, operation_name: str, attributes: dict[str, Any] | None = None
    ):
        """Context manager for tracing operations."""
        if not self.tracer:
            yield
            return

        with self.tracer.start_as_current_span(operation_name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, str(value))

            start_time = time.time()
            try:
                yield span
            finally:
                duration = time.time() - start_time
                span.set_attribute("duration_seconds", duration)


# Global tracing manager instance
tracing_manager = TracingManager()


class HealthMonitor:
    """Monitors application health."""

    def __init__(self):
        """Initialize health monitor."""
        self.health_checks: dict[str, dict[str, Any]] = {}
        self._check_results: dict[str, dict[str, Any]] = {}

    def register_check(self, name: str, check_func: callable, critical: bool = False):
        """Register a health check function."""
        self.health_checks[name] = {"func": check_func, "critical": critical}

    async def run_checks(self) -> dict[str, Any]:
        """Run all registered health checks."""
        results = {}
        overall_status = "healthy"

        for name, check_info in self.health_checks.items():
            try:
                check_func = check_info["func"]
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()

                results[name] = {
                    "status": "healthy" if result else "unhealthy",
                    "critical": check_info["critical"],
                }

                if not result and check_info["critical"]:
                    overall_status = "unhealthy"

            except Exception as e:
                logger.error(f"Health check {name} failed: {e}")
                results[name] = {
                    "status": "error",
                    "error": str(e),
                    "critical": check_info["critical"],
                }
                if check_info["critical"]:
                    overall_status = "unhealthy"

        self._check_results = {
            "status": overall_status,
            "checks": results,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        return self._check_results

    def get_latest_results(self) -> dict[str, Any]:
        """Get latest health check results."""
        return self._check_results


# Global health monitor instance
health_monitor = HealthMonitor()


# Utility functions for metrics collection
def record_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record HTTP request metrics."""
    REQUEST_COUNT.labels(
        method=method, endpoint=endpoint, status_code=str(status_code)
    ).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)


def record_agent_task(agent_type: str, task_type: str, status: str, duration: float):
    """Record agent task execution metrics."""
    AGENT_TASK_COUNT.labels(
        agent_type=agent_type, task_type=task_type, status=status
    ).inc()
    AGENT_TASK_DURATION.labels(agent_type=agent_type, task_type=task_type).observe(
        duration
    )


def record_database_query(operation: str, table: str, duration: float):
    """Record database query metrics."""
    DATABASE_QUERIES.labels(operation=operation, table=table).inc()
    DATABASE_QUERY_DURATION.labels(operation=operation, table=table).observe(duration)


def record_transparency_api_call(endpoint: str, status: str, duration: float):
    """Record transparency API call metrics."""
    TRANSPARENCY_API_CALLS.labels(endpoint=endpoint, status=status).inc()
    TRANSPARENCY_API_DURATION.labels(endpoint=endpoint).observe(duration)


def record_investigation(
    agent_type: str, investigation_type: str, status: str, duration: float
):
    """Record investigation metrics."""
    INVESTIGATIONS_TOTAL.labels(
        agent_type=agent_type, investigation_type=investigation_type, status=status
    ).inc()
    INVESTIGATION_DURATION.labels(
        agent_type=agent_type, investigation_type=investigation_type
    ).observe(duration)


def record_anomaly(anomaly_type: str, severity: str, agent: str):
    """Record anomaly detection metrics."""
    ANOMALIES_DETECTED.labels(
        anomaly_type=anomaly_type, severity=severity, agent=agent
    ).inc()


async def collect_system_metrics():
    """Collect and update system metrics."""
    await performance_metrics.start_collection()


def get_metrics_data() -> bytes:
    """Generate Prometheus metrics data."""
    return generate_latest()


# Initialize components
def initialize_monitoring():
    """Initialize monitoring components."""
    tracing_manager.initialize()
    asyncio.create_task(performance_metrics.start_collection())
    logger.info("Monitoring system initialized")


# Export all public components
__all__ = [
    "REQUEST_COUNT",
    "REQUEST_DURATION",
    "AGENT_TASK_COUNT",
    "AGENT_TASK_DURATION",
    "DATABASE_QUERIES",
    "DATABASE_QUERY_DURATION",
    "TRANSPARENCY_API_CALLS",
    "TRANSPARENCY_API_DURATION",
    "SYSTEM_CPU_USAGE",
    "SYSTEM_MEMORY_USAGE",
    "REDIS_OPERATIONS",
    "ACTIVE_CONNECTIONS",
    "INVESTIGATIONS_TOTAL",
    "ANOMALIES_DETECTED",
    "INVESTIGATION_DURATION",
    "DATA_RECORDS_PROCESSED",
    "TRANSPARENCY_API_DATA_FETCHED",
    "performance_metrics",
    "tracing_manager",
    "health_monitor",
    "record_request",
    "record_agent_task",
    "record_database_query",
    "record_transparency_api_call",
    "record_investigation",
    "record_anomaly",
    "collect_system_metrics",
    "get_metrics_data",
    "initialize_monitoring",
    "CONTENT_TYPE_LATEST",
]
