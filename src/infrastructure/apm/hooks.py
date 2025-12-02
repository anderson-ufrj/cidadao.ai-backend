"""
APM hooks for integrating with external monitoring tools.

This module provides hooks for sending performance data, errors,
and business metrics to external APM systems.
"""

import asyncio
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from functools import wraps
from typing import Any

from src.infrastructure.observability import get_structured_logger

logger = get_structured_logger(__name__, component="apm_hooks")


@dataclass
class APMEvent:
    """APM event data structure."""

    event_type: str
    timestamp: datetime
    data: dict[str, Any]
    tags: dict[str, str] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)


@dataclass
class APMError:
    """APM error data structure."""

    error_type: str
    message: str
    stack_trace: str
    timestamp: datetime
    context: dict[str, Any] = field(default_factory=dict)
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class APMPerformanceMetric:
    """APM performance metric data structure."""

    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    tags: dict[str, str] = field(default_factory=dict)
    dimensions: dict[str, Any] = field(default_factory=dict)


class APMHooks:
    """
    APM hooks for integrating with external monitoring systems.

    Provides a unified interface for sending performance data,
    errors, and business metrics to various APM tools.
    """

    def __init__(self):
        self.enabled = False
        self.integrations: list[Callable] = []
        self.error_handlers: list[Callable] = []
        self.metric_handlers: list[Callable] = []
        self.event_handlers: list[Callable] = []

        # Configuration
        self.config = {
            "enabled": False,
            "buffer_size": 1000,
            "flush_interval_seconds": 30,
            "max_retries": 3,
            "retry_delay_seconds": 1.0,
        }

        # Buffers for batching
        self.event_buffer: list[APMEvent] = []
        self.error_buffer: list[APMError] = []
        self.metric_buffer: list[APMPerformanceMetric] = []

        # Statistics
        self.stats = {
            "events_sent": 0,
            "errors_sent": 0,
            "metrics_sent": 0,
            "send_failures": 0,
            "last_flush": None,
        }

        self.logger = get_structured_logger(__name__, component="apm_hooks")

    def enable(self, config: dict[str, Any] | None = None):
        """Enable APM hooks with optional configuration."""
        if config:
            self.config.update(config)

        self.enabled = True

        # Start background flush task
        asyncio.create_task(self._background_flush())

        self.logger.info(
            "APM hooks enabled", operation="apm_enable", config=self.config
        )

    def disable(self):
        """Disable APM hooks."""
        self.enabled = False

        # Flush remaining data
        asyncio.create_task(self._flush_all())

        self.logger.info("APM hooks disabled", operation="apm_disable")

    def register_integration(self, handler: Callable):
        """Register an APM integration handler."""
        self.integrations.append(handler)
        self.logger.info(
            f"Registered APM integration: {handler.__name__}",
            operation="apm_register_integration",
        )

    def register_error_handler(self, handler: Callable):
        """Register an error handler."""
        self.error_handlers.append(handler)

    def register_metric_handler(self, handler: Callable):
        """Register a metric handler."""
        self.metric_handlers.append(handler)

    def register_event_handler(self, handler: Callable):
        """Register an event handler."""
        self.event_handlers.append(handler)

    def track_performance(
        self, operation_name: str, tags: dict[str, str] | None = None
    ):
        """
        Decorator for tracking performance of operations.

        Args:
            operation_name: Name of the operation being tracked
            tags: Additional tags for the metric
        """

        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                operation_tags = tags or {}
                operation_tags.update(
                    {"operation": operation_name, "function": func.__name__}
                )

                try:
                    result = await func(*args, **kwargs)
                    duration = (
                        time.time() - start_time
                    ) * 1000  # Convert to milliseconds

                    # Track successful operation
                    self.track_metric(
                        "operation.duration",
                        duration,
                        "milliseconds",
                        tags=operation_tags,
                    )

                    self.track_metric(
                        "operation.success", 1, "count", tags=operation_tags
                    )

                    return result

                except Exception as e:
                    duration = (time.time() - start_time) * 1000

                    # Track failed operation
                    operation_tags["error_type"] = type(e).__name__

                    self.track_metric(
                        "operation.duration",
                        duration,
                        "milliseconds",
                        tags=operation_tags,
                    )

                    self.track_metric(
                        "operation.error", 1, "count", tags=operation_tags
                    )

                    # Track the error
                    self.track_error(e, context={"operation": operation_name})

                    raise

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                operation_tags = tags or {}
                operation_tags.update(
                    {"operation": operation_name, "function": func.__name__}
                )

                try:
                    result = func(*args, **kwargs)
                    duration = (time.time() - start_time) * 1000

                    self.track_metric(
                        "operation.duration",
                        duration,
                        "milliseconds",
                        tags=operation_tags,
                    )

                    self.track_metric(
                        "operation.success", 1, "count", tags=operation_tags
                    )

                    return result

                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    operation_tags["error_type"] = type(e).__name__

                    self.track_metric(
                        "operation.duration",
                        duration,
                        "milliseconds",
                        tags=operation_tags,
                    )

                    self.track_metric(
                        "operation.error", 1, "count", tags=operation_tags
                    )

                    self.track_error(e, context={"operation": operation_name})

                    raise

            # Return appropriate wrapper based on function type
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

        return decorator

    def track_error(
        self,
        error: Exception,
        context: dict[str, Any] | None = None,
        tags: dict[str, str] | None = None,
    ):
        """
        Track an error in APM systems.

        Args:
            error: The exception that occurred
            context: Additional context about the error
            tags: Tags for categorizing the error
        """
        if not self.enabled:
            return

        apm_error = APMError(
            error_type=type(error).__name__,
            message=str(error),
            stack_trace=traceback.format_exc(),
            timestamp=datetime.now(UTC),
            context=context or {},
            tags=tags or {},
        )

        self.error_buffer.append(apm_error)

        # Immediately send to error handlers if buffer is full
        if len(self.error_buffer) >= self.config["buffer_size"]:
            asyncio.create_task(self._flush_errors())

    def track_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "count",
        tags: dict[str, str] | None = None,
        dimensions: dict[str, Any] | None = None,
    ):
        """
        Track a performance metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            tags: Tags for categorizing the metric
            dimensions: Additional dimensions for the metric
        """
        if not self.enabled:
            return

        metric = APMPerformanceMetric(
            metric_name=metric_name,
            value=value,
            unit=unit,
            timestamp=datetime.now(UTC),
            tags=tags or {},
            dimensions=dimensions or {},
        )

        self.metric_buffer.append(metric)

        # Immediately send if buffer is full
        if len(self.metric_buffer) >= self.config["buffer_size"]:
            asyncio.create_task(self._flush_metrics())

    def track_event(
        self,
        event_type: str,
        data: dict[str, Any],
        tags: dict[str, str] | None = None,
        metrics: dict[str, float] | None = None,
    ):
        """
        Track a business event.

        Args:
            event_type: Type of event
            data: Event data
            tags: Tags for categorizing the event
            metrics: Associated metrics
        """
        if not self.enabled:
            return

        event = APMEvent(
            event_type=event_type,
            timestamp=datetime.now(UTC),
            data=data,
            tags=tags or {},
            metrics=metrics or {},
        )

        self.event_buffer.append(event)

        # Immediately send if buffer is full
        if len(self.event_buffer) >= self.config["buffer_size"]:
            asyncio.create_task(self._flush_events())

    async def _background_flush(self):
        """Background task to periodically flush buffers."""
        while self.enabled:
            try:
                await asyncio.sleep(self.config["flush_interval_seconds"])
                await self._flush_all()
            except Exception as e:
                self.logger.error(f"Background flush failed: {e}")

    async def _flush_all(self):
        """Flush all buffers."""
        await asyncio.gather(
            self._flush_events(),
            self._flush_errors(),
            self._flush_metrics(),
            return_exceptions=True,
        )

        self.stats["last_flush"] = datetime.now(UTC).isoformat()

    async def _flush_events(self):
        """Flush event buffer."""
        if not self.event_buffer:
            return

        events_to_send = self.event_buffer.copy()
        self.event_buffer.clear()

        for handler in self.event_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(events_to_send)
                else:
                    handler(events_to_send)

                self.stats["events_sent"] += len(events_to_send)

            except Exception as e:
                self.logger.error(f"Event handler failed: {e}")
                self.stats["send_failures"] += 1

    async def _flush_errors(self):
        """Flush error buffer."""
        if not self.error_buffer:
            return

        errors_to_send = self.error_buffer.copy()
        self.error_buffer.clear()

        for handler in self.error_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(errors_to_send)
                else:
                    handler(errors_to_send)

                self.stats["errors_sent"] += len(errors_to_send)

            except Exception as e:
                self.logger.error(f"Error handler failed: {e}")
                self.stats["send_failures"] += 1

    async def _flush_metrics(self):
        """Flush metric buffer."""
        if not self.metric_buffer:
            return

        metrics_to_send = self.metric_buffer.copy()
        self.metric_buffer.clear()

        for handler in self.metric_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(metrics_to_send)
                else:
                    handler(metrics_to_send)

                self.stats["metrics_sent"] += len(metrics_to_send)

            except Exception as e:
                self.logger.error(f"Metric handler failed: {e}")
                self.stats["send_failures"] += 1

    def get_stats(self) -> dict[str, Any]:
        """Get APM hooks statistics."""
        return {
            "enabled": self.enabled,
            "buffer_sizes": {
                "events": len(self.event_buffer),
                "errors": len(self.error_buffer),
                "metrics": len(self.metric_buffer),
            },
            "handlers_count": {
                "integrations": len(self.integrations),
                "error_handlers": len(self.error_handlers),
                "metric_handlers": len(self.metric_handlers),
                "event_handlers": len(self.event_handlers),
            },
            "statistics": self.stats,
        }


# Global APM hooks instance
apm_hooks = APMHooks()
