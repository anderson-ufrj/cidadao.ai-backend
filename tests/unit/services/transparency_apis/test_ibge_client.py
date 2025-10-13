"""
Unit tests for IBGE API client.

Tests the IBGE client implementation including retry logic, error handling,
and data fetching methods.

Author: Anderson Henrique da Silva
Created: 2025-10-12 15:54:00 -03
License: Proprietary - All rights reserved
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.services.transparency_apis.federal_apis.exceptions import (
    NetworkError,
    NotFoundError,
    ServerError,
    TimeoutError,
)
from src.services.transparency_apis.federal_apis.ibge_client import (
    IBGEClient,
    IBGELocation,
)


class TestIBGEClientInitialization:
    """Test IBGE client initialization."""

    def test_client_initialization(self):
        """Test IBGE client initializes correctly."""
        client = IBGEClient(timeout=30)

        assert client.timeout == 30
        assert client.client is not None
        assert hasattr(client, "_make_request")

    def test_client_initialization_with_default_timeout(self):
        """Test IBGE client uses default timeout."""
        client = IBGEClient()

        assert client.timeout == 30  # Default value


class TestIBGEClientContextManager:
    """Test IBGE client async context manager."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test IBGE client works as async context manager."""
        async with IBGEClient(timeout=10) as client:
            assert client is not None
            assert isinstance(client, IBGEClient)


class TestIBGEGetStates:
    """Test get_states method."""

    @pytest.mark.asyncio
    async def test_get_states_success(self):
        """Test successful states retrieval."""
        mock_response = [
            {"id": "33", "nome": "Rio de Janeiro"},
            {"id": "31", "nome": "Minas Gerais"},
        ]

        client = IBGEClient(timeout=10)

        #  Mock the httpx client.get method to bypass everything
        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response
            mock_get.return_value = mock_http_response

            states = await client.get_states()

            assert len(states) == 2
            assert isinstance(states[0], IBGELocation)
            assert states[0].id == "33"
            assert states[0].nome == "Rio de Janeiro"

            # Verify httpx get was called with correct URL
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "estados" in call_args[0][0]

        await client.close()


class TestIBGEGetMunicipalities:
    """Test get_municipalities method."""

    @pytest.mark.asyncio
    async def test_get_municipalities_success(self):
        """Test successful municipalities retrieval."""
        mock_response = [
            {"id": "3304557", "nome": "Rio de Janeiro"},
            {"id": "3303302", "nome": "Niterói"},
        ]

        client = IBGEClient(timeout=10)

        # Mock httpx client
        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response
            mock_get.return_value = mock_http_response

            municipalities = await client.get_municipalities(state_id="33")

            assert len(municipalities) == 2
            assert isinstance(municipalities[0], IBGELocation)
            assert municipalities[0].id == "3304557"
            assert municipalities[0].nome == "Rio de Janeiro"

            # Verify URL contains state_id
            call_args = mock_get.call_args
            assert "33" in call_args[0][0]
            assert "municipios" in call_args[0][0]

        await client.close()


class TestIBGEGetPopulation:
    """Test get_population method."""

    @pytest.mark.asyncio
    async def test_get_population_success(self):
        """Test successful population retrieval."""
        mock_response = [
            {
                "localidade": {"id": 3304557, "nome": "Rio de Janeiro"},
                "res": [{"localidade": 3304557, "res": [{"res": 6748000}]}],
            }
        ]

        client = IBGEClient(timeout=10)

        # Mock httpx client
        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response
            mock_get.return_value = mock_http_response

            population_data = await client.get_population(location_id="3304557")

            assert population_data is not None
            assert len(population_data) > 0

            # Verify URL contains location_id
            call_args = mock_get.call_args
            assert "3304557" in call_args[0][0]

        await client.close()


class TestIBGEMakeRequest:
    """Test _make_request internal method."""

    @pytest.mark.asyncio
    async def test_make_request_get_success(self):
        """Test _make_request with successful GET."""
        client = IBGEClient(timeout=10)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}

        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client._make_request("https://test.com", method="GET")

            assert result == {"data": "test"}
            mock_get.assert_called_once()

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_converts_http_errors(self):
        """Test _make_request converts HTTP errors to custom exceptions."""
        client = IBGEClient(timeout=10)

        # Test 404
        mock_response_404 = MagicMock()
        mock_response_404.status_code = 404

        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_404

            with pytest.raises(NotFoundError):
                await client._make_request("https://test.com")

        # Test 500
        mock_response_500 = MagicMock()
        mock_response_500.status_code = 500

        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_500

            with pytest.raises(ServerError):
                await client._make_request("https://test.com")

        # Test 503
        mock_response_503 = MagicMock()
        mock_response_503.status_code = 503

        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_503

            with pytest.raises(ServerError):
                await client._make_request("https://test.com")

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_handles_network_error(self):
        """Test _make_request handles httpx NetworkError."""
        client = IBGEClient(timeout=10)

        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.NetworkError("Connection refused")

            with pytest.raises(NetworkError) as exc_info:
                await client._make_request("https://test.com")

            assert "IBGE" in str(exc_info.value)

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_handles_timeout(self):
        """Test _make_request handles httpx TimeoutException."""
        client = IBGEClient(timeout=10)

        with patch.object(client.client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Request timeout")

            with pytest.raises(TimeoutError) as exc_info:
                await client._make_request("https://test.com")

            assert "IBGE" in str(exc_info.value)
            assert exc_info.value.timeout_seconds == 10

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_with_post_method(self):
        """Test _make_request with POST method."""
        client = IBGEClient(timeout=10)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "created"}

        with patch.object(client.client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await client._make_request(
                "https://test.com", method="POST", json={"data": "test"}
            )

            assert result == {"result": "created"}
            mock_post.assert_called_once()

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_unsupported_method(self):
        """Test _make_request raises error for unsupported HTTP method."""
        client = IBGEClient(timeout=10)

        with pytest.raises(ValueError) as exc_info:
            await client._make_request("https://test.com", method="DELETE")

        assert "Unsupported HTTP method" in str(exc_info.value)

        await client.close()


class TestIBGERetryBehavior:
    """Test IBGE client retry behavior integration."""

    @pytest.mark.asyncio
    async def test_retry_decorator_is_applied(self):
        """Test that _make_request has retry decorator applied."""
        client = IBGEClient(timeout=10)

        # Check decorator is applied (has __wrapped__ attribute)
        assert hasattr(client._make_request, "__wrapped__")

        await client.close()


class TestIBGEClientURLs:
    """Test IBGE client uses correct API URLs."""

    def test_client_has_correct_base_urls(self):
        """Test client has correct base URLs defined."""
        assert hasattr(IBGEClient, "LOCALIDADES_URL")
        assert hasattr(IBGEClient, "AGREGADOS_URL")

        assert "ibge.gov.br" in IBGEClient.LOCALIDADES_URL
        assert "ibge.gov.br" in IBGEClient.AGREGADOS_URL
