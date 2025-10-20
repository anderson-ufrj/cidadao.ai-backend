"""
Unit tests for Zumbi Agent (InvestigatorAgent) - Anomaly detection specialist.
"""

from unittest.mock import AsyncMock, patch

import pytest

from src.agents.deodoro import AgentContext, AgentMessage, AgentResponse, AgentStatus
from src.agents.zumbi import InvestigatorAgent


@pytest.fixture
def zumbi_agent():
    """Create an InvestigatorAgent instance for testing."""
    return InvestigatorAgent(
        price_anomaly_threshold=2.5,
        concentration_threshold=0.7,
        duplicate_similarity_threshold=0.85,
    )


@pytest.fixture
def mock_transparency_collector():
    """Mock TransparencyDataCollector."""
    collector = AsyncMock()
    collector.collect_contracts.return_value = {
        "contracts": [
            {
                "id": "123/2024",
                "valorInicial": 100000.0,
                "dataAssinatura": "01/01/2024",
                "orgao": {"nome": "Ministério Teste"},
                "fornecedor": {"nome": "Empresa ABC", "cnpj": "12345678901234"},
                "objeto": "Contrato de teste",
            }
        ],
        "total": 1,
        "sources": ["Federal Portal"],
        "errors": [],
    }
    return collector


class TestZumbiAgent:
    @pytest.mark.unit
    def test_agent_initialization(self, zumbi_agent):
        """Test that the agent is properly initialized."""
        assert zumbi_agent.name == "Zumbi"
        assert "price_anomaly_detection" in zumbi_agent.capabilities
        assert "spectral_analysis" in zumbi_agent.capabilities
        assert zumbi_agent.price_threshold == 2.5
        assert zumbi_agent.concentration_threshold == 0.7

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_initialize(self, zumbi_agent):
        """Test agent initialization method."""
        await zumbi_agent.initialize()
        # Should complete without errors

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_shutdown(self, zumbi_agent):
        """Test agent shutdown method."""
        await zumbi_agent.shutdown()
        # Should complete without errors

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_investigation(
        self, zumbi_agent, mock_transparency_collector
    ):
        """Test processing an investigation request."""
        with patch(
            "src.agents.zumbi.get_transparency_collector",
            return_value=mock_transparency_collector,
        ):
            context = AgentContext(investigation_id="test-123")
            message = AgentMessage(
                sender="test",
                recipient="Zumbi",
                action="investigate",
                payload={"query": "contratos suspeitos", "max_records": 10},
            )

            response = await zumbi_agent.process(message, context)

            assert isinstance(response, AgentResponse)
            assert response.agent_name == "Zumbi"
            assert response.status == AgentStatus.COMPLETED
            assert "anomalies" in response.result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_invalid_action(self, zumbi_agent):
        """Test processing with invalid action."""
        context = AgentContext(investigation_id="test-123")
        message = AgentMessage(
            sender="test", recipient="Zumbi", action="invalid_action", payload={}
        )

        response = await zumbi_agent.process(message, context)

        assert response.status == AgentStatus.ERROR
        assert "Unsupported action" in response.error


