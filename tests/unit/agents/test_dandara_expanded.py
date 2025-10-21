"""
Expanded unit tests for Dandara Social Justice Agent.

Author: Anderson H. Silva
Date: 2025-10-21
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.agents.dandara import DandaraAgent, EquityAnalysisResult, SocialJusticeRequest
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus


@pytest.fixture
def agent():
    """Create Dandara agent instance."""
    return DandaraAgent()


@pytest.fixture
def agent_context():
    """Create agent context."""
    return AgentContext(
        investigation_id="test-inv-001",
        user_id="test-user-001",
        session_id="test-session-001",
    )


class TestDandaraAgent:
    """Test suite for Dandara Social Justice Agent."""

    @pytest.mark.unit
    def test_agent_initialization(self, agent):
        """Test agent initializes with correct attributes."""
        assert agent.name == "Dandara"
        assert "social_equity_analysis" in agent.capabilities
        assert "inclusion_policy_monitoring" in agent.capabilities
        assert agent.status == AgentStatus.IDLE
        assert agent.ibge_client is not None
        assert agent.datasus_client is not None
        assert agent.inep_client is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_initialize(self, agent):
        """Test agent initialization."""
        await agent.initialize()
        assert agent.status == AgentStatus.IDLE

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_shutdown(self, agent):
        """Test agent shutdown."""
        # Mock the close methods
        agent.ibge_client.close = AsyncMock()
        agent.datasus_client.close = AsyncMock()
        agent.inep_client.close = AsyncMock()

        await agent.shutdown()

        agent.ibge_client.close.assert_called_once()
        agent.datasus_client.close.assert_called_once()
        agent.inep_client.close.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_with_mocked_analysis(self, agent, agent_context):
        """Test process method with mocked internal analysis."""
        message = AgentMessage(
            sender="test-sender",
            recipient="dandara",
            action="analyze_social_equity",
            payload={
                "query": "Analyze education equity in Rio de Janeiro",
                "target_groups": ["children", "youth"],
                "policy_areas": ["education"],
                "geographical_scope": "RJ",
            },
        )

        # Mock the internal analysis method
        mock_result = EquityAnalysisResult(
            analysis_type="education_equity",
            gini_coefficient=0.35,
            equity_score=72,
            population_affected=1500000,
            violations_detected=[],
            gaps_identified=[{"gap": "teacher shortage", "severity": "high"}],
            recommendations=["Increase teacher hiring in low-income areas"],
            evidence_sources=["IBGE", "INEP"],
            analysis_timestamp=Mock(),
            confidence_level=0.85,
        )

        with patch.object(
            agent, "_analyze_social_equity", return_value=mock_result
        ) as mock_analyze:
            response = await agent.process(message, agent_context)

            assert response.status == AgentStatus.COMPLETED
            assert response.result is not None
            mock_analyze.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_error_handling(self, agent, agent_context):
        """Test error handling in process method."""
        message = AgentMessage(
            sender="test-sender",
            recipient="dandara",
            action="analyze_social_equity",
            payload={"query": "Test query"},
        )

        # Mock analysis to raise exception
        with patch.object(
            agent, "_analyze_social_equity", side_effect=Exception("API Error")
        ):
            response = await agent.process(message, agent_context)

            # Should handle error gracefully
            assert response.status == AgentStatus.ERROR
            assert response.error is not None
            assert "API Error" in response.error

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_gini_coefficient(self, agent):
        """Test Gini coefficient calculation."""
        # Equal distribution (Gini = 0)
        equal_data = [100.0, 100.0, 100.0, 100.0]
        gini_equal = await agent._calculate_gini(equal_data)
        assert 0.0 <= gini_equal <= 0.1

        # Unequal distribution (higher Gini)
        unequal_data = [10.0, 20.0, 30.0, 100.0]
        gini_unequal = await agent._calculate_gini(unequal_data)
        assert 0.2 <= gini_unequal <= 1.0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_atkinson_index(self, agent):
        """Test Atkinson index calculation."""
        data = [100.0, 200.0, 300.0, 400.0, 500.0]
        atkinson = await agent._calculate_atkinson(data, epsilon=0.5)

        assert isinstance(atkinson, float)
        assert 0.0 <= atkinson <= 1.0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_theil_index(self, agent):
        """Test Theil index calculation."""
        data = [100.0, 200.0, 300.0, 400.0]
        theil = await agent._calculate_theil(data)

        assert isinstance(theil, float)
        assert theil >= 0.0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_palma_ratio(self, agent):
        """Test Palma ratio calculation."""
        data = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        palma = await agent._calculate_palma(data)

        assert isinstance(palma, float)
        assert palma >= 0.0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_quintile_ratio(self, agent):
        """Test quintile ratio calculation."""
        data = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        ratio = await agent._calculate_quintile_ratio(data)

        assert isinstance(ratio, float)
        assert ratio >= 1.0

    @pytest.mark.unit
    def test_extract_state_code(self, agent):
        """Test state code extraction."""
        # Test with state name - returns IBGE code
        code = agent._extract_state_code("Rio de Janeiro")
        assert code == "33"  # IBGE code for Rio de Janeiro

        # Test with state abbreviation
        code = agent._extract_state_code("SP")
        assert code == "35"  # IBGE code for São Paulo

        # Test with unknown state
        code = agent._extract_state_code("Unknown State")
        assert code is None

    @pytest.mark.unit
    def test_extract_municipality_ids(self, agent):
        """Test municipality ID extraction."""
        result = agent._extract_municipality_ids("Rio de Janeiro")
        assert result is None or isinstance(result, list)

    @pytest.mark.unit
    def test_estimate_affected_population(self, agent):
        """Test affected population estimation."""
        mock_data = {
            "population": 1000000,
        }

        population = agent._estimate_affected_population_real(
            mock_data, ["children", "youth"]
        )

        assert isinstance(population, int)
        assert population >= 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_with_different_policy_areas(self, agent, agent_context):
        """Test processing requests for different policy areas."""
        for policy_area in ["education", "health", "housing"]:
            message = AgentMessage(
                sender="test",
                recipient="dandara",
                action="analyze_social_equity",
                payload={
                    "query": f"Analyze {policy_area} equity",
                    "policy_areas": [policy_area],
                },
            )

            with patch.object(agent, "_analyze_social_equity") as mock_analyze:
                mock_analyze.return_value = EquityAnalysisResult(
                    analysis_type=f"{policy_area}_equity",
                    gini_coefficient=0.4,
                    equity_score=70,
                    population_affected=1000000,
                    violations_detected=[],
                    gaps_identified=[],
                    recommendations=[],
                    evidence_sources=[],
                    analysis_timestamp=Mock(),
                    confidence_level=0.8,
                )

                response = await agent.process(message, agent_context)
                assert response.status == AgentStatus.COMPLETED

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_with_multiple_target_groups(self, agent, agent_context):
        """Test processing with multiple demographic target groups."""
        message = AgentMessage(
            sender="test",
            recipient="dandara",
            action="analyze_social_equity",
            payload={
                "query": "Multi-group equity analysis",
                "target_groups": ["children", "elderly", "disabled"],
                "policy_areas": ["health"],
            },
        )

        with patch.object(agent, "_analyze_social_equity") as mock_analyze:
            mock_analyze.return_value = EquityAnalysisResult(
                analysis_type="multi_group_equity",
                gini_coefficient=0.45,
                equity_score=68,
                population_affected=500000,
                violations_detected=[],
                gaps_identified=[],
                recommendations=[],
                evidence_sources=[],
                analysis_timestamp=Mock(),
                confidence_level=0.75,
            )

            response = await agent.process(message, agent_context)
            assert response.status == AgentStatus.COMPLETED
            assert response.result is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_gini_edge_cases(self, agent):
        """Test Gini coefficient with edge cases."""
        # Single value
        single = await agent._calculate_gini([100.0])
        assert single == 0.0

        # Two equal values
        equal = await agent._calculate_gini([50.0, 50.0])
        assert 0.0 <= equal <= 0.1

        # Maximum inequality (one person has everything)
        max_ineq = await agent._calculate_gini([0.0, 0.0, 0.0, 100.0])
        assert 0.5 <= max_ineq <= 1.0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_minimal_payload(self, agent, agent_context):
        """Test handling of minimal payload."""
        message = AgentMessage(
            sender="test",
            recipient="dandara",
            action="analyze_social_equity",
            payload={"query": "Minimal test query"},
        )

        # Mock analysis to return success
        mock_result = EquityAnalysisResult(
            analysis_type="minimal_test",
            gini_coefficient=0.4,
            equity_score=70,
            population_affected=100000,
            violations_detected=[],
            gaps_identified=[],
            recommendations=[],
            evidence_sources=[],
            analysis_timestamp=Mock(),
            confidence_level=0.7,
        )

        with patch.object(agent, "_analyze_social_equity", return_value=mock_result):
            response = await agent.process(message, agent_context)

            assert response.status == AgentStatus.COMPLETED
            assert response.result is not None

    @pytest.mark.unit
    def test_social_justice_request_validation(self):
        """Test SocialJusticeRequest model validation."""
        # Valid request
        request = SocialJusticeRequest(
            query="Test query",
            target_groups=["children"],
            policy_areas=["education"],
        )
        assert request.query == "Test query"

        # Test with all optional fields
        full_request = SocialJusticeRequest(
            query="Full test",
            target_groups=["children", "elderly"],
            policy_areas=["education", "health"],
            geographical_scope="RJ",
            time_period=("2020-01", "2023-12"),
            metrics_focus=["gini", "atkinson"],
        )
        assert full_request.time_period == ("2020-01", "2023-12")
