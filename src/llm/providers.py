"""
Module: llm.providers
Description: LLM provider integrations for Groq, Together AI, and Hugging Face
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

import httpx
from pydantic import BaseModel
from pydantic import Field as PydanticField

from src.core import get_llm_pool, get_logger, settings
from src.core.exceptions import LLMError, LLMRateLimitError
from src.core.json_utils import loads
from src.services.maritaca_client import MaritacaClient


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    GROQ = "groq"
    TOGETHER = "together"
    HUGGINGFACE = "huggingface"
    MARITACA = "maritaca"


@dataclass
class LLMResponse:
    """Response from LLM provider."""

    content: str
    provider: str
    model: str
    usage: dict[str, Any]
    metadata: dict[str, Any]
    response_time: float
    timestamp: datetime


class LLMRequest(BaseModel):
    """Request for LLM inference."""

    messages: list[dict[str, str]] = PydanticField(description="Conversation messages")
    system_prompt: Optional[str] = PydanticField(
        default=None, description="System prompt"
    )
    temperature: float = PydanticField(
        default=0.7, ge=0.0, le=2.0, description="Sampling temperature"
    )
    max_tokens: int = PydanticField(
        default=2048, ge=1, le=32768, description="Maximum tokens to generate"
    )
    top_p: float = PydanticField(
        default=0.9, ge=0.0, le=1.0, description="Top-p sampling"
    )
    stream: bool = PydanticField(default=False, description="Enable streaming response")
    model: Optional[str] = PydanticField(
        default=None, description="Specific model to use"
    )


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        default_model: str,
        timeout: int = 60,
        max_retries: int = 3,
    ):
        """
        Initialize LLM provider.

        Args:
            api_key: API key for authentication
            base_url: Base URL for API endpoints
            default_model: Default model to use
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = get_logger(__name__)
        self._use_pool = True  # Flag to use connection pool

        # Legacy client for backward compatibility
        self.client = None

    async def __aenter__(self):
        """Async context manager entry."""
        # Initialize legacy client if not using pool
        if not self._use_pool and not self.client:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()

    @abstractmethod
    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Complete a text generation request."""
        pass

    @abstractmethod
    async def stream_complete(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream a text generation request."""
        pass

    @abstractmethod
    def _prepare_request_data(self, request: LLMRequest) -> dict[str, Any]:
        """Prepare request data for the specific provider."""
        pass

    @abstractmethod
    def _parse_response(
        self, response_data: dict[str, Any], response_time: float
    ) -> LLMResponse:
        """Parse response data from the specific provider."""
        pass

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "CidadaoAI/1.0.0",
        }

    async def _make_request(
        self, endpoint: str, data: dict[str, Any], stream: bool = False
    ) -> Union[dict[str, Any], AsyncGenerator[dict[str, Any], None]]:
        """Make HTTP request with retry logic."""
        if stream:
            # Return async generator for streaming
            return self._stream_request(endpoint, data)
        else:
            # Return regular result for non-streaming
            return await self._non_stream_request(endpoint, data)

    async def _non_stream_request(
        self, endpoint: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Make non-streaming HTTP request."""
        # Use connection pool if available
        if self._use_pool and hasattr(self, "_provider_name"):
            try:
                pool = await get_llm_pool()
                result = await pool.post(self._provider_name, endpoint, data)
                return result
            except Exception as e:
                self.logger.warning(
                    f"Pool request failed, falling back to regular client: {e}"
                )

        # Original implementation for fallback
        if not self.client:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
            )

        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        for attempt in range(self.max_retries + 1):
            try:
                start_time = datetime.utcnow()

                self.logger.info(
                    "llm_request_started",
                    provider=self.__class__.__name__,
                    url=url,
                    attempt=attempt + 1,
                    stream=False,
                )

                response = await self.client.post(
                    url,
                    json=data,
                    headers=headers,
                )

                if response.status_code == 200:
                    response_time = (datetime.utcnow() - start_time).total_seconds()

                    self.logger.info(
                        "llm_request_success",
                        provider=self.__class__.__name__,
                        response_time=response_time,
                    )

                    return loads(response.content)
                else:
                    await self._handle_error_response(response, attempt)

            except httpx.TimeoutException:
                self.logger.error(
                    "llm_request_timeout",
                    provider=self.__class__.__name__,
                    timeout=self.timeout,
                    attempt=attempt + 1,
                )

                if attempt < self.max_retries:
                    await asyncio.sleep(2**attempt)
                    continue

                raise LLMError(
                    f"Request timeout after {self.timeout} seconds",
                    details={"provider": self.__class__.__name__},
                )

            except Exception as e:
                self.logger.error(
                    "llm_request_error",
                    provider=self.__class__.__name__,
                    error=str(e),
                    attempt=attempt + 1,
                )

                if attempt < self.max_retries:
                    await asyncio.sleep(2**attempt)
                    continue

                raise LLMError(
                    f"Unexpected error: {str(e)}",
                    details={"provider": self.__class__.__name__},
                )

        raise LLMError(
            f"Failed after {self.max_retries + 1} attempts",
            details={"provider": self.__class__.__name__},
        )

    async def _stream_request(
        self, endpoint: str, data: dict[str, Any]
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Make streaming HTTP request."""
        if not self.client:
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.timeout),
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
            )

        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()

        for attempt in range(self.max_retries + 1):
            try:
                self.logger.info(
                    "llm_stream_request_started",
                    provider=self.__class__.__name__,
                    url=url,
                    attempt=attempt + 1,
                )

                async with self.client.stream(
                    "POST",
                    url,
                    json=data,
                    headers=headers,
                ) as response:
                    if response.status_code == 200:
                        async for chunk in self._process_stream_response(response):
                            yield chunk
                        return
                    else:
                        await self._handle_error_response(response, attempt)

            except httpx.TimeoutException:
                self.logger.error(
                    "llm_stream_timeout",
                    provider=self.__class__.__name__,
                    timeout=self.timeout,
                    attempt=attempt + 1,
                )

                if attempt < self.max_retries:
                    await asyncio.sleep(2**attempt)
                    continue

                raise LLMError(
                    f"Stream request timeout after {self.timeout} seconds",
                    details={"provider": self.__class__.__name__},
                )

            except Exception as e:
                self.logger.error(
                    "llm_stream_error",
                    provider=self.__class__.__name__,
                    error=str(e),
                    attempt=attempt + 1,
                )

                if attempt < self.max_retries:
                    await asyncio.sleep(2**attempt)
                    continue

                raise LLMError(
                    f"Stream error: {str(e)}",
                    details={"provider": self.__class__.__name__},
                )

        raise LLMError(
            f"Stream failed after {self.max_retries + 1} attempts",
            details={"provider": self.__class__.__name__},
        )

    async def _handle_error_response(self, response: httpx.Response, attempt: int):
        """Handle error responses from the API."""
        if response.status_code == 429:
            # Rate limit exceeded
            retry_after = int(response.headers.get("Retry-After", 60))

            self.logger.warning(
                "llm_rate_limit_exceeded",
                provider=self.__class__.__name__,
                retry_after=retry_after,
                attempt=attempt + 1,
            )

            if attempt < self.max_retries:
                await asyncio.sleep(retry_after)
                return

            raise LLMRateLimitError(
                "Rate limit exceeded",
                details={
                    "provider": self.__class__.__name__,
                    "retry_after": retry_after,
                },
            )

        else:
            error_msg = f"API request failed with status {response.status_code}"

            try:
                error_data = response.json()
                error_msg += f": {error_data}"
            except:
                error_msg += f": {response.text}"

            self.logger.error(
                "llm_request_failed",
                provider=self.__class__.__name__,
                status_code=response.status_code,
                error=error_msg,
                attempt=attempt + 1,
            )

            if attempt < self.max_retries:
                await asyncio.sleep(2**attempt)
                return

            raise LLMError(error_msg, details={"provider": self.__class__.__name__})

    async def _process_stream_response(
        self, response: httpx.Response
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Process streaming response."""
        async for chunk in response.aiter_lines():
            if chunk.startswith("data: "):
                data = chunk[6:]  # Remove "data: " prefix
                if data == "[DONE]":
                    break
                try:
                    yield loads(data)  # Parse JSON chunk safely with orjson
                except:
                    continue


class GroqProvider(BaseLLMProvider):
    """Groq LLM provider implementation."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq provider."""
        if api_key:
            actual_api_key = api_key
        elif settings.groq_api_key:
            actual_api_key = settings.groq_api_key.get_secret_value()
        else:
            actual_api_key = "gsk-test-dummy-key"  # Dummy key for testing

        super().__init__(
            api_key=actual_api_key,
            base_url=settings.groq_api_base_url,
            default_model="mixtral-8x7b-32768",
            timeout=30,  # Reduced from 60s to 30s for faster failure
            max_retries=2,  # Reduced from 3 to 2 for faster failure
        )
        self._provider_name = "groq"

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Complete text generation using Groq."""
        data = self._prepare_request_data(request)
        start_time = datetime.utcnow()

        response_data = await self._make_request("/chat/completions", data)
        response_time = (datetime.utcnow() - start_time).total_seconds()

        return self._parse_response(response_data, response_time)

    async def stream_complete(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream text generation using Groq."""
        data = self._prepare_request_data(request)
        data["stream"] = True

        async for chunk in self._make_request("/chat/completions", data, stream=True):
            if "choices" in chunk and chunk["choices"]:
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta:
                    yield delta["content"]

    def _prepare_request_data(self, request: LLMRequest) -> dict[str, Any]:
        """Prepare request data for Groq API."""
        messages = []

        # Add system prompt if provided
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        # Add conversation messages
        messages.extend(request.messages)

        return {
            "model": request.model or self.default_model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "stream": request.stream,
        }

    def _parse_response(
        self, response_data: dict[str, Any], response_time: float
    ) -> LLMResponse:
        """Parse Groq API response."""
        choice = response_data["choices"][0]
        content = choice["message"]["content"]
        usage = response_data.get("usage", {})

        return LLMResponse(
            content=content,
            provider="groq",
            model=response_data.get("model", self.default_model),
            usage=usage,
            metadata={
                "finish_reason": choice.get("finish_reason"),
                "response_id": response_data.get("id"),
            },
            response_time=response_time,
            timestamp=datetime.utcnow(),
        )


class TogetherProvider(BaseLLMProvider):
    """Together AI provider implementation."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Together AI provider."""
        if api_key:
            actual_api_key = api_key
        elif settings.together_api_key:
            actual_api_key = settings.together_api_key.get_secret_value()
        else:
            actual_api_key = "together-test-dummy-key"  # Dummy key for testing

        super().__init__(
            api_key=actual_api_key,
            base_url=settings.together_api_base_url,
            default_model="meta-llama/Llama-2-70b-chat-hf",
            timeout=60,
            max_retries=3,
        )

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Complete text generation using Together AI."""
        data = self._prepare_request_data(request)
        start_time = datetime.utcnow()

        response_data = await self._make_request("/chat/completions", data)
        response_time = (datetime.utcnow() - start_time).total_seconds()

        return self._parse_response(response_data, response_time)

    async def stream_complete(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream text generation using Together AI."""
        data = self._prepare_request_data(request)
        data["stream"] = True

        async for chunk in self._make_request("/chat/completions", data, stream=True):
            if "choices" in chunk and chunk["choices"]:
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta:
                    yield delta["content"]

    def _prepare_request_data(self, request: LLMRequest) -> dict[str, Any]:
        """Prepare request data for Together AI API."""
        messages = []

        # Add system prompt if provided
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        # Add conversation messages
        messages.extend(request.messages)

        return {
            "model": request.model or self.default_model,
            "messages": messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "top_p": request.top_p,
            "stream": request.stream,
        }

    def _parse_response(
        self, response_data: dict[str, Any], response_time: float
    ) -> LLMResponse:
        """Parse Together AI response."""
        choice = response_data["choices"][0]
        content = choice["message"]["content"]
        usage = response_data.get("usage", {})

        return LLMResponse(
            content=content,
            provider="together",
            model=response_data.get("model", self.default_model),
            usage=usage,
            metadata={
                "finish_reason": choice.get("finish_reason"),
                "response_id": response_data.get("id"),
            },
            response_time=response_time,
            timestamp=datetime.utcnow(),
        )


class HuggingFaceProvider(BaseLLMProvider):
    """Hugging Face provider implementation."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Hugging Face provider."""
        if api_key:
            actual_api_key = api_key
        elif settings.huggingface_api_key:
            actual_api_key = settings.huggingface_api_key.get_secret_value()
        else:
            actual_api_key = "hf-test-dummy-key"  # Dummy key for testing

        super().__init__(
            api_key=actual_api_key,
            base_url="https://api-inference.huggingface.co",
            default_model="mistralai/Mistral-7B-Instruct-v0.2",
            timeout=60,
            max_retries=3,
        )

    def _get_headers(self) -> dict[str, str]:
        """Get headers for Hugging Face API."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "CidadaoAI/1.0.0",
        }

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Complete text generation using Hugging Face."""
        data = self._prepare_request_data(request)
        start_time = datetime.utcnow()

        model = request.model or self.default_model
        endpoint = f"/models/{model}"

        response_data = await self._make_request(endpoint, data)
        response_time = (datetime.utcnow() - start_time).total_seconds()

        return self._parse_response(response_data, response_time, model)

    async def stream_complete(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream text generation (not supported by Hugging Face Inference API)."""
        # Hugging Face Inference API doesn't support streaming
        # Fall back to regular completion
        response = await self.complete(request)
        yield response.content

    def _prepare_request_data(self, request: LLMRequest) -> dict[str, Any]:
        """Prepare request data for Hugging Face API."""
        # Combine system prompt and messages into a single prompt
        prompt = ""

        if request.system_prompt:
            prompt += f"System: {request.system_prompt}\n\n"

        for message in request.messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            prompt += f"{role.title()}: {content}\n"

        prompt += "Assistant: "

        return {
            "inputs": prompt,
            "parameters": {
                "temperature": request.temperature,
                "max_new_tokens": request.max_tokens,
                "top_p": request.top_p,
                "return_full_text": False,
            },
        }

    def _parse_response(
        self, response_data: dict[str, Any], response_time: float, model: str
    ) -> LLMResponse:
        """Parse Hugging Face response."""
        if isinstance(response_data, list) and response_data:
            content = response_data[0].get("generated_text", "")
        else:
            content = response_data.get("generated_text", "")

        return LLMResponse(
            content=content,
            provider="huggingface",
            model=model,
            usage={
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },  # Not provided by HF
            metadata={
                "finish_reason": "stop",
                "model_status": "loaded",
            },
            response_time=response_time,
            timestamp=datetime.utcnow(),
        )


class MaritacaProvider(BaseLLMProvider):
    """Maritaca AI provider implementation."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Maritaca AI provider."""
        # We don't use the base class init for Maritaca since it has its own client
        self.logger = get_logger(__name__)

        if api_key:
            self.api_key = api_key
        elif settings.maritaca_api_key:
            self.api_key = settings.maritaca_api_key.get_secret_value()
        else:
            # Use a dummy key for testing/development
            self.api_key = "sk-test-dummy-key"
            self.logger.warning(
                "No Maritaca API key configured. Using dummy key for testing. "
                "Set MARITACA_API_KEY environment variable for production use."
            )
        self.default_model = settings.maritaca_model

        # Create Maritaca client with shorter timeout
        self.maritaca_client = MaritacaClient(
            api_key=self.api_key,
            base_url=settings.maritaca_api_base_url,
            model=self.default_model,
            timeout=30,  # Reduced from 60s to 30s for faster failure
            max_retries=2,  # Reduced from 3 to 2 for faster failure
        )

    async def __aenter__(self):
        """Async context manager entry."""
        await self.maritaca_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.maritaca_client.__aexit__(exc_type, exc_val, exc_tb)

    async def close(self):
        """Close Maritaca client."""
        await self.maritaca_client.close()

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Complete text generation using Maritaca AI."""
        messages = self._prepare_messages(request)

        response = await self.maritaca_client.chat_completion(
            messages=messages,
            model=request.model or self.default_model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            top_p=request.top_p,
            stream=False,
        )

        return LLMResponse(
            content=response.content,
            provider="maritaca",
            model=response.model,
            usage=response.usage,
            metadata=response.metadata,
            response_time=response.response_time,
            timestamp=response.timestamp,
        )

    async def stream_complete(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Stream text generation using Maritaca AI."""
        # Note: Maritaca client doesn't support streaming yet
        # Fall back to regular completion and yield the result
        response = await self.complete(request)
        yield response.content

    def _prepare_messages(self, request: LLMRequest) -> list[dict[str, str]]:
        """Prepare messages for Maritaca API."""
        messages = []

        # Add system prompt if provided
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        # Add conversation messages
        messages.extend(request.messages)

        return messages

    def _prepare_request_data(self, request: LLMRequest) -> dict[str, Any]:
        """Not used for Maritaca - using direct client instead."""
        pass

    def _parse_response(
        self, response_data: dict[str, Any], response_time: float
    ) -> LLMResponse:
        """Not used for Maritaca - using direct client instead."""
        pass


class LLMManager:
    """Manager for multiple LLM providers with fallback support."""

    def __init__(
        self,
        primary_provider: LLMProvider = LLMProvider.GROQ,
        fallback_providers: Optional[list[LLMProvider]] = None,
        enable_fallback: bool = True,
    ):
        """
        Initialize LLM manager.

        Args:
            primary_provider: Primary LLM provider to use
            fallback_providers: List of fallback providers
            enable_fallback: Enable automatic fallback on errors
        """
        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers or [
            LLMProvider.TOGETHER,
            LLMProvider.HUGGINGFACE,
            LLMProvider.MARITACA,
        ]
        self.enable_fallback = enable_fallback
        self.logger = get_logger(__name__)

        # Provider instances
        self.providers = {
            LLMProvider.GROQ: GroqProvider(),
            LLMProvider.TOGETHER: TogetherProvider(),
            LLMProvider.HUGGINGFACE: HuggingFaceProvider(),
            LLMProvider.MARITACA: MaritacaProvider(),
        }

        self.logger.info(
            "llm_manager_initialized",
            primary_provider=primary_provider,
            fallback_providers=fallback_providers,
            enable_fallback=enable_fallback,
        )

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """
        Complete text generation with fallback support.

        Args:
            request: LLM request

        Returns:
            LLM response
        """
        providers_to_try = [self.primary_provider]
        if self.enable_fallback:
            providers_to_try.extend(self.fallback_providers)

        last_error = None

        for provider in providers_to_try:
            try:
                self.logger.info(
                    "llm_completion_attempt",
                    provider=provider,
                    primary=provider == self.primary_provider,
                )

                async with self.providers[provider] as llm:
                    response = await llm.complete(request)

                    self.logger.info(
                        "llm_completion_success",
                        provider=provider,
                        response_time=response.response_time,
                        tokens_used=response.usage.get("total_tokens", 0),
                    )

                    return response

            except Exception as e:
                last_error = e
                self.logger.warning(
                    "llm_completion_failed",
                    provider=provider,
                    error=str(e),
                    fallback_available=len(providers_to_try) > 1,
                )

                if not self.enable_fallback or provider == providers_to_try[-1]:
                    break

                continue

        # All providers failed
        self.logger.error(
            "llm_all_providers_failed",
            providers_tried=providers_to_try,
            last_error=str(last_error),
        )

        raise LLMError(
            f"All LLM providers failed. Last error: {str(last_error)}",
            details={"provider": "all"},
        )

    async def stream_complete(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """
        Stream text generation with fallback support.

        Args:
            request: LLM request

        Yields:
            Text chunks
        """
        providers_to_try = [self.primary_provider]
        if self.enable_fallback:
            providers_to_try.extend(self.fallback_providers)

        last_error = None

        for provider in providers_to_try:
            try:
                self.logger.info(
                    "llm_stream_attempt",
                    provider=provider,
                    primary=provider == self.primary_provider,
                )

                async with self.providers[provider] as llm:
                    async for chunk in llm.stream_complete(request):
                        yield chunk
                    return

            except Exception as e:
                last_error = e
                self.logger.warning(
                    "llm_stream_failed",
                    provider=provider,
                    error=str(e),
                    fallback_available=len(providers_to_try) > 1,
                )

                if not self.enable_fallback or provider == providers_to_try[-1]:
                    break

                continue

        # All providers failed
        self.logger.error(
            "llm_stream_all_providers_failed",
            providers_tried=providers_to_try,
            last_error=str(last_error),
        )

        raise LLMError(
            f"All LLM providers failed for streaming. Last error: {str(last_error)}",
            details={"provider": "all"},
        )

    async def close(self):
        """Close all provider connections."""
        for provider in self.providers.values():
            await provider.close()


# Factory function for easy LLM manager creation
def create_llm_manager(
    primary_provider: str = "groq", enable_fallback: bool = True, **kwargs
) -> LLMManager:
    """
    Create LLM manager with specified configuration.

    Args:
        primary_provider: Primary provider name
        enable_fallback: Enable fallback providers
        **kwargs: Additional configuration

    Returns:
        Configured LLM manager
    """
    provider_enum = LLMProvider(primary_provider.lower())

    return LLMManager(
        primary_provider=provider_enum, enable_fallback=enable_fallback, **kwargs
    )
