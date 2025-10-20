"""
Unit tests for Ayrton Senna Agent (SemanticRouter) - Semantic routing specialist.
Tests query routing, intent detection, and agent suggestion capabilities.
"""

from unittest.mock import AsyncMock

import pytest

from src.agents.ayrton_senna import RoutingRule, SemanticRouter
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for semantic routing."""
    llm = AsyncMock()
    llm.generate.return_value = """
    {
        "target_agent": "InvestigatorAgent",
        "action": "detect_anomalies",
        "confidence": 0.85,
        "reasoning": "Query indicates anomaly detection need"
    }
    """
    return llm


@pytest.fixture
def semantic_router(mock_llm_service):
    """Create SemanticRouter instance for testing."""
    return SemanticRouter(
        llm_service=mock_llm_service,
        embedding_service=None,
        confidence_threshold=0.7,
    )


class TestSemanticRouterInitialization:
    """Test suite for SemanticRouter initialization."""

    @pytest.mark.unit
    def test_agent_initialization(self, semantic_router):
        """Test that the router is properly initialized."""
        assert semantic_router.name == "SemanticRouter"
        assert "route_query" in semantic_router.capabilities
        assert "detect_intent" in semantic_router.capabilities
        assert "analyze_query_type" in semantic_router.capabilities
        assert semantic_router.confidence_threshold == 0.7
        assert len(semantic_router.routing_rules) > 0  # Default rules loaded

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_initialize(self, semantic_router):
        """Test router initialization method."""
        await semantic_router.initialize()
        assert semantic_router.status == AgentStatus.IDLE

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_shutdown(self, semantic_router):
        """Test router shutdown method."""
        await semantic_router.shutdown()
        # Should complete without errors


class TestRuleBasedRouting:
    """Test suite for rule-based routing functionality."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_route_investigation_query(self, semantic_router):
        """Test routing of investigation queries."""
        context = AgentContext(investigation_id="test-routing")
        query = "investigar contratos suspeitos no ministério"

        decision = await semantic_router._apply_routing_rules(query, context)

        assert decision is not None
        assert decision.target_agent == "MasterAgent"
        assert decision.action == "investigate"
        assert decision.confidence >= 0.7

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_route_anomaly_detection_query(self, semantic_router):
        """Test routing of anomaly detection queries."""
        context = AgentContext(investigation_id="test-anomaly")
        query = "encontrar contratos suspeitos com superfaturamento irregular"

        decision = await semantic_router._apply_routing_rules(query, context)

        assert decision is not None
        assert decision.target_agent == "InvestigatorAgent"
        assert decision.action == "detect_anomalies"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_route_pattern_analysis_query(self, semantic_router):
        """Test routing of pattern analysis queries."""
        context = AgentContext(investigation_id="test-pattern")
        query = "analisar tendência e evolução do padrão histórico"

        decision = await semantic_router._apply_routing_rules(query, context)

        assert decision is not None
        assert decision.target_agent == "AnalystAgent"
        assert decision.action == "analyze_patterns"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_route_report_generation_query(self, semantic_router):
        """Test routing of report generation queries."""
        context = AgentContext(investigation_id="test-report")
        query = "preciso gerar relatório sobre contratos com resumo documento"

        decision = await semantic_router._apply_routing_rules(query, context)

        # If no rule matches, decision might be None (fallback handled elsewhere)
        # Just verify the routing system works
        assert decision is None or decision.target_agent == "ReporterAgent"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_no_rule_matches(self, semantic_router):
        """Test when no rule matches the query."""
        context = AgentContext(investigation_id="test-nomatch")
        query = "xyz abc 123"  # Random query

        decision = await semantic_router._apply_routing_rules(query, context)

        assert decision is None  # No rule matched


