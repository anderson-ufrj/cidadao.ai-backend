"""
Unit tests for Zumbi Agent - Resistance and freedom analysis specialist.
"""

import pytest
from unittest.mock import AsyncMock
from src.agents.zumbi import ZumbiAgent
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus

@pytest.fixture
def zumbi_agent():
    return ZumbiAgent()

class TestZumbiAgent:
    @pytest.mark.unit
    def test_agent_initialization(self, zumbi_agent):
        assert zumbi_agent.name == "Zumbi"
        assert "resistance_analysis" in zumbi_agent.capabilities
    
    @pytest.mark.unit
    async def test_resistance_analysis(self, zumbi_agent):
        context = AgentContext(investigation_id="resistance-test")
        message = AgentMessage(
            sender="test", recipient="Zumbi", action="analyze_resistance_patterns",
            payload={"movement_id": "social_movement_001"}
        )
        response = await zumbi_agent.process(message, context)
        assert response.status == AgentStatus.COMPLETED