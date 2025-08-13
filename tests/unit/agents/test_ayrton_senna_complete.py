"""
Complete unit tests for Ayrton Senna Agent - Semantic routing and performance optimization specialist.
Tests query routing, intent detection, performance optimization, and navigation strategies.
"""

import pytest
import re
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4

from src.agents.ayrton_senna import (
    SemanticRouter,
    RoutingRule,
    RoutingDecision,
)
from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
)
from src.core.exceptions import AgentError, ValidationError


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for intent detection."""
    service = AsyncMock()
    
    service.detect_intent.return_value = {
        "intent": "data_analysis",
        "confidence": 0.89,
        "entities": [
            {"entity": "contract", "type": "data_source", "confidence": 0.92},
            {"entity": "anomaly", "type": "analysis_type", "confidence": 0.85}
        ],
        "suggested_action": "detect_anomalies",
        "reasoning": "User wants to analyze contracts for anomalies"
    }
    
    service.classify_query_complexity.return_value = {
        "complexity_level": "medium",
        "complexity_score": 0.65,
        "factors": ["multiple_entities", "analytical_intent"],
        "processing_requirements": {
            "estimated_time": 45,  # seconds
            "memory_requirement": "medium",
            "computational_intensity": "moderate"
        }
    }
    
    service.suggest_agent_routing.return_value = {
        "primary_agent": "tiradentes",
        "secondary_agents": ["anita", "machado"],
        "routing_confidence": 0.87,
        "reasoning": "Query involves anomaly detection which is Tiradentes' specialty"
    }
    
    return service


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service for semantic similarity."""
    service = AsyncMock()
    
    service.get_query_embedding.return_value = [0.1, 0.2, 0.3, 0.4, 0.5] * 20  # 100-dim vector
    
    service.calculate_similarity.return_value = {
        "similarities": {
            "contract_analysis": 0.85,
            "anomaly_detection": 0.92,
            "pattern_recognition": 0.78,
            "corruption_investigation": 0.73
        },
        "best_match": "anomaly_detection",
        "similarity_score": 0.92
    }
    
    service.find_similar_queries.return_value = [
        {
            "query": "Detect unusual patterns in government contracts",
            "similarity": 0.89,
            "previous_routing": "tiradentes",
            "success_rate": 0.94
        },
        {
            "query": "Find anomalies in public spending data",
            "similarity": 0.82,
            "previous_routing": "tiradentes",
            "success_rate": 0.91
        }
    ]
    
    return service


@pytest.fixture
def mock_performance_monitor():
    """Mock performance monitoring service."""
    monitor = AsyncMock()
    
    monitor.get_agent_performance.return_value = {
        "tiradentes": {
            "average_response_time": 2.3,
            "success_rate": 0.94,
            "load_factor": 0.65,
            "queue_length": 3
        },
        "anita": {
            "average_response_time": 1.8,
            "success_rate": 0.91,
            "load_factor": 0.45,
            "queue_length": 1
        },
        "machado": {
            "average_response_time": 1.2,
            "success_rate": 0.96,
            "load_factor": 0.35,
            "queue_length": 0
        }
    }
    
    monitor.predict_routing_performance.return_value = {
        "estimated_completion_time": 145,  # seconds
        "success_probability": 0.93,
        "resource_requirements": {
            "cpu_usage": 0.45,
            "memory_usage": 0.32,
            "io_operations": 156
        },
        "bottleneck_prediction": None
    }
    
    return monitor


@pytest.fixture
def agent_context():
    """Test agent context for semantic routing."""
    return AgentContext(
        investigation_id="routing-analysis-001",
        user_id="query-router",
        session_id="routing-session",
        metadata={
            "routing_type": "semantic_analysis",
            "priority": "high",
            "user_preferences": {"fast_response": True}
        },
        trace_id="trace-ayrton-654"
    )


