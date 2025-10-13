"""
Base Transparency API Client

Abstract base class for all transparency API integrations.
Provides common functionality for HTTP requests, rate limiting,
circuit breaker, and error handling.

Author: Anderson Henrique da Silva
Created: 2025-10-09 14:16:00 -03 (Minas Gerais, Brazil)
License: Proprietary - All rights reserved
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Optional

import httpx

from src.core import get_logger


class TransparencyAPIClient(ABC):
    """
    Abstract base class for transparency API clients.

    All API clients (federal, state, TCE) should inherit from this class
    and implement the required abstract methods.
    """

    def __init__(
        self,
        base_url: str,
        name: str,
        rate_limit_per_minute: int = 100,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        """
        Initialize transparency API client.

        Args:
            base_url: Base URL for the API
            name: Name of the API (for logging)
            rate_limit_per_minute: Maximum requests per minute
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries on failure
        """
        self.base_url = base_url.rstrip("/")
        self.name = name
        self.rate_limit = rate_limit_per_minute
        self.timeout = timeout
        self.max_retries = max_retries

        self.logger = get_logger(f"transparency_api.{name}")

        # Rate limiting state
        self._request_timestamps: list[datetime] = []
        self._rate_limit_lock = asyncio.Lock()

        # Circuit breaker state
        self._failure_count = 0
        self._circuit_open = False
        self._circuit_open_until: Optional[datetime] = None

        self.logger.info(
            f"Initialized {name} API client",
            base_url=base_url,
            rate_limit=rate_limit_per_minute,
        )

    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test if the API is accessible.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_contracts(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Get contracts from the API.

        Args:
            start_date: Start date for filtering (YYYY-MM-DD)
            end_date: End date for filtering (YYYY-MM-DD)
            **kwargs: Additional API-specific parameters

        Returns:
            List of contract dictionaries
        """
        pass

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Make HTTP request with rate limiting and circuit breaker.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
            headers: HTTP headers

        Returns:
            Response JSON data

        Raises:
            Exception: If request fails after all retries
        """
        # Check circuit breaker
        if self._circuit_open:
            if datetime.utcnow() < self._circuit_open_until:
                raise Exception(f"Circuit breaker open for {self.name} API")
            else:
                # Reset circuit breaker
                self._circuit_open = False
                self._failure_count = 0
                self.logger.info(f"Circuit breaker reset for {self.name}")

        # Rate limiting
        await self._wait_for_rate_limit()

        # Build URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Make request with retries
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.request(
                        method=method, url=url, params=params, headers=headers
                    )

                    response.raise_for_status()

                    # Success - reset failure count
                    self._failure_count = 0

                    return response.json()

            except Exception as e:
                self._failure_count += 1

                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2**attempt
                    self.logger.warning(
                        f"Request failed, retrying in {wait_time}s",
                        attempt=attempt + 1,
                        error=str(e),
                    )
                    await asyncio.sleep(wait_time)
                else:
                    # Max retries reached
                    self.logger.error(
                        f"Request failed after {self.max_retries} attempts",
                        url=url,
                        error=str(e),
                    )

                    # Open circuit breaker if too many failures
                    if self._failure_count >= 5:
                        self._circuit_open = True
                        self._circuit_open_until = datetime.utcnow() + timedelta(
                            minutes=5
                        )
                        self.logger.error(f"Circuit breaker opened for {self.name}")

                    raise

    async def _wait_for_rate_limit(self) -> None:
        """Wait if rate limit would be exceeded."""
        async with self._rate_limit_lock:
            now = datetime.utcnow()

            # Remove timestamps older than 1 minute
            self._request_timestamps = [
                ts for ts in self._request_timestamps if (now - ts).total_seconds() < 60
            ]

            # Check if we need to wait
            if len(self._request_timestamps) >= self.rate_limit:
                # Calculate wait time
                oldest = self._request_timestamps[0]
                wait_seconds = 60 - (now - oldest).total_seconds()

                if wait_seconds > 0:
                    self.logger.debug(
                        f"Rate limit reached, waiting {wait_seconds:.1f}s"
                    )
                    await asyncio.sleep(wait_seconds)

                    # Remove oldest timestamp
                    self._request_timestamps.pop(0)

            # Add current timestamp
            self._request_timestamps.append(now)
