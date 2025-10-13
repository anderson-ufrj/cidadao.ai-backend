"""Observability infrastructure for Cidadão.AI."""

from .correlation import (
    CorrelationContext,
    CorrelationLogger,
    CorrelationMiddleware,
    RequestTracker,
    get_correlation_logger,
    propagate_correlation,
    request_tracker,
    with_correlation,
)
from .metrics import (
    BusinessMetrics,
    MetricConfig,
    MetricsManager,
    MetricType,
    count_calls,
    initialize_app_info,
    metrics_manager,
    track_time,
)
from .structured_logging import (
    LogEventType,
    LogLevel,
    StructuredLogger,
    StructuredLogRecord,
    TraceContextFormatter,
    get_structured_logger,
)
from .tracing import (
    SpanMetrics,
    TraceContext,
    TracingConfig,
    TracingManager,
    get_tracer,
    trace_function,
    trace_operation,
    tracing_manager,
)

__all__ = [
    # Tracing
    "TracingManager",
    "TracingConfig",
    "TraceContext",
    "get_tracer",
    "trace_function",
    "trace_operation",
    "SpanMetrics",
    "tracing_manager",
    # Metrics
    "MetricsManager",
    "MetricConfig",
    "MetricType",
    "BusinessMetrics",
    "metrics_manager",
    "track_time",
    "count_calls",
    "initialize_app_info",
    # Correlation
    "CorrelationContext",
    "CorrelationMiddleware",
    "CorrelationLogger",
    "RequestTracker",
    "propagate_correlation",
    "with_correlation",
    "get_correlation_logger",
    "request_tracker",
    # Structured Logging
    "StructuredLogger",
    "StructuredLogRecord",
    "TraceContextFormatter",
    "LogLevel",
    "LogEventType",
    "get_structured_logger",
]
