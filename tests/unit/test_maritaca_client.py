"""
Test suite for Maritaca AI client.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.core.exceptions import LLMError, LLMRateLimitError
from src.services.maritaca_client import (
    MaritacaClient,
    MaritacaModel,
    MaritacaRequest,
    MaritacaResponse,
    create_maritaca_client,
)


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    return "test-maritaca-api-key"


@pytest.fixture
def maritaca_client(mock_api_key):
    """Create a Maritaca client instance for testing."""
    return MaritacaClient(
        api_key=mock_api_key,
        base_url="https://test.maritaca.ai/api",
        max_retries=1,
        timeout=10,
    )


@pytest.fixture
def sample_messages():
    """Sample conversation messages."""
    return [
        {"role": "system", "content": "Você é um assistente útil."},
        {"role": "user", "content": "Olá, como você está?"},
    ]


@pytest.fixture
def mock_response_data():
    """Mock API response data."""
    return {
        "id": "test-123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "sabia-3",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Olá! Estou bem, obrigado por perguntar. Como posso ajudá-lo hoje?",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 20, "completion_tokens": 15, "total_tokens": 35},
    }


class TestMaritacaClient:
    """Test cases for MaritacaClient."""

    @pytest.mark.asyncio
    async def test_client_initialization(self, mock_api_key):
        """Test client initialization with various configurations."""
        # Default initialization
        client = MaritacaClient(api_key=mock_api_key)
        assert client.api_key == mock_api_key
        assert client.default_model == MaritacaModel.SABIA_3
        assert client.timeout == 60
        assert client.max_retries == 3

        # Custom initialization
        custom_client = MaritacaClient(
            api_key=mock_api_key,
            model=MaritacaModel.SABIA_3_LARGE,
            timeout=30,
            max_retries=5,
        )
        assert custom_client.default_model == MaritacaModel.SABIA_3_LARGE
        assert custom_client.timeout == 30
        assert custom_client.max_retries == 5

        await client.close()
        await custom_client.close()

    @pytest.mark.asyncio
    async def test_chat_completion_success(
        self, maritaca_client, sample_messages, mock_response_data
    ):
        """Test successful chat completion."""
        with patch.object(maritaca_client.client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response

            response = await maritaca_client.chat_completion(
                messages=sample_messages, temperature=0.7, max_tokens=100
            )

            assert isinstance(response, MaritacaResponse)
            assert (
                response.content
                == "Olá! Estou bem, obrigado por perguntar. Como posso ajudá-lo hoje?"
            )
            assert response.model == "sabia-3"
            assert response.usage["total_tokens"] == 35
            assert response.finish_reason == "stop"

            # Verify API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "https://test.maritaca.ai/api/chat/completions"
            assert "Authorization" in call_args[1]["headers"]

    @pytest.mark.asyncio
    async def test_chat_completion_rate_limit(self, maritaca_client, sample_messages):
        """Test rate limit handling."""
        with patch.object(maritaca_client.client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.headers = {"Retry-After": "60"}
            mock_post.return_value = mock_response

            with pytest.raises(LLMRateLimitError) as exc_info:
                await maritaca_client.chat_completion(messages=sample_messages)

            assert "rate limit exceeded" in str(exc_info.value).lower()
            assert exc_info.value.details["provider"] == "maritaca"

    @pytest.mark.asyncio
    async def test_chat_completion_error_handling(
        self, maritaca_client, sample_messages
    ):
        """Test error handling for API failures."""
        with patch.object(maritaca_client.client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {
                "error": {"message": "Internal server error"}
            }
            mock_post.return_value = mock_response

            with pytest.raises(LLMError) as exc_info:
                await maritaca_client.chat_completion(messages=sample_messages)

            assert "Internal server error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_streaming_completion(self, maritaca_client, sample_messages):
        """Test streaming chat completion."""

        async def mock_aiter_lines():
            yield 'data: {"choices": [{"delta": {"content": "Olá"}}]}'
            yield 'data: {"choices": [{"delta": {"content": "! "}}]}'
            yield 'data: {"choices": [{"delta": {"content": "Como"}}]}'
            yield 'data: {"choices": [{"delta": {"content": " posso"}}]}'
            yield 'data: {"choices": [{"delta": {"content": " ajudar?"}}]}'
            yield "data: [DONE]"

        with patch.object(maritaca_client.client, "stream") as mock_stream:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.aiter_lines = mock_aiter_lines
            mock_stream.return_value.__aenter__.return_value = mock_response

            chunks = []
            async for chunk in await maritaca_client.chat_completion(
                messages=sample_messages, stream=True
            ):
                chunks.append(chunk)

            assert len(chunks) == 5
            assert "".join(chunks) == "Olá! Como posso ajudar?"

    @pytest.mark.asyncio
    async def test_circuit_breaker(self, maritaca_client, sample_messages):
        """Test circuit breaker functionality."""
        # Force multiple failures to trigger circuit breaker
        with patch.object(maritaca_client.client, "post") as mock_post:
            mock_post.side_effect = Exception("Connection failed")

            for i in range(maritaca_client._circuit_breaker_threshold):
                with pytest.raises(LLMError):
                    await maritaca_client.chat_completion(messages=sample_messages)

            # Circuit should now be open
            assert maritaca_client._check_circuit_breaker() is True

            # Next request should fail immediately
            with pytest.raises(LLMError) as exc_info:
                await maritaca_client.chat_completion(messages=sample_messages)

            assert "Circuit breaker is open" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_health_check(self, maritaca_client):
        """Test health check functionality."""
        with patch.object(maritaca_client, "chat_completion") as mock_completion:
            mock_completion.return_value = MaritacaResponse(
                content="Olá",
                model="sabia-3",
                usage={"total_tokens": 10},
                metadata={},
                response_time=0.5,
                timestamp=datetime.utcnow(),
            )

            health = await maritaca_client.health_check()

            assert health["status"] == "healthy"
            assert health["provider"] == "maritaca"
            assert health["model"] == maritaca_client.default_model
            assert health["circuit_breaker"] == "closed"

    @pytest.mark.asyncio
    async def test_context_manager(self, mock_api_key):
        """Test async context manager functionality."""
        async with MaritacaClient(api_key=mock_api_key) as client:
            assert client.api_key == mock_api_key
            assert client.client is not None

        # Client should be closed after context
        with pytest.raises(RuntimeError):
            await client.client.get("https://example.com")

    def test_factory_function(self, mock_api_key):
        """Test factory function for client creation."""
        client = create_maritaca_client(
            api_key=mock_api_key, model=MaritacaModel.SABIA_3_MEDIUM, timeout=45
        )

        assert isinstance(client, MaritacaClient)
        assert client.api_key == mock_api_key
        assert client.default_model == MaritacaModel.SABIA_3_MEDIUM
        assert client.timeout == 45


class TestMaritacaRequest:
    """Test cases for MaritacaRequest model."""

    def test_request_validation(self):
        """Test request model validation."""
        # Valid request
        request = MaritacaRequest(
            messages=[MaritacaMessage(role="user", content="Hello")],
            temperature=0.8,
            max_tokens=1000,
        )
        assert request.temperature == 0.8
        assert request.max_tokens == 1000

        # Test temperature bounds
        with pytest.raises(ValueError):
            MaritacaRequest(messages=[], temperature=2.5)  # Too high

        # Test max_tokens bounds
        with pytest.raises(ValueError):
            MaritacaRequest(messages=[], max_tokens=10000)  # Too high


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
