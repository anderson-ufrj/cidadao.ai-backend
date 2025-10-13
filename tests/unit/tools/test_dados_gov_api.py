"""
Unit tests for dados.gov.br API client.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.tools.dados_gov_api import DadosGovAPIClient, DadosGovAPIError


@pytest.fixture
def api_client():
    """Create API client instance for testing"""
    return DadosGovAPIClient(api_key="test-key")


@pytest.fixture
def mock_httpx_client():
    """Create mock httpx client"""
    mock = AsyncMock()
    mock.aclose = AsyncMock()
    return mock


class TestDadosGovAPIClient:
    """Test suite for dados.gov.br API client"""

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization with and without API key"""
        # With API key
        client = DadosGovAPIClient(api_key="test-key")
        assert client.api_key == "test-key"

        # Without API key
        client = DadosGovAPIClient()
        assert client.api_key is None

    @pytest.mark.asyncio
    async def test_search_datasets_success(self, api_client, mock_httpx_client):
        """Test successful dataset search"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "count": 2,
            "results": [
                {
                    "id": "dataset1",
                    "name": "test-dataset-1",
                    "title": "Test Dataset 1",
                },
                {
                    "id": "dataset2",
                    "name": "test-dataset-2",
                    "title": "Test Dataset 2",
                },
            ],
        }

        mock_httpx_client.request.return_value = mock_response

        with patch.object(api_client, "_get_client", return_value=mock_httpx_client):
            result = await api_client.search_datasets(
                query="test",
                limit=10,
            )

        assert result["count"] == 2
        assert len(result["results"]) == 2
        assert result["results"][0]["id"] == "dataset1"

        # Verify request parameters
        mock_httpx_client.request.assert_called_once()
        call_args = mock_httpx_client.request.call_args
        assert call_args[0][0] == "GET"
        assert call_args[0][1] == "package_search"
        assert call_args[1]["params"]["q"] == "test"
        assert call_args[1]["params"]["rows"] == 10

    @pytest.mark.asyncio
    async def test_search_datasets_with_filters(self, api_client, mock_httpx_client):
        """Test dataset search with filters"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"count": 0, "results": []}

        mock_httpx_client.request.return_value = mock_response

        with patch.object(api_client, "_get_client", return_value=mock_httpx_client):
            result = await api_client.search_datasets(
                organization="test-org",
                tags=["tag1", "tag2"],
                format="csv",
            )

        # Verify filters in request
        call_args = mock_httpx_client.request.call_args
        params = call_args[1]["params"]
        assert params["fq"] == "organization:test-org"
        assert params["tags"] == "tag1,tag2"
        assert params["res_format"] == "csv"

    @pytest.mark.asyncio
    async def test_get_dataset(self, api_client, mock_httpx_client):
        """Test getting dataset details"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "id": "test-dataset",
                "name": "test-dataset",
                "title": "Test Dataset",
                "resources": [
                    {
                        "id": "resource1",
                        "format": "CSV",
                        "url": "http://example.com/data.csv",
                    }
                ],
            }
        }

        mock_httpx_client.request.return_value = mock_response

        with patch.object(api_client, "_get_client", return_value=mock_httpx_client):
            result = await api_client.get_dataset("test-dataset")

        assert result["result"]["id"] == "test-dataset"
        assert len(result["result"]["resources"]) == 1

    @pytest.mark.asyncio
    async def test_error_handling_401(self, api_client, mock_httpx_client):
        """Test authentication error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 401

        mock_httpx_client.request.return_value = mock_response

        with patch.object(api_client, "_get_client", return_value=mock_httpx_client):
            with pytest.raises(DadosGovAPIError) as exc_info:
                await api_client.search_datasets()

        assert "Authentication failed" in str(exc_info.value)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_error_handling_403(self, api_client, mock_httpx_client):
        """Test access forbidden error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 403

        mock_httpx_client.request.return_value = mock_response

        with patch.object(api_client, "_get_client", return_value=mock_httpx_client):
            with pytest.raises(DadosGovAPIError) as exc_info:
                await api_client.search_datasets()

        assert "Access forbidden" in str(exc_info.value)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_error_handling_404(self, api_client, mock_httpx_client):
        """Test not found error handling"""
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_httpx_client.request.return_value = mock_response

        with patch.object(api_client, "_get_client", return_value=mock_httpx_client):
            with pytest.raises(DadosGovAPIError) as exc_info:
                await api_client.get_dataset("nonexistent")

        assert "Resource not found" in str(exc_info.value)
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, api_client, mock_httpx_client):
        """Test rate limit handling with retry"""
        # First response: rate limited
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "1"}

        # Second response: success
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {"count": 0, "results": []}

        mock_httpx_client.request.side_effect = [
            mock_response_429,
            mock_response_200,
        ]

        with patch.object(api_client, "_get_client", return_value=mock_httpx_client):
            with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
                result = await api_client.search_datasets()

        assert result["count"] == 0
        mock_sleep.assert_called_once_with(1)
        assert mock_httpx_client.request.call_count == 2

    @pytest.mark.asyncio
    async def test_connection_error_retry(self, api_client, mock_httpx_client):
        """Test connection error with retry logic"""
        # First two attempts fail, third succeeds
        mock_httpx_client.request.side_effect = [
            httpx.ConnectError("Connection failed"),
            httpx.TimeoutException("Timeout"),
            MagicMock(
                status_code=200,
                json=MagicMock(return_value={"count": 0, "results": []}),
            ),
        ]

        with patch.object(api_client, "_get_client", return_value=mock_httpx_client):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await api_client.search_datasets()

        assert result["count"] == 0
        assert mock_httpx_client.request.call_count == 3

    @pytest.mark.asyncio
    async def test_connection_error_max_retries(self, api_client, mock_httpx_client):
        """Test connection error exhausting retries"""
        mock_httpx_client.request.side_effect = httpx.ConnectError("Connection failed")

        with patch.object(api_client, "_get_client", return_value=mock_httpx_client):
            with patch("asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(DadosGovAPIError) as exc_info:
                    await api_client.search_datasets()

        assert "Failed to connect" in str(exc_info.value)
        assert mock_httpx_client.request.call_count == 3  # MAX_RETRIES

    @pytest.mark.asyncio
    async def test_list_organizations(self, api_client, mock_httpx_client):
        """Test listing organizations"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [
                {"id": "org1", "title": "Organization 1"},
                {"id": "org2", "title": "Organization 2"},
            ]
        }

        mock_httpx_client.request.return_value = mock_response

        with patch.object(api_client, "_get_client", return_value=mock_httpx_client):
            result = await api_client.list_organizations(limit=50)

        assert len(result["result"]) == 2
        assert result["result"][0]["id"] == "org1"

    @pytest.mark.asyncio
    async def test_client_cleanup(self, api_client):
        """Test client cleanup on close"""
        mock_client = AsyncMock()
        api_client._client = mock_client

        await api_client.close()

        mock_client.aclose.assert_called_once()
        assert api_client._client is None
