"""
Unit tests for DataSUS API client.

Tests the DataSUS client implementation including retry logic, error handling,
and data fetching methods.

Author: Anderson Henrique da Silva
Created: 2025-10-12 16:19:43 -03
License: Proprietary - All rights reserved
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from src.services.transparency_apis.federal_apis.datasus_client import DataSUSClient, DataSUSIndicator
from src.services.transparency_apis.federal_apis.exceptions import (
    NetworkError,
    TimeoutError,
    ServerError,
    NotFoundError,
)


class TestDataSUSClientInitialization:
    """Test DataSUS client initialization."""

    def test_client_initialization(self):
        """Test DataSUS client initializes correctly."""
        client = DataSUSClient(timeout=30)

        assert client.timeout == 30
        assert client.client is not None
        assert hasattr(client, '_make_request')

    def test_client_initialization_with_default_timeout(self):
        """Test DataSUS client uses default timeout."""
        client = DataSUSClient()

        assert client.timeout == 30  # Default value


class TestDataSUSClientContextManager:
    """Test DataSUS client async context manager."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test DataSUS client works as async context manager."""
        async with DataSUSClient(timeout=10) as client:
            assert client is not None
            assert isinstance(client, DataSUSClient)


class TestDataSUSSearchDatasets:
    """Test search_datasets method."""

    @pytest.mark.asyncio
    async def test_search_datasets_success(self):
        """Test successful dataset search."""
        mock_response = {
            "success": True,
            "result": {
                "count": 2,
                "results": [
                    {"name": "covid-19", "title": "COVID-19 Data"},
                    {"name": "vaccination", "title": "Vaccination Data"}
                ]
            }
        }

        client = DataSUSClient(timeout=10)

        # Mock httpx client
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response
            mock_get.return_value = mock_http_response

            result = await client.search_datasets(query="covid", limit=10)

            assert result["success"] is True
            assert result["result"]["count"] == 2

            # Verify URL contains package_search
            call_args = mock_get.call_args
            assert "package_search" in call_args[0][0]

        await client.close()


class TestDataSUSGetHealthFacilities:
    """Test get_health_facilities method."""

    @pytest.mark.asyncio
    async def test_get_health_facilities_success(self):
        """Test successful health facilities retrieval."""
        mock_response = {
            "success": True,
            "result": {
                "name": "cnes",
                "title": "CNES Data",
                "resources": []
            }
        }

        client = DataSUSClient(timeout=10)

        # Mock httpx client
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response
            mock_get.return_value = mock_http_response

            result = await client.get_health_facilities(state_code="RJ")

            assert result["source"] == "DataSUS/CNES"
            assert result["filters"]["state"] == "RJ"

            # Verify URL contains package_show
            call_args = mock_get.call_args
            assert "package_show" in call_args[0][0]

        await client.close()


class TestDataSUSGetMortalityStatistics:
    """Test get_mortality_statistics method."""

    @pytest.mark.asyncio
    async def test_get_mortality_statistics_success(self):
        """Test successful mortality statistics retrieval."""
        mock_response = {
            "success": True,
            "result": {
                "name": "sim-do",
                "title": "SIM Data",
                "resources": []
            }
        }

        client = DataSUSClient(timeout=10)

        # Mock httpx client
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response
            mock_get.return_value = mock_http_response

            result = await client.get_mortality_statistics(state_code="SP", year=2023)

            assert result["source"] == "DataSUS/SIM"
            assert result["filters"]["state"] == "SP"
            assert result["filters"]["year"] == 2023

        await client.close()


class TestDataSUSGetHospitalAdmissions:
    """Test get_hospital_admissions method."""

    @pytest.mark.asyncio
    async def test_get_hospital_admissions_success(self):
        """Test successful hospital admissions retrieval."""
        mock_response = {
            "success": True,
            "result": {
                "name": "sih-rd",
                "title": "SIH Data",
                "resources": []
            }
        }

        client = DataSUSClient(timeout=10)

        # Mock httpx client
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response
            mock_get.return_value = mock_http_response

            result = await client.get_hospital_admissions(state_code="MG", year=2023)

            assert result["source"] == "DataSUS/SIH"
            assert result["filters"]["state"] == "MG"
            assert result["filters"]["year"] == 2023

        await client.close()


class TestDataSUSGetVaccinationData:
    """Test get_vaccination_data method."""

    @pytest.mark.asyncio
    async def test_get_vaccination_data_success(self):
        """Test successful vaccination data retrieval."""
        mock_response = {
            "success": True,
            "result": {
                "name": "si-pni",
                "title": "SI-PNI Data",
                "resources": []
            }
        }

        client = DataSUSClient(timeout=10)

        # Mock httpx client
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response
            mock_get.return_value = mock_http_response

            result = await client.get_vaccination_data(state_code="RJ", vaccine_type="COVID-19")

            assert result["source"] == "DataSUS/SI-PNI"
            assert result["filters"]["state"] == "RJ"
            assert result["filters"]["vaccine_type"] == "COVID-19"

        await client.close()


