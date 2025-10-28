"""
Direct Maritaca.ai Chat Service
Provides direct access to Maritaca.ai language models for conversational AI.
Useful for testing, benchmarking, and potential partnership demonstrations.
"""

import time
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field

from src.core import get_logger
from src.core.config import get_settings

logger = get_logger(__name__)


class MaritacaMessage(BaseModel):
    """Single message in Maritaca chat format."""

    role: Literal["system", "user", "assistant"]
    content: str


class MaritacaChatRequest(BaseModel):
    """Request for direct Maritaca.ai chat."""

    messages: list[MaritacaMessage]
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=8192)
    stream: bool = Field(default=False)
    model: str | None = Field(
        default=None, description="Override default model (sabiazinho-3)"
    )


class MaritacaChatResponse(BaseModel):
    """Response from Maritaca.ai chat."""

    id: str
    model: str
    content: str
    usage: dict[str, int] | None = None
    created_at: datetime
    finish_reason: str | None = None


class MaritacaDirectService:
    """
    Service for direct interaction with Maritaca.ai language models.

    Features:
    - Direct chat completion API
    - Streaming support for real-time responses
    - Token usage tracking
    - Error handling and retries
    - Support for both Sabiá-3 and Sabiazinho-3 models
    """

    def __init__(self):
        """Initialize Maritaca Direct Service."""
        self.settings = get_settings()
        self.api_key = (
            self.settings.maritaca_api_key.get_secret_value()
            if self.settings.maritaca_api_key
            else None
        )
        self.api_base = self.settings.maritaca_api_base_url
        self.default_model = self.settings.maritaca_model
        self.timeout = 60.0

        if not self.api_key:
            raise ValueError(
                "MARITACA_API_KEY not configured. Please set it in environment variables."
            )

        logger.info(
            f"Maritaca Direct Service initialized with model: {self.default_model}"
        )

    async def chat_completion(
        self, request: MaritacaChatRequest
    ) -> MaritacaChatResponse:
        """
        Send chat completion request to Maritaca.ai API.

        Args:
            request: Chat request with messages and parameters

        Returns:
            Chat response with content and metadata

        Raises:
            HTTPException: If API request fails
        """
        start_time = time.time()
        model = request.model or self.default_model

        # Prepare request payload
        payload = {
            "model": model,
            "messages": [msg.model_dump() for msg in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": request.stream,
        }

        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(
                    f"Sending request to Maritaca API: {model}, "
                    f"messages={len(request.messages)}, "
                    f"max_tokens={request.max_tokens}"
                )

                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    json=payload,
                    headers=headers,
                )

                response.raise_for_status()
                data = response.json()

                # Parse response
                choice = data["choices"][0]
                content = choice["message"]["content"]
                finish_reason = choice.get("finish_reason")

                # Extract usage info if available
                usage = data.get("usage")

                elapsed = time.time() - start_time

                logger.info(
                    f"Maritaca response received: {len(content)} chars, "
                    f"finish_reason={finish_reason}, "
                    f"elapsed={elapsed:.2f}s"
                )

                return MaritacaChatResponse(
                    id=data.get("id", f"maritaca-{int(time.time())}"),
                    model=data.get("model", model),
                    content=content,
                    usage=usage,
                    created_at=datetime.now(),
                    finish_reason=finish_reason,
                )

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Maritaca API HTTP error: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"Maritaca API request failed: {e}")
            raise

    async def chat_completion_stream(
        self, request: MaritacaChatRequest
    ) -> AsyncIterator[str]:
        """
        Stream chat completion from Maritaca.ai API.

        Args:
            request: Chat request with streaming enabled

        Yields:
            Content chunks as they arrive

        Raises:
            HTTPException: If API request fails
        """
        model = request.model or self.default_model

        payload = {
            "model": model,
            "messages": [msg.model_dump() for msg in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": True,
        }

        headers = {
            "Authorization": f"Key {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Starting Maritaca streaming: {model}")

                async with client.stream(
                    "POST",
                    f"{self.api_base}/chat/completions",
                    json=payload,
                    headers=headers,
                ) as response:
                    response.raise_for_status()

                    async for chunk in response.aiter_lines():
                        if not chunk.strip():
                            continue

                        # Remove 'data: ' prefix if present
                        if chunk.startswith("data: "):
                            chunk = chunk[6:]

                        # Skip [DONE] marker
                        if chunk == "[DONE]":
                            break

                        try:
                            import json

                            data = json.loads(chunk)
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")

                            if content:
                                yield content

                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse streaming chunk: {chunk}")
                            continue

                logger.info("Maritaca streaming completed")

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Maritaca streaming HTTP error: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"Maritaca streaming failed: {e}")
            raise

    async def health_check(self) -> dict[str, Any]:
        """
        Check Maritaca.ai API health and availability.

        Returns:
            Health status information
        """
        try:
            # Simple ping with minimal request
            test_request = MaritacaChatRequest(
                messages=[
                    MaritacaMessage(
                        role="system", content="You are a helpful assistant."
                    ),
                    MaritacaMessage(role="user", content="Hi"),
                ],
                max_tokens=10,
            )

            response = await self.chat_completion(test_request)

            return {
                "status": "healthy",
                "model": response.model,
                "api_base": self.api_base,
                "response_received": True,
                "checked_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Maritaca health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_base": self.api_base,
                "checked_at": datetime.now().isoformat(),
            }


# Singleton instance
_maritaca_service: MaritacaDirectService | None = None


def get_maritaca_service() -> MaritacaDirectService:
    """Get or create Maritaca Direct Service singleton."""
    global _maritaca_service
    if _maritaca_service is None:
        _maritaca_service = MaritacaDirectService()
    return _maritaca_service
