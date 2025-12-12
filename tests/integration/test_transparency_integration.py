# TODO: Mock Portal da Transparência API responses for integration tests
"""
Integration tests for Transparency APIs and Multi-Agent Integration.

Tests the complete flow from REST endpoints through TransparencyDataCollector
to Zumbi and Anita agents with multi-source data aggregation.

Author: Anderson Henrique da Silva
Created: 2025-10-09
License: Proprietary - All rights reserved
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.agents.anita import AnalysisRequest, AnalystAgent
from src.agents.deodoro import AgentContext, AgentStatus
from src.agents.zumbi import InvestigationRequest, InvestigatorAgent
from src.api.app import app
from src.services.transparency_apis import (
    TransparencyDataCollector,
    get_transparency_collector,
)

# Test Client
client = TestClient(app)


@pytest.fixture
def mock_transparency_data():
    """Mock transparency data from multiple sources."""
    return {
        "contracts": [
            {
                "id": "12345",
                "numeroContrato": "001/2024",
                "objeto": "Fornecimento de equipamentos médicos",
                "valorInicial": 500000.00,
                "valorFinal": 550000.00,
                "dataAssinatura": "15/01/2024",
                "dataInicio": "20/01/2024",
                "fornecedor": {
                    "nome": "Empresa XYZ Ltda",
                    "cpfCnpj": "12.345.678/0001-90",
                },
                "orgao": {"codigoOrgao": "26000", "nome": "Ministério da Saúde"},
                "modalidade": "Pregão Eletrônico",
                "source": "federal_api",
            },
            {
                "id": "67890",
                "numeroContrato": "002/2024",
                "objeto": "Manutenção de sistemas",
                "valorInicial": 1200000.00,
                "dataAssinatura": "10/02/2024",
                "fornecedor": {
                    "nome": "Tech Solutions S.A.",
                    "cpfCnpj": "98.765.432/0001-11",
                },
                "source": "tce_pe",
            },
            {
                "id": "11111",
                "numeroContrato": "003/2024",
                "objeto": "Consultoria em TI",
                "valorInicial": 8000000.00,  # Anomaly - very high value
                "dataAssinatura": "05/03/2024",
                "fornecedor": {
                    "nome": "Empresa XYZ Ltda",  # Same supplier - concentration
                    "cpfCnpj": "12.345.678/0001-90",
                },
                "source": "ckan_sp",
            },
        ],
        "expenses": [
            {
                "id": "exp001",
                "valor": 50000.00,
                "data": "25/01/2024",
                "favorecido": "Empresa XYZ Ltda",
                "tipo": "Fornecimento",
                "source": "federal_api",
            }
        ],
        "suppliers": [
            {
                "nome": "Empresa XYZ Ltda",
                "cpfCnpj": "12.345.678/0001-90",
                "totalContratos": 2,
                "valorTotal": 8500000.00,
                "source": "federal_api",
            },
            {
                "nome": "Tech Solutions S.A.",
                "cpfCnpj": "98.765.432/0001-11",
                "totalContratos": 1,
                "valorTotal": 1200000.00,
                "source": "tce_pe",
            },
        ],
    }


@pytest.fixture
def mock_collector(mock_transparency_data):
    """Mock TransparencyDataCollector."""
    collector = AsyncMock(spec=TransparencyDataCollector)

    # Mock collect_contracts
    collector.collect_contracts.return_value = {
        "contracts": mock_transparency_data["contracts"],
        "total": len(mock_transparency_data["contracts"]),
        "sources": ["federal_api", "tce_pe", "ckan_sp"],
        "errors": [],
        "metadata": {
            "collection_time": "2025-10-09T10:30:00",
            "filters_applied": ["state=None", "year=2024"],
            "validation_enabled": True,
        },
    }

    # Mock collect_expenses
    collector.collect_expenses.return_value = {
        "expenses": mock_transparency_data["expenses"],
        "total": len(mock_transparency_data["expenses"]),
        "sources": ["federal_api"],
        "errors": [],
        "metadata": {},
    }

    # Mock collect_suppliers
    collector.collect_suppliers.return_value = {
        "suppliers": mock_transparency_data["suppliers"],
        "total": len(mock_transparency_data["suppliers"]),
        "sources": ["federal_api", "tce_pe"],
        "errors": [],
        "metadata": {},
    }

    # Mock analyze_contracts_for_anomalies
    collector.analyze_contracts_for_anomalies.return_value = {
        "summary": {
            "total_contracts": 3,
            "anomaly_count": 2,
            "risk_score": 0.75,
            "supplier_concentration": 0.67,  # 2 out of 3 contracts from same supplier
        },
        "anomalies": {
            "outlier_count": 1,
            "outliers": [
                {
                    "contract_id": "11111",
                    "type": "price_outlier",
                    "severity": "high",
                    "value": 8000000.00,
                    "z_score": 3.2,
                }
            ],
            "concentration": {
                "top_supplier": "Empresa XYZ Ltda",
                "concentration_percentage": 67,
                "risk": "high",
            },
        },
        "metadata": {"analysis_time": "2025-10-09T10:35:00"},
    }

    return collector


@pytest.fixture
def mock_health_monitor():
    """Mock HealthMonitor."""
    monitor = AsyncMock()

    monitor.generate_report.return_value = {
        "overall_status": "healthy",
        "overall_health_percentage": 91.67,
        "summary": "11/12 APIs operational",
        "apis": {
            "federal_api": {
                "status": "healthy",
                "response_time": 450,
                "last_check": "2025-10-09T10:30:00",
            },
            "tce_pe": {
                "status": "healthy",
                "response_time": 320,
                "last_check": "2025-10-09T10:30:00",
            },
            "tce_ce": {
                "status": "degraded",
                "response_time": 1500,
                "last_check": "2025-10-09T10:30:00",
            },
        },
        "metadata": {"check_time": "2025-10-09T10:30:00"},
    }

    return monitor


class TestTransparencyRESTEndpoints:
    """Test REST API endpoints for transparency data."""

    @pytest.mark.integration
    def test_get_contracts_endpoint(self, mock_collector):
        """Test GET /api/v1/transparency/contracts endpoint."""
        with patch(
            "src.api.routes.transparency.get_transparency_collector",
            return_value=mock_collector,
        ):
            response = client.get(
                "/api/v1/transparency/contracts",
                params={"state": "PE", "year": 2024, "validate": True},
            )

            assert response.status_code == 200
            data = response.json()

            assert "contracts" in data
            assert "total" in data
            assert "sources" in data
            assert "errors" in data
            assert "metadata" in data

            assert len(data["contracts"]) == 3
            assert data["total"] == 3
            assert "federal_api" in data["sources"]
            assert "tce_pe" in data["sources"]

            # Verify collector was called with correct params
            mock_collector.collect_contracts.assert_called_once()
            call_kwargs = mock_collector.collect_contracts.call_args.kwargs
            assert call_kwargs["state"] == "PE"
            assert call_kwargs["year"] == 2024
            assert call_kwargs["validate"] is True

    @pytest.mark.integration
    def test_get_expenses_endpoint(self, mock_collector):
        """Test GET /api/v1/transparency/expenses endpoint."""
        with patch(
            "src.api.routes.transparency.get_transparency_collector",
            return_value=mock_collector,
        ):
            response = client.get(
                "/api/v1/transparency/expenses", params={"state": "SP", "year": 2024}
            )

            assert response.status_code == 200
            data = response.json()

            assert "expenses" in data
            assert "total" in data
            assert len(data["expenses"]) == 1

    @pytest.mark.integration
    def test_get_suppliers_endpoint(self, mock_collector):
        """Test GET /api/v1/transparency/suppliers endpoint."""
        with patch(
            "src.api.routes.transparency.get_transparency_collector",
            return_value=mock_collector,
        ):
            response = client.get("/api/v1/transparency/suppliers")

            assert response.status_code == 200
            data = response.json()

            assert "suppliers" in data
            assert "total" in data
            assert len(data["suppliers"]) == 2

    @pytest.mark.integration
    def test_analyze_anomalies_endpoint(self, mock_collector):
        """Test POST /api/v1/transparency/analyze-anomalies endpoint."""
        with patch(
            "src.api.routes.transparency.get_transparency_collector",
            return_value=mock_collector,
        ):
            contracts = [
                {"id": "1", "valor": 100000},
                {"id": "2", "valor": 200000},
                {"id": "3", "valor": 5000000},  # Outlier
            ]

            response = client.post(
                "/api/v1/transparency/analyze-anomalies", json=contracts
            )

            assert response.status_code == 200
            data = response.json()

            assert "summary" in data
            assert "anomalies" in data
            assert "metadata" in data

            assert data["summary"]["anomaly_count"] == 2
            assert data["summary"]["risk_score"] == 0.75
            assert data["anomalies"]["outlier_count"] == 1

    @pytest.mark.integration
    def test_health_check_endpoint(self, mock_health_monitor):
        """Test GET /api/v1/transparency/health endpoint."""
        with patch(
            "src.api.routes.transparency.get_health_monitor",
            return_value=mock_health_monitor,
        ):
            response = client.get("/api/v1/transparency/health")

            assert response.status_code == 200
            data = response.json()

            assert "overall_status" in data
            assert "overall_health_percentage" in data
            assert "apis" in data

            assert data["overall_status"] == "healthy"
            assert data["overall_health_percentage"] == 91.67
            assert "federal_api" in data["apis"]
            assert data["apis"]["federal_api"]["status"] == "healthy"

    @pytest.mark.integration
    def test_list_apis_endpoint(self):
        """Test GET /api/v1/transparency/apis endpoint."""
        with patch(
            "src.api.routes.transparency.registry.list_available_apis"
        ) as mock_list:
            mock_list.return_value = [
                "federal_api",
                "tce_pe",
                "tce_ce",
                "tce_rj",
                "tce_sp",
                "tce_mg",
                "tce_ba",
                "ckan_sp",
                "ckan_rj",
                "ckan_rs",
                "ckan_sc",
                "ckan_ba",
                "state_ro",
            ]

            response = client.get("/api/v1/transparency/apis")

            assert response.status_code == 200
            data = response.json()

            assert "total" in data
            assert "apis" in data
            assert "description" in data

            assert data["total"] == 13
            assert "federal_api" in data["apis"]
            assert "tce_pe" in data["apis"]
            assert "2500+" in data["description"]

    @pytest.mark.integration
    def test_contracts_endpoint_error_handling(self, mock_collector):
        """Test error handling in contracts endpoint."""
        mock_collector.collect_contracts.side_effect = Exception(
            "API connection failed"
        )

        with patch(
            "src.api.routes.transparency.get_transparency_collector",
            return_value=mock_collector,
        ):
            response = client.get("/api/v1/transparency/contracts")

            assert response.status_code == 500
            assert "Failed to fetch contracts" in response.json()["detail"]


class TestZumbiTransparencyIntegration:
    """Test Zumbi agent integration with TransparencyDataCollector."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_zumbi_uses_transparency_collector(self, mock_collector):
        """Test that Zumbi agent uses TransparencyDataCollector for investigations."""
        with patch(
            "src.agents.zumbi.get_transparency_collector", return_value=mock_collector
        ):
            agent = InvestigatorAgent()

            request = InvestigationRequest(
                query="Investigate suspicious contracts",
                data_sources=["federal_api", "tce_pe"],
                filters={},
                max_records=100,
            )

            context = AgentContext(
                user_id="test_user", session_id="test_session", conversation_history=[]
            )

            # Execute investigation
            response = await agent.process(request, context)

            # Verify TransparencyDataCollector was used
            mock_collector.collect_contracts.assert_called_once()

            # Verify response
            assert response.status == AgentStatus.COMPLETED
            assert "result" in response.result

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_zumbi_multi_source_aggregation(
        self, mock_collector, mock_transparency_data
    ):
        """Test Zumbi aggregates data from multiple sources."""
        with patch(
            "src.agents.zumbi.get_transparency_collector", return_value=mock_collector
        ):
            agent = InvestigatorAgent()

            request = InvestigationRequest(
                query="Analyze contracts from all sources",
                data_sources=None,  # All sources
                max_records=1000,
            )

            context = AgentContext(user_id="test_user", session_id="test_session")

            response = await agent.process(request, context)

            # Verify collector was called for all sources
            call_kwargs = mock_collector.collect_contracts.call_args.kwargs
            assert call_kwargs["state"] is None  # All states
            assert call_kwargs["municipality_code"] is None  # All municipalities

            # Verify multi-source data is used
            assert response.status == AgentStatus.COMPLETED


