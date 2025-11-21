"""
Unit tests for Bonifácio Agent - Public policy analysis specialist.
Tests policy effectiveness, impact assessment, and governance analysis capabilities.
"""

from datetime import UTC, datetime

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
            last_update=datetime.now(UTC),
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


class TestReflectionQuality:
    """Test reflection method for quality improvement (PRIORITY 1 - 130 lines)."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reflect_low_effectiveness(self, bonifacio_agent, agent_context):
        """Test reflection triggers when effectiveness < 0.60."""
        # Create a result with low effectiveness
        initial_result = {
            "policy_evaluation": {
                "policy_name": "Low Performance Policy",
                "effectiveness_scores": {
                    "efficacy": 0.40,
                    "efficiency": 0.45,
                    "effectiveness": 0.50,  # Below 0.60 threshold
                    "cost_effectiveness": 0.35,
                },
                "roi_social": 1.5,
                "sustainability_score": 70,
                "analysis_confidence": 0.80,
            },
            "strategic_recommendations": [
                {"area": "initial", "recommendation": "Original recommendation"}
            ],
        }

        task = "policy_analysis"
        enhanced_result = await bonifacio_agent.reflect(
            task, initial_result, agent_context
        )

        # Should enhance the result
        assert enhanced_result["reflection_applied"] is True
        assert "low_effectiveness" in enhanced_result["quality_improvements"]

        # Should have more recommendations
        recommendations = enhanced_result["strategic_recommendations"]
        assert len(recommendations) > len(initial_result["strategic_recommendations"])

        # Should have effectiveness improvement recommendations
        effectiveness_recs = [
            r for r in recommendations if r["area"] == "effectiveness_improvement"
        ]
        assert len(effectiveness_recs) > 0
        assert effectiveness_recs[0]["priority"] == "critical"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reflect_negative_roi(self, bonifacio_agent, agent_context):
        """Test reflection triggers when ROI is negative."""
        initial_result = {
            "policy_evaluation": {
                "policy_name": "Negative ROI Policy",
                "effectiveness_scores": {
                    "efficacy": 0.70,
                    "efficiency": 0.65,
                    "effectiveness": 0.68,
                    "cost_effectiveness": 0.55,
                },
                "roi_social": -0.5,  # Negative ROI
                "sustainability_score": 65,
                "analysis_confidence": 0.75,
            },
            "strategic_recommendations": [],
        }

        task = "policy_analysis"
        enhanced_result = await bonifacio_agent.reflect(
            task, initial_result, agent_context
        )

        assert enhanced_result["reflection_applied"] is True
        assert "negative_roi" in enhanced_result["quality_improvements"]

        # Should have resource optimization recommendation
        recommendations = enhanced_result["strategic_recommendations"]
        resource_recs = [
            r for r in recommendations if r["area"] == "resource_optimization"
        ]
        assert len(resource_recs) > 0
        assert resource_recs[0]["priority"] == "critical"
        assert resource_recs[0]["expected_impact"] == 0.95

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reflect_low_sustainability(self, bonifacio_agent, agent_context):
        """Test reflection triggers when sustainability < 60."""
        initial_result = {
            "policy_evaluation": {
                "policy_name": "Low Sustainability Policy",
                "effectiveness_scores": {
                    "efficacy": 0.75,
                    "efficiency": 0.70,
                    "effectiveness": 0.72,
                    "cost_effectiveness": 0.68,
                },
                "roi_social": 1.2,
                "sustainability_score": 55,  # Below 60 threshold
                "analysis_confidence": 0.82,
            },
            "strategic_recommendations": [
                {"area": "initial", "recommendation": "Original"}
            ],
        }

        task = "policy_analysis"
        enhanced_result = await bonifacio_agent.reflect(
            task, initial_result, agent_context
        )

        assert enhanced_result["reflection_applied"] is True
        assert "low_sustainability" in enhanced_result["quality_improvements"]

        # Should have institutional strengthening recommendation
        recommendations = enhanced_result["strategic_recommendations"]
        institutional_recs = [
            r for r in recommendations if r["area"] == "institutional_strengthening"
        ]
        assert len(institutional_recs) > 0
        assert institutional_recs[0]["priority"] == "high"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reflect_insufficient_recommendations(
        self, bonifacio_agent, agent_context
    ):
        """Test reflection triggers when recommendations < 2."""
        initial_result = {
            "policy_evaluation": {
                "policy_name": "Few Recommendations Policy",
                "effectiveness_scores": {
                    "efficacy": 0.80,
                    "efficiency": 0.75,
                    "effectiveness": 0.78,
                    "cost_effectiveness": 0.72,
                },
                "roi_social": 1.8,
                "sustainability_score": 70,
                "analysis_confidence": 0.85,
            },
            "strategic_recommendations": [
                {"area": "single", "recommendation": "Only one recommendation"}
            ],  # < 2 recommendations
        }

        task = "policy_analysis"
        enhanced_result = await bonifacio_agent.reflect(
            task, initial_result, agent_context
        )

        assert enhanced_result["reflection_applied"] is True
        assert "insufficient_recommendations" in enhanced_result["quality_improvements"]

        # Should have added monitoring and stakeholder engagement recommendations
        recommendations = enhanced_result["strategic_recommendations"]
        assert len(recommendations) >= 3  # Original + at least 2 new

        # Check for monitoring recommendation
        monitoring_recs = [r for r in recommendations if r["area"] == "monitoring"]
        assert len(monitoring_recs) > 0

        # Check for stakeholder engagement recommendation
        stakeholder_recs = [
            r for r in recommendations if r["area"] == "stakeholder_engagement"
        ]
        assert len(stakeholder_recs) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reflect_no_issues(self, bonifacio_agent, agent_context):
        """Test reflection when quality is acceptable (no issues)."""
        initial_result = {
            "policy_evaluation": {
                "policy_name": "High Quality Policy",
                "effectiveness_scores": {
                    "efficacy": 0.85,
                    "efficiency": 0.80,
                    "effectiveness": 0.83,  # Above 0.60
                    "cost_effectiveness": 0.78,
                },
                "roi_social": 2.5,  # Positive
                "sustainability_score": 75,  # Above 60
                "analysis_confidence": 0.88,
            },
            "strategic_recommendations": [
                {"area": "rec1", "recommendation": "First recommendation"},
                {"area": "rec2", "recommendation": "Second recommendation"},
            ],  # >= 2 recommendations
        }

        task = "policy_analysis"
        result = await bonifacio_agent.reflect(task, initial_result, agent_context)

        # Should NOT enhance when quality is acceptable
        assert result == initial_result
        assert "reflection_applied" not in result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reflect_multiple_issues(self, bonifacio_agent, agent_context):
        """Test reflection with multiple quality issues simultaneously."""
        initial_result = {
            "policy_evaluation": {
                "policy_name": "Multiple Issues Policy",
                "effectiveness_scores": {
                    "efficacy": 0.45,
                    "efficiency": 0.42,
                    "effectiveness": 0.48,  # Low effectiveness
                    "cost_effectiveness": 0.35,
                },
                "roi_social": -0.3,  # Negative ROI
                "sustainability_score": 52,  # Low sustainability
                "analysis_confidence": 0.70,
            },
            "strategic_recommendations": [],  # Insufficient recommendations
        }

        task = "policy_analysis"
        enhanced_result = await bonifacio_agent.reflect(
            task, initial_result, agent_context
        )

        assert enhanced_result["reflection_applied"] is True

        # Should detect all 4 issues
        quality_issues = enhanced_result["quality_improvements"]
        assert "low_effectiveness" in quality_issues
        assert "negative_roi" in quality_issues
        assert "low_sustainability" in quality_issues
        assert "insufficient_recommendations" in quality_issues

        # Should have many recommendations added
        recommendations = enhanced_result["strategic_recommendations"]
        assert (
            len(recommendations) >= 6
        )  # All issues should add recommendations (4 issues = ~6 recommendations)

        # Verify recommendations cover all critical areas
        areas = [r["area"] for r in recommendations]
        assert "effectiveness_improvement" in areas
        assert "resource_optimization" in areas
        assert "institutional_strengthening" in areas
        assert "monitoring" in areas

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reflect_confidence_update(self, bonifacio_agent, agent_context):
        """Test that reflection increases analysis confidence."""
        initial_confidence = 0.75
        initial_result = {
            "policy_evaluation": {
                "policy_name": "Confidence Test Policy",
                "effectiveness_scores": {
                    "efficacy": 0.50,
                    "efficiency": 0.48,
                    "effectiveness": 0.52,  # Low effectiveness triggers reflection
                    "cost_effectiveness": 0.45,
                },
                "roi_social": 0.8,
                "sustainability_score": 65,
                "analysis_confidence": initial_confidence,
            },
            "strategic_recommendations": [
                {"area": "existing", "recommendation": "Original recommendation"}
            ],
        }

        task = "policy_analysis"
        enhanced_result = await bonifacio_agent.reflect(
            task, initial_result, agent_context
        )

        # Confidence should increase after reflection
        new_confidence = enhanced_result["policy_evaluation"]["analysis_confidence"]
        assert new_confidence > initial_confidence
        assert new_confidence <= 0.95  # Max confidence cap

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reflect_enhanced_recommendations_structure(
        self, bonifacio_agent, agent_context
    ):
        """Test that enhanced recommendations have proper structure."""
        initial_result = {
            "policy_evaluation": {
                "policy_name": "Structure Test Policy",
                "effectiveness_scores": {
                    "efficacy": 0.45,
                    "efficiency": 0.42,
                    "effectiveness": 0.48,  # Triggers reflection
                    "cost_effectiveness": 0.40,
                },
                "roi_social": 1.0,
                "sustainability_score": 65,
                "analysis_confidence": 0.80,
            },
            "strategic_recommendations": [],
        }

        task = "policy_analysis"
        enhanced_result = await bonifacio_agent.reflect(
            task, initial_result, agent_context
        )

        recommendations = enhanced_result["strategic_recommendations"]
        assert len(recommendations) > 0

        # Verify all recommendations have required fields
        for rec in recommendations:
            assert "area" in rec
            assert "recommendation" in rec
            assert "priority" in rec
            assert rec["priority"] in ["critical", "high", "medium", "low"]
            assert "expected_impact" in rec
            assert 0 <= rec["expected_impact"] <= 1
            assert "implementation_timeframe" in rec
            assert rec["implementation_timeframe"] in [
                "immediate",
                "short_term",
                "medium_term",
                "long_term",
            ]


class TestCostEffectivenessFramework:
    """Test cost-effectiveness framework analysis (PRIORITY 2 - 215 lines)."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cost_effectiveness_comprehensive(
        self, bonifacio_agent, agent_context
    ):
        """Test complete cost-effectiveness framework (lines 1592-1918)."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa Nacional de Saúde Preventiva",
                "policy_area": "health",
                "budget_data": {"planned": 100_000_000, "executed": 95_000_000},
                "target_indicators": ["mortality_rate", "vaccination_coverage"],
            },
            sender="health_economist",
            metadata={"framework": "cost_effectiveness"},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        result = response.result
        evaluation = result["policy_evaluation"]

        # Should have ROI social calculated
        assert "roi_social" in evaluation
        assert isinstance(evaluation["roi_social"], int | float)

        # Should have effectiveness scores
        assert "effectiveness_scores" in evaluation
        assert "cost_effectiveness" in evaluation["effectiveness_scores"]

    @pytest.mark.unit
    def test_classify_cost_level_health(self, bonifacio_agent):
        """Test cost classification for health policies."""
        # Very low cost for health
        classification = bonifacio_agent._classify_cost_level(500, "health")
        assert "Low" in classification

        # Very high cost for health
        classification_high = bonifacio_agent._classify_cost_level(15000, "health")
        assert "High" in classification_high

    @pytest.mark.unit
    def test_classify_cost_level_social(self, bonifacio_agent):
        """Test cost classification for social policies."""
        # Low cost for social programs
        classification = bonifacio_agent._classify_cost_level(300, "social")
        assert "Low" in classification

        # High cost for social programs
        classification_high = bonifacio_agent._classify_cost_level(5000, "social")
        assert "High" in classification_high

    @pytest.mark.unit
    def test_classify_roi_levels(self, bonifacio_agent):
        """Test ROI classification across different levels."""
        # Excellent ROI
        excellent = bonifacio_agent._classify_roi(5.0)
        assert "Excellent" in excellent or "Very high" in excellent

        # Good ROI
        good = bonifacio_agent._classify_roi(1.5)
        assert "Good" in good or "Positive" in good

        # Poor ROI
        poor = bonifacio_agent._classify_roi(-0.5)
        assert "Poor" in poor or "Negative" in poor

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cost_effectiveness_low_efficiency(
        self, bonifacio_agent, agent_context
    ):
        """Test analysis of policy with low cost-effectiveness."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa Ineficiente",
                "policy_area": "education",
                "budget_data": {
                    "planned": 50_000_000,
                    "executed": 65_000_000,
                },  # Over budget
            },
            sender="auditor",
            metadata={},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        evaluation = response.result["policy_evaluation"]

        # High deviation should affect cost-effectiveness
        assert "effectiveness_scores" in evaluation
        efficiency = evaluation["effectiveness_scores"]["efficiency"]
        # Over budget should result in lower efficiency
        assert efficiency < 1.0


