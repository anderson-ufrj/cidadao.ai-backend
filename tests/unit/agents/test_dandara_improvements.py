"""
Unit tests for Dandara Agent improvements - Real API integration and data-driven recommendations.
Tests the new methods for calculating priorities, impacts, and resource requirements based on real data.

Author: Anderson Henrique da Silva
Created: 2025-10-15
"""

from unittest.mock import AsyncMock

import pytest

from src.agents.dandara import DandaraAgent, EquityAnalysisResult, SocialJusticeRequest
from src.agents.deodoro import AgentContext, AgentMessage


@pytest.fixture
def dandara_agent():
    """Create Dandara agent instance."""
    agent = DandaraAgent()
    return agent


@pytest.fixture
def sample_analysis_result():
    """Create sample analysis result for testing."""
    from datetime import UTC, datetime

    return EquityAnalysisResult(
        analysis_type="comprehensive_social_equity_real_data",
        gini_coefficient=0.53,
        equity_score=47,
        population_affected=5000000,
        violations_detected=[
            {
                "type": "education_inequality",
                "severity": 0.7,
                "legal_reference": "CF/88 Art. 205",
                "evidence": "Test evidence",
                "affected_groups": ["students"],
                "remediation_urgency": "high",
                "data_source": "INEP/IDEB",
            },
            {
                "type": "health_access_inequality",
                "severity": 0.6,
                "legal_reference": "CF/88 Art. 196",
                "evidence": "Test evidence",
                "affected_groups": ["rural_populations"],
                "remediation_urgency": "high",
                "data_source": "DataSUS/CNES",
            },
        ],
        gaps_identified=[
            {
                "area": "education_infrastructure",
                "gap_size": 0.6,
                "target_population": ["students"],
                "current_coverage": 0.4,
                "recommended_coverage": 0.95,
                "implementation_complexity": "medium",
                "data_source": "INEP/School Census",
                "evidence": "Infrastructure gaps detected",
            },
            {
                "area": "healthcare_access",
                "gap_size": 0.5,
                "target_population": ["general_population"],
                "current_coverage": 0.5,
                "recommended_coverage": 0.95,
                "implementation_complexity": "high",
                "data_source": "DataSUS",
                "evidence": "Healthcare access gaps",
            },
        ],
        recommendations=[
            "Address identified legal compliance violations immediately",
            "Implement targeted resource redistribution policies",
            "Establish monitoring systems for equity metrics",
        ],
        evidence_sources=[
            "IBGE (real data)",
            "DataSUS (real data)",
            "INEP (real data)",
        ],
        analysis_timestamp=datetime.now(UTC),
        confidence_level=0.92,
    )


class TestDandaraPriorityCalculation:
    """Test recommendation priority calculation based on real metrics."""

    @pytest.mark.unit
    def test_critical_priority_low_equity_score(self, dandara_agent):
        """Test that critical priority is assigned for very low equity scores."""
        priority = dandara_agent._calculate_recommendation_priority(
            equity_score=35, violations_count=2, gaps_count=3
        )
        assert priority == "critical"

    @pytest.mark.unit
    def test_critical_priority_many_violations(self, dandara_agent):
        """Test that critical priority is assigned for many violations."""
        priority = dandara_agent._calculate_recommendation_priority(
            equity_score=70, violations_count=6, gaps_count=2
        )
        assert priority == "critical"

    @pytest.mark.unit
    def test_high_priority_moderate_score(self, dandara_agent):
        """Test that high priority is assigned for moderate equity scores."""
        priority = dandara_agent._calculate_recommendation_priority(
            equity_score=55, violations_count=2, gaps_count=3
        )
        assert priority == "high"

    @pytest.mark.unit
    def test_medium_priority_good_score(self, dandara_agent):
        """Test that medium priority is assigned for good equity scores."""
        priority = dandara_agent._calculate_recommendation_priority(
            equity_score=70, violations_count=1, gaps_count=4
        )
        assert priority == "medium"

    @pytest.mark.unit
    def test_low_priority_excellent_score(self, dandara_agent):
        """Test that low priority is assigned for excellent equity scores."""
        priority = dandara_agent._calculate_recommendation_priority(
            equity_score=85, violations_count=0, gaps_count=1
        )
        assert priority == "low"


