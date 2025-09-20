"""
Distributed tracing implementation using OpenTelemetry.

This module provides comprehensive tracing capabilities for tracking
requests across microservices and system components.
"""

import asyncio
from typing import Dict, Any, Optional, Callable, Union
from contextlib import asynccontextmanager
import time
import uuid
from functools import wraps

from opentelemetry import trace, context, baggage
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.propagators.jaeger import JaegerPropagator
from opentelemetry.propagators.composite import CompositeHTTPPropagator
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace.status import Status, StatusCode

from src.core import get_logger, settings

logger = get_logger(__name__)


class TracingConfig:
    """Configuration for distributed tracing."""
    
    def __init__(
        self,
        service_name: str = "cidadao-ai-backend",
        service_version: str = "1.0.0",
        jaeger_endpoint: Optional[str] = None,
        otlp_endpoint: Optional[str] = None,
        enable_console_export: bool = False,
        sample_rate: float = 1.0,
        max_tag_value_length: int = 1024
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.jaeger_endpoint = jaeger_endpoint
        self.otlp_endpoint = otlp_endpoint
        self.enable_console_export = enable_console_export
        self.sample_rate = sample_rate
        self.max_tag_value_length = max_tag_value_length


class TracingManager:
    """
    Manager for distributed tracing setup and configuration.
    
    Provides centralized configuration for OpenTelemetry tracing
    with support for multiple exporters and instrumentation.
    """
    
    def __init__(self, config: TracingConfig):
        """
        Initialize tracing manager.
        
        Args:
            config: Tracing configuration
        """
        self.config = config
        self.tracer_provider: Optional[TracerProvider] = None
        self.tracer: Optional[trace.Tracer] = None
        self._initialized = False
    
    def initialize(self):
        """Initialize OpenTelemetry tracing."""
        if self._initialized:
            logger.warning("Tracing already initialized")
            return
        
        # Create resource
        resource = Resource.create({
            SERVICE_NAME: self.config.service_name,
            SERVICE_VERSION: self.config.service_version,
            "service.instance.id": str(uuid.uuid4()),
            "deployment.environment": getattr(settings, 'app_env', 'development')
        })
        
        # Create tracer provider
        self.tracer_provider = TracerProvider(resource=resource)
        
        # Add span processors/exporters
        self._setup_exporters()
        
        # Set global tracer provider
        trace.set_tracer_provider(self.tracer_provider)
        
        # Create tracer
        self.tracer = trace.get_tracer(
            __name__,
            version=self.config.service_version
        )
        
        # Setup propagators
        self._setup_propagators()
        
        # Auto-instrument
        self._setup_auto_instrumentation()
        
        self._initialized = True
        logger.info(f"Distributed tracing initialized for {self.config.service_name}")
    
    def _setup_exporters(self):
        """Setup span exporters."""
        if not self.tracer_provider:
            return
        
        # Console exporter for development
        if self.config.enable_console_export:
            console_exporter = ConsoleSpanExporter()
            console_processor = BatchSpanProcessor(console_exporter)
            self.tracer_provider.add_span_processor(console_processor)
            logger.info("Console span exporter enabled")
        
        # Jaeger exporter
        if self.config.jaeger_endpoint:
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=14268,
                collector_endpoint=self.config.jaeger_endpoint
            )
            jaeger_processor = BatchSpanProcessor(jaeger_exporter)
            self.tracer_provider.add_span_processor(jaeger_processor)
            logger.info(f"Jaeger exporter configured: {self.config.jaeger_endpoint}")
        
        # OTLP exporter (for generic OpenTelemetry collectors)
        if self.config.otlp_endpoint:
            otlp_exporter = OTLPSpanExporter(
                endpoint=self.config.otlp_endpoint,
                insecure=True
            )
            otlp_processor = BatchSpanProcessor(otlp_exporter)
            self.tracer_provider.add_span_processor(otlp_processor)
            logger.info(f"OTLP exporter configured: {self.config.otlp_endpoint}")
    
    def _setup_propagators(self):
        """Setup trace context propagators."""
        # Support multiple propagation formats
        propagators = [
            B3MultiFormat(),
            JaegerPropagator()
        ]
        
        composite_propagator = CompositeHTTPPropagator(propagators)
        set_global_textmap(composite_propagator)
        
        logger.info("Trace propagators configured")
    
    def _setup_auto_instrumentation(self):
        """Setup automatic instrumentation for common libraries."""
        try:
            # FastAPI instrumentation
            FastAPIInstrumentor().instrument()
            logger.info("FastAPI auto-instrumentation enabled")
            
            # HTTP client instrumentation
            HTTPXClientInstrumentor().instrument()
            logger.info("HTTPX auto-instrumentation enabled")
            
            # Redis instrumentation
            RedisInstrumentor().instrument()
            logger.info("Redis auto-instrumentation enabled")
            
            # Database instrumentation
            SQLAlchemyInstrumentor().instrument()
            AsyncPGInstrumentor().instrument()
            logger.info("Database auto-instrumentation enabled")
            
        except Exception as e:
            logger.warning(f"Some auto-instrumentation failed: {e}")
    
    def get_tracer(self) -> trace.Tracer:
        """Get the configured tracer."""
        if not self._initialized:
            self.initialize()
        
        return self.tracer
    
    def shutdown(self):
        """Shutdown tracing and flush remaining spans."""
        if self.tracer_provider:
            self.tracer_provider.shutdown()
            logger.info("Tracing shutdown completed")


