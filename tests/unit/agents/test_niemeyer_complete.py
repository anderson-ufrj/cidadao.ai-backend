"""
Complete unit tests for Niemeyer Agent - Infrastructure and architecture analysis specialist.
Tests infrastructure assessment, architectural planning, and urban development analysis.
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.agents.niemeyer import NiemeyerAgent
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus

@pytest.fixture
def mock_infrastructure_service():
    service = AsyncMock()
    service.assess_infrastructure.return_value = {
        "infrastructure_health": {
            "transportation": 0.65,
            "utilities": 0.72,
            "communications": 0.88,
            "public_buildings": 0.58
        },
        "investment_efficiency": 0.67,
        "maintenance_needs": [
            {"category": "roads", "urgency": "high", "cost": 50000000},
            {"category": "bridges", "urgency": "medium", "cost": 25000000}
        ],
        "architectural_quality": 0.74
    }
    return service

@pytest.fixture
def niemeyer_agent(mock_infrastructure_service):
    with patch("src.agents.niemeyer.InfrastructureService", return_value=mock_infrastructure_service):
        return NiemeyerAgent(infrastructure_threshold=0.7)

class TestNiemeyerAgent:
    @pytest.mark.unit
    def test_agent_initialization(self, niemeyer_agent):
        assert niemeyer_agent.name == "Niemeyer"
        assert "infrastructure_analysis" in niemeyer_agent.capabilities
        assert "architectural_assessment" in niemeyer_agent.capabilities
        assert "urban_planning_evaluation" in niemeyer_agent.capabilities
        assert niemeyer_agent.infrastructure_threshold == 0.7
    
    @pytest.mark.unit
    async def test_infrastructure_assessment(self, niemeyer_agent):
        context = AgentContext(investigation_id="infra-test")
        message = AgentMessage(
            sender="test", recipient="Niemeyer", action="assess_infrastructure",
            payload={"region": "metropolitan", "categories": ["transport", "utilities"]}
        )
        response = await niemeyer_agent.process(message, context)
        assert response.status == AgentStatus.COMPLETED
        assert "infrastructure_assessment" in response.result
        assert response.result["infrastructure_assessment"]["investment_efficiency"] == 0.67
    
    @pytest.mark.unit
    async def test_architectural_quality_analysis(self, niemeyer_agent):
        context = AgentContext(investigation_id="architecture-test")
        message = AgentMessage(
            sender="test", recipient="Niemeyer", action="analyze_architectural_quality",
            payload={"projects": ["public_hospital", "school_complex"]}
        )
        response = await niemeyer_agent.process(message, context)
        assert response.status == AgentStatus.COMPLETED
        assert "architectural_analysis" in response.result