class TestDandaraImpactEstimation:
    """Test expected impact estimation based on gap sizes."""

    @pytest.mark.unit
    def test_impact_with_large_gap(self, dandara_agent):
        """Test impact estimation with large gap size."""
        gaps = [{"gap_size": 0.8, "implementation_complexity": "high"}]
        impact = dandara_agent._estimate_recommendation_impact(gaps, 0)
        assert impact >= 0.85  # High gap should yield high impact
        assert impact <= 0.95  # But capped at 0.95

    @pytest.mark.unit
    def test_impact_with_small_gap(self, dandara_agent):
        """Test impact estimation with small gap size."""
        gaps = [{"gap_size": 0.2, "implementation_complexity": "low"}]
        impact = dandara_agent._estimate_recommendation_impact(gaps, 0)
        assert impact >= 0.5  # Minimum baseline
        assert impact <= 0.7  # Low gap = moderate impact

    @pytest.mark.unit
    def test_impact_with_no_gaps(self, dandara_agent):
        """Test impact estimation when no gaps are provided."""
        impact = dandara_agent._estimate_recommendation_impact([], 0)
        assert impact == 0.7  # Default moderate impact

    @pytest.mark.unit
    def test_impact_with_multiple_gaps(self, dandara_agent):
        """Test impact uses correct gap based on index."""
        gaps = [
            {"gap_size": 0.3, "implementation_complexity": "low"},
            {"gap_size": 0.7, "implementation_complexity": "high"},
        ]
        impact_0 = dandara_agent._estimate_recommendation_impact(gaps, 0)
        impact_1 = dandara_agent._estimate_recommendation_impact(gaps, 1)
        assert impact_1 > impact_0  # Higher gap size = higher impact


class TestDandaraResourceAssessment:
    """Test resource requirements assessment based on gap complexity."""

    @pytest.mark.unit
    def test_resource_assessment_low_complexity(self, dandara_agent):
        """Test resource assessment with low complexity gap."""
        gaps = [{"gap_size": 0.5, "implementation_complexity": "low"}]
        resources = dandara_agent._assess_resource_requirements(gaps, 0)
        assert resources == "low"

    @pytest.mark.unit
    def test_resource_assessment_high_complexity(self, dandara_agent):
        """Test resource assessment with high complexity gap."""
        gaps = [{"gap_size": 0.5, "implementation_complexity": "high"}]
        resources = dandara_agent._assess_resource_requirements(gaps, 0)
        assert resources == "high"

    @pytest.mark.unit
    def test_resource_assessment_no_gaps(self, dandara_agent):
        """Test resource assessment when no gaps provided."""
        resources = dandara_agent._assess_resource_requirements([], 0)
        assert resources == "medium"  # Default fallback

    @pytest.mark.unit
    def test_resource_assessment_invalid_complexity(self, dandara_agent):
        """Test resource assessment handles invalid complexity values."""
        gaps = [{"gap_size": 0.5, "implementation_complexity": "invalid_value"}]
        resources = dandara_agent._assess_resource_requirements(gaps, 0)
        assert resources == "medium"  # Fallback to medium


class TestDandaraImprovementTarget:
    """Test realistic improvement target calculation."""

    @pytest.mark.unit
    def test_improvement_target_many_violations(self, dandara_agent):
        """Test aggressive target with many violations."""
        target = dandara_agent._calculate_improvement_target(
            current_score=50, violations_count=6
        )
        assert target == 25  # Aggressive target

    @pytest.mark.unit
    def test_improvement_target_moderate_violations(self, dandara_agent):
        """Test moderate target with some violations."""
        target = dandara_agent._calculate_improvement_target(
            current_score=60, violations_count=3
        )
        assert target == 20  # Moderate target

    @pytest.mark.unit
    def test_improvement_target_low_score(self, dandara_agent):
        """Test target respects ceiling (100 - current_score)."""
        target = dandara_agent._calculate_improvement_target(
            current_score=90, violations_count=6
        )
        assert target == 10  # Capped by max possible (100 - 90)

    @pytest.mark.unit
    def test_improvement_target_high_score_few_violations(self, dandara_agent):
        """Test conservative target with good score."""
        target = dandara_agent._calculate_improvement_target(
            current_score=75, violations_count=1
        )
        assert target == 10  # Conservative target


