"""
Complete unit tests for Maria Quitéria Agent - Security and defense analysis specialist.
Tests security assessments, defense planning, and protection strategies.
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.agents.maria_quiteria import MariaQuiteriaAgent
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus

@pytest.fixture 
def mock_security_service():
    service = AsyncMock()
    service.assess_security_risks.return_value = {
        "risk_level": "medium",
        "threat_assessment": {"cyber": 0.65, "physical": 0.45, "social": 0.55},
        "vulnerabilities": [{"type": "data_breach", "severity": "high"}],
        "recommendations": ["Implement multi-factor authentication", "Regular security audits"]
    }
    return service

@pytest.fixture
def maria_quiteria_agent(mock_security_service):
    with patch("src.agents.maria_quiteria.SecurityService", return_value=mock_security_service):
        return MariaQuiteriaAgent(security_threshold=0.8)

class TestMariaQuiteriaAgent:
    @pytest.mark.unit
    def test_agent_initialization(self, maria_quiteria_agent):
        assert maria_quiteria_agent.name == "MariaQuiteria"
        assert "security_assessment" in maria_quiteria_agent.capabilities
        assert "defense_planning" in maria_quiteria_agent.capabilities
        assert "threat_analysis" in maria_quiteria_agent.capabilities
    
    @pytest.mark.unit
    async def test_security_risk_assessment(self, maria_quiteria_agent):
        context = AgentContext(investigation_id="security-test")
        message = AgentMessage(
            sender="test", recipient="MariaQuiteria", action="assess_security_risks",
            payload={"system": "transparency_portal", "scope": "comprehensive"}
        )
        response = await maria_quiteria_agent.process(message, context)
        assert response.status == AgentStatus.COMPLETED
        assert "security_assessment" in response.result
        assert response.result["security_assessment"]["risk_level"] == "medium"
    
    @pytest.mark.unit
    async def test_threat_analysis(self, maria_quiteria_agent):
        context = AgentContext(investigation_id="threat-test")
        message = AgentMessage(
            sender="test", recipient="MariaQuiteria", action="analyze_threats",
            payload={"threat_types": ["cyber", "physical", "social"]}
        )
        response = await maria_quiteria_agent.process(message, context)
        assert response.status == AgentStatus.COMPLETED
        assert "threat_analysis" in response.result