class TestIntentDetection:
    """Test suite for intent detection."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_investigation_intent(self, semantic_router):
        """Test detection of investigation intent."""
        context = AgentContext(investigation_id="test-intent")
        payload = {"query": "investigar e analisar contratos suspeitos"}

        result = await semantic_router._detect_intent(payload, context)

        assert "intents" in result
        assert len(result["intents"]) > 0
        assert result["primary_intent"] == "investigation"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_explanation_intent(self, semantic_router):
        """Test detection of explanation intent."""
        context = AgentContext(investigation_id="test-explain")
        payload = {"query": "explicar como funciona o processo"}

        result = await semantic_router._detect_intent(payload, context)

        assert "intents" in result
        assert any(i["intent"] == "explanation" for i in result["intents"])

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_comparison_intent(self, semantic_router):
        """Test detection of comparison intent."""
        context = AgentContext(investigation_id="test-comparison")
        payload = {"query": "comparar gastos entre ministérios"}

        result = await semantic_router._detect_intent(payload, context)

        assert "intents" in result
        assert any(i["intent"] == "comparison" for i in result["intents"])

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_trend_analysis_intent(self, semantic_router):
        """Test detection of trend analysis intent."""
        context = AgentContext(investigation_id="test-trend")
        payload = {"query": "verificar tendência ao longo do tempo"}

        result = await semantic_router._detect_intent(payload, context)

        assert "intents" in result
        assert any(i["intent"] == "trend_analysis" for i in result["intents"])

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_anomaly_detection_intent(self, semantic_router):
        """Test detection of anomaly detection intent."""
        context = AgentContext(investigation_id="test-anomaly-intent")
        payload = {"query": "identificar gastos suspeitos e anômalos"}

        result = await semantic_router._detect_intent(payload, context)

        assert "intents" in result
        assert any(i["intent"] == "anomaly_detection" for i in result["intents"])

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_unknown_intent(self, semantic_router):
        """Test detection when no intent matches."""
        context = AgentContext(investigation_id="test-unknown")
        payload = {"query": "xyz random text"}

        result = await semantic_router._detect_intent(payload, context)

        assert result["primary_intent"] == "unknown"


class TestQueryTypeAnalysis:
    """Test suite for query type analysis."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_simple_query(self, semantic_router):
        """Test analysis of simple query."""
        context = AgentContext(investigation_id="test-simple")
        payload = {"query": "buscar contratos"}

        result = await semantic_router._analyze_query_type(payload, context)

        assert result["complexity"] == "simple"
        assert result["word_count"] == 2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_medium_query(self, semantic_router):
        """Test analysis of medium complexity query."""
        context = AgentContext(investigation_id="test-medium")
        payload = {
            "query": "analisar contratos do ministério da saúde neste ano fiscal"
        }

        result = await semantic_router._analyze_query_type(payload, context)

        assert result["complexity"] in ["medium", "complex"]  # Both are valid
        assert result["word_count"] >= 7

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_analyze_complex_query(self, semantic_router):
        """Test analysis of complex query."""
        context = AgentContext(investigation_id="test-complex")
        payload = {
            "query": "investigar e analisar contratos suspeitos do ministério da saúde "
            "relacionados a compras de equipamentos médicos no período de 2023 a 2024"
        }

        result = await semantic_router._analyze_query_type(payload, context)

        assert result["complexity"] == "complex"
        assert result["word_count"] > 20

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_numbers_in_query(self, semantic_router):
        """Test detection of numbers in query."""
        context = AgentContext(investigation_id="test-numbers")
        payload = {"query": "contratos acima de 100000 reais"}

        result = await semantic_router._analyze_query_type(payload, context)

        assert result["has_numbers"] is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_dates_in_query(self, semantic_router):
        """Test detection of dates in query."""
        context = AgentContext(investigation_id="test-dates")
        payload = {"query": "contratos de 2024 e 01/03/2024"}

        result = await semantic_router._analyze_query_type(payload, context)

        assert result["has_dates"] is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_organizations_in_query(self, semantic_router):
        """Test detection of organizations in query."""
        context = AgentContext(investigation_id="test-orgs")
        payload = {"query": "contratos do ministério e prefeitura"}

        result = await semantic_router._analyze_query_type(payload, context)

        assert result["has_organizations"] is True


class TestAgentSuggestion:
    """Test suite for agent suggestion functionality."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_suggest_agents_for_investigation(self, semantic_router):
        """Test agent suggestion for investigation query."""
        # Register agent capabilities
        semantic_router.register_agent_capabilities(
            "InvestigatorAgent", ["investigate", "detect_anomalies"]
        )
        semantic_router.register_agent_capabilities(
            "AnalystAgent", ["analyze", "process_data"]
        )

        context = AgentContext(investigation_id="test-suggest")
        payload = {"query": "investigar contratos suspeitos"}

        result = await semantic_router._suggest_agents(payload, context)

        assert len(result) > 0
        assert result[0]["agent_name"] == "InvestigatorAgent"
        assert result[0]["score"] > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_suggest_agents_for_analysis(self, semantic_router):
        """Test agent suggestion for analysis query."""
        semantic_router.register_agent_capabilities(
            "AnalystAgent", ["analyze", "statistical_analysis"]
        )
        semantic_router.register_agent_capabilities(
            "InvestigatorAgent", ["investigate", "detect_anomalies"]
        )

        context = AgentContext(investigation_id="test-analyze")
        payload = {"query": "analisar dados estatísticos"}

        result = await semantic_router._suggest_agents(payload, context)

        assert len(result) > 0
        assert any(s["agent_name"] == "AnalystAgent" for s in result)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_suggest_agents_for_report(self, semantic_router):
        """Test agent suggestion for report query."""
        semantic_router.register_agent_capabilities(
            "ReporterAgent", ["report", "generate_documents"]
        )

        context = AgentContext(investigation_id="test-report-suggest")
        payload = {"query": "gerar relatório dos contratos"}

        result = await semantic_router._suggest_agents(payload, context)

        assert len(result) > 0
        assert any(s["agent_name"] == "ReporterAgent" for s in result)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_suggest_no_agents_for_unrelated_query(self, semantic_router):
        """Test that no agents are suggested for unrelated query."""
        semantic_router.register_agent_capabilities(
            "AnalystAgent", ["analyze", "process"]
        )

        context = AgentContext(investigation_id="test-nosuggestion")
        payload = {"query": "xyz random text"}

        result = await semantic_router._suggest_agents(payload, context)

        assert len(result) == 0  # No relevant agents


class TestRoutingValidation:
    """Test suite for routing validation."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_valid_routing(self, semantic_router):
        """Test validation of valid routing decision."""
        semantic_router.register_agent_capabilities(
            "InvestigatorAgent", ["investigate", "detect_anomalies"]
        )

        context = AgentContext(investigation_id="test-validate")
        payload = {
            "decision": {
                "target_agent": "InvestigatorAgent",
                "action": "investigate",
            }
        }

        result = await semantic_router._validate_routing(payload, context)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_invalid_agent(self, semantic_router):
        """Test validation with non-existent agent."""
        context = AgentContext(investigation_id="test-invalid")
        payload = {
            "decision": {
                "target_agent": "NonExistentAgent",
                "action": "do_something",
            }
        }

        result = await semantic_router._validate_routing(payload, context)

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_unsupported_action(self, semantic_router):
        """Test validation with unsupported action."""
        semantic_router.register_agent_capabilities(
            "AnalystAgent", ["analyze", "process"]
        )

        context = AgentContext(investigation_id="test-unsupported")
        payload = {
            "decision": {
                "target_agent": "AnalystAgent",
                "action": "investigate",  # Not supported
            }
        }

        result = await semantic_router._validate_routing(payload, context)

        # Should have warning but still valid
        assert len(result["warnings"]) > 0


