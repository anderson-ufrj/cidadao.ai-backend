"""
Unit tests for Ayrton Senna Agent - Performance optimization specialist.
Tests system performance, optimization strategies, and efficiency analysis.
"""

from unittest.mock import AsyncMock, patch

import pytest

from src.agents.ayrton_senna import (
    SemanticRouter,
)
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus


@pytest.fixture
def mock_performance_monitor():
    """Mock performance monitoring service."""
    monitor = AsyncMock()
    monitor.get_system_metrics.return_value = {
        "cpu_usage": 0.65,
        "memory_usage": 0.72,
        "response_time": 150.5,
        "throughput": 1200,
    }
    return monitor


@pytest.fixture
def ayrton_agent(mock_performance_monitor):
    """Create Ayrton Senna agent with mocked dependencies."""
    with patch(
        "src.agents.ayrton_senna.PerformanceMonitor",
        return_value=mock_performance_monitor,
    ):
        agent = SemanticRouter()
        return agent


class TestSemanticRouter:
    """Test suite for Ayrton Senna (Performance Agent)."""

    @pytest.mark.unit
    def test_agent_initialization(self, ayrton_agent):
        """Test Ayrton Senna agent initialization."""
        assert ayrton_agent.name == "AyrtonSenna"
        assert "performance_optimization" in ayrton_agent.capabilities
        assert "system_analysis" in ayrton_agent.capabilities

    @pytest.mark.unit
    async def test_performance_analysis(self, ayrton_agent):
        """Test system performance analysis."""
        context = AgentContext(investigation_id="performance-test")
        message = AgentMessage(
            sender="test",
            recipient="AyrtonSenna",
            action="analyze_performance",
            payload={"system_id": "api_system"},
        )

        response = await ayrton_agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert "performance_analysis" in response.result

    @pytest.mark.unit
    async def test_optimization_recommendations(self, ayrton_agent):
        """Test optimization recommendations."""
        context = AgentContext(investigation_id="optimization-test")
        message = AgentMessage(
            sender="test",
            recipient="AyrtonSenna",
            action="recommend_optimizations",
            payload={"target_improvement": 0.25},
        )

        response = await ayrton_agent.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert "optimization_recommendations" in response.result