@pytest.fixture
def semantic_router(mock_llm_service, mock_embedding_service, mock_performance_monitor):
    """Create Semantic Router with mocked dependencies."""
    with patch("src.agents.ayrton_senna.LLMService", return_value=mock_llm_service), \
         patch("src.agents.ayrton_senna.EmbeddingService", return_value=mock_embedding_service), \
         patch("src.agents.ayrton_senna.PerformanceMonitor", return_value=mock_performance_monitor):
        
        router = SemanticRouter(
            llm_service=mock_llm_service,
            embedding_service=mock_embedding_service,
            confidence_threshold=0.7
        )
        return router


class TestSemanticRouter:
    """Comprehensive test suite for Ayrton Senna (Semantic Router)."""
    
    @pytest.mark.unit
    def test_router_initialization(self, semantic_router):
        """Test semantic router initialization."""
        assert semantic_router.name == "SemanticRouter"
        assert semantic_router.confidence_threshold == 0.7
        assert hasattr(semantic_router, 'routing_rules')
        assert hasattr(semantic_router, 'agent_capabilities')
        
        # Check capabilities
        expected_capabilities = [
            "route_query",
            "detect_intent", 
            "analyze_query_type",
            "suggest_agents",
            "validate_routing"
        ]
        
        for capability in expected_capabilities:
            assert capability in semantic_router.capabilities
        
        # Check default rules are loaded
        assert len(semantic_router.routing_rules) > 0
    
    @pytest.mark.unit
    async def test_query_routing_by_intent(self, semantic_router, agent_context):
        """Test query routing based on intent detection."""
        message = AgentMessage(
            sender="user_interface",
            recipient="SemanticRouter",
            action="route_query",
            payload={
                "query": "Find anomalies in government contract data from the last quarter",
                "context": "investigation",
                "priority": "high",
                "user_preferences": {"prefer_accuracy": True}
            }
        )
        
        response = await semantic_router.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "routing_decision" in response.result
        
        decision = response.result["routing_decision"]
        assert "target_agent" in decision
        assert "confidence" in decision
        assert decision["confidence"] >= 0.7
        assert "rule_used" in decision
        assert "parameters" in decision
    
    @pytest.mark.unit
    async def test_semantic_similarity_routing(self, semantic_router, agent_context):
        """Test routing based on semantic similarity."""
        message = AgentMessage(
            sender="analyst",
            recipient="SemanticRouter",
            action="route_by_similarity",
            payload={
                "query": "Investigate suspicious patterns in procurement processes",
                "use_semantic_matching": True,
                "similarity_threshold": 0.8,
                "include_historical_data": True
            }
        )
        
        response = await semantic_router.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "semantic_routing" in response.result
        
        routing = response.result["semantic_routing"]
        assert "similarity_scores" in routing
        assert "best_match" in routing
        assert "historical_matches" in routing
        assert routing["similarity_scores"]["anomaly_detection"] == 0.92
    
    @pytest.mark.unit
    async def test_multi_agent_routing_strategy(self, semantic_router, agent_context):
        """Test complex routing requiring multiple agents."""
        message = AgentMessage(
            sender="complex_analyst",
            recipient="SemanticRouter",
            action="route_complex_query",
            payload={
                "query": "Analyze contract patterns, detect anomalies, and generate a comprehensive report with NLP insights",
                "workflow_optimization": True,
                "parallel_processing": True,
                "dependency_analysis": True
            }
        )
        
        response = await semantic_router.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "multi_agent_routing" in response.result
        
        multi_routing = response.result["multi_agent_routing"]
        assert "agent_workflow" in multi_routing
        assert "execution_order" in multi_routing
        assert "dependencies" in multi_routing
        assert "estimated_completion_time" in multi_routing
        
        # Check multiple agents are involved
        workflow = multi_routing["agent_workflow"]
        assert len(workflow) >= 2  # Multiple agents
    
    @pytest.mark.unit
    async def test_performance_optimized_routing(self, semantic_router, agent_context):
        """Test routing optimized for performance."""
        message = AgentMessage(
            sender="performance_optimizer",
            recipient="SemanticRouter",
            action="optimize_routing",
            payload={
                "query": "Quick analysis of budget allocation efficiency",
                "optimization_criteria": {
                    "prioritize": "speed",
                    "max_response_time": 30,  # seconds
                    "acceptable_accuracy_tradeoff": 0.05
                },
                "load_balancing": True
            }
        )
        
        response = await semantic_router.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "optimized_routing" in response.result
        
        optimized = response.result["optimized_routing"]
        assert "performance_metrics" in optimized
        assert "selected_agent" in optimized
        assert "optimization_rationale" in optimized
        
        # Check performance considerations
        metrics = optimized["performance_metrics"]
        assert "estimated_response_time" in metrics
        assert metrics["estimated_response_time"] <= 30
    
    @pytest.mark.unit
    async def test_fallback_routing_strategies(self, semantic_router, agent_context):
        """Test fallback strategies when primary routing fails."""
        # Mock primary agent as unavailable
        semantic_router.performance_monitor.get_agent_performance.return_value = {
            "tiradentes": {
                "average_response_time": 2.3,
                "success_rate": 0.94,
                "load_factor": 0.95,  # Very high load
                "queue_length": 15,   # Long queue
                "available": False
            }
        }
        
        message = AgentMessage(
            sender="fallback_tester",
            recipient="SemanticRouter",
            action="route_with_fallback",
            payload={
                "query": "Detect anomalies in expense data",
                "require_fallback_options": True,
                "fallback_priority": ["accuracy", "availability", "speed"]
            }
        )
        
        response = await semantic_router.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "fallback_routing" in response.result
        
        fallback = response.result["fallback_routing"]
        assert "primary_agent_unavailable" in fallback
        assert "fallback_agent_selected" in fallback
        assert "fallback_reasoning" in fallback
        assert "performance_impact" in fallback
    
    @pytest.mark.unit
    async def test_rule_based_routing(self, semantic_router, agent_context):
        """Test rule-based routing with custom rules."""
        # Add custom routing rule
        custom_rule = RoutingRule(
            name="contract_analysis_rule",
            patterns=[r".*contrat.*", r".*licitaç.*"],
            keywords=["contract", "procurement", "bid"],
            target_agent="bonifacio",
            action="analyze_contracts",
            priority=8,
            confidence_threshold=0.8
        )
        
        semantic_router.add_routing_rule(custom_rule)
        
        message = AgentMessage(
            sender="rule_tester",
            recipient="SemanticRouter",
            action="route_by_rules",
            payload={
                "query": "Analisar contratos de licitação pública",
                "enforce_rule_matching": True,
                "rule_priority_override": True
            }
        )
        
        response = await semantic_router.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "rule_based_routing" in response.result
        
        rule_routing = response.result["rule_based_routing"]
        assert rule_routing["target_agent"] == "bonifacio"
        assert rule_routing["rule_used"] == "contract_analysis_rule"
        assert rule_routing["confidence"] >= 0.8
    
    @pytest.mark.unit
    async def test_contextual_routing(self, semantic_router, agent_context):
        """Test routing that considers conversation context."""
        # Set up conversation history
        agent_context.memory_context = {
            "previous_queries": [
                "What are the major corruption risks?",
                "Show me contract anomalies"
            ],
            "current_investigation": "procurement_irregularities",
            "user_expertise": "advanced",
            "session_focus": "deep_analysis"
        }
        
        message = AgentMessage(
            sender="contextual_analyzer",
            recipient="SemanticRouter",
            action="route_with_context",
            payload={
                "query": "Continue the analysis with pattern recognition",
                "use_conversation_context": True,
                "context_weight": 0.3,
                "maintain_investigation_focus": True
            }
        )
        
        response = await semantic_router.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "contextual_routing" in response.result
        
        contextual = response.result["contextual_routing"]
        assert "context_influence" in contextual
        assert "investigation_continuity" in contextual
        assert "routing_adjustment" in contextual
    
    @pytest.mark.unit
    async def test_agent_capability_matching(self, semantic_router, agent_context):
        """Test routing based on agent capability matching."""
        # Update agent capabilities
        semantic_router.agent_capabilities = {
            "tiradentes": ["anomaly_detection", "corruption_analysis"],
            "anita": ["pattern_recognition", "correlation_analysis"],
            "machado": ["text_analysis", "sentiment_analysis"],
            "bonifacio": ["contract_analysis", "policy_evaluation"]
        }
        
        message = AgentMessage(
            sender="capability_matcher",
            recipient="SemanticRouter",
            action="match_capabilities",
            payload={
                "required_capabilities": ["pattern_recognition", "statistical_analysis"],
                "capability_importance": {
                    "pattern_recognition": 0.8,
                    "statistical_analysis": 0.6
                },
                "exclude_agents": ["machado"]
            }
        )
        
        response = await semantic_router.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "capability_matching" in response.result
        
        matching = response.result["capability_matching"]
        assert "capability_scores" in matching
        assert "best_match_agent" in matching
        assert "missing_capabilities" in matching
        assert matching["best_match_agent"] == "anita"
    
    @pytest.mark.unit
    async def test_query_complexity_analysis(self, semantic_router, agent_context):
        """Test analysis of query complexity for routing decisions."""
        message = AgentMessage(
            sender="complexity_analyzer",
            recipient="SemanticRouter",
            action="analyze_query_complexity",
            payload={
                "query": "Perform comprehensive cross-dimensional analysis of budget allocation efficiency across multiple ministries with temporal correlation and predictive modeling",
                "complexity_factors": ["entity_count", "analysis_depth", "data_volume"],
                "recommend_decomposition": True
            }
        )
        
        response = await semantic_router.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "complexity_analysis" in response.result
        
        complexity = response.result["complexity_analysis"]
        assert "complexity_score" in complexity
        assert complexity["complexity_level"] == "medium"
        assert "decomposition_suggestion" in complexity
        assert "processing_requirements" in complexity
    
    @pytest.mark.unit
    async def test_load_balancing_routing(self, semantic_router, agent_context):
        """Test load balancing across available agents."""
        message = AgentMessage(
            sender="load_balancer",
            recipient="SemanticRouter",
            action="balance_load",
            payload={
                "queries": [
                    "Analyze budget data for ministry A",
                    "Analyze budget data for ministry B", 
                    "Analyze budget data for ministry C"
                ],
                "load_balancing_strategy": "round_robin",
                "consider_agent_performance": True
            }
        )
        
        response = await semantic_router.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "load_balanced_routing" in response.result
        
        load_balanced = response.result["load_balanced_routing"]
        assert "agent_assignments" in load_balanced
        assert "load_distribution" in load_balanced
        assert "estimated_completion_times" in load_balanced
        
        # Check load is distributed
        assignments = load_balanced["agent_assignments"]
        assert len(assignments) == 3  # All queries assigned
    
    @pytest.mark.unit
    async def test_routing_validation_and_feedback(self, semantic_router, agent_context):
        """Test routing decision validation and feedback loop."""
        message = AgentMessage(
            sender="validation_system",
            recipient="SemanticRouter",
            action="validate_routing",
            payload={
                "proposed_routing": {
                    "target_agent": "tiradentes",
                    "action": "detect_anomalies",
                    "confidence": 0.85
                },
                "validation_criteria": ["capability_match", "performance_feasibility"],
                "feedback_integration": True
            }
        )
        
        response = await semantic_router.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "routing_validation" in response.result
        
        validation = response.result["routing_validation"]
        assert "validation_passed" in validation
        assert "validation_score" in validation
        assert "improvement_suggestions" in validation
        assert "feedback_incorporated" in validation
    
    @pytest.mark.unit
    async def test_error_handling_ambiguous_query(self, semantic_router, agent_context):
        """Test error handling for ambiguous queries."""
        # Mock low confidence intent detection
        semantic_router.llm_service.detect_intent.return_value = {
            "intent": "unclear",
            "confidence": 0.45,  # Below threshold
            "entities": [],
            "ambiguity_factors": ["multiple_interpretations", "unclear_context"]
        }
        
        message = AgentMessage(
            sender="ambiguous_tester",
            recipient="SemanticRouter",
            action="route_query",
            payload={
                "query": "Do something with the data",
                "handle_ambiguity": True
            }
        )
        
        response = await semantic_router.process(message, agent_context)
        
        assert response.status == AgentStatus.WARNING
        assert "ambiguous_query" in response.result
        assert "clarification_needed" in response.result["ambiguous_query"]
        assert "suggested_clarifications" in response.result["ambiguous_query"]
    
    @pytest.mark.unit
    async def test_concurrent_routing_requests(self, semantic_router):
        """Test handling multiple concurrent routing requests."""
        contexts = [
            AgentContext(investigation_id=f"concurrent-{i}")
            for i in range(5)
        ]
        
        messages = [
            AgentMessage(
                sender="concurrent_tester",
                recipient="SemanticRouter",
                action="route_query",
                payload={"query": f"Analysis request {i}"}
            )
            for i in range(5)
        ]
        
        # Process concurrently
        import asyncio
        responses = await asyncio.gather(*[
            semantic_router.process(msg, ctx)
            for msg, ctx in zip(messages, contexts)
        ])
        
        assert len(responses) == 5
        assert all(r.status == AgentStatus.COMPLETED for r in responses)
        assert len(set(r.metadata.get("investigation_id") for r in responses)) == 5
    
    @pytest.mark.unit
    async def test_routing_performance_metrics(self, semantic_router, agent_context):
        """Test collection of routing performance metrics."""
        message = AgentMessage(
            sender="metrics_collector",
            recipient="SemanticRouter",
            action="collect_routing_metrics",
            payload={
                "metrics_types": ["response_time", "accuracy", "throughput"],
                "time_window": "last_hour",
                "include_agent_breakdown": True
            }
        )
        
        response = await semantic_router.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "routing_metrics" in response.result
        
        metrics = response.result["routing_metrics"]
        assert "performance_summary" in metrics
        assert "agent_performance" in metrics
        assert "routing_accuracy" in metrics
        assert "throughput_statistics" in metrics


