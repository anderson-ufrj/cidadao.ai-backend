"""
Request correlation ID management for distributed tracing.

This module provides correlation ID generation, propagation,
and context management across service boundaries.
"""

import asyncio
import time
import uuid
from collections.abc import Callable
from contextvars import ContextVar
from functools import wraps
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core import get_logger

logger = get_logger(__name__)

# Context variables for correlation tracking
correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_ctx: ContextVar[str | None] = ContextVar("user_id", default=None)
session_id_ctx: ContextVar[str | None] = ContextVar("session_id", default=None)
span_id_ctx: ContextVar[str | None] = ContextVar("span_id", default=None)

# Headers for correlation propagation
CORRELATION_ID_HEADER = "X-Correlation-ID"
REQUEST_ID_HEADER = "X-Request-ID"
USER_ID_HEADER = "X-User-ID"
SESSION_ID_HEADER = "X-Session-ID"
SPAN_ID_HEADER = "X-Span-ID"


class CorrelationContext:
    """
    Utility class for managing correlation context.

    Provides methods to get, set, and propagate correlation IDs
    across async boundaries and service calls.
    """

    @staticmethod
    def get_correlation_id() -> str:
        """
        Get current correlation ID, generating one if needed.

        Returns:
            Correlation ID string
        """
        correlation_id = correlation_id_ctx.get()
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
            correlation_id_ctx.set(correlation_id)
        return correlation_id

    @staticmethod
    def set_correlation_id(correlation_id: str):
        """
        Set correlation ID in context.

        Args:
            correlation_id: Correlation ID to set
        """
        correlation_id_ctx.set(correlation_id)

    @staticmethod
    def get_request_id() -> str:
        """
        Get current request ID, generating one if needed.

        Returns:
            Request ID string
        """
        request_id = request_id_ctx.get()
        if not request_id:
            request_id = str(uuid.uuid4())
            request_id_ctx.set(request_id)
        return request_id

    @staticmethod
    def set_request_id(request_id: str):
        """
        Set request ID in context.

        Args:
            request_id: Request ID to set
        """
        request_id_ctx.set(request_id)

    @staticmethod
    def get_user_id() -> str | None:
        """Get current user ID from context."""
        return user_id_ctx.get()

    @staticmethod
    def set_user_id(user_id: str):
        """
        Set user ID in context.

        Args:
            user_id: User ID to set
        """
        user_id_ctx.set(user_id)

    @staticmethod
    def get_session_id() -> str | None:
        """Get current session ID from context."""
        return session_id_ctx.get()

    @staticmethod
    def set_session_id(session_id: str):
        """
        Set session ID in context.

        Args:
            session_id: Session ID to set
        """
        session_id_ctx.set(session_id)

    @staticmethod
    def get_span_id() -> str | None:
        """Get current span ID from context."""
        return span_id_ctx.get()

    @staticmethod
    def set_span_id(span_id: str):
        """
        Set span ID in context.

        Args:
            span_id: Span ID to set
        """
        span_id_ctx.set(span_id)

    @staticmethod
    def get_all_ids() -> dict[str, str | None]:
        """
        Get all correlation IDs from context.

        Returns:
            Dictionary with all correlation IDs
        """
        return {
            "correlation_id": correlation_id_ctx.get(),
            "request_id": request_id_ctx.get(),
            "user_id": user_id_ctx.get(),
            "session_id": session_id_ctx.get(),
            "span_id": span_id_ctx.get(),
        }

    @staticmethod
    def clear_context():
        """Clear all correlation context."""
        correlation_id_ctx.set(None)
        request_id_ctx.set(None)
        user_id_ctx.set(None)
        session_id_ctx.set(None)
        span_id_ctx.set(None)

    @staticmethod
    def copy_context() -> dict[str, str | None]:
        """
        Copy current context for propagation.

        Returns:
            Dictionary with current context values
        """
        return CorrelationContext.get_all_ids()

    @staticmethod
    def restore_context(context: dict[str, str | None]):
        """
        Restore context from dictionary.

        Args:
            context: Context dictionary to restore
        """
        if context.get("correlation_id"):
            correlation_id_ctx.set(context["correlation_id"])
        if context.get("request_id"):
            request_id_ctx.set(context["request_id"])
        if context.get("user_id"):
            user_id_ctx.set(context["user_id"])
        if context.get("session_id"):
            session_id_ctx.set(context["session_id"])
        if context.get("span_id"):
            span_id_ctx.set(context["span_id"])