class TestDataSUSMakeRequest:
    """Test _make_request internal method."""

    @pytest.mark.asyncio
    async def test_make_request_get_success(self):
        """Test _make_request with successful GET."""
        client = DataSUSClient(timeout=10)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            result = await client._make_request("https://test.com", method="GET")

            assert result == {"data": "test"}
            mock_get.assert_called_once()

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_converts_http_errors(self):
        """Test _make_request converts HTTP errors to custom exceptions."""
        client = DataSUSClient(timeout=10)

        # Test 404
        mock_response_404 = MagicMock()
        mock_response_404.status_code = 404

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_404

            with pytest.raises(NotFoundError):
                await client._make_request("https://test.com")

        # Test 500
        mock_response_500 = MagicMock()
        mock_response_500.status_code = 500

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_500

            with pytest.raises(ServerError):
                await client._make_request("https://test.com")

        # Test 503
        mock_response_503 = MagicMock()
        mock_response_503.status_code = 503

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_503

            with pytest.raises(ServerError):
                await client._make_request("https://test.com")

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_handles_network_error(self):
        """Test _make_request handles httpx NetworkError."""
        client = DataSUSClient(timeout=10)

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.NetworkError("Connection refused")

            with pytest.raises(NetworkError) as exc_info:
                await client._make_request("https://test.com")

            assert "DataSUS" in str(exc_info.value)

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_handles_timeout(self):
        """Test _make_request handles httpx TimeoutException."""
        client = DataSUSClient(timeout=10)

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Request timeout")

            with pytest.raises(TimeoutError) as exc_info:
                await client._make_request("https://test.com")

            assert "DataSUS" in str(exc_info.value)
            assert exc_info.value.timeout_seconds == 10

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_with_post_method(self):
        """Test _make_request with POST method."""
        client = DataSUSClient(timeout=10)

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "created"}

        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await client._make_request("https://test.com", method="POST", json={"data": "test"})

            assert result == {"result": "created"}
            mock_post.assert_called_once()

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_unsupported_method(self):
        """Test _make_request raises error for unsupported HTTP method."""
        client = DataSUSClient(timeout=10)

        with pytest.raises(ValueError) as exc_info:
            await client._make_request("https://test.com", method="DELETE")

        assert "Unsupported HTTP method" in str(exc_info.value)

        await client.close()


class TestDataSUSRetryBehavior:
    """Test DataSUS client retry behavior integration."""

    @pytest.mark.asyncio
    async def test_retry_decorator_is_applied(self):
        """Test that _make_request has retry decorator applied."""
        client = DataSUSClient(timeout=10)

        # Check decorator is applied (has __wrapped__ attribute)
        assert hasattr(client._make_request, '__wrapped__')

        await client.close()


class TestDataSUSClientConstants:
    """Test DataSUS client constants and configuration."""

    def test_client_has_correct_urls(self):
        """Test client has correct base URLs defined."""
        assert hasattr(DataSUSClient, 'OPENDATASUS_URL')
        assert hasattr(DataSUSClient, 'CNES_URL')

        assert "opendatasus.saude.gov.br" in DataSUSClient.OPENDATASUS_URL
        assert "cnes.datasus.gov.br" in DataSUSClient.CNES_URL

    def test_client_has_dataset_mapping(self):
        """Test client has dataset ID mapping."""
        assert hasattr(DataSUSClient, 'DATASETS')
        assert isinstance(DataSUSClient.DATASETS, dict)

        # Check key datasets are present
        assert "mortality" in DataSUSClient.DATASETS
        assert "hospital_admissions" in DataSUSClient.DATASETS
        assert "vaccination" in DataSUSClient.DATASETS
        assert "health_facilities" in DataSUSClient.DATASETS


class TestDataSUSIndicatorModel:
    """Test DataSUSIndicator Pydantic model."""

    def test_indicator_model_valid(self):
        """Test DataSUSIndicator model with valid data."""
        indicator = DataSUSIndicator(
            code="IND001",
            name="Infant Mortality Rate",
            category="Mortality",
            unit="per 1000 live births"
        )

        assert indicator.code == "IND001"
        assert indicator.name == "Infant Mortality Rate"
        assert indicator.category == "Mortality"
        assert indicator.unit == "per 1000 live births"

    def test_indicator_model_optional_unit(self):
        """Test DataSUSIndicator model with optional unit."""
        indicator = DataSUSIndicator(
            code="IND002",
            name="Hospital Coverage",
            category="Infrastructure"
        )

        assert indicator.code == "IND002"
        assert indicator.unit is None
