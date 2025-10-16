"""
Complete unit tests for Zumbi Agent - Resistance and freedom analysis specialist.
Tests resistance patterns, freedom indicators, and liberation strategies.
"""

from unittest.mock import AsyncMock, patch

import pytest

from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus
from src.agents.zumbi import InvestigatorAgent


@pytest.fixture
def mock_resistance_service():
    service = AsyncMock()
    service.analyze_resistance_patterns.return_value = {
        "resistance_indicators": {
            "civil_resistance_level": 0.68,
            "institutional_pushback": 0.45,
            "grassroots_organization": 0.72,
        },
        "freedom_metrics": {
            "press_freedom": 0.65,
            "assembly_rights": 0.78,
            "information_access": 0.82,
        },
        "liberation_strategies": [
            {"strategy": "transparency_campaigns", "effectiveness": 0.75},
            {"strategy": "community_mobilization", "effectiveness": 0.68},
        ],
    }
    return service


@pytest.fixture
def zumbi_agent(mock_resistance_service):
    with patch(
        "src.agents.zumbi.ResistanceService", return_value=mock_resistance_service
    ):
        return InvestigatorAgent()


class TestInvestigatorAgent:
    @pytest.mark.unit
    def test_agent_initialization(self, zumbi_agent):
        assert zumbi_agent.name == "Zumbi"
        assert "resistance_analysis" in zumbi_agent.capabilities
        assert "freedom_assessment" in zumbi_agent.capabilities
        assert "liberation_planning" in zumbi_agent.capabilities
        assert zumbi_agent.resistance_threshold == 0.6

    @pytest.mark.unit
    async def test_resistance_pattern_analysis(self, zumbi_agent):
        context = AgentContext(investigation_id="resistance-test")
        message = AgentMessage(
            sender="test",
            recipient="Zumbi",
            action="analyze_resistance_patterns",
            payload={"movement": "transparency_advocacy", "timeframe": "2020-2024"},
        )
        response = await zumbi_agent.process(message, context)
        assert response.status == AgentStatus.COMPLETED
        assert "resistance_analysis" in response.result
        assert response.result["resistance_analysis"]["civil_resistance_level"] == 0.68

    @pytest.mark.unit
    async def test_freedom_indicators_assessment(self, zumbi_agent):
        context = AgentContext(investigation_id="freedom-test")
        message = AgentMessage(
            sender="test",
            recipient="Zumbi",
            action="assess_freedom_indicators",
            payload={"dimensions": ["press", "assembly", "information"]},
        )
        response = await zumbi_agent.process(message, context)
        assert response.status == AgentStatus.COMPLETED
        assert "freedom_assessment" in response.result