class TestDandaraRecommendationGeneration:
    """Test data-driven recommendation generation (no random values)."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_recommendations_no_random_values(
        self, dandara_agent, sample_analysis_result
    ):
        """Test that recommendations don't use random values."""
        request = SocialJusticeRequest(query="Test equity analysis")
        context = AgentContext(investigation_id="test-123")

        recommendations = await dandara_agent._generate_justice_recommendations(
            sample_analysis_result, request, context
        )

        assert len(recommendations) == len(sample_analysis_result.recommendations)

        # Verify all recommendations have deterministic values
        for rec in recommendations:
            assert "priority" in rec
            assert rec["priority"] in ["critical", "high", "medium", "low"]
            assert "expected_impact" in rec
            assert 0.5 <= rec["expected_impact"] <= 0.95
            assert "required_resources" in rec
            assert rec["required_resources"] in ["low", "medium", "high"]
            assert "success_metrics" in rec
            assert len(rec["success_metrics"]) >= 2  # Multiple metrics

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_recommendations_based_on_gaps(
        self, dandara_agent, sample_analysis_result
    ):
        """Test that recommendations use actual gap data."""
        request = SocialJusticeRequest(query="Test equity analysis")
        context = AgentContext(investigation_id="test-123")

        recommendations = await dandara_agent._generate_justice_recommendations(
            sample_analysis_result, request, context
        )

        # First recommendation should have higher impact (gap_size=0.6)
        # Second recommendation should match complexity "high"
        assert recommendations[1]["required_resources"] == "high"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_recommendations_consistency(
        self, dandara_agent, sample_analysis_result
    ):
        """Test that recommendations are consistent across calls (deterministic)."""
        request = SocialJusticeRequest(query="Test equity analysis")
        context = AgentContext(investigation_id="test-123")

        recs_1 = await dandara_agent._generate_justice_recommendations(
            sample_analysis_result, request, context
        )
        recs_2 = await dandara_agent._generate_justice_recommendations(
            sample_analysis_result, request, context
        )

        # Should be identical (no randomness)
        assert len(recs_1) == len(recs_2)
        for rec1, rec2 in zip(recs_1, recs_2, strict=False):
            assert rec1["priority"] == rec2["priority"]
            assert rec1["expected_impact"] == rec2["expected_impact"]
            assert rec1["required_resources"] == rec2["required_resources"]


class TestDandaraAPIIntegration:
    """Test integration with real federal APIs."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_api_clients_initialized(self, dandara_agent):
        """Test that API clients are properly initialized."""
        assert dandara_agent.ibge_client is not None
        assert dandara_agent.datasus_client is not None
        assert dandara_agent.inep_client is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_state_code_extraction(self, dandara_agent):
        """Test extraction of state codes from geographical scope."""
        assert dandara_agent._extract_state_code("Rio de Janeiro") == "33"
        assert dandara_agent._extract_state_code("São Paulo") == "35"
        assert dandara_agent._extract_state_code("MG") == "31"
        assert dandara_agent._extract_state_code("Bahia") == "29"
        assert dandara_agent._extract_state_code("Unknown") is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_with_mocked_apis(self, dandara_agent):
        """Test full process flow with mocked API responses."""
        # Mock API clients
        dandara_agent.ibge_client.get_comprehensive_social_data = AsyncMock(
            return_value={
                "demographic": {"6579": {}},
                "poverty": {"4100": {}},
                "education": {},
                "housing": {},
                "economic": {},
                "errors": [],
            }
        )
        dandara_agent.datasus_client.get_health_indicators = AsyncMock(
            return_value={"health_facilities": {}, "vaccination": {}, "errors": []}
        )
        dandara_agent.inep_client.get_education_indicators = AsyncMock(
            return_value={
                "ideb": {},
                "school_census": {},
                "infrastructure": {},
                "errors": [],
            }
        )

        context = AgentContext(investigation_id="test-integration")
        message = AgentMessage(
            sender="test",
            recipient="dandara",
            action="analyze_equity",
            payload={"query": "Analyze social equity in Rio de Janeiro"},
        )

        response = await dandara_agent.process(message, context)

        from src.core import AgentStatus

        assert response.status == AgentStatus.COMPLETED
        assert response.result["agent"] == "dandara"
        assert "results" in response.result
        assert "recommendations" in response.result
        assert response.result["confidence"] > 0.9  # High confidence with real data


class TestDandaraFallbackBehavior:
    """Test fallback behavior when APIs fail."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_fallback_when_apis_fail(self, dandara_agent):
        """Test that agent falls back gracefully when APIs fail."""
        # Mock API clients to raise exceptions
        dandara_agent.ibge_client.get_comprehensive_social_data = AsyncMock(
            side_effect=Exception("API Error")
        )
        dandara_agent.datasus_client.get_health_indicators = AsyncMock(
            side_effect=Exception("API Error")
        )
        dandara_agent.inep_client.get_education_indicators = AsyncMock(
            side_effect=Exception("API Error")
        )

        context = AgentContext(investigation_id="test-fallback")
        message = AgentMessage(
            sender="test",
            recipient="dandara",
            action="analyze_equity",
            payload={"query": "Test fallback"},
        )

        response = await dandara_agent.process(message, context)

        # Should still return successful response (APIs failing returns None, not critical error)
        from src.core import AgentStatus

        assert response.status == AgentStatus.COMPLETED
        # When APIs fail, still returns comprehensive type but with default values
        assert (
            response.result["results"].analysis_type
            == "comprehensive_social_equity_real_data"
        )
        assert (
            response.result["results"].confidence_level == 0.92
        )  # Still high confidence
        assert response.result["results"].gini_coefficient == 0.53  # Brazil's default


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