# Global tracing manager
tracing_config = TracingConfig(
    jaeger_endpoint=getattr(settings, 'jaeger_endpoint', None),
    otlp_endpoint=getattr(settings, 'otlp_endpoint', None),
    enable_console_export=getattr(settings, 'debug', False)
)

tracing_manager = TracingManager(tracing_config)


def get_tracer() -> trace.Tracer:
    """Get the global tracer instance."""
    return tracing_manager.get_tracer()


class TraceContext:
    """
    Utility class for managing trace context and correlation IDs.
    """
    
    @staticmethod
    def get_correlation_id() -> str:
        """Get correlation ID from current trace context."""
        span = trace.get_current_span()
        if span and span.get_span_context().is_valid:
            return f"{span.get_span_context().trace_id:032x}"
        return str(uuid.uuid4())
    
    @staticmethod
    def get_span_id() -> str:
        """Get current span ID."""
        span = trace.get_current_span()
        if span and span.get_span_context().is_valid:
            return f"{span.get_span_context().span_id:016x}"
        return ""
    
    @staticmethod
    def set_user_context(user_id: str, user_email: Optional[str] = None):
        """Set user context in current trace."""
        span = trace.get_current_span()
        if span:
            span.set_attribute("user.id", user_id)
            if user_email:
                span.set_attribute("user.email", user_email)
            
            # Also set in baggage for propagation
            ctx = baggage.set_baggage("user.id", user_id)
            context.attach(ctx)
    
    @staticmethod
    def set_investigation_context(investigation_id: str):
        """Set investigation context in current trace."""
        span = trace.get_current_span()
        if span:
            span.set_attribute("investigation.id", investigation_id)
            
            # Set in baggage
            ctx = baggage.set_baggage("investigation.id", investigation_id)
            context.attach(ctx)
    
    @staticmethod
    def add_event(name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add event to current span."""
        span = trace.get_current_span()
        if span:
            span.add_event(name, attributes or {})


def trace_function(
    operation_name: Optional[str] = None,
    include_args: bool = False,
    include_result: bool = False
):
    """
    Decorator to trace function execution.
    
    Args:
        operation_name: Custom operation name (defaults to function name)
        include_args: Include function arguments in span
        include_result: Include function result in span
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(span_name) as span:
                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                # Add arguments if requested
                if include_args:
                    try:
                        # Only include simple types to avoid serialization issues
                        for i, arg in enumerate(args):
                            if isinstance(arg, (str, int, float, bool)):
                                span.set_attribute(f"args.{i}", str(arg))
                        
                        for key, value in kwargs.items():
                            if isinstance(value, (str, int, float, bool)):
                                span.set_attribute(f"kwargs.{key}", str(value))
                    except Exception as e:
                        logger.debug(f"Failed to add args to span: {e}")
                
                try:
                    start_time = time.time()
                    
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = func(*args, **kwargs)
                    
                    execution_time = time.time() - start_time
                    span.set_attribute("function.duration_ms", execution_time * 1000)
                    
                    # Add result if requested
                    if include_result and result is not None:
                        try:
                            if isinstance(result, (str, int, float, bool)):
                                span.set_attribute("function.result", str(result))
                            elif hasattr(result, '__len__'):
                                span.set_attribute("function.result_length", len(result))
                        except Exception as e:
                            logger.debug(f"Failed to add result to span: {e}")
                    
                    span.set_status(Status(StatusCode.OK))
                    return result
                
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = get_tracer()
            span_name = operation_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(span_name) as span:
                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    span.set_attribute("function.duration_ms", execution_time * 1000)
                    span.set_status(Status(StatusCode.OK))
                    return result
                
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@asynccontextmanager
async def trace_operation(
    operation_name: str,
    attributes: Optional[Dict[str, Any]] = None
):
    """
    Context manager for tracing operations.
    
    Args:
        operation_name: Name of the operation
        attributes: Additional attributes to add to span
    """
    tracer = get_tracer()
    
    with tracer.start_as_current_span(operation_name) as span:
        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)
        
        try:
            yield span
            span.set_status(Status(StatusCode.OK))
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            raise