class TestRoutingRule:
    """Test RoutingRule data model."""
    
    @pytest.mark.unit
    def test_routing_rule_creation(self):
        """Test creating routing rule."""
        rule = RoutingRule(
            name="anomaly_detection_rule",
            patterns=[r".*anomal.*", r".*irregular.*"],
            keywords=["anomaly", "outlier", "unusual"],
            target_agent="tiradentes",
            action="detect_anomalies",
            priority=9,
            confidence_threshold=0.85,
            metadata={"category": "investigation", "complexity": "medium"}
        )
        
        assert rule.name == "anomaly_detection_rule"
        assert len(rule.patterns) == 2
        assert len(rule.keywords) == 3
        assert rule.target_agent == "tiradentes"
        assert rule.priority == 9
        assert rule.confidence_threshold == 0.85
    
    @pytest.mark.unit
    def test_rule_pattern_matching(self):
        """Test rule pattern matching functionality."""
        rule = RoutingRule(
            name="test_rule",
            patterns=[r".*contract.*", r".*procurement.*"],
            keywords=["contract", "bid"],
            target_agent="bonifacio",
            action="analyze_contracts"
        )
        
        # Test pattern matching
        test_queries = [
            "Analyze government contracts",
            "Review procurement processes",
            "Contract bidding irregularities"
        ]
        
        for query in test_queries:
            matches_pattern = any(re.search(pattern, query.lower()) for pattern in rule.patterns)
            matches_keyword = any(keyword in query.lower() for keyword in rule.keywords)
            assert matches_pattern or matches_keyword


