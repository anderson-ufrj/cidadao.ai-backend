"""
Unit tests for Bonifácio Agent - Public policy analysis specialist.
Tests policy effectiveness, impact assessment, and governance analysis capabilities.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4

from src.agents.bonifacio import (
    BonifacioAgent,
    PolicyStatus,
    ImpactLevel,
    PolicyIndicator,
    PolicyAnalysisRequest,
    PolicyEffectivenessReport,
)
from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
)
from src.core.exceptions import AgentExecutionError, DataAnalysisError


@pytest.fixture
def mock_policy_data_service():
    """Mock policy data service for testing."""
    service = AsyncMock()
    
    # Mock policy database
    service.get_policies.return_value = [
        {
            "id": "policy_001",
            "name": "Programa Nacional de Educação Digital",
            "status": PolicyStatus.ACTIVE.value,
            "start_date": "2023-01-01",
            "budget_allocated": 500000000.0,
            "budget_executed": 350000000.0,
            "target_beneficiaries": 1000000,
            "actual_beneficiaries": 750000,
            "ministry": "Ministério da Educação",
            "indicators": [
                {
                    "name": "digital_literacy_rate",
                    "baseline": 0.45,
                    "current": 0.62,
                    "target": 0.75
                },
                {
                    "name": "internet_access_schools",
                    "baseline": 0.60,
                    "current": 0.78,
                    "target": 0.90
                }
            ]
        },
        {
            "id": "policy_002",
            "name": "Programa de Saúde Preventiva",
            "status": PolicyStatus.UNDER_REVIEW.value,
            "start_date": "2023-06-01",
            "budget_allocated": 800000000.0,  
            "budget_executed": 200000000.0,
            "target_beneficiaries": 2000000,
            "actual_beneficiaries": 400000,
            "ministry": "Ministério da Saúde",
            "indicators": [
                {
                    "name": "vaccination_coverage",
                    "baseline": 0.70,
                    "current": 0.85,
                    "target": 0.95
                }
            ]
        }
    ]
    
    # Mock impact assessment data
    service.get_impact_metrics.return_value = {
        "social_impact": {
            "education_improvement": 0.78,
            "health_outcomes": 0.65,
            "poverty_reduction": 0.42
        },
        "economic_impact": {
            "gdp_growth_contribution": 0.03,
            "employment_created": 125000,
            "productivity_increase": 0.15
        },
        "sustainability_score": 0.72,
        "stakeholder_satisfaction": 0.68
    }
    
    # Mock comparative analysis data
    service.get_historical_policies.return_value = [
        {
            "id": "historical_001",
            "name": "Previous Digital Program",
            "effectiveness_score": 0.65,
            "budget_efficiency": 0.70,
            "completion_rate": 0.80
        }
    ]
    
    return service


@pytest.fixture
def mock_statistical_engine():
    """Mock statistical analysis engine."""
    engine = AsyncMock()
    
    engine.calculate_effectiveness_score.return_value = {
        "overall_score": 0.73,
        "dimension_scores": {
            "implementation": 0.75,
            "outcomes": 0.78,
            "efficiency": 0.65,
            "sustainability": 0.72
        },
        "confidence_interval": [0.68, 0.78],
        "statistical_significance": 0.001
    }
    
    engine.perform_impact_assessment.return_value = {
        "impact_level": ImpactLevel.HIGH.value,
        "causal_inference": {
            "treatment_effect": 0.15,
            "control_group_comparison": 0.08,
            "attribution_confidence": 0.82
        },
        "spillover_effects": {
            "positive_spillovers": ["increased_digital_skills", "improved_connectivity"],
            "negative_spillovers": ["digital_divide_widening"],
            "spillover_magnitude": 0.23
        }
    }
    
    engine.forecast_policy_outcomes.return_value = {
        "projected_effectiveness": [0.73, 0.76, 0.79, 0.81],
        "confidence_bands": {
            "upper": [0.78, 0.82, 0.85, 0.87],
            "lower": [0.68, 0.70, 0.73, 0.75]
        },
        "key_assumptions": [
            "Continued budget allocation",
            "Stable political support",
            "No major external shocks"
        ]
    }
    
    return engine


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
            "time_horizon": "2023-2024"
        },
        trace_id="trace-bonifacio-456"
    )


@pytest.fixture
def bonifacio_agent(mock_policy_data_service, mock_statistical_engine):
    """Create Bonifácio agent with mocked dependencies."""
    with patch("src.agents.bonifacio.PolicyDataService", return_value=mock_policy_data_service), \
         patch("src.agents.bonifacio.StatisticalEngine", return_value=mock_statistical_engine):
        
        agent = BonifacioAgent(
            effectiveness_threshold=0.7,
            impact_significance_level=0.05,
            forecast_horizon_months=12,
            comparative_analysis_enabled=True
        )
        return agent


class TestBonifacioAgent:
    """Test suite for Bonifácio (Policy Analysis Agent)."""
    
    @pytest.mark.unit
    def test_agent_initialization(self, bonifacio_agent):
        """Test Bonifácio agent initialization."""
        assert bonifacio_agent.name == "Bonifácio"
        assert bonifacio_agent.effectiveness_threshold == 0.7
        assert bonifacio_agent.impact_significance_level == 0.05
        assert bonifacio_agent.forecast_horizon_months == 12
        assert bonifacio_agent.comparative_analysis_enabled is True
        
        # Check capabilities
        expected_capabilities = [
            "policy_analysis",
            "impact_assessment",
            "effectiveness_evaluation",
            "comparative_analysis",
            "outcome_forecasting",
            "governance_assessment"
        ]
        
        for capability in expected_capabilities:
            assert capability in bonifacio_agent.capabilities
    
    @pytest.mark.unit
    async def test_policy_effectiveness_analysis(self, bonifacio_agent, agent_context):
        """Test comprehensive policy effectiveness analysis."""
        message = AgentMessage(
            sender="policy_manager",
            recipient="Bonifácio",
            action="analyze_policy_effectiveness",
            payload={
                "policy_id": "policy_001",
                "analysis_dimensions": ["implementation", "outcomes", "efficiency", "sustainability"],
                "include_benchmarking": True,
                "stakeholder_feedback": True
            }
        )
        
        response = await bonifacio_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "effectiveness_analysis" in response.result
        
        analysis = response.result["effectiveness_analysis"]
        assert "overall_score" in analysis
        assert analysis["overall_score"] == 0.73
        assert "dimension_scores" in analysis
        assert len(analysis["dimension_scores"]) == 4
        
        # Check all dimensions are analyzed
        for dimension in ["implementation", "outcomes", "efficiency", "sustainability"]:
            assert dimension in analysis["dimension_scores"]
    
    @pytest.mark.unit
    async def test_impact_assessment(self, bonifacio_agent, agent_context):
        """Test policy impact assessment with causal inference."""
        message = AgentMessage(
            sender="impact_evaluator",
            recipient="Bonifácio", 
            action="assess_policy_impact",
            payload={
                "policy_id": "policy_001",
                "impact_dimensions": ["social", "economic", "environmental"],
                "causal_inference_method": "difference_in_differences",
                "control_group_analysis": True,
                "spillover_analysis": True
            }
        )
        
        response = await bonifacio_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "impact_assessment" in response.result
        
        impact = response.result["impact_assessment"]
        assert impact["impact_level"] == ImpactLevel.HIGH.value
        assert "causal_inference" in impact
        assert "spillover_effects" in impact
        
        # Check causal inference results
        causal = impact["causal_inference"]
        assert causal["treatment_effect"] > 0
        assert causal["attribution_confidence"] > 0.8
    
    @pytest.mark.unit
    async def test_comparative_policy_analysis(self, bonifacio_agent, agent_context):
        """Test comparative analysis with similar policies."""
        message = AgentMessage(
            sender="comparative_analyst",
            recipient="Bonifácio",
            action="compare_policies",
            payload={
                "primary_policy_id": "policy_001",
                "comparison_policies": ["historical_001"],
                "comparison_dimensions": ["effectiveness", "efficiency", "outcomes"],
                "similarity_threshold": 0.7,
                "include_best_practices": True
            }
        )
        
        response = await bonifacio_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "comparative_analysis" in response.result
        
        comparison = response.result["comparative_analysis"]
        assert "policy_rankings" in comparison
        assert "performance_gaps" in comparison
        assert "best_practices" in comparison
        
        # Check rankings
        rankings = comparison["policy_rankings"]
        assert len(rankings) >= 2  # Primary + comparison policies
    
    @pytest.mark.unit
    async def test_outcome_forecasting(self, bonifacio_agent, agent_context):
        """Test policy outcome forecasting."""
        message = AgentMessage(
            sender="planning_unit",
            recipient="Bonifácio",
            action="forecast_policy_outcomes",
            payload={
                "policy_id": "policy_001",
                "forecast_horizon": 12,  # months
                "scenario_analysis": True,
                "scenarios": ["optimistic", "realistic", "pessimistic"],
                "include_uncertainty": True
            }
        )
        
        response = await bonifacio_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "outcome_forecast" in response.result
        
        forecast = response.result["outcome_forecast"]
        assert "projected_effectiveness" in forecast
        assert "confidence_bands" in forecast
        assert len(forecast["projected_effectiveness"]) == 4  # Quarterly projections
        
        # Check confidence intervals
        bands = forecast["confidence_bands"]
        assert len(bands["upper"]) == len(bands["lower"])
        assert all(u >= l for u, l in zip(bands["upper"], bands["lower"]))
    
    @pytest.mark.unit
    async def test_budget_efficiency_analysis(self, bonifacio_agent, agent_context):
        """Test budget efficiency and resource allocation analysis."""
        message = AgentMessage(
            sender="budget_analyst",
            recipient="Bonifácio",
            action="analyze_budget_efficiency",
            payload={
                "policy_id": "policy_001",
                "efficiency_metrics": ["cost_per_beneficiary", "outcome_per_dollar", "budget_execution_rate"],
                "benchmark_similar_programs": True,
                "identify_optimization_opportunities": True
            }
        )
        
        response = await bonifacio_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "budget_efficiency" in response.result
        
        efficiency = response.result["budget_efficiency"]
        assert "efficiency_score" in efficiency
        assert "cost_effectiveness_ratio" in efficiency
        assert "optimization_recommendations" in efficiency
        
        # Check efficiency metrics
        assert efficiency["efficiency_score"] > 0
        assert len(efficiency["optimization_recommendations"]) > 0
    
    @pytest.mark.unit
    async def test_stakeholder_impact_analysis(self, bonifacio_agent, agent_context):
        """Test stakeholder impact and satisfaction analysis."""
        message = AgentMessage(
            sender="stakeholder_manager",
            recipient="Bonifácio",
            action="analyze_stakeholder_impact",
            payload={
                "policy_id": "policy_001",
                "stakeholder_groups": ["beneficiaries", "implementers", "taxpayers", "civil_society"],
                "impact_dimensions": ["direct_benefits", "costs", "satisfaction", "participation"],
                "include_feedback_analysis": True
            }
        )
        
        response = await bonifacio_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "stakeholder_analysis" in response.result
        
        stakeholder = response.result["stakeholder_analysis"]
        assert "stakeholder_impact_matrix" in stakeholder
        assert "satisfaction_scores" in stakeholder
        assert "engagement_levels" in stakeholder
        
        # Check stakeholder groups coverage
        matrix = stakeholder["stakeholder_impact_matrix"]
        assert len(matrix) >= 4  # All stakeholder groups
    
    @pytest.mark.unit
    async def test_policy_risk_assessment(self, bonifacio_agent, agent_context):
        """Test policy implementation risk assessment."""
        message = AgentMessage(
            sender="risk_manager",
            recipient="Bonifácio",
            action="assess_policy_risks",
            payload={
                "policy_id": "policy_001",
                "risk_categories": ["implementation", "political", "economic", "social"],
                "risk_assessment_method": "monte_carlo",
                "mitigation_strategies": True,
                "probability_impact_matrix": True
            }
        )
        
        response = await bonifacio_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "risk_assessment" in response.result
        
        risks = response.result["risk_assessment"]
        assert "overall_risk_score" in risks
        assert "risk_categories" in risks
        assert "mitigation_strategies" in risks
        assert "probability_impact_matrix" in risks
        
        # Check risk score is valid
        assert 0 <= risks["overall_risk_score"] <= 1
    
    @pytest.mark.unit
    async def test_governance_quality_evaluation(self, bonifacio_agent, agent_context):
        """Test governance quality evaluation."""
        message = AgentMessage(
            sender="governance_auditor",
            recipient="Bonifácio",
            action="evaluate_governance_quality",
            payload={
                "policy_id": "policy_001",
                "governance_dimensions": ["transparency", "accountability", "participation", "effectiveness"],
                "governance_indicators": True,
                "international_benchmarks": True
            }
        )
        
        response = await bonifacio_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "governance_evaluation" in response.result
        
        governance = response.result["governance_evaluation"]
        assert "governance_score" in governance
        assert "dimension_scores" in governance
        assert "benchmark_comparison" in governance
        
        # Check governance dimensions
        dimensions = governance["dimension_scores"]
        for dim in ["transparency", "accountability", "participation", "effectiveness"]:
            assert dim in dimensions
            assert 0 <= dimensions[dim] <= 1
    
    @pytest.mark.unit
    async def test_policy_lifecycle_analysis(self, bonifacio_agent, agent_context):
        """Test complete policy lifecycle analysis."""
        message = AgentMessage(
            sender="lifecycle_analyst",
            recipient="Bonifácio",
            action="analyze_policy_lifecycle",
            payload={
                "policy_id": "policy_001",
                "lifecycle_stages": ["design", "implementation", "monitoring", "evaluation"],
                "stage_effectiveness": True,
                "transition_analysis": True,
                "lessons_learned": True
            }
        )
        
        response = await bonifacio_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "lifecycle_analysis" in response.result
        
        lifecycle = response.result["lifecycle_analysis"]
        assert "stage_effectiveness" in lifecycle
        assert "transition_quality" in lifecycle
        assert "lessons_learned" in lifecycle
        
        # Check all stages analyzed
        stages = lifecycle["stage_effectiveness"]
        assert len(stages) == 4
    
    @pytest.mark.unit
    async def test_policy_portfolio_optimization(self, bonifacio_agent, agent_context):
        """Test policy portfolio optimization analysis."""
        message = AgentMessage(
            sender="portfolio_manager",
            recipient="Bonifácio",
            action="optimize_policy_portfolio",
            payload={
                "policy_ids": ["policy_001", "policy_002"],
                "optimization_objective": "maximize_impact_per_dollar",
                "constraints": {
                    "total_budget": 1000000000,
                    "minimum_coverage": 0.8
                },
                "synergy_analysis": True
            }
        )
        
        response = await bonifacio_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "portfolio_optimization" in response.result
        
        portfolio = response.result["portfolio_optimization"]
        assert "optimal_allocation" in portfolio
        assert "expected_impact" in portfolio
        assert "synergy_effects" in portfolio
        
        # Check budget constraint satisfaction
        allocation = portfolio["optimal_allocation"]
        total_allocated = sum(allocation.values())
        assert total_allocated <= 1000000000  # Budget constraint
    
    @pytest.mark.unit
    async def test_error_handling_invalid_policy(self, bonifacio_agent, agent_context):
        """Test error handling for invalid policy ID."""
        # Mock empty policy response
        bonifacio_agent.policy_data_service.get_policies.return_value = []
        
        message = AgentMessage(
            sender="test_agent",
            recipient="Bonifácio",
            action="analyze_policy_effectiveness",
            payload={"policy_id": "invalid_policy_id"}
        )
        
        response = await bonifacio_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.ERROR
        assert "policy not found" in response.error.lower()
    
    @pytest.mark.unit
    async def test_batch_policy_analysis(self, bonifacio_agent, agent_context):
        """Test batch analysis of multiple policies."""
        message = AgentMessage(
            sender="batch_analyst",
            recipient="Bonifácio",
            action="batch_analyze_policies",
            payload={
                "policy_ids": ["policy_001", "policy_002"],
                "analysis_types": ["effectiveness", "impact", "efficiency"],
                "comparative_report": True,
                "prioritize_by": "effectiveness_score"
            }
        )
        
        response = await bonifacio_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "batch_analysis" in response.result
        
        batch = response.result["batch_analysis"]
        assert "individual_results" in batch
        assert "comparative_summary" in batch
        assert "policy_rankings" in batch
        
        # Check all policies analyzed
        assert len(batch["individual_results"]) == 2
    
    @pytest.mark.unit
    async def test_real_time_monitoring_integration(self, bonifacio_agent, agent_context):
        """Test real-time policy monitoring integration."""
        message = AgentMessage(
            sender="monitoring_system",
            recipient="Bonifácio",
            action="setup_policy_monitoring",
            payload={
                "policy_id": "policy_001",
                "monitoring_frequency": "weekly",
                "alert_thresholds": {
                    "effectiveness_drop": 0.1,
                    "budget_deviation": 0.15
                },
                "automated_reporting": True
            }
        )
        
        response = await bonifacio_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "monitoring_setup" in response.result
        
        monitoring = response.result["monitoring_setup"]
        assert "monitoring_dashboard" in monitoring
        assert "alert_configuration" in monitoring
        assert "reporting_schedule" in monitoring


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
            measurement_unit="percentage",
            data_source="National Education Survey"
        )
        
        assert indicator.name == "digital_literacy_rate"
        assert indicator.baseline_value == 0.45
        assert indicator.current_value == 0.62
        assert indicator.target_value == 0.75
    
    @pytest.mark.unit
    def test_indicator_progress_calculation(self):
        """Test progress calculation for indicators."""
        indicator = PolicyIndicator(
            name="test_indicator",
            baseline_value=0.3,
            current_value=0.6,
            target_value=0.9
        )
        
        # Progress = (current - baseline) / (target - baseline)
        expected_progress = (0.6 - 0.3) / (0.9 - 0.3)  # = 0.5
        assert abs(indicator.calculate_progress() - expected_progress) < 0.01


class TestPolicyEffectivenessReport:
    """Test PolicyEffectivenessReport data model."""
    
    @pytest.mark.unit
    def test_report_creation(self):
        """Test creating effectiveness report."""
        report = PolicyEffectivenessReport(
            policy_id="policy_001",
            policy_name="Test Policy",
            analysis_date=datetime.utcnow(),
            overall_effectiveness_score=0.75,
            dimension_scores={
                "implementation": 0.8,
                "outcomes": 0.7,
                "efficiency": 0.7,
                "sustainability": 0.8
            },
            key_findings=[
                "Strong implementation progress",
                "Moderate outcome achievement",
                "Efficiency improvements needed"
            ],
            recommendations=[
                "Increase resource allocation to underperforming areas",
                "Enhance monitoring systems",
                "Strengthen stakeholder engagement"
            ]
        )
        
        assert report.policy_id == "policy_001"
        assert report.overall_effectiveness_score == 0.75
        assert len(report.key_findings) == 3
        assert len(report.recommendations) == 3
    
    @pytest.mark.unit
    def test_report_effectiveness_categorization(self):
        """Test effectiveness score categorization."""
        high_effectiveness = PolicyEffectivenessReport(
            policy_id="high_policy",
            policy_name="High Performing Policy",
            overall_effectiveness_score=0.85
        )
        
        low_effectiveness = PolicyEffectivenessReport(
            policy_id="low_policy", 
            policy_name="Underperforming Policy",
            overall_effectiveness_score=0.45
        )
        
        assert high_effectiveness.get_effectiveness_category() == "High"
        assert low_effectiveness.get_effectiveness_category() == "Low"