class SpanMetrics:
    """Utility for adding common metrics to spans."""
    
    @staticmethod
    def record_agent_execution(
        span: trace.Span,
        agent_name: str,
        task_type: str,
        confidence_score: Optional[float] = None
    ):
        """Record agent execution metrics."""
        span.set_attribute("agent.name", agent_name)
        span.set_attribute("agent.task_type", task_type)
        
        if confidence_score is not None:
            span.set_attribute("agent.confidence_score", confidence_score)
    
    @staticmethod
    def record_database_operation(
        span: trace.Span,
        operation: str,
        table: str,
        rows_affected: Optional[int] = None
    ):
        """Record database operation metrics."""
        span.set_attribute("db.operation", operation)
        span.set_attribute("db.table", table)
        
        if rows_affected is not None:
            span.set_attribute("db.rows_affected", rows_affected)
    
    @staticmethod
    def record_cache_operation(
        span: trace.Span,
        operation: str,
        cache_key: str,
        hit: Optional[bool] = None
    ):
        """Record cache operation metrics."""
        span.set_attribute("cache.operation", operation)
        span.set_attribute("cache.key", cache_key)
        
        if hit is not None:
            span.set_attribute("cache.hit", hit)
    
    @staticmethod
    def record_api_call(
        span: trace.Span,
        service_name: str,
        endpoint: str,
        status_code: Optional[int] = None
    ):
        """Record external API call metrics."""
        span.set_attribute("http.client.service", service_name)
        span.set_attribute("http.client.endpoint", endpoint)
        
        if status_code is not None:
            span.set_attribute("http.status_code", status_code)


# Example usage functions
@trace_function(operation_name="investigation.create", include_args=True)
async def example_traced_function(investigation_query: str, user_id: str):
    """Example of a traced function."""
    # Set context
    TraceContext.set_user_context(user_id)
    
    # Add custom event
    TraceContext.add_event("investigation.started", {
        "query_length": len(investigation_query)
    })
    
    # Simulate work
    await asyncio.sleep(0.1)
    
    return {"status": "created", "query": investigation_query}