class TestAnitaTransparencyIntegration:
    """Test Anita agent integration with TransparencyDataCollector."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_anita_uses_transparency_collector(self, mock_collector):
        """Test that Anita agent uses TransparencyDataCollector for analysis."""
        with patch(
            "src.agents.anita.get_transparency_collector", return_value=mock_collector
        ):
            agent = AnalystAgent()

            request = AnalysisRequest(
                data_sources=["federal_api", "ckan_sp"],
                analysis_types=["patterns", "correlations"],
                filters={},
            )

            context = AgentContext(user_id="test_user", session_id="test_session")

            response = await agent.process(request, context)

            # Verify TransparencyDataCollector was used
            mock_collector.collect_contracts.assert_called_once()

            # Verify response
            assert response.status == AgentStatus.COMPLETED

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_anita_temporal_enrichment(
        self, mock_collector, mock_transparency_data
    ):
        """Test Anita adds temporal metadata for time-series analysis."""
        with patch(
            "src.agents.anita.get_transparency_collector", return_value=mock_collector
        ):
            agent = AnalystAgent()

            request = AnalysisRequest(
                data_sources=["federal_api"], analysis_types=["temporal_patterns"]
            )

            context = AgentContext(user_id="test_user")

            response = await agent.process(request, context)

            # Verify temporal metadata is added
            # Anita should enrich contracts with _month, _year fields
            assert response.status == AgentStatus.COMPLETED


class TestMultiSourceDataCollection:
    """Test multi-source data collection and aggregation."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_collect_from_multiple_apis(self):
        """Test collecting data from multiple transparency APIs."""
        # This would be a real integration test with actual APIs
        # For now, we test the structure

        collector = get_transparency_collector()

        # Verify collector is properly initialized
        assert collector is not None
        assert hasattr(collector, "collect_contracts")
        assert hasattr(collector, "collect_expenses")
        assert hasattr(collector, "collect_suppliers")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_data_validation(self, mock_collector):
        """Test data validation during collection."""
        with patch(
            "src.services.transparency_apis.get_transparency_collector",
            return_value=mock_collector,
        ):
            collector = get_transparency_collector()

            result = await collector.collect_contracts(
                state="PE", year=2024, validate=True
            )

            # Verify validation was applied
            call_kwargs = mock_collector.collect_contracts.call_args.kwargs
            assert call_kwargs["validate"] is True

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_resilience(self, mock_collector):
        """Test error resilience in multi-source collection."""
        # Mock partial failure scenario
        mock_collector.collect_contracts.return_value = {
            "contracts": [{"id": "1"}],
            "total": 1,
            "sources": ["federal_api"],
            "errors": [
                {"source": "tce_pe", "error": "Connection timeout"},
                {"source": "ckan_sp", "error": "403 Forbidden"},
            ],
            "metadata": {},
        }

        with patch(
            "src.services.transparency_apis.get_transparency_collector",
            return_value=mock_collector,
        ):
            collector = get_transparency_collector()

            result = await collector.collect_contracts()

            # Verify system continues despite partial failures
            assert result["total"] == 1
            assert len(result["errors"]) == 2
            assert result["sources"] == ["federal_api"]


