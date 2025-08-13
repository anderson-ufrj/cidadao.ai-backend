"""
Complete unit tests for Dandara Agent - Social inclusion and equity analysis specialist.
Tests diversity metrics, inclusion analysis, social impact assessment, and equity calculations.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4

from src.agents.dandara import (
    DandaraAgent,
    EquityAnalysisResult,
    SocialJusticeRequest,
)
from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
)
from src.core.exceptions import AgentExecutionError, DataAnalysisError


@pytest.fixture
def mock_social_data_service():
    """Mock comprehensive social data service."""
    service = AsyncMock()
    
    # Mock demographic data
    service.get_demographic_data.return_value = {
        "total_population": 10000000,
        "demographics": {
            "gender": {"female": 0.52, "male": 0.48, "non_binary": 0.005},
            "race": {
                "white": 0.43, "black": 0.35, "mixed": 0.20, 
                "indigenous": 0.015, "asian": 0.005
            },
            "age_groups": {
                "0-17": 0.22, "18-30": 0.25, "31-50": 0.35, 
                "51-65": 0.13, "65+": 0.05
            },
            "income_quintiles": {
                "q1": 0.02, "q2": 0.07, "q3": 0.13, 
                "q4": 0.28, "q5": 0.50
            },
            "education_levels": {
                "no_education": 0.08, "elementary": 0.35, 
                "high_school": 0.40, "higher_education": 0.17
            }
        },
        "geographic_distribution": {
            "urban": 0.85, "rural": 0.15
        }
    }
    
    # Mock policy access data
    service.get_policy_access_data.return_value = {
        "healthcare_access": {
            "overall": 0.72,
            "by_race": {"white": 0.85, "black": 0.62, "mixed": 0.68},
            "by_income": {"q1": 0.45, "q2": 0.58, "q3": 0.72, "q4": 0.82, "q5": 0.95},
            "by_gender": {"male": 0.70, "female": 0.74}
        },
        "education_access": {
            "overall": 0.89,
            "by_race": {"white": 0.95, "black": 0.82, "mixed": 0.87},
            "by_income": {"q1": 0.68, "q2": 0.78, "q3": 0.88, "q4": 0.94, "q5": 0.98}
        },
        "housing_access": {
            "overall": 0.78,
            "adequate_housing": 0.65,
            "by_income": {"q1": 0.35, "q2": 0.52, "q3": 0.68, "q4": 0.85, "q5": 0.95}
        }
    }
    
    # Mock employment data
    service.get_employment_data.return_value = {
        "employment_rate": 0.68,
        "unemployment_by_race": {"white": 0.08, "black": 0.15, "mixed": 0.12},
        "wage_gap_gender": {"male": 1.0, "female": 0.77},
        "formal_employment": 0.62,
        "income_distribution": [0.02, 0.05, 0.08, 0.15, 0.25, 0.45]  # Deciles
    }
    
    return service


@pytest.fixture
def mock_policy_database():
    """Mock policy database for inclusion policies."""
    db = AsyncMock()
    
    db.get_inclusion_policies.return_value = [
        {
            "id": "policy_001",
            "name": "Programa Nacional de Inclusão Digital",
            "target_groups": ["rural_population", "elderly", "low_income"],
            "budget": 500000000.0,
            "beneficiaries_target": 2000000,
            "beneficiaries_reached": 1400000,
            "effectiveness_score": 0.70,
            "start_date": "2023-01-01",
            "status": "active"
        },
        {
            "id": "policy_002",
            "name": "Programa de Habitação Social",
            "target_groups": ["low_income", "homeless", "single_mothers"],
            "budget": 2000000000.0,
            "beneficiaries_target": 500000,
            "beneficiaries_reached": 320000,
            "effectiveness_score": 0.64,
            "start_date": "2022-06-01",
            "status": "active"
        }
    ]
    
    return db


@pytest.fixture
def mock_statistical_engine():
    """Mock statistical engine for equity calculations."""
    engine = AsyncMock()
    
    engine.calculate_gini_coefficient.return_value = {
        "overall_gini": 0.53,
        "by_region": {"northeast": 0.58, "southeast": 0.48, "south": 0.45},
        "by_demographic": {
            "race_gini": {"white": 0.42, "black": 0.38, "mixed": 0.40},
            "gender_gini": {"male": 0.51, "female": 0.48}
        },
        "temporal_trend": [0.57, 0.55, 0.54, 0.53],  # Last 4 years
        "confidence_interval": [0.51, 0.55]
    }
    
    engine.perform_intersectional_analysis.return_value = {
        "intersections": [
            {
                "groups": ["black", "female", "low_income"],
                "population_size": 850000,
                "disadvantage_score": 0.82,
                "policy_gaps": ["healthcare_access", "employment_opportunities"]
            },
            {
                "groups": ["indigenous", "rural", "elderly"],
                "population_size": 120000,
                "disadvantage_score": 0.89,
                "policy_gaps": ["digital_inclusion", "healthcare_access", "transportation"]
            }
        ],
        "compound_discrimination_index": 0.67,
        "most_vulnerable_intersection": ["black", "female", "low_income"]
    }
    
    return engine


@pytest.fixture
def agent_context():
    """Test agent context for social justice analysis."""
    return AgentContext(
        investigation_id="social-justice-001",
        user_id="social-analyst",
        session_id="equity-analysis-session",
        metadata={
            "analysis_type": "social_equity",
            "scope": "national",
            "focus_areas": ["education", "healthcare", "housing"]
        },
        trace_id="trace-dandara-321"
    )


@pytest.fixture
def dandara_agent(mock_social_data_service, mock_policy_database, mock_statistical_engine):
    """Create Dandara agent with mocked dependencies."""
    with patch("src.agents.dandara.SocialDataService", return_value=mock_social_data_service), \
         patch("src.agents.dandara.PolicyDatabase", return_value=mock_policy_database), \
         patch("src.agents.dandara.StatisticalEngine", return_value=mock_statistical_engine):
        
        agency = DandaraAgent()
        return agency


class TestDandaraAgent:
    """Comprehensive test suite for Dandara (Social Justice Agent)."""
    
    @pytest.mark.unit
    def test_agent_initialization(self, dandara_agent):
        """Test Dandara agent initialization and capabilities."""
        assert dandara_agent.name == "dandara"
        assert "Social Justice Agent" in dandara_agent.description
        
        # Check comprehensive capabilities
        expected_capabilities = [
            "social_equity_analysis",
            "inclusion_policy_monitoring",
            "gini_coefficient_calculation", 
            "demographic_disparity_detection",
            "social_justice_violation_identification",
            "distributive_justice_assessment",
            "policy_effectiveness_evaluation",
            "intersectional_analysis",
            "vulnerability_mapping",
            "equity_gap_identification"
        ]
        
        for capability in expected_capabilities:
            assert capability in dandara_agent.capabilities
        
        # Check equity metrics are loaded
        assert hasattr(dandara_agent, '_equity_metrics')
        assert "gini_coefficient" in dandara_agent._equity_metrics
        assert "atkinson_index" in dandara_agent._equity_metrics
    
    @pytest.mark.unit
    async def test_comprehensive_equity_analysis(self, dandara_agent, agent_context):
        """Test comprehensive social equity analysis."""
        message = AgentMessage(
            sender="policy_analyst",
            recipient="dandara",
            action="analyze_social_equity",
            payload={
                "analysis_scope": "national",
                "target_groups": ["black", "indigenous", "women", "elderly"],
                "policy_areas": ["education", "healthcare", "housing", "employment"],
                "metrics": ["gini", "atkinson", "theil", "palma_ratio"],
                "include_intersectional": True
            }
        )
        
        response = await dandara_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "equity_analysis" in response.result
        
        analysis = response.result["equity_analysis"]
        assert "overall_gini" in analysis
        assert analysis["overall_gini"] == 0.53
        assert "demographic_disparities" in analysis
        assert "policy_effectiveness" in analysis
        assert "intersectional_analysis" in analysis
    
    @pytest.mark.unit
    async def test_gini_coefficient_calculation(self, dandara_agent, agent_context):
        """Test Gini coefficient calculation for different groups."""
        message = AgentMessage(
            sender="statistical_analyst",
            recipient="dandara", 
            action="calculate_gini_coefficient",
            payload={
                "income_data": [100, 200, 300, 400, 500, 1000, 2000, 5000],
                "group_breakdowns": ["race", "gender", "region"],
                "confidence_intervals": True,
                "temporal_analysis": True
            }
        )
        
        response = await dandara_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "gini_analysis" in response.result
        
        gini = response.result["gini_analysis"]
        assert "overall_gini" in gini
        assert "by_demographic" in gini
        assert "temporal_trend" in gini
        assert "confidence_interval" in gini
        
        # Validate Gini coefficient range
        assert 0 <= gini["overall_gini"] <= 1
    
    @pytest.mark.unit
    async def test_intersectional_discrimination_analysis(self, dandara_agent, agent_context):
        """Test intersectional analysis of compound discrimination."""
        message = AgentMessage(
            sender="discrimination_analyst",
            recipient="dandara",
            action="analyze_intersectional_discrimination",
            payload={
                "intersection_groups": [
                    ["black", "female"],
                    ["indigenous", "rural"],
                    ["elderly", "low_income"],
                    ["lgbtq", "young_adult"]
                ],
                "outcome_variables": ["income", "education", "healthcare_access"],
                "comparison_method": "multiple_regression",
                "control_variables": ["region", "age", "education_level"]
            }
        )
        
        response = await dandara_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "intersectional_analysis" in response.result
        
        intersectional = response.result["intersectional_analysis"]
        assert "intersections" in intersectional
        assert "compound_discrimination_index" in intersectional
        assert "most_vulnerable_intersection" in intersectional
        
        # Check intersections are properly analyzed
        intersections = intersectional["intersections"]
        assert len(intersections) >= 2
        for intersection in intersections:
            assert "groups" in intersection
            assert "disadvantage_score" in intersection
            assert 0 <= intersection["disadvantage_score"] <= 1
    
    @pytest.mark.unit
    async def test_policy_effectiveness_monitoring(self, dandara_agent, agent_context):
        """Test monitoring of inclusion policy effectiveness."""
        message = AgentMessage(
            sender="policy_monitor",
            recipient="dandara",
            action="monitor_inclusion_policies",
            payload={
                "policy_categories": ["housing", "education", "healthcare", "employment"],
                "effectiveness_metrics": ["coverage", "impact", "equity_improvement"],
                "target_groups": ["vulnerable_populations"],
                "evaluation_period": "2023-2024"
            }
        )
        
        response = await dandara_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "policy_monitoring" in response.result
        
        monitoring = response.result["policy_monitoring"]
        assert "policy_effectiveness" in monitoring
        assert "coverage_analysis" in monitoring
        assert "equity_impact" in monitoring
        assert "recommendations" in monitoring
        
        # Check policy evaluation results
        effectiveness = monitoring["policy_effectiveness"]
        assert len(effectiveness) >= 2  # At least 2 policies evaluated
    
    @pytest.mark.unit
    async def test_vulnerability_mapping(self, dandara_agent, agent_context):
        """Test vulnerability mapping and risk assessment."""
        message = AgentMessage(
            sender="vulnerability_analyst",
            recipient="dandara",
            action="map_social_vulnerabilities",
            payload={
                "vulnerability_dimensions": [
                    "economic", "social", "environmental", "political"
                ],
                "geographic_granularity": "municipality",
                "risk_factors": [
                    "poverty", "unemployment", "poor_housing", 
                    "limited_education", "health_risks"
                ],
                "priority_ranking": True
            }
        )
        
        response = await dandara_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "vulnerability_mapping" in response.result
        
        mapping = response.result["vulnerability_mapping"]
        assert "vulnerability_index" in mapping
        assert "geographic_distribution" in mapping
        assert "priority_areas" in mapping
        assert "intervention_recommendations" in mapping
    
    @pytest.mark.unit
    async def test_demographic_disparity_detection(self, dandara_agent, agent_context):
        """Test detection of demographic disparities."""
        message = AgentMessage(
            sender="disparity_detector",
            recipient="dandara",
            action="detect_demographic_disparities",
            payload={
                "outcome_variables": ["income", "education_attainment", "healthcare_access"],
                "demographic_groups": ["race", "gender", "age", "location"],
                "statistical_tests": ["chi_square", "anova", "regression"],
                "significance_level": 0.05,
                "effect_size_threshold": 0.2
            }
        )
        
        response = await dandara_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "disparity_analysis" in response.result
        
        disparities = response.result["disparity_analysis"]
        assert "significant_disparities" in disparities
        assert "effect_sizes" in disparities
        assert "statistical_significance" in disparities
        assert "disparity_ranking" in disparities
    
    @pytest.mark.unit
    async def test_distributive_justice_assessment(self, dandara_agent, agent_context):
        """Test distributive justice assessment."""
        message = AgentMessage(
            sender="justice_assessor",
            recipient="dandara",
            action="assess_distributive_justice",
            payload={
                "distribution_type": "public_resources",
                "justice_principles": ["equality", "equity", "need_based", "merit_based"],
                "resource_categories": ["education_funding", "healthcare_spending", "infrastructure"],
                "population_segments": ["income_quintiles", "geographic_regions"],
                "fairness_metrics": ["deviation_from_equality", "needs_satisfaction"]
            }
        )
        
        response = await dandara_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "distributive_justice" in response.result
        
        justice = response.result["distributive_justice"]
        assert "justice_scores" in justice
        assert "resource_allocation" in justice
        assert "fairness_assessment" in justice
        assert "redistribution_recommendations" in justice
    
    @pytest.mark.unit
    async def test_social_justice_violation_identification(self, dandara_agent, agent_context):
        """Test identification of social justice violations."""
        message = AgentMessage(
            sender="violation_detector", 
            recipient="dandara",
            action="identify_justice_violations",
            payload={
                "violation_types": [
                    "discriminatory_practices", "unequal_access", 
                    "systemic_bias", "procedural_unfairness"
                ],
                "evidence_sources": ["policy_documents", "outcome_data", "citizen_complaints"],
                "severity_classification": True,
                "legal_framework_reference": True
            }
        )
        
        response = await dandara_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "violation_analysis" in response.result
        
        violations = response.result["violation_analysis"]
        assert "identified_violations" in violations
        assert "severity_classification" in violations
        assert "evidence_strength" in violations
        assert "legal_implications" in violations
        assert "remediation_recommendations" in violations
    
    @pytest.mark.unit
    async def test_equity_gap_identification(self, dandara_agent, agent_context):
        """Test identification and quantification of equity gaps."""
        message = AgentMessage(
            sender="gap_analyst",
            recipient="dandara",
            action="identify_equity_gaps",
            payload={
                "gap_dimensions": ["outcome_gaps", "access_gaps", "treatment_gaps"],
                "target_groups": ["racial_minorities", "women", "rural_populations"],
                "benchmark_standards": ["national_average", "international_standards"],
                "gap_size_thresholds": {"minor": 0.1, "moderate": 0.2, "severe": 0.3},
                "prioritization_criteria": ["population_affected", "gap_severity", "remedy_feasibility"]
            }
        )
        
        response = await dandara_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "equity_gaps" in response.result
        
        gaps = response.result["equity_gaps"]
        assert "identified_gaps" in gaps
        assert "gap_prioritization" in gaps  
        assert "closure_strategies" in gaps
        assert "resource_requirements" in gaps
    
    @pytest.mark.unit
    async def test_temporal_equity_analysis(self, dandara_agent, agent_context):
        """Test temporal analysis of equity trends."""
        message = AgentMessage(
            sender="temporal_analyst",
            recipient="dandara",
            action="analyze_equity_trends",
            payload={
                "time_period": "2020-2024",
                "trend_indicators": ["gini_coefficient", "poverty_rate", "education_gap"],
                "trend_analysis_methods": ["linear_regression", "breakpoint_detection"],
                "forecast_horizon": 24,  # months
                "policy_impact_assessment": True
            }
        )
        
        response = await dandara_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "temporal_analysis" in response.result
        
        temporal = response.result["temporal_analysis"]
        assert "trend_analysis" in temporal
        assert "change_patterns" in temporal
        assert "forecast_projections" in temporal
        assert "policy_impact_evaluation" in temporal
    
    @pytest.mark.unit
    async def test_comparative_equity_analysis(self, dandara_agent, agent_context):
        """Test comparative analysis with other regions/countries."""
        message = AgentMessage(
            sender="comparative_analyst",
            recipient="dandara",
            action="compare_equity_performance",
            payload={
                "comparison_entities": ["other_countries", "other_states", "peer_cities"],
                "comparison_metrics": ["gini_coefficient", "social_mobility", "inequality_trends"],
                "benchmarking_standards": ["OECD_average", "Latin_America_average"],
                "best_practices_identification": True,
                "performance_ranking": True
            }
        )
        
        response = await dandara_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "comparative_analysis" in response.result
        
        comparison = response.result["comparative_analysis"]
        assert "performance_ranking" in comparison
        assert "benchmark_comparison" in comparison
        assert "best_practices" in comparison
        assert "improvement_potential" in comparison
    
    @pytest.mark.unit
    async def test_error_handling_insufficient_data(self, dandara_agent, agent_context):
        """Test error handling when demographic data is insufficient."""
        # Mock empty data response
        dandara_agent.social_data_service.get_demographic_data.return_value = {"total_population": 0}
        
        message = AgentMessage(
            sender="test_agent",
            recipient="dandara",
            action="analyze_social_equity",
            payload={"analysis_scope": "regional"}
        )
        
        response = await dandara_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.ERROR
        assert "insufficient data" in response.error.lower()
    
    @pytest.mark.unit
    async def test_batch_equity_analysis(self, dandara_agent, agent_context):
        """Test batch analysis of multiple regions/populations."""
        message = AgentMessage(
            sender="batch_analyst",
            recipient="dandara",
            action="batch_equity_analysis",
            payload={
                "analysis_units": ["northeast", "southeast", "south", "center_west", "north"],
                "comparison_metrics": ["gini", "poverty_rate", "education_index"],
                "standardized_reporting": True,
                "cross_regional_comparison": True
            }
        )
        
        response = await dandara_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "batch_analysis" in response.result
        
        batch = response.result["batch_analysis"]
        assert "regional_results" in batch
        assert "comparative_summary" in batch
        assert "regional_rankings" in batch
        assert len(batch["regional_results"]) == 5  # All regions analyzed
    
    @pytest.mark.unit
    async def test_real_time_equity_monitoring(self, dandara_agent, agent_context):
        """Test real-time equity monitoring setup."""
        message = AgentMessage(
            sender="monitoring_system",
            recipient="dandara",
            action="setup_equity_monitoring",
            payload={
                "monitoring_indicators": ["gini_coefficient", "poverty_rate", "education_gap"],
                "update_frequency": "monthly",
                "alert_thresholds": {"gini_increase": 0.02, "poverty_increase": 0.05},
                "dashboard_integration": True,
                "automated_reporting": True
            }
        )
        
        response = await dandara_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "monitoring_setup" in response.result
        
        monitoring = response.result["monitoring_setup"]
        assert "dashboard_configuration" in monitoring
        assert "alert_system" in monitoring
        assert "reporting_schedule" in monitoring
        assert "data_pipelines" in monitoring


class TestEquityAnalysisResult:
    """Test EquityAnalysisResult data model."""
    
    @pytest.mark.unit
    def test_equity_result_creation(self):
        """Test creating equity analysis result."""
        result = EquityAnalysisResult(
            analysis_type="comprehensive_equity",
            gini_coefficient=0.53,
            equity_score=67,
            population_affected=8500000,
            violations_detected=[
                {"type": "access_discrimination", "severity": "high", "affected_groups": ["black", "indigenous"]}
            ],
            gaps_identified=[
                {"dimension": "education", "gap_size": 0.25, "priority": "high"}
            ],
            recommendations=["Increase targeted education funding", "Implement anti-discrimination measures"],
            evidence_sources=["IBGE", "PNAD", "DataSUS"],
            analysis_timestamp=datetime.utcnow(),
            confidence_level=0.85
        )
        
        assert result.analysis_type == "comprehensive_equity"
        assert result.gini_coefficient == 0.53
        assert result.equity_score == 67
        assert len(result.violations_detected) == 1
        assert len(result.gaps_identified) == 1
        assert len(result.recommendations) == 2
    
    @pytest.mark.unit
    def test_equity_score_validation(self):
        """Test equity score validation and categorization."""
        high_equity = EquityAnalysisResult(
            analysis_type="test",
            gini_coefficient=0.25,  # Low inequality
            equity_score=85,  # High equity
            population_affected=1000000,
            violations_detected=[],
            gaps_identified=[],
            recommendations=[],
            evidence_sources=[],
            analysis_timestamp=datetime.utcnow(),
            confidence_level=0.9
        )
        
        low_equity = EquityAnalysisResult(
            analysis_type="test",
            gini_coefficient=0.75,  # High inequality
            equity_score=25,  # Low equity
            population_affected=1000000,
            violations_detected=[],
            gaps_identified=[],
            recommendations=[],
            evidence_sources=[],
            analysis_timestamp=datetime.utcnow(),
            confidence_level=0.8
        )
        
        assert high_equity.equity_score > 80  # High equity
        assert low_equity.equity_score < 40   # Low equity
        assert high_equity.gini_coefficient < 0.3  # Low inequality
        assert low_equity.gini_coefficient > 0.7   # High inequality


class TestSocialJusticeRequest:
    """Test SocialJusticeRequest data model."""
    
    @pytest.mark.unit
    def test_request_creation(self):
        """Test creating social justice request."""
        request = SocialJusticeRequest(
            query="Analyze gender equity in healthcare access",
            target_groups=["women", "transgender"],
            policy_areas=["healthcare", "reproductive_rights"],
            geographical_scope="national",
            time_period=("2020-01-01", "2024-12-31"),
            metrics_focus=["access_rates", "quality_measures", "satisfaction_scores"]
        )
        
        assert "gender equity" in request.query
        assert len(request.target_groups) == 2
        assert len(request.policy_areas) == 2
        assert request.geographical_scope == "national"
        assert len(request.metrics_focus) == 3
    
    @pytest.mark.unit
    def test_request_validation(self):
        """Test request validation."""
        # Valid request
        valid_request = SocialJusticeRequest(
            query="Valid social justice analysis query"
        )
        assert "Valid" in valid_request.query
        
        # Test with empty query
        with pytest.raises(ValueError):
            SocialJusticeRequest(query="")


@pytest.mark.integration
class TestDandaraIntegration:
    """Integration tests for Dandara agent with realistic scenarios."""
    
    @pytest.mark.integration
    async def test_comprehensive_national_equity_assessment(self, dandara_agent):
        """Test comprehensive national equity assessment workflow."""
        context = AgentContext(
            investigation_id="national-equity-assessment",
            metadata={"scope": "national", "priority": "high"}
        )
        
        # Step 1: Demographic analysis
        demographic_msg = AgentMessage(
            sender="national_planner",
            recipient="dandara",
            action="analyze_social_equity",  
            payload={
                "analysis_scope": "national",
                "comprehensive_assessment": True
            }
        )
        
        demographic_response = await dandara_agent.process(demographic_msg, context)
        assert demographic_response.status == AgentStatus.COMPLETED
        
        # Step 2: Policy effectiveness analysis
        policy_msg = AgentMessage(
            sender="national_planner",
            recipient="dandara",
            action="monitor_inclusion_policies",
            payload={"evaluation_period": "2023-2024"}
        )
        
        policy_response = await dandara_agent.process(policy_msg, context)
        assert policy_response.status == AgentStatus.COMPLETED
        
        # Verify comprehensive analysis
        assert "equity_analysis" in demographic_response.result
        assert "policy_monitoring" in policy_response.result
    
    @pytest.mark.integration
    async def test_real_world_discrimination_investigation(self, dandara_agent):
        """Test real-world discrimination investigation scenario."""
        context = AgentContext(
            investigation_id="discrimination-investigation",
            metadata={"urgency": "high", "legal_implications": True}
        )
        
        # Investigate potential discrimination in hiring practices
        message = AgentMessage(
            sender="legal_investigator",
            recipient="dandara",
            action="analyze_intersectional_discrimination",
            payload={
                "investigation_context": "employment_discrimination",
                "suspected_bias": ["racial", "gender"],
                "evidence_analysis": True
            }
        )
        
        response = await dandara_agent.process(message, context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "intersectional_analysis" in response.result
        
        # Check investigation thoroughness
        analysis = response.result["intersectional_analysis"]
        assert "compound_discrimination_index" in analysis
        assert "most_vulnerable_intersection" in analysis