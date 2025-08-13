"""
Unit tests for Lampião Agent - Regional and cultural analysis specialist.
"""

import pytest
from unittest.mock import AsyncMock
from src.agents.lampiao import LampiaoAgent
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus

@pytest.fixture
def lampiao_agent():
    return LampiaoAgent()

class TestLampiaoAgent:
    @pytest.mark.unit
    def test_agent_initialization(self, lampiao_agent):
        assert lampiao_agent.name == "Lampião"
        assert "regional_analysis" in lampiao_agent.capabilities
    
    @pytest.mark.unit
    async def test_regional_analysis(self, lampiao_agent):
        context = AgentContext(investigation_id="regional-test")
        message = AgentMessage(
            sender="test", recipient="Lampião", action="analyze_regional_patterns",
            payload={"region": "northeast"}
        )
        response = await lampiao_agent.process(message, context)
        assert response.status == AgentStatus.COMPLETED