class TestZumbiPriceAnomalies:
    """Test suite for price anomaly detection."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_price_anomalies_with_outliers(self, zumbi_agent):
        """Test detection of price outliers using z-score analysis."""
        contracts = []

        # Create 20 contracts with normal prices around 100k
        for i in range(20):
            contracts.append(
                {
                    "id": f"CONTRACT-{i}",
                    "valorInicial": 100000.0 + (i * 1000),  # Normal range
                    "objeto": f"Contrato normal {i}",
                    "fornecedor": {"nome": f"Fornecedor {i}", "cnpj": f"{i:014d}"},
                    "_org_code": "ORG001",
                }
            )

        # Add 3 outliers with very high values
        contracts.append(
            {
                "id": "CONTRACT-OUTLIER-1",
                "valorInicial": 500000.0,  # 5x average
                "objeto": "Contrato suspeito 1",
                "fornecedor": {"nome": "Fornecedor X", "cnpj": "99999999999999"},
                "_org_code": "ORG001",
            }
        )
        contracts.append(
            {
                "id": "CONTRACT-OUTLIER-2",
                "valorInicial": 600000.0,  # 6x average
                "objeto": "Contrato suspeito 2",
                "fornecedor": {"nome": "Fornecedor Y", "cnpj": "88888888888888"},
                "_org_code": "ORG001",
            }
        )

        context = AgentContext(investigation_id="test-price-anomalies")
        anomalies = await zumbi_agent._detect_price_anomalies(contracts, context)

        assert len(anomalies) >= 2  # Should detect at least the 2 major outliers
        assert all(a.anomaly_type == "price_anomaly" for a in anomalies)
        assert all(a.confidence > 0.5 for a in anomalies)
        assert all("z_score" in a.evidence for a in anomalies)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_price_anomalies_insufficient_data(self, zumbi_agent):
        """Test that price detection requires minimum 10 contracts."""
        contracts = [
            {"id": f"C{i}", "valorInicial": 100000.0}
            for i in range(5)  # Only 5 contracts
        ]

        context = AgentContext(investigation_id="test-insufficient")
        anomalies = await zumbi_agent._detect_price_anomalies(contracts, context)

        assert len(anomalies) == 0  # Not enough data

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_price_anomalies_all_normal(self, zumbi_agent):
        """Test that no anomalies are detected when all prices are normal."""
        contracts = [
            {"id": f"C{i}", "valorInicial": 100000.0 + (i * 100)} for i in range(15)
        ]

        context = AgentContext(investigation_id="test-normal")
        anomalies = await zumbi_agent._detect_price_anomalies(contracts, context)

        assert len(anomalies) == 0  # All values within normal range

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_price_anomalies_with_valor_global(self, zumbi_agent):
        """Test price detection using valorGlobal when valorInicial is missing."""
        contracts = []

        # Normal contracts with valorGlobal
        for i in range(15):
            contracts.append(
                {
                    "id": f"C{i}",
                    "valorGlobal": 100000.0 + (i * 1000),
                    "objeto": f"Contrato {i}",
                }
            )

        # Add outlier
        contracts.append(
            {
                "id": "OUTLIER",
                "valorGlobal": 500000.0,
                "objeto": "Contrato suspeito",
            }
        )

        context = AgentContext(investigation_id="test-valor-global")
        anomalies = await zumbi_agent._detect_price_anomalies(contracts, context)

        assert len(anomalies) >= 1
        assert anomalies[0].evidence["contract_value"] == 500000.0


class TestZumbiVendorConcentration:
    """Test suite for vendor concentration detection."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_vendor_concentration_high(self, zumbi_agent):
        """Test detection of excessive vendor concentration (>70%)."""
        contracts = []

        # Vendor A gets 80% of contracts (8 out of 10)
        for i in range(8):
            contracts.append(
                {
                    "id": f"C{i}",
                    "valorInicial": 100000.0,
                    "fornecedor": {"nome": "Vendor A", "cnpj": "11111111111111"},
                }
            )

        # Vendor B gets 20%
        for i in range(2):
            contracts.append(
                {
                    "id": f"C{8+i}",
                    "valorInicial": 25000.0,
                    "fornecedor": {"nome": "Vendor B", "cnpj": "22222222222222"},
                }
            )

        context = AgentContext(investigation_id="test-concentration")
        anomalies = await zumbi_agent._detect_vendor_concentration(contracts, context)

        assert len(anomalies) >= 1
        assert anomalies[0].anomaly_type == "vendor_concentration"
        assert anomalies[0].evidence["concentration_percentage"] > 70
        assert "Vendor A" in anomalies[0].description

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_vendor_concentration_normal(self, zumbi_agent):
        """Test that normal vendor distribution doesn't trigger alerts."""
        contracts = []

        # 5 vendors, each with 20% (normal distribution)
        for vendor_idx in range(5):
            for contract_idx in range(2):
                contracts.append(
                    {
                        "id": f"C-{vendor_idx}-{contract_idx}",
                        "valorInicial": 100000.0,
                        "fornecedor": {
                            "nome": f"Vendor {vendor_idx}",
                            "cnpj": f"{vendor_idx:014d}",
                        },
                    }
                )

        context = AgentContext(investigation_id="test-normal-distribution")
        anomalies = await zumbi_agent._detect_vendor_concentration(contracts, context)

        assert len(anomalies) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_vendor_concentration_single_vendor(self, zumbi_agent):
        """Test detection when single vendor has 100% of contracts."""
        contracts = [
            {
                "id": f"C{i}",
                "valorInicial": 100000.0,
                "fornecedor": {"nome": "Monopoly Inc", "cnpj": "99999999999999"},
            }
            for i in range(10)
        ]

        context = AgentContext(investigation_id="test-monopoly")
        anomalies = await zumbi_agent._detect_vendor_concentration(contracts, context)

        assert len(anomalies) == 1
        assert anomalies[0].evidence["concentration_percentage"] == 100.0
        assert anomalies[0].confidence == 1.0


