"""
Unit tests for Niemeyer Agent - Infrastructure and architecture analysis specialist.
"""


import pytest

from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus
from src.agents.niemeyer import NiemeyerAgent


@pytest.fixture
def niemeyer_agent():
    """Create Niemeyer agent."""
    return NiemeyerAgent()


class TestNiemeyerAgent:
    @pytest.mark.unit
    def test_agent_initialization(self, niemeyer_agent):
        assert niemeyer_agent.name == "Niemeyer"
        assert "infrastructure_analysis" in niemeyer_agent.capabilities

    @pytest.mark.unit
    async def test_infrastructure_analysis(self, niemeyer_agent):
        context = AgentContext(investigation_id="infra-test")
        message = AgentMessage(
            sender="test",
            recipient="Niemeyer",
            action="analyze_infrastructure",
            payload={"project_id": "infra_001"},
        )
        response = await niemeyer_agent.process(message, context)
        assert response.status == AgentStatus.COMPLETED
