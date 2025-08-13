"""
Unit tests for Drummond Agent - Literary and communication analysis specialist.
"""

import pytest
from unittest.mock import AsyncMock
from src.agents.drummond import DrummondAgent
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus

@pytest.fixture
def drummond_agent():
    return DrummondAgent()

class TestDrummondAgent:
    @pytest.mark.unit
    def test_agent_initialization(self, drummond_agent):
        assert drummond_agent.name == "Drummond"
        assert "communication_analysis" in drummond_agent.capabilities
    
    @pytest.mark.unit
    async def test_communication_analysis(self, drummond_agent):
        context = AgentContext(investigation_id="comm-test")
        message = AgentMessage(
            sender="test", recipient="Drummond", action="analyze_communication",
            payload={"document_id": "doc_001"}
        )
        response = await drummond_agent.process(message, context)
        assert response.status == AgentStatus.COMPLETED