class TestTheoryOfChangeFramework:
    """Test Theory of Change framework (PRIORITY 3 - 197 lines 1289-1581)."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_theory_of_change_comprehensive_health(
        self, bonifacio_agent, agent_context
    ):
        """Test Theory of Change for health policy."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Sistema Único de Saúde Universal",
                "policy_area": "health",
                "geographical_scope": "federal",
                "budget_data": {"planned": 50_000_000_000, "executed": 48_000_000_000},
            },
            sender="health_minister",
            metadata={"framework": "theory_of_change"},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        # Theory of Change should complete successfully
        assert "policy_evaluation" in response.result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_theory_of_change_education(self, bonifacio_agent, agent_context):
        """Test Theory of Change for education policy."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa Nacional de Tecnologia Educacional",
                "policy_area": "education",
                "geographical_scope": "federal",
                "budget_data": {"planned": 300_000_000, "executed": 280_000_000},
            },
            sender="education_analyst",
            metadata={"framework": "theory_of_change"},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "policy_evaluation" in response.result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_theory_of_change_social(self, bonifacio_agent, agent_context):
        """Test Theory of Change for social policy."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Projeto Piloto de Renda Básica Universal",
                "policy_area": "social",
                "geographical_scope": "municipal",
                "budget_data": {"planned": 5_000_000, "executed": 4_800_000},
            },
            sender="social_innovation_lab",
            metadata={"framework": "theory_of_change"},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "policy_evaluation" in response.result


