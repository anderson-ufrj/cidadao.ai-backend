"""Tests for data service."""

import hashlib
import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.data_service import DataService, data_service
from src.services.transparency_orchestrator import DataSource, QueryStrategy


class TestDataServiceInitialization:
    """Tests for DataService initialization."""

    def test_initialization(self):
        """Test data service initialization."""
        service = DataService()

        assert service._contract_cache == {}
        assert service._expense_cache == {}
        assert service._last_updated is None
        assert service._api_client is None

    def test_singleton_instance(self):
        """Test singleton data_service exists."""
        assert data_service is not None
        assert isinstance(data_service, DataService)


class TestApiClient:
    """Tests for API client management."""

    @pytest.fixture
    def service(self):
        """Create data service for testing."""
        return DataService()

    @pytest.mark.asyncio
    async def test_get_api_client_creates_instance(self, service):
        """Test lazy API client creation."""
        with patch(
            "src.services.data_service.TransparencyAPIClient"
        ) as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            client = await service._get_api_client()

            assert client is mock_client
            mock_client_class.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_api_client_returns_cached(self, service):
        """Test API client is reused."""
        with patch(
            "src.services.data_service.TransparencyAPIClient"
        ) as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            client1 = await service._get_api_client()
            client2 = await service._get_api_client()

            assert client1 is client2
            mock_client_class.assert_called_once()