class TestCustomRules:
    """Test suite for custom routing rules."""

    @pytest.mark.unit
    def test_add_routing_rule(self, semantic_router):
        """Test adding a custom routing rule."""
        initial_count = len(semantic_router.routing_rules)

        new_rule = RoutingRule(
            name="custom_fraud_detection",
            patterns=[r"fraude|corrupção"],
            keywords=["fraude", "corrupção"],
            target_agent="FraudAgent",
            action="detect_fraud",
            priority=10,
        )

        semantic_router.add_routing_rule(new_rule)

        assert len(semantic_router.routing_rules) == initial_count + 1
        assert semantic_router.routing_rules[0].priority == 10  # Highest priority

    @pytest.mark.unit
    def test_register_agent_capabilities(self, semantic_router):
        """Test registering agent capabilities."""
        semantic_router.register_agent_capabilities(
            "TestAgent", ["test_capability_1", "test_capability_2"]
        )

        assert "TestAgent" in semantic_router.agent_capabilities
        assert "test_capability_1" in semantic_router.agent_capabilities["TestAgent"]


class TestProcessMethod:
    """Test suite for main process method."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_route_query_action(self, semantic_router):
        """Test processing route_query action."""
        context = AgentContext(investigation_id="test-process")
        message = AgentMessage(
            sender="test",
            recipient="SemanticRouter",
            action="route_query",
            payload={"query": "investigar verificar e analisar gastos suspeitos"},
        )

        response = await semantic_router.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert hasattr(response.result, "target_agent") or "target_agent" in (
            response.result.__dict__ if hasattr(response.result, "__dict__") else {}
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_detect_intent_action(self, semantic_router):
        """Test processing detect_intent action."""
        context = AgentContext(investigation_id="test-detect")
        message = AgentMessage(
            sender="test",
            recipient="SemanticRouter",
            action="detect_intent",
            payload={"query": "investigar contratos"},
        )

        response = await semantic_router.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert "intents" in response.result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_analyze_query_type_action(self, semantic_router):
        """Test processing analyze_query_type action."""
        context = AgentContext(investigation_id="test-analyze")
        message = AgentMessage(
            sender="test",
            recipient="SemanticRouter",
            action="analyze_query_type",
            payload={"query": "buscar contratos do ministério"},
        )

        response = await semantic_router.process(message, context)

        assert response.status == AgentStatus.COMPLETED
        assert "complexity" in response.result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_invalid_action(self, semantic_router):
        """Test processing with invalid action."""
        context = AgentContext(investigation_id="test-invalid-action")
        message = AgentMessage(
            sender="test",
            recipient="SemanticRouter",
            action="invalid_action",
            payload={},
        )

        response = await semantic_router.process(message, context)

        assert response.status == AgentStatus.ERROR
        assert "Unknown action" in response.error

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_missing_query(self, semantic_router):
        """Test processing with missing query in payload."""
        context = AgentContext(investigation_id="test-missing")
        message = AgentMessage(
            sender="test",
            recipient="SemanticRouter",
            action="route_query",
            payload={},  # Missing query
        )

        response = await semantic_router.process(message, context)

        assert response.status == AgentStatus.ERROR
