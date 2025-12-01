"""
Tests for centralized agent routing module.

These tests verify that agent selection is consistent across all endpoints
and that Abaporu is used as the default orchestrator.
"""

from src.services.agent_routing import (
    AGENT_REGISTRY,
    DEFAULT_ORCHESTRATOR,
    FALLBACK_CONVERSATIONAL,
    get_agent_for_intent,
    get_agent_info,
    is_valid_agent,
    list_available_agents,
    resolve_agent_id,
)


class TestAgentRegistry:
    """Tests for agent registry structure."""

    def test_default_orchestrator_is_abaporu(self):
        """Verify Abaporu is the default orchestrator."""
        assert DEFAULT_ORCHESTRATOR == "abaporu"

    def test_fallback_is_drummond(self):
        """Verify Drummond is the fallback for conversational intents."""
        assert FALLBACK_CONVERSATIONAL == "drummond"

    def test_all_registered_agents_have_required_fields(self):
        """All agents must have name, role, description, avatar."""
        required_fields = ["name", "role", "description", "avatar", "is_orchestrator"]
        for agent_id, info in AGENT_REGISTRY.items():
            for field in required_fields:
                assert field in info, f"Agent {agent_id} missing field: {field}"

    def test_abaporu_is_marked_as_orchestrator(self):
        """Abaporu should be marked as orchestrator."""
        assert AGENT_REGISTRY["abaporu"]["is_orchestrator"] is True

    def test_minimum_agents_registered(self):
        """Ensure we have at least the core agents registered."""
        core_agents = [
            "abaporu",
            "zumbi",
            "anita",
            "tiradentes",
            "drummond",
        ]
        for agent in core_agents:
            assert agent in AGENT_REGISTRY, f"Core agent {agent} not registered"


class TestGetAgentForIntent:
    """Tests for intent-based agent selection."""

    def test_investigate_routes_to_abaporu(self):
        """Investigation intents should go to Abaporu for orchestration."""
        assert get_agent_for_intent("investigate") == "abaporu"
        assert get_agent_for_intent("contract_anomaly_detection") == "abaporu"
        assert get_agent_for_intent("supplier_investigation") == "abaporu"
        assert get_agent_for_intent("corruption_indicators") == "abaporu"

    def test_analyze_routes_to_anita(self):
        """Analysis intents should go to Anita."""
        assert get_agent_for_intent("analyze") == "anita"
        assert get_agent_for_intent("statistical") == "anita"

    def test_report_routes_to_tiradentes(self):
        """Report intents should go to Tiradentes."""
        assert get_agent_for_intent("report") == "tiradentes"

    def test_conversational_routes_to_drummond(self):
        """Conversational intents should go to Drummond."""
        conversational = [
            "greeting",
            "conversation",
            "help_request",
            "help",
            "about_system",
            "smalltalk",
            "thanks",
            "goodbye",
            "question",
        ]
        for intent in conversational:
            assert (
                get_agent_for_intent(intent) == "drummond"
            ), f"Intent '{intent}' should route to drummond"

    def test_data_hunting_routes_to_oxossi(self):
        """Data hunting intents should go to Oxóssi."""
        assert get_agent_for_intent("data") == "oxossi"
        assert get_agent_for_intent("search") == "oxossi"
        assert get_agent_for_intent("fraud_detection") == "oxossi"

    def test_specialized_agents(self):
        """Test specialized agent routing."""
        assert get_agent_for_intent("text_analysis") == "machado"
        assert get_agent_for_intent("legal_compliance") == "bonifacio"
        assert get_agent_for_intent("security_audit") == "maria_quiteria"
        assert get_agent_for_intent("visualization") == "oscar_niemeyer"

    def test_unknown_intent_low_confidence_routes_to_drummond(self):
        """Unknown intent with low confidence should go to Drummond."""
        assert get_agent_for_intent("random_gibberish", 0.3) == "drummond"
        assert get_agent_for_intent("asdfghjkl", 0.5) == "drummond"

    def test_unknown_intent_high_confidence_routes_to_abaporu(self):
        """Unknown intent with high confidence should go to Abaporu."""
        assert get_agent_for_intent("unknown_but_confident", 0.8) == "abaporu"

    def test_case_insensitive(self):
        """Intent matching should be case insensitive."""
        assert get_agent_for_intent("INVESTIGATE") == "abaporu"
        assert get_agent_for_intent("Greeting") == "drummond"
        assert get_agent_for_intent("ANALYZE") == "anita"


