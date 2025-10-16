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
