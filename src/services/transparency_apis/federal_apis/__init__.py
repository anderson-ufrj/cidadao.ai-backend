"""
Federal Government APIs Module

This module provides clients for federal government data sources:
- IBGE (Brazilian Institute of Geography and Statistics)
- DataSUS (Health Ministry data)
- INEP (Education data)

Plus common utilities:
- Custom exceptions for error handling
- Retry logic with exponential backoff

Author: Anderson Henrique da Silva
Created: 2025-10-12
License: Proprietary - All rights reserved
"""

from .ibge_client import IBGEClient
from .datasus_client import DataSUSClient
from .inep_client import INEPClient

# Exceptions
from .exceptions import (
    FederalAPIError,
    NetworkError,
    TimeoutError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    ServerError,
    ValidationError,
    ParseError,
    CacheError,
    exception_from_response,
)

# Retry utilities
from .retry import (
    retry_with_backoff,
    retry_on_network_error,
    retry_on_server_error,
    aggressive_retry,
    RetryContext,
    calculate_backoff,
    should_retry_exception,
)

__all__ = [
    # Clients
    "IBGEClient",
    "DataSUSClient",
    "INEPClient",
    # Exceptions
    "FederalAPIError",
    "NetworkError",
    "TimeoutError",
    "RateLimitError",
    "AuthenticationError",
    "NotFoundError",
    "ServerError",
    "ValidationError",
    "ParseError",
    "CacheError",
    "exception_from_response",
    # Retry utilities
    "retry_with_backoff",
    "retry_on_network_error",
    "retry_on_server_error",
    "aggressive_retry",
    "RetryContext",
    "calculate_backoff",
    "should_retry_exception",
]
