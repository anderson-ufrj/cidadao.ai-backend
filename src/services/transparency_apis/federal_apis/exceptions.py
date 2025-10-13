"""
Custom exceptions for federal API clients.

Provides specific exception types for better error handling and debugging.

Author: Anderson Henrique da Silva
Created: 2025-10-12
License: Proprietary - All rights reserved
"""

from typing import Any, Optional


class FederalAPIError(Exception):
    """Base exception for all federal API errors."""

    def __init__(
        self,
        message: str,
        api_name: str = "Unknown",
        status_code: Optional[int] = None,
        response_data: Optional[dict[str, Any]] = None,
        original_error: Optional[Exception] = None,
    ):
        self.message = message
        self.api_name = api_name
        self.status_code = status_code
        self.response_data = response_data
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self) -> str:
        parts = [f"{self.api_name}: {self.message}"]
        if self.status_code:
            parts.append(f"(HTTP {self.status_code})")
        if self.original_error:
            parts.append(f"[caused by: {str(self.original_error)}]")
        return " ".join(parts)


class NetworkError(FederalAPIError):
    """Network-related errors (connection, DNS, timeout)."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, **kwargs)


class TimeoutError(NetworkError):
    """Request timeout errors."""

    def __init__(
        self,
        message: str = "Request timed out",
        timeout_seconds: Optional[float] = None,
        **kwargs,
    ):
        self.timeout_seconds = timeout_seconds
        if timeout_seconds:
            message = f"{message} (timeout: {timeout_seconds}s)"
        super().__init__(message, **kwargs)


class RateLimitError(FederalAPIError):
    """Rate limit exceeded errors (HTTP 429)."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        **kwargs,
    ):
        self.retry_after = retry_after
        if retry_after:
            message = f"{message} (retry after: {retry_after}s)"
        super().__init__(message, status_code=429, **kwargs)


class AuthenticationError(FederalAPIError):
    """Authentication/authorization errors (HTTP 401, 403)."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, **kwargs)


class NotFoundError(FederalAPIError):
    """Resource not found errors (HTTP 404)."""

    def __init__(
        self,
        message: str = "Resource not found",
        resource_id: Optional[str] = None,
        **kwargs,
    ):
        self.resource_id = resource_id
        if resource_id:
            message = f"{message}: {resource_id}"
        super().__init__(message, status_code=404, **kwargs)


class ServerError(FederalAPIError):
    """Server-side errors (HTTP 5xx)."""

    def __init__(self, message: str = "Server error", **kwargs):
        super().__init__(message, **kwargs)


class ValidationError(FederalAPIError):
    """Data validation errors."""

    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        self.field = field
        if field:
            message = f"{message} (field: {field})"
        super().__init__(message, **kwargs)


class ParseError(FederalAPIError):
    """Response parsing errors."""

    def __init__(self, message: str = "Failed to parse response", **kwargs):
        super().__init__(message, **kwargs)


class CacheError(FederalAPIError):
    """Cache-related errors."""

    def __init__(self, message: str = "Cache operation failed", **kwargs):
        super().__init__(message, **kwargs)


# HTTP status code to exception mapping
HTTP_EXCEPTION_MAP = {
    400: ValidationError,
    401: AuthenticationError,
    403: AuthenticationError,
    404: NotFoundError,
    429: RateLimitError,
    500: ServerError,
    502: ServerError,
    503: ServerError,
    504: TimeoutError,
}


def exception_from_response(
    status_code: int,
    message: str,
    api_name: str = "Unknown",
    response_data: Optional[dict[str, Any]] = None,
) -> FederalAPIError:
    """
    Create appropriate exception from HTTP response.

    Args:
        status_code: HTTP status code
        message: Error message
        api_name: Name of the API
        response_data: Response data if available

    Returns:
        Appropriate exception instance
    """
    exception_class = HTTP_EXCEPTION_MAP.get(status_code, FederalAPIError)

    # Special handling for RateLimitError (429) - it defines status_code internally
    if status_code == 429:
        retry_after = response_data.get("retry_after") if response_data else None
        return exception_class(
            message,
            api_name=api_name,
            response_data=response_data,
            retry_after=retry_after,
        )

    # Special handling for NotFoundError (404) - it defines status_code internally
    if status_code == 404:
        return exception_class(message, api_name=api_name, response_data=response_data)

    # For all other exceptions, pass status_code
    return exception_class(
        message, api_name=api_name, status_code=status_code, response_data=response_data
    )
