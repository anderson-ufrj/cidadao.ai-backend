"""
Unit tests for INEP API client.

Tests the INEP client implementation including retry logic, error handling,
and data fetching methods.

Author: Anderson Henrique da Silva
Created: 2025-10-12 18:31:39 -03
License: Proprietary - All rights reserved
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from src.services.transparency_apis.federal_apis.inep_client import INEPClient, INEPSchool, IDEBIndicator
from src.services.transparency_apis.federal_apis.exceptions import (
    NetworkError,
    TimeoutError,
    ServerError,
    NotFoundError,
)


class TestINEPClientInitialization:
    """Test INEP client initialization."""

    def test_client_initialization(self):
        """Test INEP client initializes correctly."""
        client = INEPClient(timeout=30)

        assert client.timeout == 30
        assert client.client is not None
        assert hasattr(client, '_make_request')

    def test_client_initialization_with_default_timeout(self):
        """Test INEP client uses default timeout."""
        client = INEPClient()

        assert client.timeout == 30  # Default value


class TestINEPClientContextManager:
    """Test INEP client async context manager."""

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test INEP client works as async context manager."""
        async with INEPClient(timeout=10) as client:
            assert client is not None
            assert isinstance(client, INEPClient)


class TestINEPSearchDatasets:
    """Test search_datasets method."""

    @pytest.mark.asyncio
    async def test_search_datasets_success(self):
        """Test successful dataset search."""
        mock_response = {
            "success": True,
            "result": {
                "count": 2,
                "results": [
                    {"name": "censo-escolar", "title": "Censo Escolar"},
                    {"name": "ideb", "title": "IDEB Data"}
                ]
            }
        }

        client = INEPClient(timeout=10)

        # Mock httpx client
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response
            mock_get.return_value = mock_http_response

            result = await client.search_datasets(query="escola", limit=10)

            assert result["success"] is True
            assert result["result"]["count"] == 2

            # Verify URL contains package_search
            call_args = mock_get.call_args
            assert "package_search" in call_args[0][0]

        await client.close()


class TestINEPGetSchoolCensusData:
    """Test get_school_census_data method."""

    @pytest.mark.asyncio
    async def test_get_school_census_data_success(self):
        """Test successful school census data retrieval."""
        mock_response = {
            "success": True,
            "result": {
                "name": "microdados-do-censo-escolar",
                "title": "Censo Escolar Data",
                "resources": []
            }
        }

        client = INEPClient(timeout=10)

        # Mock httpx client
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response
            mock_get.return_value = mock_http_response

            result = await client.get_school_census_data(state_code="SP", year=2023)

            assert result["source"] == "INEP/Censo Escolar"
            assert result["filters"]["state"] == "SP"
            assert result["filters"]["year"] == 2023

            # Verify URL contains package_show
            call_args = mock_get.call_args
            assert "package_show" in call_args[0][0]

        await client.close()


class TestINEPGetIDEBIndicators:
    """Test get_ideb_indicators method."""

    @pytest.mark.asyncio
    async def test_get_ideb_indicators_success(self):
        """Test successful IDEB indicators retrieval."""
        mock_response = {
            "success": True,
            "result": {
                "name": "indice-de-desenvolvimento-da-educacao-basica-ideb",
                "title": "IDEB Data",
                "resources": []
            }
        }

        client = INEPClient(timeout=10)

        # Mock httpx client
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response
            mock_get.return_value = mock_http_response

            result = await client.get_ideb_indicators(
                state_code="RJ",
                year=2021,
                education_level="anos_iniciais"
            )

            assert result["source"] == "INEP/IDEB"
            assert result["filters"]["state"] == "RJ"
            assert result["filters"]["year"] == 2021
            assert result["filters"]["education_level"] == "anos_iniciais"

        await client.close()


class TestINEPGetENEMResults:
    """Test get_enem_results method."""

    @pytest.mark.asyncio
    async def test_get_enem_results_success(self):
        """Test successful ENEM results retrieval."""
        mock_response = {
            "success": True,
            "result": {
                "name": "microdados-do-enem",
                "title": "ENEM Data",
                "resources": []
            }
        }

        client = INEPClient(timeout=10)

        # Mock httpx client
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response
            mock_get.return_value = mock_http_response

            result = await client.get_enem_results(state_code="MG", year=2023)

            assert result["source"] == "INEP/ENEM"
            assert result["filters"]["state"] == "MG"
            assert result["filters"]["year"] == 2023

        await client.close()


class TestINEPGetSchoolInfrastructure:
    """Test get_school_infrastructure method."""

    @pytest.mark.asyncio
    async def test_get_school_infrastructure_success(self):
        """Test successful school infrastructure retrieval."""
        mock_response = {
            "success": True,
            "result": {
                "name": "censo-escolar-escolas",
                "title": "Schools Data",
                "resources": []
            }
        }

        client = INEPClient(timeout=10)

        # Mock httpx client
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response
            mock_get.return_value = mock_http_response

            result = await client.get_school_infrastructure(state_code="RS")

            assert result["source"] == "INEP/Censo Escolar - Escolas"
            assert result["filters"]["state"] == "RS"

        await client.close()