class TestResolveAgentId:
    """Tests for the main agent resolution function."""

    def test_explicit_agent_id_respected(self):
        """When agent_id is provided, it should be used."""
        agent_id, agent_name = resolve_agent_id(requested_agent_id="zumbi")
        assert agent_id == "zumbi"
        assert agent_name == "Zumbi dos Palmares"

    def test_explicit_agent_id_case_insensitive(self):
        """Agent ID matching should be case insensitive."""
        agent_id, _ = resolve_agent_id(requested_agent_id="ZUMBI")
        assert agent_id == "zumbi"

        agent_id, _ = resolve_agent_id(requested_agent_id="Anita")
        assert agent_id == "anita"

    def test_invalid_agent_falls_back_to_intent(self):
        """Invalid agent_id should fall back to intent-based routing."""
        agent_id, _ = resolve_agent_id(
            requested_agent_id="invalid_agent", intent_type="greeting"
        )
        assert agent_id == "drummond"

    def test_no_agent_no_intent_uses_abaporu(self):
        """No agent_id and no intent should use Abaporu."""
        agent_id, agent_name = resolve_agent_id(requested_agent_id=None)
        assert agent_id == "abaporu"
        assert agent_name == "Abaporu"

    def test_no_agent_with_intent_uses_routing(self):
        """No agent_id but with intent should use intent routing."""
        agent_id, _ = resolve_agent_id(
            requested_agent_id=None, intent_type="investigate"
        )
        assert agent_id == "abaporu"

        agent_id, _ = resolve_agent_id(requested_agent_id=None, intent_type="greeting")
        assert agent_id == "drummond"

    def test_returns_tuple(self):
        """resolve_agent_id should return tuple of (id, name)."""
        result = resolve_agent_id(requested_agent_id="anita")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == "anita"
        assert result[1] == "Anita Garibaldi"


class TestHelperFunctions:
    """Tests for utility functions."""

    def test_get_agent_info(self):
        """get_agent_info should return full agent metadata."""
        info = get_agent_info("zumbi")
        assert info is not None
        assert info["name"] == "Zumbi dos Palmares"
        assert "avatar" in info
        assert "description" in info

    def test_get_agent_info_invalid(self):
        """get_agent_info should return None for invalid agent."""
        assert get_agent_info("invalid") is None

    def test_is_valid_agent(self):
        """is_valid_agent should correctly identify valid agents."""
        assert is_valid_agent("zumbi") is True
        assert is_valid_agent("abaporu") is True
        assert is_valid_agent("invalid") is False
        assert is_valid_agent("") is False
        assert is_valid_agent(None) is False

    def test_list_available_agents(self):
        """list_available_agents should return all agents."""
        agents = list_available_agents()
        assert len(agents) > 0
        assert all("id" in a for a in agents)
        assert all("name" in a for a in agents)
        assert any(a["id"] == "abaporu" for a in agents)


class TestIntegrationWithFrontend:
    """Tests that verify the fix for the frontend issue."""

    def test_automatic_mode_uses_abaporu_not_anita(self):
        """
        When frontend sends no agent_id (automatic mode), should use Abaporu.
        This was the original bug - it was using Anita instead.
        """
        # Simulate automatic mode (no agent_id, question intent)
        agent_id, _ = resolve_agent_id(
            requested_agent_id=None, intent_type="question", intent_confidence=0.7
        )
        # Should NOT be anita anymore
        assert agent_id == "drummond"  # Questions go to Drummond now

        # Investigation should go to Abaporu (orchestrator)
        agent_id, _ = resolve_agent_id(
            requested_agent_id=None, intent_type="investigate", intent_confidence=0.9
        )
        assert agent_id == "abaporu"

    def test_manual_mode_respects_agent_choice(self):
        """
        When frontend sends specific agent_id (manual mode), should use that agent.
        """
        agent_id, _ = resolve_agent_id(requested_agent_id="anita")
        assert agent_id == "anita"

        agent_id, _ = resolve_agent_id(requested_agent_id="zumbi")
        assert agent_id == "zumbi"
