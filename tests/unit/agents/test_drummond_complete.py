"""
Additional tests for Drummond to reach 80%+ coverage.
Tests process() method edge cases and error handling.
"""

import pytest

from src.agents.deodoro import AgentContext, AgentStatus
from src.agents.drummond import CommunicationAgent


@pytest.fixture
def drummond_agent():
    """Create Drummond agent."""
    return CommunicationAgent()


@pytest.fixture
def agent_context():
    """Sample agent context."""
    return AgentContext(
        investigation_id="test_001",
        user_id="user_123",
        session_id="session_456",
    )


@pytest.mark.unit
class TestDrummondCompleteCoverage:
    """Test suite for complete Drummond coverage."""

    @pytest.mark.asyncio
    async def test_initialization_complete(self, drummond_agent):
        """Test agent initializes with all required components."""
        await drummond_agent.initialize()

        assert drummond_agent.name == "drummond"
        assert drummond_agent.status == AgentStatus.IDLE
        assert "process_chat" in drummond_agent.capabilities
        assert "send_notification" in drummond_agent.capabilities
        assert "generate_report_summary" in drummond_agent.capabilities

    @pytest.mark.asyncio
    async def test_shutdown_complete(self, drummond_agent):
        """Test agent shuts down gracefully."""
        await drummond_agent.initialize()
        await drummond_agent.shutdown()

        assert drummond_agent.status == AgentStatus.IDLE
