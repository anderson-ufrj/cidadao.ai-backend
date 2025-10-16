"""
Complete unit tests for Nana Agent - Healthcare and wellbeing analysis specialist.
Tests health metrics, medical data analysis, and wellness indicators.
"""

from unittest.mock import AsyncMock, patch

import pytest

from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus
from src.agents.nana import ContextMemoryAgent


@pytest.fixture
def mock_health_service():
    service = AsyncMock()
    service.analyze_health_metrics.return_value = {
        "health_indicators": {
            "infant_mortality": 0.012,
            "life_expectancy": 76.2,
            "vaccination_coverage": 0.89,
        },
        "healthcare_access": 0.74,
        "quality_scores": {"primary_care": 0.68, "emergency_care": 0.82},
        "disparities": {"urban_rural": 0.15, "income_based": 0.23},
    }
    return service


@pytest.fixture
def nana_agent(mock_health_service):
    with patch("src.agents.nana.HealthDataService", return_value=mock_health_service):
        return ContextMemoryAgent()


class TestContextMemoryAgent:
    @pytest.mark.unit
    def test_agent_initialization(self, nana_agent):
        assert nana_agent.name == "Nana"
        assert "health_analysis" in nana_agent.capabilities
        assert "medical_data_processing" in nana_agent.capabilities
        assert "wellness_assessment" in nana_agent.capabilities
        assert nana_agent.health_threshold == 0.75

    @pytest.mark.unit
    async def test_health_metrics_analysis(self, nana_agent):
        context = AgentContext(investigation_id="health-test")
        message = AgentMessage(
            sender="test",
            recipient="Nana",
            action="analyze_health_metrics",
            payload={"region": "southeast", "indicators": ["mortality", "vaccination"]},
        )
        response = await nana_agent.process(message, context)
        assert response.status == AgentStatus.COMPLETED
        assert "health_analysis" in response.result
        assert response.result["health_analysis"]["healthcare_access"] == 0.74

    @pytest.mark.unit
    async def test_healthcare_disparity_analysis(self, nana_agent):
        context = AgentContext(investigation_id="disparity-test")
        message = AgentMessage(
            sender="test",
            recipient="Nana",
            action="analyze_health_disparities",
            payload={"dimensions": ["geographic", "socioeconomic", "demographic"]},
        )
        response = await nana_agent.process(message, context)
        assert response.status == AgentStatus.COMPLETED
        assert "disparity_analysis" in response.result