class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for correlation ID management in FastAPI.

    Automatically extracts correlation IDs from headers,
    generates new ones if missing, and adds them to responses.
    """

    def __init__(self, app, generate_request_id: bool = True):
        """
        Initialize correlation middleware.

        Args:
            app: FastAPI application
            generate_request_id: Whether to generate request IDs
        """
        super().__init__(app)
        self.generate_request_id = generate_request_id

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with correlation ID management.

        Args:
            request: Incoming request
            call_next: Next middleware in chain

        Returns:
            Response with correlation headers
        """
        start_time = time.time()

        # Extract or generate correlation ID
        correlation_id = request.headers.get(CORRELATION_ID_HEADER) or str(uuid.uuid4())
        CorrelationContext.set_correlation_id(correlation_id)

        # Extract or generate request ID
        if self.generate_request_id:
            request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
            CorrelationContext.set_request_id(request_id)

        # Extract user context if available
        user_id = request.headers.get(USER_ID_HEADER)
        if user_id:
            CorrelationContext.set_user_id(user_id)

        session_id = request.headers.get(SESSION_ID_HEADER)
        if session_id:
            CorrelationContext.set_session_id(session_id)

        span_id = request.headers.get(SPAN_ID_HEADER)
        if span_id:
            CorrelationContext.set_span_id(span_id)

        # Log request start
        logger.info(
            "Request started",
            extra={
                "correlation_id": correlation_id,
                "request_id": CorrelationContext.get_request_id(),
                "method": request.method,
                "url": str(request.url),
                "user_agent": request.headers.get("user-agent"),
                "client_ip": request.client.host if request.client else None,
            },
        )

        try:
            # Process request
            response = await call_next(request)

            # Add correlation headers to response
            response.headers[CORRELATION_ID_HEADER] = correlation_id

            if self.generate_request_id:
                response.headers[REQUEST_ID_HEADER] = (
                    CorrelationContext.get_request_id()
                )

            # Log successful response
            duration = time.time() - start_time
            logger.info(
                "Request completed",
                extra={
                    "correlation_id": correlation_id,
                    "request_id": CorrelationContext.get_request_id(),
                    "status_code": response.status_code,
                    "duration_ms": duration * 1000,
                    "response_size": response.headers.get("content-length"),
                },
            )

            return response

        except Exception as e:
            # Log error
            duration = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    "correlation_id": correlation_id,
                    "request_id": CorrelationContext.get_request_id(),
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": duration * 1000,
                },
                exc_info=True,
            )
            raise

        finally:
            # Clear context after request
            CorrelationContext.clear_context()


def propagate_correlation(headers: dict[str, str] | None = None) -> dict[str, str]:
    """
    Generate headers for correlation propagation.

    Args:
        headers: Existing headers to extend

    Returns:
        Headers with correlation information
    """
    propagation_headers = headers.copy() if headers else {}

    correlation_id = CorrelationContext.get_correlation_id()
    if correlation_id:
        propagation_headers[CORRELATION_ID_HEADER] = correlation_id

    request_id = CorrelationContext.get_request_id()
    if request_id:
        propagation_headers[REQUEST_ID_HEADER] = request_id

    user_id = CorrelationContext.get_user_id()
    if user_id:
        propagation_headers[USER_ID_HEADER] = user_id

    session_id = CorrelationContext.get_session_id()
    if session_id:
        propagation_headers[SESSION_ID_HEADER] = session_id

    span_id = CorrelationContext.get_span_id()
    if span_id:
        propagation_headers[SPAN_ID_HEADER] = span_id

    return propagation_headers


def with_correlation(func: Callable) -> Callable:
    """
    Decorator to preserve correlation context in async functions.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function with correlation context
    """

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Capture current context
        context = CorrelationContext.copy_context()

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            return result
        finally:
            # Restore context if it was cleared
            if not CorrelationContext.get_correlation_id() and context.get(
                "correlation_id"
            ):
                CorrelationContext.restore_context(context)

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        # For sync functions, just call directly
        return func(*args, **kwargs)

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


