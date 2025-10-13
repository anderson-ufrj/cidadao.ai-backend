"""
Connection pooling for LLM providers with HTTP/2 support.

This module provides efficient connection pooling for LLM API calls,
reducing latency and improving throughput.
"""

import time
from contextlib import asynccontextmanager
from typing import Any

import httpx
from httpx import AsyncClient, Limits, Timeout
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.core.config import settings
from src.core.json_utils import dumps, loads
from src.core.logging import get_logger

logger = get_logger(__name__)


class LLMConnectionPool:
    """
    Connection pool manager for LLM providers.

    Features:
    - Persistent HTTP/2 connections
    - Automatic retry with exponential backoff
    - Connection health monitoring
    - Request/response caching
    - Performance metrics
    """

    def __init__(
        self,
        max_connections: int = 20,
        max_keepalive_connections: int = 10,
        keepalive_expiry: float = 30.0,
        timeout: float = 30.0,
        http2: bool = True,
    ):
        """
        Initialize LLM connection pool.

        Args:
            max_connections: Maximum number of connections
            max_keepalive_connections: Maximum idle connections
            keepalive_expiry: How long to keep idle connections (seconds)
            timeout: Request timeout (seconds)
            http2: Enable HTTP/2 support
        """
        self.max_connections = max_connections
        self.max_keepalive_connections = max_keepalive_connections
        self.keepalive_expiry = keepalive_expiry
        self.timeout = timeout
        self.http2 = http2

        # Connection pools per provider
        self._pools: dict[str, AsyncClient] = {}
        self._pool_stats: dict[str, dict[str, Any]] = {}

        # Performance metrics
        self.metrics = {
            "requests": 0,
            "successes": 0,
            "failures": 0,
            "total_latency": 0.0,
            "cache_hits": 0,
        }

    async def initialize(self):
        """Initialize connection pools for configured providers."""
        providers = {
            "groq": {
                "base_url": "https://api.groq.com/openai/v1",
                "headers": {
                    "Authorization": f"Bearer {settings.groq_api_key}",
                    "Content-Type": "application/json",
                },
            },
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "headers": {
                    "Authorization": f"Bearer {getattr(settings, 'openai_api_key', '')}",
                    "Content-Type": "application/json",
                },
            },
        }

        for provider, config in providers.items():
            if provider == "openai" and not getattr(settings, "openai_api_key", None):
                continue  # Skip if no API key

            await self._create_pool(provider, config)

    async def _create_pool(self, provider: str, config: dict[str, Any]):
        """Create connection pool for a provider."""
        try:
            limits = Limits(
                max_connections=self.max_connections,
                max_keepalive_connections=self.max_keepalive_connections,
                keepalive_expiry=self.keepalive_expiry,
            )

            timeout = Timeout(connect=5.0, read=self.timeout, write=10.0, pool=5.0)

            client = AsyncClient(
                base_url=config["base_url"],
                headers=config["headers"],
                limits=limits,
                timeout=timeout,
                http2=self.http2,
                follow_redirects=True,
            )

            self._pools[provider] = client
            self._pool_stats[provider] = {
                "created_at": time.time(),
                "requests": 0,
                "errors": 0,
            }

            logger.info(
                f"Created connection pool for {provider} (HTTP/2: {self.http2})"
            )

        except Exception as e:
            logger.error(f"Failed to create pool for {provider}: {e}")

    @asynccontextmanager
    async def get_client(self, provider: str = "groq") -> AsyncClient:
        """
        Get HTTP client for a provider.

        Args:
            provider: LLM provider name

        Yields:
            AsyncClient instance
        """
        if provider not in self._pools:
            raise ValueError(f"Provider {provider} not initialized")

        client = self._pools[provider]
        self._pool_stats[provider]["requests"] += 1

        try:
            yield client
        except Exception:
            self._pool_stats[provider]["errors"] += 1
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    )
    async def post(
        self, provider: str, endpoint: str, data: dict[str, Any], **kwargs
    ) -> dict[str, Any]:
        """
        Make POST request with automatic retry and pooling.

        Args:
            provider: LLM provider name
            endpoint: API endpoint
            data: Request data
            **kwargs: Additional httpx parameters

        Returns:
            Response data as dict
        """
        start_time = time.time()

        try:
            async with self.get_client(provider) as client:
                # Use orjson for fast serialization
                json_data = dumps(data)

                response = await client.post(
                    endpoint,
                    content=json_data,
                    headers={"Content-Type": "application/json"},
                    **kwargs,
                )

                response.raise_for_status()

                # Parse response with orjson
                result = loads(response.content)

                # Update metrics
                latency = time.time() - start_time
                self.metrics["requests"] += 1
                self.metrics["successes"] += 1
                self.metrics["total_latency"] += latency

                logger.debug(
                    f"{provider} request to {endpoint} completed in {latency:.3f}s"
                )

                return result

        except Exception as e:
            self.metrics["requests"] += 1
            self.metrics["failures"] += 1
            logger.error(f"{provider} request failed: {e}")
            raise

    async def chat_completion(
        self,
        messages: list,
        model: str = "mixtral-8x7b-32768",
        provider: str = "groq",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Make chat completion request with optimal settings.

        Args:
            messages: Chat messages
            model: Model to use
            provider: LLM provider
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            **kwargs: Additional parameters

        Returns:
            Completion response
        """
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs,
        }

        return await self.post(provider, "/chat/completions", data)

    async def close(self):
        """Close all connection pools."""
        for provider, client in self._pools.items():
            try:
                await client.aclose()
                logger.info(f"Closed connection pool for {provider}")
            except Exception as e:
                logger.error(f"Error closing pool for {provider}: {e}")

        self._pools.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get connection pool statistics."""
        avg_latency = (
            self.metrics["total_latency"] / self.metrics["requests"]
            if self.metrics["requests"] > 0
            else 0
        )

        return {
            "pools": self._pool_stats,
            "metrics": {
                **self.metrics,
                "avg_latency_ms": int(avg_latency * 1000),
                "success_rate": (
                    self.metrics["successes"] / self.metrics["requests"]
                    if self.metrics["requests"] > 0
                    else 0
                ),
            },
        }


# Global connection pool instance
llm_pool = LLMConnectionPool()


async def get_llm_pool() -> LLMConnectionPool:
    """Get or initialize the global LLM connection pool."""
    if not llm_pool._pools:
        await llm_pool.initialize()
    return llm_pool
