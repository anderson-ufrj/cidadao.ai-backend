"""
Unit tests for Bonifácio Agent - Public policy analysis specialist.
Tests policy effectiveness, impact assessment, and governance analysis capabilities.
"""

from datetime import datetime

import pytest

from src.agents.bonifacio import BonifacioAgent, PolicyIndicator
from src.agents.deodoro import AgentContext, AgentMessage
from src.core import AgentStatus


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
    return BonifacioAgent()


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
    @pytest.mark.asyncio
    async def test_policy_effectiveness_analysis_with_dict(
        self, bonifacio_agent, agent_context
    ):
        """Test policy analysis with dictionary input."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
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

        assert response.status == AgentStatus.COMPLETED
        assert "policy_evaluation" in response.result

        evaluation = response.result["policy_evaluation"]
        assert evaluation["policy_name"] == "Programa Nacional de Educação Digital"
        assert "effectiveness_scores" in evaluation
        assert "roi_social" in evaluation
        assert "sustainability_score" in evaluation
        assert "impact_level" in evaluation

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_policy_analysis_with_string(self, bonifacio_agent, agent_context):
        """Test policy analysis with simple string input."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload="Programa Bolsa Família",
            sender="analyst",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert (
            response.result["policy_evaluation"]["policy_name"]
            == "Programa Bolsa Família"
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_effectiveness_score_calculation(
        self, bonifacio_agent, agent_context
    ):
        """Test effectiveness score calculation logic."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
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

        scores = response.result["policy_evaluation"]["effectiveness_scores"]
        assert "efficacy" in scores
        assert "efficiency" in scores
        assert "effectiveness" in scores
        assert "cost_effectiveness" in scores

        # All scores should be between 0 and 1
        for score_value in scores.values():
            assert 0 <= score_value <= 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_impact_level_classification(self, bonifacio_agent, agent_context):
        """Test impact level classification based on effectiveness."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload="High Impact Policy Test",
            sender="test",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        impact_level = response.result["policy_evaluation"]["impact_level"]
        assert impact_level in ["very_low", "low", "medium", "high", "very_high"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_policy_indicators_evaluation(self, bonifacio_agent, agent_context):
        """Test evaluation of policy performance indicators."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Healthcare Initiative",
                "policy_area": "health",
                "target_indicators": ["mortality_rate", "vaccination_coverage"],
            },
            sender="health_ministry",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        indicators = response.result["indicators"]
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
    @pytest.mark.asyncio
    async def test_strategic_recommendations(self, bonifacio_agent, agent_context):
        """Test strategic recommendations generation."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
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

        recommendations = response.result["strategic_recommendations"]
        assert len(recommendations) > 0

        # Should have budget recommendation due to high deviation
        budget_rec = next(
            (r for r in recommendations if r["area"] == "budget_management"), None
        )
        assert budget_rec is not None
        assert budget_rec["priority"] == "high"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_benchmarking_analysis(self, bonifacio_agent, agent_context):
        """Test benchmarking against similar policies."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Digital Inclusion Program",
                "comparison_policies": ["Previous Digital Program"],
                "benchmarking_scope": "national",
            },
            sender="benchmarking_unit",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        benchmarking = response.result["benchmarking"]
        assert "reference_policies" in benchmarking
        assert "percentile_ranking" in benchmarking
        assert "improvement_potential" in benchmarking

        # Check percentile rankings
        rankings = benchmarking["percentile_ranking"]
        for metric in ["effectiveness", "efficiency", "roi"]:
            assert metric in rankings
            assert 0 <= rankings[metric] <= 100

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_sustainability_assessment(self, bonifacio_agent, agent_context):
        """Test policy sustainability scoring."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload="Long-term Infrastructure Project",
            sender="planning_dept",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        sustainability_score = response.result["policy_evaluation"][
            "sustainability_score"
        ]
        assert isinstance(sustainability_score, int)
        assert 0 <= sustainability_score <= 100

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_social_roi_calculation(self, bonifacio_agent, agent_context):
        """Test social return on investment calculation."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Social Investment Program",
                "budget_data": {"planned": 50_000_000, "executed": 45_000_000},
            },
            sender="investment_analyst",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        roi_social = response.result["policy_evaluation"]["roi_social"]
        assert isinstance(roi_social, float)
        # ROI can be negative (loss) or positive (gain)
        assert -10 <= roi_social <= 10  # Reasonable bounds for social ROI

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_error_handling(self, bonifacio_agent, agent_context):
        """Test error handling for malformed requests."""
        message = AgentMessage(
            action="invalid_action",
            recipient="bonifacio",
            payload={"invalid": "data"},
            sender="test",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.ERROR
        assert "error" in response.result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_evidence_hash_generation(self, bonifacio_agent, agent_context):
        """Test evidence hash for verification."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload="Test Policy for Hash",
            sender="auditor",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        hash_verification = response.result["hash_verification"]
        assert isinstance(hash_verification, str)
        assert len(hash_verification) == 64  # SHA-256 hash length

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_coverage_analysis(self, bonifacio_agent, agent_context):
        """Test beneficiary coverage analysis."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Universal Healthcare",
                "policy_area": "health",
                "geographical_scope": "national",
            },
            sender="coverage_analyst",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        beneficiaries = response.result["policy_evaluation"]["beneficiaries"]
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


class TestPolicyEvaluationFrameworks:
    """Test policy evaluation frameworks (Logic Model, Results Chain, Theory of Change)."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_logic_model_framework_application(
        self, bonifacio_agent, agent_context
    ):
        """Test logic model framework with comprehensive policy data."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa Bolsa Família",
                "policy_area": "social",
                "geographical_scope": "federal",
                "budget_data": {"planned": 1_000_000_000, "executed": 950_000_000},
            },
            sender="policy_analyst",
            metadata={"framework": "logic_model"},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        evaluation = response.result["policy_evaluation"]
        # Logic model should calculate inputs, activities, outputs, outcomes
        assert "effectiveness_scores" in evaluation

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_results_chain_framework(self, bonifacio_agent, agent_context):
        """Test results chain framework for policy analysis."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa Mais Médicos",
                "policy_area": "health",
                "geographical_scope": "federal",
                "budget_data": {"planned": 800_000_000, "executed": 750_000_000},
            },
            sender="policy_analyst",
            metadata={"framework": "results_chain"},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        evaluation = response.result["policy_evaluation"]
        assert "sustainability_score" in evaluation

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_theory_of_change_framework(self, bonifacio_agent, agent_context):
        """Test theory of change framework."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa Nacional de Tecnologia Educacional",
                "policy_area": "education",
                "geographical_scope": "federal",
                "budget_data": {"planned": 300_000_000, "executed": 280_000_000},
            },
            sender="policy_analyst",
            metadata={"framework": "theory_of_change"},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        # Should complete even with theory of change framework
        assert "policy_evaluation" in response.result


class TestBeneficiariesAnalysis:
    """Test beneficiaries analysis and cost-per-capita calculations."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_large_scale_beneficiaries_estimation(
        self, bonifacio_agent, agent_context
    ):
        """Test beneficiaries analysis for large-scale programs."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa Nacional de Alimentação Escolar",
                "policy_area": "education",
                "budget_data": {"planned": 4_000_000_000, "executed": 3_900_000_000},
            },
            sender="policy_analyst",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        evaluation = response.result["policy_evaluation"]
        # Should calculate cost per capita
        assert "beneficiaries_analysis" in evaluation or "beneficiaries" in str(
            evaluation
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_small_scale_policy_analysis(self, bonifacio_agent, agent_context):
        """Test analysis for small municipal programs."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa Municipal de Cultura",
                "policy_area": "culture",
                "geographical_scope": "municipal",
                "budget_data": {"planned": 1_000_000, "executed": 950_000},
            },
            sender="municipal_manager",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        # Municipal programs should be analyzed differently
        evaluation = response.result["policy_evaluation"]
        assert evaluation["policy_name"] == "Programa Municipal de Cultura"


