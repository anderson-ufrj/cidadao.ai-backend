"""Observability infrastructure for Cidadão.AI."""

from .tracing import (
    TracingManager,
    TracingConfig,
    TraceContext,
    get_tracer,
    trace_function,
    trace_operation,
    SpanMetrics,
    tracing_manager
)
from .metrics import (
    MetricsManager,
    MetricConfig,
    MetricType,
    BusinessMetrics,
    metrics_manager,
    track_time,
    count_calls,
    initialize_app_info
)
from .correlation import (
    CorrelationContext,
    CorrelationMiddleware,
    CorrelationLogger,
    RequestTracker,
    propagate_correlation,
    with_correlation,
    get_correlation_logger,
    request_tracker
)
from .structured_logging import (
    StructuredLogger,
    StructuredLogRecord,
    TraceContextFormatter,
    LogLevel,
    LogEventType,
    get_structured_logger
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
    "get_structured_logger"
]