class TestRoutingDecision:
    """Test RoutingDecision data model."""
    
    @pytest.mark.unit
    def test_routing_decision_creation(self):
        """Test creating routing decision."""
        decision = RoutingDecision(
            target_agent="tiradentes",
            action="detect_anomalies",
            confidence=0.89,
            rule_used="anomaly_detection_rule",
            parameters={
                "data_source": "contracts",
                "threshold": 0.8,
                "include_context": True
            },
            fallback_agents=["anita", "bonifacio"]
        )
        
        assert decision.target_agent == "tiradentes"
        assert decision.action == "detect_anomalies"
        assert decision.confidence == 0.89
        assert decision.rule_used == "anomaly_detection_rule"
        assert len(decision.parameters) == 3
        assert len(decision.fallback_agents) == 2
    
    @pytest.mark.unit
    def test_decision_confidence_validation(self):
        """Test routing decision confidence validation."""
        high_confidence = RoutingDecision(
            target_agent="agent1",
            action="action1", 
            confidence=0.95,
            rule_used="rule1"
        )
        
        low_confidence = RoutingDecision(
            target_agent="agent2",
            action="action2",
            confidence=0.55,
            rule_used="rule2"
        )
        
        assert high_confidence.confidence > 0.9  # High confidence
        assert low_confidence.confidence < 0.6   # Low confidence