class TestZumbiTemporalAnomalies:
    """Test suite for temporal pattern detection."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_temporal_anomalies_with_spike(self, zumbi_agent):
        """Test detection of unusual activity spikes in specific periods."""
        contracts = []

        # Normal activity: 5 contracts per month for 6 months
        for month in range(1, 7):
            for i in range(5):
                contracts.append(
                    {
                        "id": f"C-{month}-{i}",
                        "dataAssinatura": f"15/{month:02d}/2024",
                        "valorInicial": 100000.0,
                    }
                )

        # Spike: 25 contracts in July (5x normal)
        for i in range(25):
            contracts.append(
                {
                    "id": f"C-SPIKE-{i}",
                    "dataAssinatura": "15/07/2024",
                    "valorInicial": 100000.0,
                }
            )

        context = AgentContext(investigation_id="test-temporal-spike")
        anomalies = await zumbi_agent._detect_temporal_anomalies(contracts, context)

        assert len(anomalies) >= 1
        assert anomalies[0].anomaly_type == "temporal_patterns"
        assert "2024-07" in anomalies[0].description or "2024-07" in str(
            anomalies[0].evidence
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_temporal_anomalies_normal_distribution(self, zumbi_agent):
        """Test that evenly distributed contracts don't trigger alerts."""
        contracts = []

        # 10 contracts per month for 6 months (consistent pattern)
        for month in range(1, 7):
            for i in range(10):
                contracts.append(
                    {
                        "id": f"C-{month}-{i}",
                        "dataAssinatura": f"15/{month:02d}/2024",
                        "valorInicial": 100000.0,
                    }
                )

        context = AgentContext(investigation_id="test-temporal-normal")
        anomalies = await zumbi_agent._detect_temporal_anomalies(contracts, context)

        assert len(anomalies) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_temporal_anomalies_insufficient_periods(self, zumbi_agent):
        """Test that insufficient time periods don't trigger analysis."""
        contracts = [
            {"id": "C1", "dataAssinatura": "15/01/2024", "valorInicial": 100000.0},
            {"id": "C2", "dataAssinatura": "15/02/2024", "valorInicial": 100000.0},
        ]

        context = AgentContext(investigation_id="test-insufficient-periods")
        anomalies = await zumbi_agent._detect_temporal_anomalies(contracts, context)

        assert len(anomalies) == 0  # Need at least 3 periods


