"""
Federal Government APIs Module

This module provides clients for federal government data sources:
- IBGE (Brazilian Institute of Geography and Statistics)
- DataSUS (Health Ministry data)
- INEP (Education data)
- SICONFI (Tesouro Nacional - fiscal and accounting data)

Plus common utilities:
- Custom exceptions for error handling
- Retry logic with exponential backoff

Author: Anderson Henrique da Silva
Created: 2025-10-12
License: Proprietary - All rights reserved
"""

from .datasus_client import DataSUSClient

# Exceptions
from .exceptions import (
    AuthenticationError,
    CacheError,
    FederalAPIError,
    NetworkError,
    NotFoundError,
    ParseError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
    exception_from_response,
)
from .ibge_client import IBGEClient
from .inep_client import INEPClient

# Retry utilities
from .retry import (
    RetryContext,
    aggressive_retry,
    calculate_backoff,
    retry_on_network_error,
    retry_on_server_error,
    retry_with_backoff,
    should_retry_exception,
)
from .siconfi_client import SICONFIClient

__all__ = [
    # Clients
    "IBGEClient",
    "DataSUSClient",
    "INEPClient",
    "SICONFIClient",
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