@pytest.mark.integration
class TestSemanticRouterIntegration:
    """Integration tests for semantic router with realistic scenarios."""
    
    @pytest.mark.integration
    async def test_end_to_end_query_routing(self, semantic_router):
        """Test complete end-to-end query routing workflow."""
        context = AgentContext(
            investigation_id="e2e-routing-test",
            metadata={"session_type": "investigation", "user_level": "expert"}
        )
        
        # Complex multi-step query
        message = AgentMessage(
            sender="investigation_team",
            recipient="SemanticRouter",
            action="route_investigation_query",
            payload={
                "query": "I need to investigate potential procurement irregularities in the education ministry, analyze spending patterns, detect anomalies, and generate a comprehensive report",
                "investigation_context": "corruption_analysis",
                "deliverable_requirements": ["statistical_analysis", "visual_reports", "legal_documentation"]
            }
        )
        
        response = await semantic_router.process(message, context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "investigation_routing" in response.result
        
        # Verify comprehensive routing
        routing = response.result["investigation_routing"]
        assert "multi_agent_workflow" in routing
        assert "execution_plan" in routing
        assert "deliverable_mapping" in routing
    
    @pytest.mark.integration
    async def test_adaptive_routing_based_on_feedback(self, semantic_router):
        """Test adaptive routing that improves based on feedback."""
        context = AgentContext(investigation_id="adaptive-routing-test")
        
        # Initial routing
        initial_message = AgentMessage(
            sender="adaptive_tester",
            recipient="SemanticRouter", 
            action="route_with_learning",
            payload={
                "query": "Analyze budget efficiency metrics",
                "enable_learning": True
            }
        )
        
        initial_response = await semantic_router.process(initial_message, context)
        assert initial_response.status == AgentStatus.COMPLETED
        
        # Provide feedback
        feedback_message = AgentMessage(
            sender="adaptive_tester",
            recipient="SemanticRouter",
            action="provide_routing_feedback",
            payload={
                "previous_routing": initial_response.result["routing_decision"],
                "feedback": {
                    "accuracy": 0.7,  # Lower accuracy
                    "user_satisfaction": 0.6,
                    "improvement_suggestions": ["consider_performance_context"]
                }
            }
        )
        
        feedback_response = await semantic_router.process(feedback_message, context)
        assert feedback_response.status == AgentStatus.COMPLETED
        
        # Route similar query again (should show improvement)
        improved_message = AgentMessage(
            sender="adaptive_tester",
            recipient="SemanticRouter",
            action="route_with_learning",
            payload={
                "query": "Analyze spending efficiency indicators",
                "enable_learning": True
            }
        )
        
        improved_response = await semantic_router.process(improved_message, context)
        assert improved_response.status == AgentStatus.COMPLETED
        
        # Verify learning applied
        assert "learning_applied" in improved_response.result
        assert "routing_improvement" in improved_response.result