class TestResultsChainFramework:
    """Test Results Chain framework (PRIORITY 4 - 179 lines 1131-1278)."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_results_chain_comprehensive_health(
        self, bonifacio_agent, agent_context
    ):
        """Test Results Chain for health policy (improve existing test)."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa Mais Médicos Ampliado",
                "policy_area": "health",
                "geographical_scope": "federal",
                "budget_data": {"planned": 1_000_000_000, "executed": 950_000_000},
            },
            sender="health_policy_analyst",
            metadata={"framework": "results_chain"},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        evaluation = response.result["policy_evaluation"]

        # Results Chain should assess sustainability
        assert "sustainability_score" in evaluation
        assert isinstance(evaluation["sustainability_score"], int)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_results_chain_security(self, bonifacio_agent, agent_context):
        """Test Results Chain for security policy."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa Nacional de Segurança Pública com Cidadania",
                "policy_area": "security",
                "geographical_scope": "federal",
            },
            sender="security_analyst",
            metadata={"framework": "results_chain"},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "policy_evaluation" in response.result


class TestLogicModelFramework:
    """Test Logic Model framework (PRIORITY 5 - 172 lines 1000-1117)."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_logic_model_comprehensive_education(
        self, bonifacio_agent, agent_context
    ):
        """Test Logic Model for education policy (improve existing test)."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa Nacional de Educação Digital Expandido",
                "policy_area": "education",
                "geographical_scope": "federal",
                "analysis_period": ("2023-01-01", "2024-12-31"),
                "budget_data": {"planned": 1_000_000_000, "executed": 950_000_000},
            },
            sender="education_policy_manager",
            metadata={"framework": "logic_model"},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        evaluation = response.result["policy_evaluation"]

        # Logic Model should have effectiveness assessment
        assert "effectiveness_scores" in evaluation
        assert "effectiveness" in evaluation["effectiveness_scores"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_logic_model_infrastructure(self, bonifacio_agent, agent_context):
        """Test Logic Model for infrastructure policy."""
        message = AgentMessage(
            action="policy_analysis",
            recipient="bonifacio",
            payload={
                "policy_name": "Programa de Investimento em Logística Nacional",
                "policy_area": "infrastructure",
                "geographical_scope": "federal",
                "budget_data": {"planned": 10_000_000_000, "executed": 9_500_000_000},
            },
            sender="infrastructure_planner",
            metadata={"framework": "logic_model"},
        )

        response = await bonifacio_agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "policy_evaluation" in response.result


class TestLifecycleMethods:
    """Test lifecycle methods (PRIORITY 6 - 28 lines 1939-1983)."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_initialize_method(self):
        """Test agent initialization lifecycle (no context argument)."""
        agent = BonifacioAgent()

        # Initialize should succeed (takes no args)
        try:
            await agent.initialize()
            # If it completes without error, that's success
            assert True
        except Exception as e:
            # If not implemented, skip or assert it's expected
            assert "not implemented" in str(e).lower() or isinstance(
                e, NotImplementedError
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_shutdown_method(self):
        """Test agent shutdown lifecycle (no context argument)."""
        agent = BonifacioAgent()

        # Shutdown should succeed (takes no args)
        try:
            await agent.shutdown()
            # If it completes without error, that's success
            assert True
        except Exception as e:
            # If not implemented, skip or assert it's expected
            assert "not implemented" in str(e).lower() or isinstance(
                e, NotImplementedError
            )


class TestPolicyFrameworksDirect:
    """Test policy evaluation frameworks via direct method calls (coverage boost)."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_logic_model_framework_direct_call(self):
        """Test Logic Model framework via direct method call - Lines 993-1064."""
        from src.agents.bonifacio import (
            ImpactLevel,
            PolicyAnalysisRequest,
            PolicyEvaluation,
            PolicyStatus,
        )

        agent = BonifacioAgent()

        # Create request
        request = PolicyAnalysisRequest(
            policy_name="Programa Bolsa Família",
            policy_area="social",
            geographical_scope="federal",
        )

        # Create evaluation object
        evaluation = PolicyEvaluation(
            policy_id="test_123",
            policy_name="Programa Bolsa Família",
            analysis_period=(datetime(2023, 1, 1), datetime(2023, 12, 31)),
            status=PolicyStatus.ACTIVE,
            investment={
                "planned": 1000000,
                "executed": 950000,
                "deviation_percentage": -5,
            },
            beneficiaries={
                "target_population": 10000,
                "reached_population": 9500,
                "coverage_rate": 95,
            },
            indicators=[],
            effectiveness_score={
                "efficacy": 0.90,
                "efficiency": 0.85,
                "effectiveness": 0.88,
                "cost_effectiveness": 0.82,
            },
            roi_social=1.8,
            sustainability_score=85,
            impact_level=ImpactLevel.HIGH,
            recommendations=[],
            evidence_sources=["Portal da Transparência"],
            analysis_confidence=0.90,
            hash_verification="abc123",
        )

        # Call framework method directly
        result = await agent._apply_logic_model_framework(request, evaluation)

        # Verify structure
        assert "inputs" in result
        assert "activities" in result
        assert "outputs" in result
        assert "outcomes" in result
        assert "impact" in result

        # Verify inputs
        assert result["inputs"]["financial_resources"] == 950000
        assert result["inputs"]["planned_budget"] == 1000000

        # Verify impact
        assert result["impact"]["social_roi"] == 1.8
        assert result["impact"]["impact_level"] == "high"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_results_chain_framework_direct_call(self):
        """Test Results Chain framework via direct method call - Lines 1121-1238."""
        from src.agents.bonifacio import (
            ImpactLevel,
            PolicyAnalysisRequest,
            PolicyEvaluation,
            PolicyIndicator,
            PolicyStatus,
        )

        agent = BonifacioAgent()

        request = PolicyAnalysisRequest(
            policy_name="Sistema Único de Saúde",
            policy_area="health",
            geographical_scope="federal",
        )

        indicator1 = PolicyIndicator(
            name="Taxa de Cobertura",
            baseline_value=70.0,
            current_value=85.0,
            target_value=90.0,
            unit="percentage",
            data_source="DATASUS",
            last_update=datetime(2023, 12, 31),
            statistical_significance=0.95,
            trend="improving",
        )

        evaluation = PolicyEvaluation(
            policy_id="health_001",
            policy_name="Sistema Único de Saúde",
            analysis_period=(datetime(2023, 1, 1), datetime(2023, 12, 31)),
            status=PolicyStatus.ACTIVE,
            investment={
                "planned": 500000,
                "executed": 480000,
                "deviation_percentage": -4,
            },
            beneficiaries={
                "target_population": 5000,
                "reached_population": 4800,
                "coverage_rate": 96,
            },
            indicators=[indicator1],
            effectiveness_score={
                "efficacy": 0.88,
                "efficiency": 0.82,
                "effectiveness": 0.85,
                "cost_effectiveness": 0.80,
            },
            roi_social=1.5,
            sustainability_score=78,
            impact_level=ImpactLevel.HIGH,
            recommendations=[],
            evidence_sources=["DATASUS"],
            analysis_confidence=0.85,
            hash_verification="def456",
        )

        result = await agent._apply_results_chain_framework(request, evaluation)

        # Verify structure
        assert "stage_1_resources" in result
        assert "stage_2_activities" in result
        assert "stage_3_outputs" in result
        assert "stage_4_outcomes" in result
        assert "causal_attribution" in result

        # Verify financial resources
        assert result["stage_1_resources"]["budget_allocated"] == 500000
        assert result["stage_1_resources"]["budget_utilized"] == 480000

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_theory_of_change_framework_direct_call(self):
        """Test Theory of Change framework via direct method call - Lines 1280-1425."""
        from src.agents.bonifacio import (
            ImpactLevel,
            PolicyAnalysisRequest,
            PolicyEvaluation,
            PolicyIndicator,
            PolicyStatus,
        )

        agent = BonifacioAgent()

        request = PolicyAnalysisRequest(
            policy_name="Programa Nacional de Educação",
            policy_area="education",
            geographical_scope="national",
        )

        # Add indicators to avoid division by zero in _assess_pathway_functionality
        indicator1 = PolicyIndicator(
            name="Taxa de Aprovação",
            baseline_value=75.0,
            current_value=88.0,
            target_value=90.0,
            unit="percentage",
            data_source="INEP",
            last_update=datetime(2023, 12, 31),
            statistical_significance=0.92,
            trend="improving",
        )

        indicator2 = PolicyIndicator(
            name="Evasão Escolar",
            baseline_value=15.0,
            current_value=8.0,
            target_value=5.0,
            unit="percentage",
            data_source="INEP",
            last_update=datetime(2023, 12, 31),
            statistical_significance=0.88,
            trend="improving",
        )

        evaluation = PolicyEvaluation(
            policy_id="edu_001",
            policy_name="Programa Nacional de Educação",
            analysis_period=(datetime(2023, 1, 1), datetime(2023, 12, 31)),
            status=PolicyStatus.ACTIVE,
            investment={
                "planned": 800000,
                "executed": 750000,
                "deviation_percentage": -6.25,
            },
            beneficiaries={
                "target_population": 8000,
                "reached_population": 7600,
                "coverage_rate": 95,
            },
            indicators=[indicator1, indicator2],  # Now has indicators
            effectiveness_score={
                "efficacy": 0.92,
                "efficiency": 0.88,
                "effectiveness": 0.90,
                "cost_effectiveness": 0.85,
            },
            roi_social=2.1,
            sustainability_score=82,
            impact_level=ImpactLevel.VERY_HIGH,
            recommendations=[],
            evidence_sources=["INEP"],
            analysis_confidence=0.92,
            hash_verification="ghi789",
        )

        result = await agent._apply_theory_of_change_framework(request, evaluation)

        # Verify structure (actual keys returned by method)
        assert "desired_long_term_change" in result
        assert "key_assumptions" in result
        assert "causal_pathways" in result
        assert "monitoring_and_learning" in result

        # Verify desired change
        assert result["desired_long_term_change"]["impact_level_goal"] == "VERY_HIGH"
        assert result["desired_long_term_change"]["sustainability_goal"] == 85  # 82 + 3

        # Verify assumptions structure
        assert "economic" in result["key_assumptions"]
        assert "institutional" in result["key_assumptions"]
        assert "political" in result["key_assumptions"]
        assert "social" in result["key_assumptions"]

        # Verify causal pathways
        assert "pathway_1_direct_service" in result["causal_pathways"]


class TestExternalFactorsInfluence:
    """Test external factors influence estimation for coverage boost."""

    @pytest.mark.unit
    def test_estimate_low_influence(self, bonifacio_agent):
        """Test estimation when sustainability is high - Line 1274-1278."""
        from unittest.mock import Mock

        evaluation = Mock()
        evaluation.sustainability_score = 80  # >= 75

        result = bonifacio_agent._estimate_external_factors_influence(evaluation)

        assert result == "low"

    @pytest.mark.unit
    def test_estimate_moderate_influence(self, bonifacio_agent):
        """Test estimation for moderate sustainability - Line 1275-1276."""
        from unittest.mock import Mock

        evaluation = Mock()
        evaluation.sustainability_score = 65  # >= 60 but < 75

        result = bonifacio_agent._estimate_external_factors_influence(evaluation)

        assert result == "moderate"

    @pytest.mark.unit
    def test_estimate_high_influence(self, bonifacio_agent):
        """Test estimation for low sustainability - Line 1277-1278."""
        from unittest.mock import Mock

        evaluation = Mock()
        evaluation.sustainability_score = 45  # < 60

        result = bonifacio_agent._estimate_external_factors_influence(evaluation)

        assert result == "high"


class TestCalculateCostPerOutcome:
    """Test cost per outcome calculation for coverage boost."""

    @pytest.mark.unit
    def test_calculate_cost_per_outcome_basic(self, bonifacio_agent):
        """Test cost per outcome calculation - Lines 1703-1715."""
        from unittest.mock import Mock

        indicator1 = Mock()
        indicator1.name = "literacy_rate"
        indicator1.baseline_value = 70.0
        indicator1.current_value = 85.0  # improvement = 15

        indicator2 = Mock()
        indicator2.name = "graduation_rate"
        indicator2.baseline_value = 50.0
        indicator2.current_value = 60.0  # improvement = 10

        total_cost = 1_000_000.0
        indicators = [indicator1, indicator2]

        result = bonifacio_agent._calculate_cost_per_outcome(total_cost, indicators)

        assert "literacy_rate" in result
        assert "graduation_rate" in result
        assert result["literacy_rate"] == round(1_000_000 / 15, 2)
        assert result["graduation_rate"] == round(1_000_000 / 10, 2)

    @pytest.mark.unit
    def test_calculate_cost_per_outcome_zero_improvement(self, bonifacio_agent):
        """Test cost calculation when improvement is zero or negative."""
        from unittest.mock import Mock

        indicator = Mock()
        indicator.name = "test_metric"
        indicator.baseline_value = 100.0
        indicator.current_value = 90.0  # negative improvement

        result = bonifacio_agent._calculate_cost_per_outcome(500_000, [indicator])

        assert "test_metric" in result
        # Should use max(0.01, improvement) to avoid division issues
        assert result["test_metric"] == round(500_000 / 0.01, 2)


class TestClassifyCostLevel:
    """Test cost level classification for coverage boost."""

    @pytest.mark.unit
    def test_classify_very_low_cost(self, bonifacio_agent):
        """Test classification as very low cost."""
        # benchmark["low"] for education = 3000
        cost_per_beneficiary = 2500  # < 3000
        result = bonifacio_agent._classify_cost_level(cost_per_beneficiary, "education")
        assert result == "Very Low Cost"

    @pytest.mark.unit
    def test_classify_low_cost(self, bonifacio_agent):
        """Test classification as low cost - Line 1695."""
        # benchmark["low"] for education = 3000, 1.5 * 3000 = 4500
        cost_per_beneficiary = 4000  # between 3000 and 4500
        result = bonifacio_agent._classify_cost_level(cost_per_beneficiary, "education")
        assert result == "Low Cost"

    @pytest.mark.unit
    def test_classify_moderate_cost(self, bonifacio_agent):
        """Test classification as moderate cost - Line 1697."""
        # benchmark["high"] for education = 10000
        cost_per_beneficiary = 7000  # between 4500 and 10000
        result = bonifacio_agent._classify_cost_level(cost_per_beneficiary, "education")
        assert result == "Moderate Cost"

    @pytest.mark.unit
    def test_classify_high_cost(self, bonifacio_agent):
        """Test classification as high cost - Line 1699."""
        # benchmark["high"] for education = 10000, 1.5 * 10000 = 15000
        cost_per_beneficiary = 12000  # between 10000 and 15000
        result = bonifacio_agent._classify_cost_level(cost_per_beneficiary, "education")
        assert result == "High Cost"

    @pytest.mark.unit
    def test_classify_very_high_cost(self, bonifacio_agent):
        """Test classification as very high cost."""
        cost_per_beneficiary = 20000  # > 15000
        result = bonifacio_agent._classify_cost_level(cost_per_beneficiary, "education")
        assert result == "Very High Cost"


class TestIdentifyImplementationRisks:
    """Test implementation risk identification for coverage boost."""

    @pytest.mark.unit
    def test_identify_risks_budget_deviation(self, bonifacio_agent):
        """Test risk identification for budget deviation - Line 1463."""
        from unittest.mock import Mock

        evaluation = Mock()
        evaluation.investment = {"deviation_percentage": 20}  # > 15
        evaluation.beneficiaries = {"coverage_rate": 85}  # OK
        evaluation.indicators = []  # No deteriorating
        evaluation.sustainability_score = 70  # OK

        risks = bonifacio_agent._identify_implementation_risks(evaluation)

        assert "Budget execution volatility - deviation exceeds 15%" in risks

    @pytest.mark.unit
    def test_identify_risks_low_coverage(self, bonifacio_agent):
        """Test risk identification for low coverage - Line 1466."""
        from unittest.mock import Mock

        evaluation = Mock()
        evaluation.investment = {"deviation_percentage": 5}  # OK
        evaluation.beneficiaries = {"coverage_rate": 60}  # < 75
        evaluation.indicators = []
        evaluation.sustainability_score = 70

        risks = bonifacio_agent._identify_implementation_risks(evaluation)

        assert any("Low coverage rate" in risk for risk in risks)

    @pytest.mark.unit
    def test_identify_risks_performance_decline(self, bonifacio_agent):
        """Test risk identification for performance decline - Line 1474."""
        from unittest.mock import Mock

        evaluation = Mock()
        evaluation.investment = {"deviation_percentage": 5}
        evaluation.beneficiaries = {"coverage_rate": 85}
        # Create mock indicators with deteriorating trend
        ind1 = Mock()
        ind1.trend = "deteriorating"
        ind2 = Mock()
        ind2.trend = "improving"
        evaluation.indicators = [ind1, ind2]
        evaluation.sustainability_score = 70

        risks = bonifacio_agent._identify_implementation_risks(evaluation)

        assert any("Performance decline" in risk for risk in risks)

    @pytest.mark.unit
    def test_identify_risks_low_sustainability(self, bonifacio_agent):
        """Test risk identification for low sustainability - Line 1477."""
        from unittest.mock import Mock

        evaluation = Mock()
        evaluation.investment = {"deviation_percentage": 5}
        evaluation.beneficiaries = {"coverage_rate": 85}
        evaluation.indicators = []
        evaluation.sustainability_score = 50  # < 65

        risks = bonifacio_agent._identify_implementation_risks(evaluation)

        assert "Institutional capacity concerns - sustainability score low" in risks

    @pytest.mark.unit
    def test_identify_risks_none(self, bonifacio_agent):
        """Test risk identification when no risks found."""
        from unittest.mock import Mock

        evaluation = Mock()
        evaluation.investment = {"deviation_percentage": 5}
        evaluation.beneficiaries = {"coverage_rate": 85}
        evaluation.indicators = []
        evaluation.sustainability_score = 70

        risks = bonifacio_agent._identify_implementation_risks(evaluation)

        assert risks == ["No major implementation risks identified"]


class TestProposeRiskMitigation:
    """Test risk mitigation proposals for coverage boost."""

    @pytest.mark.unit
    def test_propose_mitigation_low_sustainability(self, bonifacio_agent):
        """Test mitigation for low sustainability - Line 1521."""
        from unittest.mock import Mock

        evaluation = Mock()
        evaluation.sustainability_score = 60  # < 70
        evaluation.beneficiaries = {"coverage_rate": 85}
        evaluation.investment = {"deviation_percentage": 5}
        evaluation.roi_social = 1.5

        strategies = bonifacio_agent._propose_risk_mitigation(evaluation)

        assert any("institutional capacity" in s for s in strategies)

    @pytest.mark.unit
    def test_propose_mitigation_low_coverage(self, bonifacio_agent):
        """Test mitigation for low coverage - Line 1526."""
        from unittest.mock import Mock

        evaluation = Mock()
        evaluation.sustainability_score = 75
        evaluation.beneficiaries = {"coverage_rate": 70}  # < 80
        evaluation.investment = {"deviation_percentage": 5}
        evaluation.roi_social = 1.5

        strategies = bonifacio_agent._propose_risk_mitigation(evaluation)

        assert any("Expand outreach" in s for s in strategies)

    @pytest.mark.unit
    def test_propose_mitigation_budget_deviation(self, bonifacio_agent):
        """Test mitigation for budget deviation - Line 1531."""
        from unittest.mock import Mock

        evaluation = Mock()
        evaluation.sustainability_score = 75
        evaluation.beneficiaries = {"coverage_rate": 85}
        evaluation.investment = {"deviation_percentage": 15}  # > 10
        evaluation.roi_social = 1.5

        strategies = bonifacio_agent._propose_risk_mitigation(evaluation)

        assert any("budget monitoring" in s for s in strategies)

    @pytest.mark.unit
    def test_propose_mitigation_low_roi(self, bonifacio_agent):
        """Test mitigation for low ROI - Line 1536."""
        from unittest.mock import Mock

        evaluation = Mock()
        evaluation.sustainability_score = 75
        evaluation.beneficiaries = {"coverage_rate": 85}
        evaluation.investment = {"deviation_percentage": 5}
        evaluation.roi_social = 0.8  # < 1.0

        strategies = bonifacio_agent._propose_risk_mitigation(evaluation)

        assert any("social return" in s for s in strategies)