class TestINEPGetTeacherStatistics:
    """Test get_teacher_statistics method."""

    @pytest.mark.asyncio
    async def test_get_teacher_statistics_success(self):
        """Test successful teacher statistics retrieval."""
        mock_response = {
            "success": True,
            "result": {
                "name": "censo-escolar-docentes",
                "title": "Teachers Data",
                "resources": []
            }
        }

        client = INEPClient(timeout=10)

        # Mock httpx client
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_http_response = MagicMock()
            mock_http_response.status_code = 200
            mock_http_response.json.return_value = mock_response
            mock_get.return_value = mock_http_response

            result = await client.get_teacher_statistics(state_code="BA")

            assert result["source"] == "INEP/Censo Escolar - Docentes"
            assert result["filters"]["state"] == "BA"

        await client.close()


class TestINEPMakeRequest:
    """Test _make_request internal method."""

    @pytest.mark.asyncio
    async def test_make_request_get_success(self):
        """Test _make_request with successful GET."""
        client = INEPClient(timeout=10)

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
        client = INEPClient(timeout=10)

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
        client = INEPClient(timeout=10)

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.NetworkError("Connection refused")

            with pytest.raises(NetworkError) as exc_info:
                await client._make_request("https://test.com")

            assert "INEP" in str(exc_info.value)

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_handles_timeout(self):
        """Test _make_request handles httpx TimeoutException."""
        client = INEPClient(timeout=10)

        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Request timeout")

            with pytest.raises(TimeoutError) as exc_info:
                await client._make_request("https://test.com")

            assert "INEP" in str(exc_info.value)
            assert exc_info.value.timeout_seconds == 10

        await client.close()

    @pytest.mark.asyncio
    async def test_make_request_with_post_method(self):
        """Test _make_request with POST method."""
        client = INEPClient(timeout=10)

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
        client = INEPClient(timeout=10)

        with pytest.raises(ValueError) as exc_info:
            await client._make_request("https://test.com", method="DELETE")

        assert "Unsupported HTTP method" in str(exc_info.value)

        await client.close()


class TestINEPRetryBehavior:
    """Test INEP client retry behavior integration."""

    @pytest.mark.asyncio
    async def test_retry_decorator_is_applied(self):
        """Test that _make_request has retry decorator applied."""
        client = INEPClient(timeout=10)

        # Check decorator is applied (has __wrapped__ attribute)
        assert hasattr(client._make_request, '__wrapped__')

        await client.close()


class TestINEPClientConstants:
    """Test INEP client constants and configuration."""

    def test_client_has_correct_url(self):
        """Test client has correct base URL defined."""
        assert hasattr(INEPClient, 'DADOS_GOV_URL')
        assert "dados.gov.br" in INEPClient.DADOS_GOV_URL

    def test_client_has_dataset_mapping(self):
        """Test client has dataset ID mapping."""
        assert hasattr(INEPClient, 'DATASETS')
        assert isinstance(INEPClient.DATASETS, dict)

        # Check key datasets are present
        assert "school_census" in INEPClient.DATASETS
        assert "ideb" in INEPClient.DATASETS
        assert "enem" in INEPClient.DATASETS
        assert "teachers" in INEPClient.DATASETS
        assert "schools" in INEPClient.DATASETS


class TestINEPSchoolModel:
    """Test INEPSchool Pydantic model."""

    def test_school_model_valid(self):
        """Test INEPSchool model with valid data."""
        school = INEPSchool(
            code="33051341",
            name="Escola Municipal Test",
            location={"state": "RJ", "city": "Rio de Janeiro"},
            education_levels=["ensino_fundamental", "ensino_medio"]
        )

        assert school.code == "33051341"
        assert school.name == "Escola Municipal Test"
        assert school.location["state"] == "RJ"
        assert len(school.education_levels) == 2


class TestIDEBIndicatorModel:
    """Test IDEBIndicator Pydantic model."""

    def test_ideb_indicator_model_valid(self):
        """Test IDEBIndicator model with valid data."""
        indicator = IDEBIndicator(
            year=2021,
            value=5.8,
            location_type="municipal",
            location_code="3304557",
            education_level="anos_iniciais"
        )

        assert indicator.year == 2021
        assert indicator.value == 5.8
        assert indicator.location_type == "municipal"
        assert indicator.location_code == "3304557"
        assert indicator.education_level == "anos_iniciais"

    def test_ideb_indicator_model_optional_location_code(self):
        """Test IDEBIndicator model with optional location_code."""
        indicator = IDEBIndicator(
            year=2021,
            value=5.2,
            location_type="national",
            education_level="anos_finais"
        )

        assert indicator.year == 2021
        assert indicator.location_code is None