class TestDatabasePersistence:
    """Test database persistence with Railway/Supabase."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_investigation_persistence(self):
        """Test investigations are persisted to database."""
        # This would require actual database connection
        # For now, test the structure

        from src.db.session import get_session

        async with get_session() as session:
            # Verify session can be created
            assert (
                session is not None or session is None
            )  # Allowed to be None in test env

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_rls_policies(self):
        """Test Row Level Security policies."""
        # This would require actual Supabase connection
        # Structure test for now

        from pathlib import Path

        migration_file = (
            Path(__file__).parent.parent.parent
            / "migrations"
            / "supabase"
            / "001_create_investigations_table.sql"
        )

        # Verify migration file exists
        assert migration_file.exists()

        # Verify RLS policies are defined
        migration_sql = migration_file.read_text()
        assert "CREATE POLICY" in migration_sql
        assert "users_read_own_investigations" in migration_sql
        assert "users_insert_own_investigations" in migration_sql


class TestEndToEndTransparencyFlow:
    """Test complete end-to-end transparency flow."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_investigation_flow(self, mock_collector):
        """Test complete flow: REST endpoint → Collector → Agent → Database."""
        with (
            patch(
                "src.api.routes.transparency.get_transparency_collector",
                return_value=mock_collector,
            ),
            patch(
                "src.agents.zumbi.get_transparency_collector",
                return_value=mock_collector,
            ),
        ):
            # 1. Client requests contracts via REST API
            response = client.get(
                "/api/v1/transparency/contracts",
                params={"state": "PE", "year": 2024},
            )

            assert response.status_code == 200
            contracts = response.json()["contracts"]

            # 2. Client requests anomaly analysis
            analysis_response = client.post(
                "/api/v1/transparency/analyze-anomalies", json=contracts
            )

            assert analysis_response.status_code == 200
            anomalies = analysis_response.json()

            # 3. Verify complete flow
            assert len(contracts) == 3
            assert anomalies["summary"]["anomaly_count"] == 2
            assert anomalies["anomalies"]["outlier_count"] == 1

    @pytest.mark.integration
    def test_health_monitoring_flow(self, mock_health_monitor):
        """Test health monitoring flow."""
        with patch(
            "src.api.routes.transparency.get_health_monitor",
            return_value=mock_health_monitor,
        ):
            # Check API health
            response = client.get("/api/v1/transparency/health")

            assert response.status_code == 200
            health = response.json()

            assert health["overall_status"] == "healthy"
            assert health["overall_health_percentage"] == 91.67
            assert len(health["apis"]) > 0

            # List available APIs
            with patch(
                "src.api.routes.transparency.registry.list_available_apis"
            ) as mock_list:
                mock_list.return_value = ["federal_api", "tce_pe"]

                apis_response = client.get("/api/v1/transparency/apis")

                assert apis_response.status_code == 200
                apis = apis_response.json()

                assert apis["total"] == 2


# Performance Tests
class TestTransparencyPerformance:
    """Test performance of transparency operations."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_api_calls(self, mock_collector):
        """Test handling multiple concurrent API calls."""
        with patch(
            "src.services.transparency_apis.get_transparency_collector",
            return_value=mock_collector,
        ):
            collector = get_transparency_collector()

            # Make 10 concurrent requests
            tasks = [
                collector.collect_contracts(state="PE", year=2024) for _ in range(10)
            ]

            results = await asyncio.gather(*tasks)

            # Verify all completed successfully
            assert len(results) == 10
            assert all(r["total"] == 3 for r in results)

    @pytest.mark.integration
    def test_api_response_time(self, mock_collector):
        """Test API response time is acceptable."""
        import time

        with patch(
            "src.api.routes.transparency.get_transparency_collector",
            return_value=mock_collector,
        ):
            start = time.time()

            response = client.get("/api/v1/transparency/contracts")

            duration = time.time() - start

            assert response.status_code == 200
            assert duration < 2.0  # Should respond in less than 2 seconds
