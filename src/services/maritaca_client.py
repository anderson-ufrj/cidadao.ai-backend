"""
Module: services.maritaca_client
Description: Maritaca AI/Sabiá-3 API client for Brazilian Portuguese language models
Author: Anderson H. Silva
Date: 2025-01-19
License: Proprietary - All rights reserved
"""

import asyncio
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

import httpx
from pydantic import BaseModel, Field

from src.core import get_logger, json_utils
from src.core.exceptions import LLMError, LLMRateLimitError


class MaritacaModel(str, Enum):
    """Available Maritaca AI models."""

    SABIAZINHO_3 = "sabiazinho-3"  # Mais barato e eficiente
    SABIA_3 = "sabia-3"
    SABIA_3_MEDIUM = "sabia-3-medium"
    SABIA_3_LARGE = "sabia-3-large"


@dataclass
class MaritacaResponse:
    """Response from Maritaca AI API."""

    content: str
    model: str
    usage: dict[str, Any]
    metadata: dict[str, Any]
    response_time: float
    timestamp: datetime
    finish_reason: Optional[str] = None


class MaritacaMessage(BaseModel):
    """Message format for Maritaca AI."""

    role: str = Field(description="Message role (system, user, assistant)")
    content: str = Field(description="Message content")


class MaritacaRequest(BaseModel):
    """Request format for Maritaca AI."""

    messages: list[MaritacaMessage] = Field(description="Conversation messages")
    model: str = Field(default=MaritacaModel.SABIA_3, description="Model to use")
    temperature: float = Field(
        default=0.7, ge=0.0, le=2.0, description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=2048, ge=1, le=8192, description="Maximum tokens to generate"
    )
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="Top-p sampling")
    frequency_penalty: float = Field(
        default=0.0, ge=-2.0, le=2.0, description="Frequency penalty"
    )
    presence_penalty: float = Field(
        default=0.0, ge=-2.0, le=2.0, description="Presence penalty"
    )
    stream: bool = Field(default=False, description="Enable streaming response")
    stop: Optional[list[str]] = Field(default=None, description="Stop sequences")