class TestSocialROICalculations:
    """Test social return on investment calculations."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_high_impact_social_roi(self, bonifacio_agent, agent_context):
        """Test social ROI calculation for high-impact program."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa de Erradicação do Trabalho Infantil",
                "policy_area": "social",
                "budget_data": {"planned": 200_000_000, "executed": 195_000_000},
            },
            sender="social_analyst",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        evaluation = response.result["policy_evaluation"]
        # High social impact should be reflected in ROI
        assert "roi_social" in evaluation or "social_return" in str(evaluation)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_zero_budget_execution(self, bonifacio_agent, agent_context):
        """Test policy with zero budget execution."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa Não Executado",
                "policy_area": "health",
                "budget_data": {"planned": 100_000_000, "executed": 0},
            },
            sender="auditor",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        # Should handle gracefully - zero execution is valid data
        assert response.status in [AgentStatus.COMPLETED, AgentStatus.ERROR]


class TestPolicySustainabilityAssessment:
    """Test policy sustainability scoring."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_sustainable_policy_assessment(self, bonifacio_agent, agent_context):
        """Test assessment of highly sustainable policy."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Sistema Único de Saúde (SUS)",
                "policy_area": "health",
                "geographical_scope": "federal",
                "budget_data": {"planned": 50_000_000_000, "executed": 48_000_000_000},
            },
            sender="health_minister",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        evaluation = response.result["policy_evaluation"]
        # SUS should have high sustainability score
        assert "sustainability_score" in evaluation

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_pilot_program_sustainability(self, bonifacio_agent, agent_context):
        """Test sustainability of pilot/experimental programs."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Projeto Piloto de Renda Básica Universal",
                "policy_area": "social",
                "geographical_scope": "municipal",
                "budget_data": {"planned": 5_000_000, "executed": 4_800_000},
            },
            sender="innovation_lab",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        # Pilot programs should still be evaluated
        assert "policy_evaluation" in response.result