class TestZumbiDuplicateContracts:
    """Test suite for duplicate contract detection."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_duplicate_contracts_high_similarity(self, zumbi_agent):
        """Test detection of contracts with very similar descriptions."""
        contracts = [
            {
                "id": "C1",
                "objeto": "Aquisição de equipamentos de informática computadores servidores notebooks para setor administrativo",
                "valorInicial": 50000.0,
            },
            {
                "id": "C2",
                "objeto": "Aquisição de equipamentos de informática computadores servidores notebooks para setor administrativo",
                "valorInicial": 52000.0,
            },
        ]

        context = AgentContext(investigation_id="test-duplicates")
        anomalies = await zumbi_agent._detect_duplicate_contracts(contracts, context)

        assert len(anomalies) >= 1
        assert anomalies[0].anomaly_type == "duplicate_contracts"
        assert anomalies[0].evidence["similarity_score"] >= 0.85

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_duplicate_contracts_different(self, zumbi_agent):
        """Test that different contracts are not flagged as duplicates."""
        contracts = [
            {
                "id": "C1",
                "objeto": "Aquisição de equipamentos de informática",
                "valorInicial": 50000.0,
            },
            {
                "id": "C2",
                "objeto": "Contratação de serviços de limpeza predial",
                "valorInicial": 30000.0,
            },
        ]

        context = AgentContext(investigation_id="test-different")
        anomalies = await zumbi_agent._detect_duplicate_contracts(contracts, context)

        assert len(anomalies) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_duplicate_contracts_short_descriptions(self, zumbi_agent):
        """Test that very short descriptions are skipped."""
        contracts = [
            {"id": "C1", "objeto": "Compra", "valorInicial": 1000.0},  # Too short
            {"id": "C2", "objeto": "Venda", "valorInicial": 1000.0},  # Too short
        ]

        context = AgentContext(investigation_id="test-short")
        anomalies = await zumbi_agent._detect_duplicate_contracts(contracts, context)

        assert len(anomalies) == 0  # Short descriptions skipped


class TestZumbiPaymentAnomalies:
    """Test suite for payment anomaly detection."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_payment_anomalies_large_discrepancy(self, zumbi_agent):
        """Test detection of large discrepancies between initial and global values."""
        contracts = [
            {
                "id": "C1",
                "valorInicial": 100000.0,
                "valorGlobal": 250000.0,  # 150% increase (ratio = 0.6)
                "objeto": "Contrato com aditivos suspeitos",
                "fornecedor": {"nome": "Fornecedor X"},
            }
        ]

        context = AgentContext(investigation_id="test-payment-discrepancy")
        anomalies = await zumbi_agent._detect_payment_anomalies(contracts, context)

        assert len(anomalies) >= 1
        assert anomalies[0].anomaly_type == "payment_patterns"
        assert anomalies[0].evidence["discrepancy_ratio"] > 0.5

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_payment_anomalies_normal_values(self, zumbi_agent):
        """Test that similar initial and global values don't trigger alerts."""
        contracts = [
            {
                "id": "C1",
                "valorInicial": 100000.0,
                "valorGlobal": 105000.0,  # Only 5% difference
                "objeto": "Contrato normal",
            }
        ]

        context = AgentContext(investigation_id="test-payment-normal")
        anomalies = await zumbi_agent._detect_payment_anomalies(contracts, context)

        assert len(anomalies) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_payment_anomalies_missing_values(self, zumbi_agent):
        """Test handling of contracts with missing payment values."""
        contracts = [
            {"id": "C1", "objeto": "Contrato sem valores"},  # Missing both values
            {"id": "C2", "valorInicial": 100000.0},  # Missing valorGlobal
        ]

        context = AgentContext(investigation_id="test-missing-values")
        anomalies = await zumbi_agent._detect_payment_anomalies(contracts, context)

        assert len(anomalies) == 0  # Should handle gracefully


