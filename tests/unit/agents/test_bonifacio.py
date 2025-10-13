"""
Unit tests for Bonifácio Agent - Public policy analysis specialist.
Tests policy effectiveness, impact assessment, and governance analysis capabilities.
"""

from datetime import datetime

import pytest

from src.agents.bonifacio import (
    BonifacioAgent,
    PolicyIndicator,
)
from src.agents.deodoro import AgentContext, AgentMessage


@pytest.fixture
def agent_context():
    """Test agent context for policy analysis."""
    return AgentContext(
        investigation_id="policy-analysis-001",
        user_id="policy-analyst",
        session_id="policy-session",
        metadata={
            "analysis_type": "policy_effectiveness",
            "scope": "national_programs",
            "time_horizon": "2023-2024",
        },
        trace_id="trace-bonifacio-456",
    )


@pytest.fixture
def bonifacio_agent():
    """Create Bonifácio agent."""
    agent = BonifacioAgent()
    return agent


class TestBonifacioAgent:
    """Test suite for Bonifácio (Policy Analysis Agent)."""

    @pytest.mark.unit
    def test_agent_initialization(self, bonifacio_agent):
        """Test Bonifácio agent initialization."""
        assert bonifacio_agent.name == "bonifacio"
        assert "policy_effectiveness_analysis" in bonifacio_agent.capabilities
        assert "institutional_reform_evaluation" in bonifacio_agent.capabilities
        assert "social_roi_calculation" in bonifacio_agent.capabilities
        assert "policy_impact_assessment" in bonifacio_agent.capabilities
        assert len(bonifacio_agent.capabilities) == 14

    @pytest.mark.unit
    async def test_policy_effectiveness_analysis_with_dict(
        self, bonifacio_agent, agent_context
    ):
        """Test policy analysis with dictionary input."""
        message = AgentMessage(
            type="policy_analysis",
            data={
                "policy_name": "Programa Nacional de Educação Digital",
                "policy_area": "education",
                "geographical_scope": "federal",
                "analysis_period": ("2023-01-01", "2024-01-01"),
                "budget_data": {"planned": 500_000_000, "executed": 450_000_000},
            },
            sender="policy_manager",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.success is True
        assert response.response_type == "policy_analysis"
        assert "policy_evaluation" in response.data

        evaluation = response.data["policy_evaluation"]
        assert evaluation["policy_name"] == "Programa Nacional de Educação Digital"
        assert "effectiveness_scores" in evaluation
        assert "roi_social" in evaluation
        assert "sustainability_score" in evaluation
        assert "impact_level" in evaluation

    @pytest.mark.unit
    async def test_policy_analysis_with_string(self, bonifacio_agent, agent_context):
        """Test policy analysis with simple string input."""
        message = AgentMessage(
            type="policy_analysis",
            data="Programa Bolsa Família",
            sender="analyst",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.success is True
        assert (
            response.data["policy_evaluation"]["policy_name"]
            == "Programa Bolsa Família"
        )

    @pytest.mark.unit
    async def test_effectiveness_score_calculation(
        self, bonifacio_agent, agent_context
    ):
        """Test effectiveness score calculation logic."""
        message = AgentMessage(
            type="policy_analysis",
            data={
                "policy_name": "Test Policy",
                "budget_data": {
                    "planned": 100_000_000,
                    "executed": 90_000_000,  # 10% deviation - good efficiency
                },
            },
            sender="test",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        scores = response.data["policy_evaluation"]["effectiveness_scores"]
        assert "efficacy" in scores
        assert "efficiency" in scores
        assert "effectiveness" in scores
        assert "cost_effectiveness" in scores

        # All scores should be between 0 and 1
        for score_value in scores.values():
            assert 0 <= score_value <= 1

    @pytest.mark.unit
    async def test_impact_level_classification(self, bonifacio_agent, agent_context):
        """Test impact level classification based on effectiveness."""
        message = AgentMessage(
            type="policy_analysis",
            data="High Impact Policy Test",
            sender="test",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        impact_level = response.data["policy_evaluation"]["impact_level"]
        assert impact_level in ["very_low", "low", "medium", "high", "very_high"]

    @pytest.mark.unit
    async def test_policy_indicators_evaluation(self, bonifacio_agent, agent_context):
        """Test evaluation of policy performance indicators."""
        message = AgentMessage(
            type="policy_analysis",
            data={
                "policy_name": "Healthcare Initiative",
                "policy_area": "health",
                "target_indicators": ["mortality_rate", "vaccination_coverage"],
            },
            sender="health_ministry",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        indicators = response.data["indicators"]
        assert len(indicators) > 0

        for indicator in indicators:
            assert "name" in indicator
            assert "baseline" in indicator
            assert "current" in indicator
            assert "target" in indicator
            assert "performance_ratio" in indicator
            assert "goal_achievement" in indicator
            assert "trend" in indicator
            assert indicator["trend"] in ["improving", "deteriorating", "stable"]

    @pytest.mark.unit
    async def test_strategic_recommendations(self, bonifacio_agent, agent_context):
        """Test strategic recommendations generation."""
        message = AgentMessage(
            type="policy_analysis",
            data={
                "policy_name": "Education Reform",
                "budget_data": {
                    "planned": 100_000_000,
                    "executed": 130_000_000,  # 30% over budget
                },
            },
            sender="policy_board",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        recommendations = response.data["strategic_recommendations"]
        assert len(recommendations) > 0

        # Should have budget recommendation due to high deviation
        budget_rec = next(
            (r for r in recommendations if r["area"] == "budget_management"), None
        )
        assert budget_rec is not None
        assert budget_rec["priority"] == "high"

    @pytest.mark.unit
    async def test_benchmarking_analysis(self, bonifacio_agent, agent_context):
        """Test benchmarking against similar policies."""
        message = AgentMessage(
            type="policy_analysis",
            data={
                "policy_name": "Digital Inclusion Program",
                "comparison_policies": ["Previous Digital Program"],
                "benchmarking_scope": "national",
            },
            sender="benchmarking_unit",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        benchmarking = response.data["benchmarking"]
        assert "reference_policies" in benchmarking
        assert "percentile_ranking" in benchmarking
        assert "improvement_potential" in benchmarking

        # Check percentile rankings
        rankings = benchmarking["percentile_ranking"]
        for metric in ["effectiveness", "efficiency", "roi"]:
            assert metric in rankings
            assert 0 <= rankings[metric] <= 100

    @pytest.mark.unit
    async def test_sustainability_assessment(self, bonifacio_agent, agent_context):
        """Test policy sustainability scoring."""
        message = AgentMessage(
            type="policy_analysis",
            data="Long-term Infrastructure Project",
            sender="planning_dept",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        sustainability_score = response.data["policy_evaluation"][
            "sustainability_score"
        ]
        assert isinstance(sustainability_score, int)
        assert 0 <= sustainability_score <= 100

    @pytest.mark.unit
    async def test_social_roi_calculation(self, bonifacio_agent, agent_context):
        """Test social return on investment calculation."""
        message = AgentMessage(
            type="policy_analysis",
            data={
                "policy_name": "Social Investment Program",
                "budget_data": {"planned": 50_000_000, "executed": 45_000_000},
            },
            sender="investment_analyst",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        roi_social = response.data["policy_evaluation"]["roi_social"]
        assert isinstance(roi_social, float)
        # ROI can be negative (loss) or positive (gain)
        assert -10 <= roi_social <= 10  # Reasonable bounds for social ROI

    @pytest.mark.unit
    async def test_error_handling(self, bonifacio_agent, agent_context):
        """Test error handling for malformed requests."""
        message = AgentMessage(
            type="invalid_action", data={"invalid": "data"}, sender="test", metadata={}
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.success is False
        assert response.response_type == "error"
        assert "error" in response.data

    @pytest.mark.unit
    async def test_evidence_hash_generation(self, bonifacio_agent, agent_context):
        """Test evidence hash for verification."""
        message = AgentMessage(
            type="policy_analysis",
            data="Test Policy for Hash",
            sender="auditor",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        hash_verification = response.data["hash_verification"]
        assert isinstance(hash_verification, str)
        assert len(hash_verification) == 64  # SHA-256 hash length

    @pytest.mark.unit
    async def test_coverage_analysis(self, bonifacio_agent, agent_context):
        """Test beneficiary coverage analysis."""
        message = AgentMessage(
            type="policy_analysis",
            data={
                "policy_name": "Universal Healthcare",
                "policy_area": "health",
                "geographical_scope": "national",
            },
            sender="coverage_analyst",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        beneficiaries = response.data["policy_evaluation"]["beneficiaries"]
        assert "target_population" in beneficiaries
        assert "reached_population" in beneficiaries
        assert "coverage_rate" in beneficiaries
        assert "demographic_breakdown" in beneficiaries

        # Check demographic breakdown
        breakdown = beneficiaries["demographic_breakdown"]
        assert "urban" in breakdown
        assert "rural" in breakdown
        assert "vulnerable_groups" in breakdown


class TestPolicyIndicator:
    """Test PolicyIndicator data model."""

    @pytest.mark.unit
    def test_indicator_creation(self):
        """Test creating policy indicator."""
        indicator = PolicyIndicator(
            name="digital_literacy_rate",
            baseline_value=0.45,
            current_value=0.62,
            target_value=0.75,
            unit="percentage",
            data_source="National Education Survey",
            last_update=datetime.utcnow(),
            statistical_significance=0.95,
            trend="improving",
        )

        assert indicator.name == "digital_literacy_rate"
        assert indicator.baseline_value == 0.45
        assert indicator.current_value == 0.62
        assert indicator.target_value == 0.75
        assert indicator.trend == "improving"