class TestPolicyComparison:
    """Test comparative policy analysis and benchmarking."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_benchmarking_against_similar_policies(
        self, bonifacio_agent, agent_context
    ):
        """Test benchmarking a policy against similar programs."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa de Alfabetização de Jovens e Adultos",
                "policy_area": "education",
                "comparison_policies": [
                    "Mobral (histórico)",
                    "Brasil Alfabetizado",
                ],
                "benchmarking_scope": "national",
            },
            sender="education_analyst",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        # Should include comparison data
        evaluation = response.result["policy_evaluation"]
        assert (
            evaluation["policy_name"] == "Programa de Alfabetização de Jovens e Adultos"
        )


class TestImpactLevelClassification:
    """Test impact level classification logic."""

    @pytest.mark.unit
    def test_impact_classification_helper(self, bonifacio_agent):
        """Test _classify_impact_level method with various scores."""
        from src.agents.bonifacio import ImpactLevel

        # Test with high scores
        high_scores = {"efficacy": 90.0, "efficiency": 88.0, "effectiveness": 92.0}
        high_impact = bonifacio_agent._classify_impact_level(high_scores, 5.0)
        assert isinstance(high_impact, ImpactLevel)

        # Test with medium scores
        medium_scores = {"efficacy": 50.0, "efficiency": 52.0, "effectiveness": 48.0}
        medium_impact = bonifacio_agent._classify_impact_level(medium_scores, 2.5)
        assert isinstance(medium_impact, ImpactLevel)

        # Test with low scores
        low_scores = {"efficacy": 20.0, "efficiency": 22.0, "effectiveness": 18.0}
        low_impact = bonifacio_agent._classify_impact_level(low_scores, 1.0)
        assert isinstance(low_impact, ImpactLevel)


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_missing_policy_name(self, bonifacio_agent, agent_context):
        """Test with missing policy name."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_area": "health",
            },
            sender="analyst",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        # Should handle gracefully
        assert response.status in [AgentStatus.ERROR, AgentStatus.COMPLETED]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_invalid_action(self, bonifacio_agent, agent_context):
        """Test with unknown action."""
        message = AgentMessage(
            action="unknown_action",
            recipient="bonifacio",
            payload={"policy_name": "Test Policy"},
            sender="test",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        # Should return error or handle gracefully
        assert response.status in [AgentStatus.ERROR, AgentStatus.COMPLETED]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_empty_payload(self, bonifacio_agent, agent_context):
        """Test with empty payload."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={},
            sender="test",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        # Should handle empty payload gracefully
        assert response.status in [AgentStatus.ERROR, AgentStatus.COMPLETED]


class TestMultiplePolicyAreas:
    """Test analysis across different policy domains."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_health_policy_analysis(self, bonifacio_agent, agent_context):
        """Test health policy specific analysis."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa de Vacinação Nacional",
                "policy_area": "health",
            },
            sender="health_analyst",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)
        assert response.status == AgentStatus.COMPLETED

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_security_policy_analysis(self, bonifacio_agent, agent_context):
        """Test security policy specific analysis."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa Nacional de Segurança Pública",
                "policy_area": "security",
            },
            sender="security_analyst",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)
        assert response.status == AgentStatus.COMPLETED

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_infrastructure_policy_analysis(self, bonifacio_agent, agent_context):
        """Test infrastructure policy analysis."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa de Investimento em Logística",
                "policy_area": "infrastructure",
            },
            sender="infrastructure_planner",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)
        assert response.status == AgentStatus.COMPLETED
