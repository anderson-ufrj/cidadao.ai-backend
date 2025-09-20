"""
Telemetry stub for HuggingFace deployment with minimal dependencies.
Provides mock implementations when full OpenTelemetry is not available.
"""

import functools
from typing import Any, Callable, Optional


class MockTracer:
    """Mock tracer for when OpenTelemetry is not available."""
    
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
        return MockSpan()


class MockMeter:
    """Mock meter for when OpenTelemetry is not available."""
    
    def create_counter(self, name: str, **kwargs):
        """Mock counter."""
        class MockCounter:
            def add(self, amount: int = 1, attributes: Optional[dict] = None):
                pass
        return MockCounter()
    
    def create_histogram(self, name: str, **kwargs):
        """Mock histogram."""
        class MockHistogram:
            def record(self, amount: float, attributes: Optional[dict] = None):
                pass
        return MockHistogram()
    
    def create_up_down_counter(self, name: str, **kwargs):
        """Mock up-down counter."""
        class MockUpDownCounter:
            def add(self, amount: int = 1, attributes: Optional[dict] = None):
                pass
        return MockUpDownCounter()


# Global mock instances
mock_tracer = MockTracer()
mock_meter = MockMeter()


def trace_method(span_name: Optional[str] = None) -> Callable:
    """Decorator for tracing methods - no-op version."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


import asyncio