class TestZumbiSpectralAnomalies:
    """Test suite for spectral analysis and FFT-based detection."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_spectral_anomalies_insufficient_data(self, zumbi_agent):
        """Test that spectral analysis requires minimum 30 data points."""
        contracts = [
            {
                "id": f"C{i}",
                "dataAssinatura": f"{i+1:02d}/01/2024",
                "valorInicial": 100000.0,
            }
            for i in range(10)  # Only 10 contracts
        ]

        context = AgentContext(investigation_id="test-spectral-insufficient")
        anomalies = await zumbi_agent._detect_spectral_anomalies(contracts, context)

        # Should return empty or handle gracefully
        assert isinstance(anomalies, list)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_spectral_anomalies_with_sufficient_data(self, zumbi_agent):
        """Test spectral analysis with sufficient data points."""
        contracts = []

        # Create 50 contracts over 50 days with periodic pattern
        for i in range(50):
            # Add periodic spike every 7 days (weekly pattern)
            value = 100000.0
            if i % 7 == 0:
                value = 200000.0  # Weekly spike

            contracts.append(
                {
                    "id": f"C{i}",
                    "dataAssinatura": f"{(i % 28) + 1:02d}/01/2024",
                    "valorInicial": value,
                }
            )

        context = AgentContext(investigation_id="test-spectral-sufficient")
        anomalies = await zumbi_agent._detect_spectral_anomalies(contracts, context)

        # Should complete analysis without errors
        assert isinstance(anomalies, list)


class TestZumbiIntegration:
    """Integration tests for Zumbi agent with multiple detection methods."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_multiple_anomaly_types_detected(self, zumbi_agent):
        """Test that agent can detect multiple types of anomalies simultaneously."""
        contracts = []

        # Add contracts with price anomalies
        # Use only 2 vendors (Vendor 1 and Vendor 2) for initial contracts
        for i in range(10):
            contracts.append(
                {
                    "id": f"NORMAL-{i}",
                    "valorInicial": 100000.0,
                    "dataAssinatura": f"15/0{(i % 5) + 1}/2024",
                    "fornecedor": {
                        "nome": f"Vendor {(i % 2) + 1}",
                        "cnpj": f"{(i % 2) + 1:014d}",
                    },
                    "objeto": f"Contrato normal {i}",
                }
            )

        contracts.append(
            {
                "id": "PRICE-OUTLIER",
                "valorInicial": 500000.0,  # 5x average
                "dataAssinatura": "15/01/2024",
                "fornecedor": {"nome": "Vendor 0", "cnpj": "00000000000000"},
                "objeto": "Contrato suspeito de superfaturamento",
            }
        )

        # Add vendor concentration (Vendor 0 gets 75% of total value)
        for i in range(30):
            contracts.append(
                {
                    "id": f"CONCENTRATION-{i}",
                    "valorInicial": 100000.0,
                    "dataAssinatura": "15/02/2024",
                    "fornecedor": {"nome": "Vendor 0", "cnpj": "00000000000000"},
                    "objeto": f"Contrato concentrado {i}",
                }
            )

        context = AgentContext(investigation_id="test-multi-anomaly")

        # Test each detection method
        price_anomalies = await zumbi_agent._detect_price_anomalies(contracts, context)
        vendor_anomalies = await zumbi_agent._detect_vendor_concentration(
            contracts, context
        )

        # Should detect both types
        assert len(price_anomalies) > 0
        assert len(vendor_anomalies) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_anomaly_result_structure(self, zumbi_agent):
        """Test that all anomaly results have required fields."""
        contracts = [
            {
                "id": f"C{i}",
                "valorInicial": 100000.0 if i < 10 else 500000.0,
                "fornecedor": {"nome": "Vendor A", "cnpj": "11111111111111"},
                "objeto": "Contrato de teste",
                "_org_code": "ORG001",
            }
            for i in range(12)
        ]

        context = AgentContext(investigation_id="test-structure")
        anomalies = await zumbi_agent._detect_price_anomalies(contracts, context)

        for anomaly in anomalies:
            # Verify all required fields exist
            assert hasattr(anomaly, "anomaly_type")
            assert hasattr(anomaly, "severity")
            assert hasattr(anomaly, "confidence")
            assert hasattr(anomaly, "description")
            assert hasattr(anomaly, "explanation")
            assert hasattr(anomaly, "evidence")
            assert hasattr(anomaly, "recommendations")
            assert isinstance(anomaly.recommendations, list)
            assert len(anomaly.recommendations) > 0