class TestFetchContracts:
    """Tests for fetch_contracts method."""

    @pytest.fixture
    def service(self):
        """Create data service for testing."""
        return DataService()

    @pytest.mark.asyncio
    async def test_fetch_contracts_success(self, service):
        """Test successful contract fetch."""
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "123", "valor": 1000},
            {"id": "456", "valor": 2000},
        ]

        with patch.object(service, "_get_api_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_contracts = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await service.fetch_contracts()

            assert len(result) == 2
            assert result[0]["id"] == "123"
            assert "123" in service._contract_cache

    @pytest.mark.asyncio
    async def test_fetch_contracts_with_filters(self, service):
        """Test contract fetch with filters."""
        mock_response = MagicMock()
        mock_response.data = [{"id": "789", "valor": 3000}]

        with patch.object(service, "_get_api_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_contracts = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            filters = {"ano": 2024, "codigo_orgao": "26000"}
            result = await service.fetch_contracts(filters)

            assert len(result) == 1
            mock_client.get_contracts.assert_called_once()
            # Verify filter was passed (as TransparencyAPIFilter)
            call_args = mock_client.get_contracts.call_args
            assert call_args[0][0] is not None

    @pytest.mark.asyncio
    async def test_fetch_contracts_error_returns_empty(self, service):
        """Test error handling returns empty list."""
        with patch.object(service, "_get_api_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_contracts = AsyncMock(
                side_effect=Exception("API Error")
            )
            mock_get_client.return_value = mock_client

            result = await service.fetch_contracts()

            assert result == []


class TestGetContract:
    """Tests for get_contract method."""

    @pytest.fixture
    def service(self):
        """Create data service for testing."""
        return DataService()

    @pytest.mark.asyncio
    async def test_get_contract_cache_hit(self, service):
        """Test getting contract from cache."""
        service._contract_cache["test-123"] = {"id": "test-123", "valor": 5000}

        result = await service.get_contract("test-123")

        assert result is not None
        assert result["id"] == "test-123"
        assert result["valor"] == 5000

    @pytest.mark.asyncio
    async def test_get_contract_cache_miss_fetches(self, service):
        """Test cache miss triggers fetch."""
        mock_response = MagicMock()
        mock_response.data = [{"id": "new-456", "valor": 8000}]

        with patch.object(service, "_get_api_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_contracts = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await service.get_contract("new-456")

            mock_client.get_contracts.assert_called_once()
            assert result is not None
            assert result["id"] == "new-456"

    @pytest.mark.asyncio
    async def test_get_contract_not_found(self, service):
        """Test contract not found returns None."""
        mock_response = MagicMock()
        mock_response.data = [{"id": "other-id", "valor": 1000}]

        with patch.object(service, "_get_api_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_contracts = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await service.get_contract("nonexistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_contract_error_returns_none(self, service):
        """Test error handling returns None."""
        with patch.object(service, "_get_api_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_contracts = AsyncMock(
                side_effect=Exception("Network Error")
            )
            mock_get_client.return_value = mock_client

            result = await service.get_contract("any-id")

            assert result is None


class TestGenerateContractId:
    """Tests for _generate_contract_id method."""

    @pytest.fixture
    def service(self):
        """Create data service for testing."""
        return DataService()

    def test_generate_with_id_field(self, service):
        """Test ID generation with id field."""
        contract = {"id": "contract-123", "valor": 1000}
        result = service._generate_contract_id(contract)
        assert result == "contract-123"

    def test_generate_with_numero_contrato(self, service):
        """Test ID generation with numero_contrato."""
        contract = {"numero_contrato": "NC-456", "valor": 2000}
        result = service._generate_contract_id(contract)
        assert result == "NC-456"

    def test_generate_with_numeroContrato(self, service):
        """Test ID generation with numeroContrato (camelCase)."""
        contract = {"numeroContrato": "NC-789", "valor": 3000}
        result = service._generate_contract_id(contract)
        assert result == "NC-789"

    def test_generate_from_combined_fields(self, service):
        """Test ID generation from combined fields."""
        contract = {"codigoOrgao": "26000", "ano": 2024, "numero": "001"}
        result = service._generate_contract_id(contract)
        assert result == "26000-2024-001"

    def test_generate_partial_combined_fields(self, service):
        """Test ID with partial combined fields."""
        contract = {"codigoOrgao": "25000", "numero": "002"}
        result = service._generate_contract_id(contract)
        assert result == "25000-002"

    def test_generate_hash_fallback(self, service):
        """Test hash fallback for unknown structure."""
        contract = {"unknown_field": "value", "other": 123}
        result = service._generate_contract_id(contract)

        # Should be 12-char hex hash
        assert len(result) == 12
        assert all(c in "0123456789abcdef" for c in result)


class TestGetRecentContractIds:
    """Tests for get_recent_contract_ids method."""

    @pytest.fixture
    def service(self):
        """Create data service for testing."""
        return DataService()

    @pytest.mark.asyncio
    async def test_get_recent_ids_from_cache(self, service):
        """Test getting IDs from populated cache."""
        # Pre-populate cache
        for i in range(25):
            service._contract_cache[f"id-{i}"] = {"id": f"id-{i}"}

        result = await service.get_recent_contract_ids(limit=10)

        assert len(result) == 10
        assert all(id.startswith("id-") for id in result)

    @pytest.mark.asyncio
    async def test_get_recent_ids_fetches_when_empty(self, service):
        """Test fetching when cache is empty."""
        mock_response = MagicMock()
        mock_response.data = [
            {"id": f"new-{i}"} for i in range(10)
        ]

        with patch.object(service, "_get_api_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_contracts = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await service.get_recent_contract_ids(limit=10)

            mock_client.get_contracts.assert_called_once()
            assert len(result) <= 10

    @pytest.mark.asyncio
    async def test_get_recent_ids_error_returns_empty(self, service):
        """Test error handling returns empty list."""
        with patch.object(service, "_get_api_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_contracts = AsyncMock(
                side_effect=Exception("Timeout")
            )
            mock_get_client.return_value = mock_client

            result = await service.get_recent_contract_ids()

            assert result == []


class TestFetchExpenses:
    """Tests for fetch_expenses method."""

    @pytest.fixture
    def service(self):
        """Create data service for testing."""
        return DataService()

    @pytest.mark.asyncio
    async def test_fetch_expenses_success(self, service):
        """Test successful expense fetch."""
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "exp-1", "valor": 1000},
            {"id": "exp-2", "valor": 2000},
        ]

        with patch.object(service, "_get_api_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_expenses = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await service.fetch_expenses()

            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_fetch_expenses_with_filters(self, service):
        """Test expense fetch with filters."""
        mock_response = MagicMock()
        mock_response.data = [{"id": "exp-3", "valor": 3000}]

        with patch.object(service, "_get_api_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_expenses = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await service.fetch_expenses({"ano": 2024})

            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_fetch_expenses_error_returns_empty(self, service):
        """Test error handling returns empty list."""
        with patch.object(service, "_get_api_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_expenses = AsyncMock(
                side_effect=Exception("API Error")
            )
            mock_get_client.return_value = mock_client

            result = await service.fetch_expenses()

            assert result == []


class TestFetchAgreements:
    """Tests for fetch_agreements method."""

    @pytest.fixture
    def service(self):
        """Create data service for testing."""
        return DataService()

    @pytest.mark.asyncio
    async def test_fetch_agreements_success(self, service):
        """Test successful agreement fetch."""
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "agr-1", "valor": 5000},
            {"id": "agr-2", "valor": 6000},
        ]

        with patch.object(service, "_get_api_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_agreements = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await service.fetch_agreements()

            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_fetch_agreements_error_returns_empty(self, service):
        """Test error handling returns empty list."""
        with patch.object(service, "_get_api_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get_agreements = AsyncMock(
                side_effect=Exception("API Error")
            )
            mock_get_client.return_value = mock_client

            result = await service.fetch_agreements()

            assert result == []


class TestSearchEntities:
    """Tests for search_entities method."""

    @pytest.fixture
    def service(self):
        """Create data service for testing."""
        return DataService()

    @pytest.mark.asyncio
    async def test_search_entities_stub(self, service):
        """Test search_entities returns empty (stub implementation)."""
        result = await service.search_entities("any query")
        assert result == []


class TestGetDataSummary:
    """Tests for get_data_summary method."""

    @pytest.fixture
    def service(self):
        """Create data service for testing."""
        return DataService()

    @pytest.mark.asyncio
    async def test_get_data_summary_contracts(self, service):
        """Test summary for contracts data type."""
        # Add some contracts to cache
        service._contract_cache = {"c1": {}, "c2": {}, "c3": {}}

        result = await service.get_data_summary("contracts")

        assert result["type"] == "contracts"
        assert result["status"] == "implemented"
        assert result["cached_contracts"] == 3
        assert result["total_records"] == 0
        assert result["last_updated"] is None

    @pytest.mark.asyncio
    async def test_get_data_summary_other_type(self, service):
        """Test summary for non-contracts type."""
        result = await service.get_data_summary("expenses")

        assert result["type"] == "expenses"
        assert result["status"] == "stub"


class TestClearCache:
    """Tests for clear_cache method."""

    @pytest.fixture
    def service(self):
        """Create data service for testing."""
        return DataService()

    def test_clear_cache(self, service):
        """Test cache clearing."""
        # Pre-populate caches
        service._contract_cache = {"c1": {}, "c2": {}}
        service._expense_cache = {"e1": {}}
        service._last_updated = None

        service.clear_cache()

        assert service._contract_cache == {}
        assert service._expense_cache == {}
        assert service._last_updated is not None
        assert isinstance(service._last_updated, datetime)


class TestMultiSourceMethods:
    """Tests for multi-source orchestrator methods."""

    @pytest.fixture
    def service(self):
        """Create data service for testing."""
        return DataService()

    @pytest.mark.asyncio
    async def test_get_contracts_multi_source(self, service):
        """Test multi-source contract fetch."""
        mock_result = {
            "data": [{"id": "multi-1"}],
            "sources": ["PORTAL_FEDERAL"],
            "metadata": {},
        }

        with patch(
            "src.services.data_service.orchestrator.get_contracts",
            new_callable=AsyncMock,
        ) as mock_orchestrator:
            mock_orchestrator.return_value = mock_result

            result = await service.get_contracts_multi_source(
                filters={"ano": 2024},
                strategy=QueryStrategy.FALLBACK,
            )

            assert result == mock_result
            mock_orchestrator.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contracts_multi_source_with_sources(self, service):
        """Test multi-source with specific sources."""
        mock_result = {"data": [], "sources": [], "metadata": {}}

        with patch(
            "src.services.data_service.orchestrator.get_contracts",
            new_callable=AsyncMock,
        ) as mock_orchestrator:
            mock_orchestrator.return_value = mock_result

            await service.get_contracts_multi_source(
                sources=[DataSource.PORTAL_FEDERAL, DataSource.PNCP]
            )

            call_args = mock_orchestrator.call_args
            assert call_args.kwargs["sources"] is not None

    @pytest.mark.asyncio
    async def test_get_state_contracts(self, service):
        """Test state-specific contract fetch."""
        mock_result = {"data": [], "sources": [], "metadata": {}}

        with patch(
            "src.services.data_service.orchestrator.get_contracts",
            new_callable=AsyncMock,
        ) as mock_orchestrator:
            mock_orchestrator.return_value = mock_result

            await service.get_state_contracts("MG", {"ano": 2024})

            call_args = mock_orchestrator.call_args
            assert call_args.kwargs["filters"]["estado"] == "MG"
            assert call_args.kwargs["strategy"] == QueryStrategy.AGGREGATE

    @pytest.mark.asyncio
    async def test_get_state_contracts_lowercase_code(self, service):
        """Test state code is uppercased."""
        mock_result = {"data": [], "sources": [], "metadata": {}}

        with patch(
            "src.services.data_service.orchestrator.get_contracts",
            new_callable=AsyncMock,
        ) as mock_orchestrator:
            mock_orchestrator.return_value = mock_result

            await service.get_state_contracts("sp")

            call_args = mock_orchestrator.call_args
            assert call_args.kwargs["filters"]["estado"] == "SP"

    @pytest.mark.asyncio
    async def test_get_state_contracts_no_federal(self, service):
        """Test excluding federal portal."""
        mock_result = {"data": [], "sources": [], "metadata": {}}

        with patch(
            "src.services.data_service.orchestrator.get_contracts",
            new_callable=AsyncMock,
        ) as mock_orchestrator:
            mock_orchestrator.return_value = mock_result

            await service.get_state_contracts("RJ", include_federal=False)

            call_args = mock_orchestrator.call_args
            assert DataSource.PORTAL_FEDERAL not in call_args.kwargs["sources"]

    @pytest.mark.asyncio
    async def test_search_contracts_fastest(self, service):
        """Test fastest-first search strategy."""
        mock_result = {"data": [{"id": "fast-1"}], "sources": [], "metadata": {}}

        with patch(
            "src.services.data_service.orchestrator.get_contracts",
            new_callable=AsyncMock,
        ) as mock_orchestrator:
            mock_orchestrator.return_value = mock_result

            result = await service.search_contracts_fastest({"ano": 2024})

            call_args = mock_orchestrator.call_args
            assert call_args.kwargs["strategy"] == QueryStrategy.FASTEST
            assert result == mock_result


class TestOrchestratorStats:
    """Tests for get_orchestrator_stats method."""

    @pytest.fixture
    def service(self):
        """Create data service for testing."""
        return DataService()

    def test_get_orchestrator_stats(self, service):
        """Test getting orchestrator statistics."""
        mock_stats = {
            "total_requests": 100,
            "cache_hits": 50,
            "source_usage": {},
        }

        with patch(
            "src.services.data_service.orchestrator.get_statistics"
        ) as mock_get_stats:
            mock_get_stats.return_value = mock_stats

            result = service.get_orchestrator_stats()

            assert result == mock_stats
            mock_get_stats.assert_called_once()


class TestClose:
    """Tests for close method."""

    @pytest.fixture
    def service(self):
        """Create data service for testing."""
        return DataService()

    @pytest.mark.asyncio
    async def test_close_with_client(self, service):
        """Test closing with active client."""
        mock_client = AsyncMock()
        mock_client.close = AsyncMock()
        service._api_client = mock_client

        await service.close()

        mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_without_client(self, service):
        """Test closing without active client."""
        service._api_client = None

        # Should not raise
        await service.close()
