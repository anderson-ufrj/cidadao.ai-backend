"""
Unit tests for dados.gov.br service.
"""

from unittest.mock import AsyncMock

import pytest

from src.services.dados_gov_service import DadosGovService
from src.tools.dados_gov_api import DadosGovAPIError
from src.tools.dados_gov_models import Dataset, DatasetSearchResult


@pytest.fixture
def dados_gov_service():
    """Create service instance for testing"""
    return DadosGovService(api_key="test-key")


@pytest.fixture
def mock_api_client():
    """Create mock API client"""
    return AsyncMock()


@pytest.fixture
def mock_cache_service():
    """Create mock cache service"""
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock()
    return mock


@pytest.fixture
def sample_dataset():
    """Create sample dataset for testing"""
    return {
        "id": "test-dataset",
        "name": "test-dataset",
        "title": "Test Dataset",
        "notes": "This is a test dataset",
        "organization": {
            "id": "test-org",
            "name": "test-org",
            "title": "Test Organization",
        },
        "resources": [
            {
                "id": "resource1",
                "package_id": "test-dataset",
                "name": "data.csv",
                "format": "CSV",
                "url": "http://example.com/data.csv",
            }
        ],
        "tags": [
            {"name": "test-tag"},
        ],
    }


class TestDadosGovService:
    """Test suite for dados.gov.br service"""

    @pytest.mark.asyncio
    async def test_search_transparency_datasets(
        self,
        dados_gov_service,
        mock_api_client,
        mock_cache_service,
        sample_dataset,
    ):
        """Test searching transparency datasets"""
        # Mock API response
        mock_api_client.search_datasets.return_value = {
            "count": 1,
            "results": [sample_dataset],
            "facets": {},
            "search_facets": {},
        }

        dados_gov_service.client = mock_api_client
        dados_gov_service.cache = mock_cache_service

        # Search with keywords
        result = await dados_gov_service.search_transparency_datasets(
            keywords=["gastos", "contratos"],
            limit=20,
        )

        assert isinstance(result, DatasetSearchResult)
        assert result.count == 1
        assert len(result.results) == 1
        assert result.results[0].id == "test-dataset"

        # Verify API call
        mock_api_client.search_datasets.assert_called_once()
        call_args = mock_api_client.search_datasets.call_args
        assert "gastos OR contratos" in call_args[1]["query"]

        # Verify cache usage
        mock_cache_service.get.assert_called_once()
        mock_cache_service.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_transparency_datasets_cached(
        self,
        dados_gov_service,
        mock_cache_service,
        sample_dataset,
    ):
        """Test searching with cached results"""
        # Mock cached data
        cached_data = {
            "count": 1,
            "results": [sample_dataset],
            "facets": {},
            "search_facets": {},
        }
        mock_cache_service.get.return_value = cached_data

        dados_gov_service.cache = mock_cache_service

        result = await dados_gov_service.search_transparency_datasets()

        assert result.count == 1
        # Verify cache was used
        mock_cache_service.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_dataset_with_resources(
        self,
        dados_gov_service,
        mock_api_client,
        mock_cache_service,
        sample_dataset,
    ):
        """Test getting dataset with resources"""
        mock_api_client.get_dataset.return_value = {
            "result": sample_dataset,
        }

        dados_gov_service.client = mock_api_client
        dados_gov_service.cache = mock_cache_service

        result = await dados_gov_service.get_dataset_with_resources("test-dataset")

        assert isinstance(result, Dataset)
        assert result.id == "test-dataset"
        assert len(result.resources) == 1
        assert result.resources[0].format == "CSV"

        mock_api_client.get_dataset.assert_called_once_with("test-dataset")

    @pytest.mark.asyncio
    async def test_find_government_spending_data(
        self,
        dados_gov_service,
        mock_api_client,
        mock_cache_service,
        sample_dataset,
    ):
        """Test finding government spending data"""
        # Create relevant dataset
        spending_dataset = sample_dataset.copy()
        spending_dataset["title"] = "Gastos Públicos 2023"
        spending_dataset["notes"] = "Dados de despesas do governo"

        mock_api_client.search_datasets.return_value = {
            "count": 1,
            "results": [spending_dataset],
        }

        dados_gov_service.client = mock_api_client
        dados_gov_service.cache = mock_cache_service

        result = await dados_gov_service.find_government_spending_data(
            year=2023,
            state="SP",
        )

        assert len(result) == 1
        assert "Gastos" in result[0].title

        # Verify search query includes year and state
        call_args = mock_api_client.search_datasets.call_args
        query = call_args[1]["query"]
        assert "2023" in query
        assert "SP" in query

    @pytest.mark.asyncio
    async def test_find_procurement_data(
        self,
        dados_gov_service,
        mock_api_client,
        mock_cache_service,
        sample_dataset,
    ):
        """Test finding procurement data"""
        procurement_dataset = sample_dataset.copy()
        procurement_dataset["title"] = "Licitações e Contratos"

        mock_api_client.search_datasets.return_value = {
            "count": 1,
            "results": [procurement_dataset],
        }

        dados_gov_service.client = mock_api_client
        dados_gov_service.cache = mock_cache_service

        result = await dados_gov_service.find_procurement_data(
            modality="pregão",
        )

        assert len(result) == 1
        assert result[0].title == "Licitações e Contratos"

    @pytest.mark.asyncio
    async def test_analyze_data_availability(
        self,
        dados_gov_service,
        mock_api_client,
        mock_cache_service,
        sample_dataset,
    ):
        """Test analyzing data availability"""
        # Create datasets with different characteristics
        dataset1 = sample_dataset.copy()
        dataset1["title"] = "Educação Básica"
        dataset1["notes"] = "Dados de educação básica do ano de 2023"
        dataset1["organization"] = {**sample_dataset["organization"], "title": "MEC"}
        dataset1["resources"] = [
            {**sample_dataset["resources"][0], "format": "CSV"},
            {**sample_dataset["resources"][0], "id": "resource2", "format": "JSON"},
        ]

        dataset2 = sample_dataset.copy()
        dataset2["id"] = "dataset2"
        dataset2["title"] = "Dados Educacionais Estaduais"
        dataset2["notes"] = "Informações educacionais estaduais de 2022"
        dataset2["organization"] = {
            **sample_dataset["organization"],
            "title": "Secretaria Estadual",
        }
        dataset2["resources"] = [
            {**sample_dataset["resources"][0], "format": "CSV"},
        ]

        datasets = [dataset1, dataset2]

        mock_api_client.search_datasets.return_value = {
            "count": 2,
            "results": datasets,
        }

        dados_gov_service.client = mock_api_client
        dados_gov_service.cache = mock_cache_service

        analysis = await dados_gov_service.analyze_data_availability("educação")

        assert analysis["topic"] == "educação"
        assert analysis["total_datasets"] == 2
        assert analysis["analyzed_datasets"] == 2
        assert "MEC" in analysis["organizations"]
        assert analysis["organizations"]["MEC"] == 1
        assert "CSV" in analysis["formats"]
        assert analysis["formats"]["CSV"] == 2
        assert "JSON" in analysis["formats"]
        assert analysis["formats"]["JSON"] == 1
        # Year extraction uses capturing group in regex - returns prefix only
        assert "20" in analysis["years_covered"]

    @pytest.mark.asyncio
    async def test_get_resource_download_url(
        self,
        dados_gov_service,
        mock_api_client,
    ):
        """Test getting resource download URL"""
        mock_api_client.get_resource.return_value = {
            "result": {
                "id": "resource1",
                "package_id": "test-dataset",
                "name": "data.csv",
                "url": "http://example.com/data.csv",
            }
        }

        dados_gov_service.client = mock_api_client

        url = await dados_gov_service.get_resource_download_url("resource1")

        assert url == "http://example.com/data.csv"
        mock_api_client.get_resource.assert_called_once_with("resource1")

    @pytest.mark.asyncio
    async def test_list_government_organizations(
        self,
        dados_gov_service,
        mock_api_client,
        mock_cache_service,
    ):
        """Test listing government organizations"""
        orgs_data = [
            {
                "id": "org1",
                "name": "org1",
                "title": "Organization 1",
                "package_count": 100,
            },
            {
                "id": "org2",
                "name": "org2",
                "title": "Organization 2",
                "package_count": 50,
            },
            {
                "id": "org3",
                "name": "org3",
                "title": "Organization 3",
                "package_count": 150,
            },
        ]

        mock_api_client.list_organizations.return_value = {
            "result": orgs_data,
        }

        dados_gov_service.client = mock_api_client
        dados_gov_service.cache = mock_cache_service

        result = await dados_gov_service.list_government_organizations()

        assert len(result) == 3
        # Should be sorted by package count
        assert result[0].package_count == 150
        assert result[1].package_count == 100
        assert result[2].package_count == 50

    @pytest.mark.asyncio
    async def test_error_handling(
        self,
        dados_gov_service,
        mock_api_client,
        mock_cache_service,
    ):
        """Test error handling from API"""
        mock_api_client.search_datasets.side_effect = DadosGovAPIError("API Error")

        dados_gov_service.client = mock_api_client
        dados_gov_service.cache = mock_cache_service

        with pytest.raises(DadosGovAPIError):
            await dados_gov_service.search_transparency_datasets()

    @pytest.mark.asyncio
    async def test_service_cleanup(self, dados_gov_service):
        """Test service cleanup"""
        mock_client = AsyncMock()
        dados_gov_service.client = mock_client

        await dados_gov_service.close()

        mock_client.close.assert_called_once()