class CorrelationLogger:
    """
    Logger wrapper that automatically includes correlation IDs.
    """

    def __init__(self, logger_instance):
        """
        Initialize correlation logger.

        Args:
            logger_instance: Logger instance to wrap
        """
        self.logger = logger_instance

    def _add_correlation_extra(
        self, extra: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Add correlation IDs to log extra data."""
        correlation_extra = extra.copy() if extra else {}

        # Add correlation IDs
        correlation_id = CorrelationContext.get_correlation_id()
        if correlation_id:
            correlation_extra["correlation_id"] = correlation_id

        request_id = CorrelationContext.get_request_id()
        if request_id:
            correlation_extra["request_id"] = request_id

        user_id = CorrelationContext.get_user_id()
        if user_id:
            correlation_extra["user_id"] = user_id

        session_id = CorrelationContext.get_session_id()
        if session_id:
            correlation_extra["session_id"] = session_id

        return correlation_extra

    def debug(self, msg: str, *args, extra: dict[str, Any] | None = None, **kwargs):
        """Log debug message with correlation IDs."""
        self.logger.debug(
            msg, *args, extra=self._add_correlation_extra(extra), **kwargs
        )

    def info(self, msg: str, *args, extra: dict[str, Any] | None = None, **kwargs):
        """Log info message with correlation IDs."""
        self.logger.info(msg, *args, extra=self._add_correlation_extra(extra), **kwargs)

    def warning(self, msg: str, *args, extra: dict[str, Any] | None = None, **kwargs):
        """Log warning message with correlation IDs."""
        self.logger.warning(
            msg, *args, extra=self._add_correlation_extra(extra), **kwargs
        )

    def error(self, msg: str, *args, extra: dict[str, Any] | None = None, **kwargs):
        """Log error message with correlation IDs."""
        self.logger.error(
            msg, *args, extra=self._add_correlation_extra(extra), **kwargs
        )

    def critical(self, msg: str, *args, extra: dict[str, Any] | None = None, **kwargs):
        """Log critical message with correlation IDs."""
        self.logger.critical(
            msg, *args, extra=self._add_correlation_extra(extra), **kwargs
        )


def get_correlation_logger(name: str) -> CorrelationLogger:
    """
    Get a correlation-aware logger.

    Args:
        name: Logger name

    Returns:
        CorrelationLogger instance
    """
    from src.core import get_logger

    base_logger = get_logger(name)
    return CorrelationLogger(base_logger)


class RequestTracker:
    """
    Track request lifecycle and performance metrics.
    """

    def __init__(self):
        """Initialize request tracker."""
        self.active_requests: dict[str, dict[str, Any]] = {}
        self.request_stats = {
            "total_requests": 0,
            "active_requests": 0,
            "avg_duration_ms": 0.0,
            "error_rate": 0.0,
        }

    def start_request(
        self, request_id: str, method: str, path: str, user_id: str | None = None
    ):
        """
        Start tracking a request.

        Args:
            request_id: Request ID
            method: HTTP method
            path: Request path
            user_id: Optional user ID
        """
        self.active_requests[request_id] = {
            "start_time": time.time(),
            "method": method,
            "path": path,
            "user_id": user_id,
            "correlation_id": CorrelationContext.get_correlation_id(),
        }

        self.request_stats["active_requests"] = len(self.active_requests)
        self.request_stats["total_requests"] += 1

    def end_request(
        self, request_id: str, status_code: int, error: str | None = None
    ) -> float | None:
        """
        End tracking a request.

        Args:
            request_id: Request ID
            status_code: HTTP status code
            error: Optional error message

        Returns:
            Request duration in seconds, or None if not found
        """
        if request_id not in self.active_requests:
            return None

        request_info = self.active_requests.pop(request_id)
        duration = time.time() - request_info["start_time"]

        # Update stats
        self.request_stats["active_requests"] = len(self.active_requests)

        # Update average duration (simple moving average)
        current_avg = self.request_stats["avg_duration_ms"]
        new_avg = (current_avg + (duration * 1000)) / 2
        self.request_stats["avg_duration_ms"] = new_avg

        # Update error rate
        if status_code >= 400 or error:
            total = self.request_stats["total_requests"]
            current_errors = self.request_stats["error_rate"] * (total - 1)
            new_error_rate = (current_errors + 1) / total
            self.request_stats["error_rate"] = new_error_rate

        return duration

    def get_active_requests(self) -> list[dict[str, Any]]:
        """Get list of currently active requests."""
        current_time = time.time()
        return [
            {
                "request_id": req_id,
                "duration_ms": (current_time - info["start_time"]) * 1000,
                "method": info["method"],
                "path": info["path"],
                "user_id": info["user_id"],
                "correlation_id": info["correlation_id"],
            }
            for req_id, info in self.active_requests.items()
        ]

    def get_stats(self) -> dict[str, Any]:
        """Get request tracking statistics."""
        return self.request_stats.copy()


# Global request tracker
request_tracker = RequestTracker()