class TestZumbiSummaryGeneration:
    """Test suite for summary generation functionality."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_summary_with_no_anomalies(self, zumbi_agent):
        """Test summary generation when no anomalies found."""
        context = AgentContext(investigation_id="test-summary-empty")
        results = []

        summary = await zumbi_agent.generate_summary(results, context)

        assert "Nenhuma anomalia" in summary or "sem anomalias" in summary.lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_summary_with_high_severity(self, zumbi_agent):
        """Test summary generation with high severity anomalies."""
        from src.agents.zumbi import AnomalyResult

        context = AgentContext(investigation_id="test-summary-high")
        results = [
            AnomalyResult(
                anomaly_type="price_anomaly",
                severity=0.9,
                confidence=0.85,
                description="Alto superfaturamento",
                explanation="Valor muito acima da média",
                evidence={"value": 500000},
                recommendations=["Investigar imediatamente"],
                affected_entities=[{"id": "C1", "nome": "Contrato 1"}],
            ),
            AnomalyResult(
                anomaly_type="vendor_concentration",
                severity=0.8,
                confidence=0.9,
                description="Monopolização",
                explanation="Único fornecedor",
                evidence={"concentration": 100},
                recommendations=["Revisar processo licitatório"],
                affected_entities=[{"id": "F1", "nome": "Fornecedor 1"}],
            ),
        ]

        summary = await zumbi_agent.generate_summary(results, context)

        assert "2" in summary
        assert "anomalia" in summary.lower()
        assert isinstance(summary, str)
        assert len(summary) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_summary_with_mixed_severity(self, zumbi_agent):
        """Test summary generation with mixed severity levels."""
        from src.agents.zumbi import AnomalyResult

        context = AgentContext(investigation_id="test-summary-mixed")
        results = [
            AnomalyResult(
                anomaly_type="price_anomaly",
                severity=0.9,  # High
                confidence=0.85,
                description="High severity",
                explanation="Test",
                evidence={},
                recommendations=["Test recommendation"],
                affected_entities=[],
            ),
            AnomalyResult(
                anomaly_type="temporal_patterns",
                severity=0.6,  # Medium
                confidence=0.7,
                description="Medium severity",
                explanation="Test",
                evidence={},
                recommendations=["Another recommendation"],
                affected_entities=[],
            ),
            AnomalyResult(
                anomaly_type="duplicate_contracts",
                severity=0.3,  # Low
                confidence=0.5,
                description="Low severity",
                explanation="Test",
                evidence={},
                recommendations=["Low priority action"],
                affected_entities=[],
            ),
        ]

        summary = await zumbi_agent.generate_summary(results, context)

        assert "3" in summary
        assert "anomalia" in summary.lower()
        assert isinstance(summary, str)
        assert len(summary) > 50  # Should have substantial content

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_summary_with_long_recommendation(self, zumbi_agent):
        """Test summary handles long recommendations correctly."""
        from src.agents.zumbi import AnomalyResult

        context = AgentContext(investigation_id="test-summary-long")
        long_recommendation = "A" * 150  # 150 chars - should be truncated

        results = [
            AnomalyResult(
                anomaly_type="price_anomaly",
                severity=0.8,
                confidence=0.9,
                description="Test",
                explanation="Test",
                evidence={},
                recommendations=[long_recommendation],
                affected_entities=[],
            )
        ]

        summary = await zumbi_agent.generate_summary(results, context)

        # Should have summary content
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "anomalia" in summary.lower() or "analysis" in summary.lower()


class TestZumbiEdgeCases:
    """Test suite for edge cases and error handling."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_price_anomalies_with_none_values(self, zumbi_agent):
        """Test price detection handles None values gracefully."""
        contracts = [
            {"id": "C1", "valorInicial": None, "valorGlobal": None},
            {"id": "C2", "valorInicial": 100000.0},
            {"id": "C3"},  # Missing value fields
        ]

        # Add more valid contracts to reach minimum
        for i in range(10):
            contracts.append({"id": f"VALID-{i}", "valorInicial": 100000.0})

        context = AgentContext(investigation_id="test-none-values")
        anomalies = await zumbi_agent._detect_price_anomalies(contracts, context)

        # Should handle gracefully without errors
        assert isinstance(anomalies, list)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_vendor_concentration_with_zero_total(self, zumbi_agent):
        """Test vendor concentration when total value is zero."""
        contracts = [
            {
                "id": "C1",
                "valorInicial": 0,
                "fornecedor": {"nome": "Vendor A", "cnpj": "111"},
            },
            {
                "id": "C2",
                "valorInicial": 0,
                "fornecedor": {"nome": "Vendor B", "cnpj": "222"},
            },
        ]

        context = AgentContext(investigation_id="test-zero-total")
        anomalies = await zumbi_agent._detect_vendor_concentration(contracts, context)

        # Should return empty list when total is zero
        assert len(anomalies) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_temporal_anomalies_with_invalid_dates(self, zumbi_agent):
        """Test temporal detection handles invalid dates."""
        contracts = [
            {"id": "C1", "dataAssinatura": "invalid-date", "valorInicial": 100000.0},
            {"id": "C2", "dataAssinatura": "99/99/9999", "valorInicial": 100000.0},
            {"id": "C3", "dataAssinatura": "", "valorInicial": 100000.0},
        ]

        # Add valid dates
        for month in range(1, 7):
            for i in range(5):
                contracts.append(
                    {
                        "id": f"VALID-{month}-{i}",
                        "dataAssinatura": f"15/{month:02d}/2024",
                        "valorInicial": 100000.0,
                    }
                )

        context = AgentContext(investigation_id="test-invalid-dates")
        anomalies = await zumbi_agent._detect_temporal_anomalies(contracts, context)

        # Should skip invalid dates and process valid ones
        assert isinstance(anomalies, list)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_duplicate_contracts_with_empty_objects(self, zumbi_agent):
        """Test duplicate detection handles empty object descriptions."""
        contracts = [
            {"id": "C1", "objeto": ""},
            {"id": "C2", "objeto": ""},
            {"id": "C3"},  # Missing objeto field
        ]

        context = AgentContext(investigation_id="test-empty-objects")
        anomalies = await zumbi_agent._detect_duplicate_contracts(contracts, context)

        # Should skip empty/short descriptions
        assert len(anomalies) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_payment_anomalies_with_invalid_types(self, zumbi_agent):
        """Test payment detection handles invalid value types."""
        contracts = [
            {
                "id": "C1",
                "valorInicial": "not_a_number",
                "valorGlobal": "also_not_a_number",
            },
            {"id": "C2", "valorInicial": [], "valorGlobal": {}},
            {"id": "C3", "valorInicial": 100000.0, "valorGlobal": "invalid"},
        ]

        context = AgentContext(investigation_id="test-invalid-types")
        anomalies = await zumbi_agent._detect_payment_anomalies(contracts, context)

        # Should handle type errors gracefully
        assert isinstance(anomalies, list)


class TestZumbiProcessMethod:
    """Test suite for the main process method with different actions."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_with_unsupported_action(self, zumbi_agent):
        """Test process method with unsupported action."""
        context = AgentContext(investigation_id="test-unsupported")
        message = AgentMessage(
            sender="test",
            recipient="Zumbi",
            action="unsupported_action",
            payload={},
        )

        response = await zumbi_agent.process(message, context)

        assert response.status == AgentStatus.ERROR
        assert "Unsupported action" in response.error
