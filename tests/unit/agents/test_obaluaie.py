"""
Complete unit tests for Obaluaiê Agent - Healing and recovery analysis specialist.
Tests recovery patterns, healing processes, and restoration strategies.
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.agents.obaluaie import ObaluaieAgent
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus

@pytest.fixture
def mock_healing_service():
    service = AsyncMock()
    service.analyze_recovery_patterns.return_value = {
        "recovery_metrics": {
            "economic_recovery_rate": 0.67,
            "social_healing_index": 0.72,
            "institutional_trust_recovery": 0.58
        },
        "healing_strategies": [
            {"strategy": "transparency_increase", "effectiveness": 0.78},
            {"strategy": "community_engagement", "effectiveness": 0.65}
        ],
        "recovery_timeline": {"estimated_months": 18, "confidence": 0.73}
    }
    return service

@pytest.fixture
def obaluaie_agent(mock_healing_service):
    with patch("src.agents.obaluaie.HealingAnalysisService", return_value=mock_healing_service):
        return ObaluaieAgent(healing_threshold=0.7)

class TestObaluaieAgent:
    @pytest.mark.unit
    def test_agent_initialization(self, obaluaie_agent):
        assert obaluaie_agent.name == "Obaluaiê"
        assert "healing_analysis" in obaluaie_agent.capabilities
        assert "recovery_planning" in obaluaie_agent.capabilities
        assert "restoration_strategies" in obaluaie_agent.capabilities
        assert obaluaie_agent.healing_threshold == 0.7
    
    @pytest.mark.unit
    async def test_recovery_pattern_analysis(self, obaluaie_agent):
        context = AgentContext(investigation_id="recovery-test")
        message = AgentMessage(
            sender="test", recipient="Obaluaiê", action="analyze_recovery_patterns",
            payload={"crisis_type": "corruption_scandal", "recovery_dimensions": ["trust", "economic"]}
        )
        response = await obaluaie_agent.process(message, context)
        assert response.status == AgentStatus.COMPLETED
        assert "recovery_analysis" in response.result
        assert response.result["recovery_analysis"]["social_healing_index"] == 0.72
    
    @pytest.mark.unit
    async def test_healing_strategy_recommendation(self, obaluaie_agent):
        context = AgentContext(investigation_id="healing-test")
        message = AgentMessage(
            sender="test", recipient="Obaluaiê", action="recommend_healing_strategies",
            payload={"affected_areas": ["public_trust", "institutional_credibility"]}
        )
        response = await obaluaie_agent.process(message, context)
        assert response.status == AgentStatus.COMPLETED
        assert "healing_strategies" in response.result