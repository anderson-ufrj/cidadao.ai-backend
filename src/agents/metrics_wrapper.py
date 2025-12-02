"""
Metrics wrapper for automatic agent performance tracking.
"""

import functools
import os
from collections.abc import Callable

import psutil

from src.core import get_logger
from src.services.agent_metrics import MetricsCollector, agent_metrics_service

logger = get_logger("agent.metrics_wrapper")


def track_agent_metrics(action: str = None):
    """
    Decorator to automatically track agent metrics.

    Args:
        action: Override action name (default: use function name)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            # Determine action name
            action_name = action or func.__name__

            # Skip if this is not an agent instance
            if not hasattr(self, "name"):
                return await func(self, *args, **kwargs)

            agent_name = self.name

            # Track memory before execution
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss

            # Use metrics collector
            async with MetricsCollector(agent_name, action_name) as collector:
                try:
                    # Execute the function
                    result = await func(self, *args, **kwargs)

                    # Extract quality score if available
                    if hasattr(result, "metadata") and isinstance(
                        result.metadata, dict
                    ):
                        quality_score = result.metadata.get("quality_score")
                        if quality_score is not None:
                            collector.set_quality_score(quality_score)

                    # Extract reflection count if this is a reflective agent
                    if hasattr(self, "_reflection_count"):
                        collector.reflection_iterations = getattr(
                            self, "_reflection_count", 0
                        )

                    # Track memory after execution
                    final_memory = process.memory_info().rss
                    memory_delta = final_memory - initial_memory

                    # Record memory usage
                    await agent_metrics_service.record_memory_usage(
                        agent_name, final_memory
                    )

                    return result

                except Exception:
                    # Let the collector handle error tracking
                    raise

        @functools.wraps(func)
        def sync_wrapper(self, *args, **kwargs):
            # For synchronous methods, we just pass through
            # Metrics are primarily for async agent operations
            return func(self, *args, **kwargs)

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class MetricsAwareAgent:
    """
    Mixin class to make agents metrics-aware.
    Add this to agent inheritance to get automatic metrics tracking.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._metrics_enabled = True
        self._reflection_count = 0

    async def _record_quality_metric(self, quality_score: float):
        """Record quality score for the agent."""
        if self._metrics_enabled and hasattr(self, "name"):
            # This is handled by the decorator now
            pass

    def _increment_reflection(self):
        """Increment reflection counter."""
        self._reflection_count += 1

    def _reset_reflection_count(self):
        """Reset reflection counter."""
        self._reflection_count = 0

    def enable_metrics(self):
        """Enable metrics collection."""
        self._metrics_enabled = True

    def disable_metrics(self):
        """Disable metrics collection."""
        self._metrics_enabled = False


# Import asyncio for the decorator
import asyncio