class MaritacaClient:
    """
    Async client for Maritaca AI/Sabiá-3 API.

    This client provides:
    - Async/await support for all operations
    - Automatic retry with exponential backoff
    - Rate limit handling
    - Streaming support
    - Comprehensive error handling
    - Request/response logging
    - Circuit breaker pattern for resilience
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://chat.maritaca.ai/api",
        model: str = MaritacaModel.SABIAZINHO_3,
        timeout: int = 60,
        max_retries: int = 3,
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: int = 60,
    ):
        """
        Initialize Maritaca AI client.

        Args:
            api_key: API key for authentication
            base_url: Base URL for Maritaca AI API
            model: Default model to use
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries on failure
            circuit_breaker_threshold: Number of failures before circuit opens
            circuit_breaker_timeout: Time in seconds before circuit breaker resets
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = get_logger(__name__)

        # Circuit breaker state
        self._circuit_breaker_failures = 0
        self._circuit_breaker_threshold = circuit_breaker_threshold
        self._circuit_breaker_timeout = circuit_breaker_timeout
        self._circuit_breaker_opened_at: Optional[datetime] = None

        # HTTP client configuration
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(
                max_keepalive_connections=10, max_connections=20, keepalive_expiry=30.0
            ),
            headers={
                "User-Agent": "CidadaoAI/1.0.0 (Maritaca Client)",
                "Accept": "application/json",
                "Accept-Language": "pt-BR,pt;q=0.9",
            },
        )

        self.logger.info(
            "maritaca_client_initialized",
            base_url=base_url,
            model=model,
            timeout=timeout,
            max_retries=max_retries,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close HTTP client and cleanup resources."""
        await self.client.aclose()
        self.logger.info("maritaca_client_closed")

    async def shutdown(self):
        """Alias for close method for compatibility."""
        await self.close()

    def _check_circuit_breaker(self) -> bool:
        """
        Check if circuit breaker is open.

        Returns:
            True if circuit is open (requests should be blocked)
        """
        if self._circuit_breaker_opened_at:
            elapsed = (
                datetime.utcnow() - self._circuit_breaker_opened_at
            ).total_seconds()
            if elapsed >= self._circuit_breaker_timeout:
                # Reset circuit breaker
                self._circuit_breaker_failures = 0
                self._circuit_breaker_opened_at = None
                self.logger.info("circuit_breaker_reset")
                return False
            return True
        return False

    def _record_failure(self):
        """Record a failure for circuit breaker."""
        self._circuit_breaker_failures += 1
        if self._circuit_breaker_failures >= self._circuit_breaker_threshold:
            self._circuit_breaker_opened_at = datetime.utcnow()
            self.logger.warning(
                "circuit_breaker_opened",
                failures=self._circuit_breaker_failures,
                timeout=self._circuit_breaker_timeout,
            )

    def _record_success(self):
        """Record a success and reset failure count."""
        self._circuit_breaker_failures = 0

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        top_p: float = 0.9,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[list[str]] = None,
        stream: bool = False,
        **kwargs,
    ) -> Union[MaritacaResponse, AsyncGenerator[str, None]]:
        """
        Create a chat completion with Maritaca AI.

        Args:
            messages: List of conversation messages
            model: Model to use (defaults to client default)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            top_p: Top-p sampling parameter
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            presence_penalty: Presence penalty (-2.0 to 2.0)
            stop: List of stop sequences
            stream: Enable streaming response
            **kwargs: Additional parameters

        Returns:
            MaritacaResponse for non-streaming, AsyncGenerator for streaming

        Raises:
            LLMError: On API errors
            LLMRateLimitError: On rate limit exceeded
        """
        # Check circuit breaker
        if self._check_circuit_breaker():
            raise LLMError(
                "Circuit breaker is open due to repeated failures",
                details={
                    "provider": "maritaca",
                    "failures": self._circuit_breaker_failures,
                },
            )

        # Prepare request
        request = MaritacaRequest(
            messages=[
                MaritacaMessage(role=msg["role"], content=msg["content"])
                for msg in messages
            ],
            model=model or self.default_model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=stream,
            stop=stop,
        )

        # Log request
        self.logger.info(
            "maritaca_request_started",
            model=request.model,
            message_count=len(messages),
            stream=stream,
            max_tokens=max_tokens,
        )

        if stream:
            return self._stream_completion(request)
        else:
            return await self._complete(request)

    async def _complete(self, request: MaritacaRequest) -> MaritacaResponse:
        """
        Make a non-streaming completion request.

        Args:
            request: Maritaca request object

        Returns:
            MaritacaResponse with generated content
        """
        endpoint = "/chat/completions"
        data = request.model_dump(exclude_none=True)

        for attempt in range(self.max_retries + 1):
            try:
                start_time = datetime.utcnow()

                response = await self.client.post(
                    f"{self.base_url}{endpoint}", json=data, headers=self._get_headers()
                )

                response_time = (datetime.utcnow() - start_time).total_seconds()

                if response.status_code == 200:
                    self._record_success()
                    response_data = response.json()

                    # Parse response
                    choice = response_data["choices"][0]
                    content = choice["message"]["content"]

                    self.logger.info(
                        "maritaca_request_success",
                        model=request.model,
                        response_time=response_time,
                        tokens_used=response_data.get("usage", {}).get(
                            "total_tokens", 0
                        ),
                    )

                    return MaritacaResponse(
                        content=content,
                        model=response_data.get("model", request.model),
                        usage=response_data.get("usage", {}),
                        metadata={
                            "id": response_data.get("id"),
                            "created": response_data.get("created"),
                            "object": response_data.get("object"),
                        },
                        response_time=response_time,
                        timestamp=datetime.utcnow(),
                        finish_reason=choice.get("finish_reason"),
                    )

                elif response.status_code == 429:
                    # Rate limit exceeded
                    self._record_failure()
                    retry_after = int(response.headers.get("Retry-After", 60))

                    self.logger.warning(
                        "maritaca_rate_limit_exceeded",
                        retry_after=retry_after,
                        attempt=attempt + 1,
                    )

                    if attempt < self.max_retries:
                        await asyncio.sleep(retry_after)
                        continue

                    raise LLMRateLimitError(
                        "Maritaca AI rate limit exceeded",
                        details={"provider": "maritaca", "retry_after": retry_after},
                    )

                else:
                    # Other errors
                    self._record_failure()
                    error_msg = f"API request failed with status {response.status_code}"

                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get(
                            "message", error_msg
                        )
                    except:
                        error_msg += f": {response.text}"

                    self.logger.error(
                        "maritaca_request_failed",
                        status_code=response.status_code,
                        error=error_msg,
                        attempt=attempt + 1,
                    )

                    if attempt < self.max_retries:
                        await asyncio.sleep(2**attempt)
                        continue

                    raise LLMError(
                        error_msg,
                        details={
                            "provider": "maritaca",
                            "status_code": response.status_code,
                        },
                    )

            except httpx.TimeoutException:
                self._record_failure()
                self.logger.error(
                    "maritaca_request_timeout",
                    timeout=self.timeout,
                    attempt=attempt + 1,
                )

                if attempt < self.max_retries:
                    await asyncio.sleep(2**attempt)
                    continue

                raise LLMError(
                    f"Request timeout after {self.timeout} seconds",
                    details={"provider": "maritaca"},
                )

            except Exception as e:
                self._record_failure()
                self.logger.error(
                    "maritaca_request_error",
                    error=str(e),
                    error_type=type(e).__name__,
                    attempt=attempt + 1,
                )

                if attempt < self.max_retries:
                    await asyncio.sleep(2**attempt)
                    continue

                raise LLMError(
                    f"Unexpected error: {str(e)}",
                    details={"provider": "maritaca", "error_type": type(e).__name__},
                )

        # Should not reach here
        raise LLMError(
            f"Failed after {self.max_retries + 1} attempts",
            details={"provider": "maritaca"},
        )

    async def _stream_completion(
        self, request: MaritacaRequest
    ) -> AsyncGenerator[str, None]:
        """
        Make a streaming completion request.

        Args:
            request: Maritaca request object

        Yields:
            Text chunks as they are received
        """
        endpoint = "/chat/completions"
        data = request.model_dump(exclude_none=True)

        for attempt in range(self.max_retries + 1):
            try:
                self.logger.info(
                    "maritaca_stream_started", model=request.model, attempt=attempt + 1
                )

                async with self.client.stream(
                    "POST",
                    f"{self.base_url}{endpoint}",
                    json=data,
                    headers=self._get_headers(),
                ) as response:
                    if response.status_code == 200:
                        self._record_success()

                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:]  # Remove "data: " prefix

                                if data_str == "[DONE]":
                                    break

                                try:
                                    chunk_data = json_utils.loads(data_str)
                                    if (
                                        "choices" in chunk_data
                                        and chunk_data["choices"]
                                    ):
                                        delta = chunk_data["choices"][0].get(
                                            "delta", {}
                                        )
                                        if "content" in delta:
                                            yield delta["content"]
                                except json_utils.JSONDecodeError:
                                    self.logger.warning(
                                        "maritaca_stream_parse_error", data=data_str
                                    )
                                    continue

                        self.logger.info("maritaca_stream_completed")
                        return

                    elif response.status_code == 429:
                        # Rate limit in streaming mode
                        self._record_failure()
                        retry_after = int(response.headers.get("Retry-After", 60))

                        if attempt < self.max_retries:
                            await asyncio.sleep(retry_after)
                            continue

                        raise LLMRateLimitError(
                            "Maritaca AI rate limit exceeded during streaming",
                            details={
                                "provider": "maritaca",
                                "retry_after": retry_after,
                            },
                        )

                    else:
                        # Other streaming errors
                        self._record_failure()
                        error_text = await response.aread()

                        if attempt < self.max_retries:
                            await asyncio.sleep(2**attempt)
                            continue

                        raise LLMError(
                            f"Streaming failed with status {response.status_code}: {error_text}",
                            details={
                                "provider": "maritaca",
                                "status_code": response.status_code,
                            },
                        )

            except Exception as e:
                self._record_failure()
                self.logger.error(
                    "maritaca_stream_error",
                    error=str(e),
                    error_type=type(e).__name__,
                    attempt=attempt + 1,
                )

                if attempt < self.max_retries:
                    await asyncio.sleep(2**attempt)
                    continue

                raise LLMError(
                    f"Streaming error: {str(e)}",
                    details={"provider": "maritaca", "error_type": type(e).__name__},
                )

    async def chat(
        self, messages: list[Union[MaritacaMessage, dict[str, str]]], **kwargs
    ) -> MaritacaResponse:
        """
        Simplified chat method that accepts MaritacaMessage objects or dicts.

        Args:
            messages: List of MaritacaMessage objects or dicts with role/content
            **kwargs: Additional parameters passed to chat_completion

        Returns:
            MaritacaResponse with generated content
        """
        # Convert MaritacaMessage objects to dicts if needed
        msg_dicts = []
        for msg in messages:
            if isinstance(msg, MaritacaMessage):
                msg_dicts.append({"role": msg.role, "content": msg.content})
            elif isinstance(msg, dict):
                msg_dicts.append(msg)
            else:
                raise ValueError(f"Invalid message type: {type(msg)}")

        return await self.chat_completion(messages=msg_dicts, **kwargs)

    async def health_check(self) -> dict[str, Any]:
        """
        Check Maritaca AI API health.

        Returns:
            Health status information
        """
        try:
            # Make a minimal request to check API availability
            response = await self.chat_completion(
                messages=[{"role": "user", "content": "Olá"}],
                max_tokens=10,
                temperature=0.0,
            )

            return {
                "status": "healthy",
                "provider": "maritaca",
                "model": self.default_model,
                "circuit_breaker": (
                    "closed" if not self._check_circuit_breaker() else "open"
                ),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "maritaca",
                "model": self.default_model,
                "circuit_breaker": (
                    "closed" if not self._check_circuit_breaker() else "open"
                ),
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Factory function for easy client creation
def create_maritaca_client(
    api_key: str, model: str = MaritacaModel.SABIAZINHO_3, **kwargs
) -> MaritacaClient:
    """
    Create a Maritaca AI client with specified configuration.

    Args:
        api_key: Maritaca AI API key
        model: Default model to use
        **kwargs: Additional configuration options

    Returns:
        Configured MaritacaClient instance
    """
    return MaritacaClient(api_key=api_key, model=model, **kwargs)
