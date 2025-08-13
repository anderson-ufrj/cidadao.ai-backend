"""
Unit tests for Dandara Agent - Social inclusion and equity analysis specialist.
Tests diversity metrics, inclusion analysis, and social impact assessment.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4

from src.agents.dandara import (
    DandaraAgent,
    InclusionMetric,
    DiversityAnalysis,
    EquityAssessment,
)
from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
)


@pytest.fixture
def mock_social_data_service():
    """Mock social data service."""
    service = AsyncMock()
    service.get_demographic_data.return_value = {
        "total_population": 10000000,
        "demographics": {
            "gender": {"female": 0.52, "male": 0.48},
            "race": {"white": 0.45, "black": 0.35, "mixed": 0.18, "other": 0.02},
            "age_groups": {"18-30": 0.25, "31-50": 0.35, "51+": 0.40}
        }
    }
    return service


@pytest.fixture
def dandara_agent(mock_social_data_service):
    """Create Dandara agent with mocked dependencies."""
    with patch("src.agents.dandara.SocialDataService", return_value=mock_social_data_service):
        agent = DandaraAgent(
            inclusion_threshold=0.7,
            diversity_target=0.8
        )
        return agent


class TestDandaraAgent:
    """Test suite for Dandara (Social Inclusion Agent)."""
    
    @pytest.mark.unit
    def test_agent_initialization(self, dandara_agent):
        """Test Dandara agent initialization."""
        assert dandara_agent.name == "Dandara"
        assert "social_inclusion" in dandara_agent.capabilities
        assert "diversity_analysis" in dandara_agent.capabilities
    
    @pytest.mark.unit
    async def test_inclusion_analysis(self, dandara_agent):
        """Test social inclusion analysis."""
        context = AgentContext(investigation_id="inclusion-test")
        message = AgentMessage(
            sender="test",
            recipient="Dandara",
            action="analyze_inclusion",
            payload={"program_id": "social_program_001"}
        )
        
        response = await dandara_agent.process(message, context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "inclusion_analysis" in response.result
    
    @pytest.mark.unit
    async def test_diversity_metrics(self, dandara_agent):
        """Test diversity metrics calculation."""
        context = AgentContext(investigation_id="diversity-test")
        message = AgentMessage(
            sender="test",
            recipient="Dandara", 
            action="calculate_diversity_metrics",
            payload={"dataset": "employment_data"}
        )
        
        response = await dandara_agent.process(message, context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "diversity_metrics" in response.result