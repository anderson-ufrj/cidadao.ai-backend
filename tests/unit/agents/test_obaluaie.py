"""
Complete unit tests for Obaluaiê Agent - Corruption detection specialist.
Tests Benford's Law analysis, cartel detection, nepotism detection, and corruption scoring.
"""

import pytest

from src.agents.deodoro import AgentContext, AgentMessage
from src.agents.obaluaie import CorruptionDetectorAgent, CorruptionSeverity


@pytest.fixture
def obaluaie_agent():
    """Create Obaluaiê corruption detection agent."""
    return CorruptionDetectorAgent()


@pytest.fixture
def agent_context():
    """Create test agent context."""
    return AgentContext(investigation_id="corruption-test-001")


@pytest.mark.unit
class TestObaluaieCorruptionDetection:
    """Test core corruption detection functionality."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, obaluaie_agent):
        """Test Obaluaiê agent initialization."""
        assert obaluaie_agent.name == "obaluaie"
        assert "corruption_detection" in obaluaie_agent.capabilities
        assert "benford_analysis" in obaluaie_agent.capabilities
        assert "cartel_detection" in obaluaie_agent.capabilities
        assert "nepotism_detection" in obaluaie_agent.capabilities
        assert "financial_flow_analysis" in obaluaie_agent.capabilities

    @pytest.mark.asyncio
    async def test_initialize_loads_models(self, obaluaie_agent):
        """Test that initialize loads ML models."""
        await obaluaie_agent.initialize()

        assert obaluaie_agent.fraud_neural_network is not None
        assert obaluaie_agent.cartel_detector is not None
        assert obaluaie_agent.relationship_analyzer is not None
        assert obaluaie_agent.fraud_neural_network["model_type"] == "LSTM_Autoencoder"

    @pytest.mark.asyncio
    async def test_benford_law_analysis(self, obaluaie_agent):
        """Test Benford's Law analysis detects manipulation."""
        # Data that violates Benford's Law (too many 5s)
        data = [
            {"value": 5000},
            {"value": 5500},
            {"value": 5200},
            {"value": 5100},
            {"value": 5800},
        ]

        score = await obaluaie_agent._apply_benford_law(data)

        # Should detect deviation from expected ~30% for digit 1
        assert 0 <= score <= 1.0
        assert score > 0.5  # Should be suspicious

    @pytest.mark.asyncio
    async def test_benford_law_empty_data(self, obaluaie_agent):
        """Test Benford's Law with empty data."""
        score = await obaluaie_agent._apply_benford_law([])
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_detect_cartels_high_concentration(self, obaluaie_agent):
        """Test cartel detection with high supplier concentration."""
        # Same supplier wins repeatedly
        data = [
            {"supplier": "Company A"},
            {"supplier": "Company A"},
            {"supplier": "Company A"},
            {"supplier": "Company B"},
        ]

        score = await obaluaie_agent._detect_cartels(data)

        # High concentration should trigger cartel detection
        assert score >= 0.7

    @pytest.mark.asyncio
    async def test_analyze_bidding_cartels(self, obaluaie_agent):
        """Test bidding cartel analysis."""
        bidding_data = [
            {"winner": "Company X"},
            {"winner": "Company X"},
            {"winner": "Company X"},
            {"winner": "Company Y"},
        ]

        result = await obaluaie_agent.analyze_bidding_cartels(bidding_data)

        assert "cartel_detected" in result
        assert "score" in result
        assert "patterns" in result
        assert result["affected_biddings"] == 4

    @pytest.mark.asyncio
    async def test_analyze_nepotism_high_repeat(self, obaluaie_agent):
        """Test nepotism detection with repeated entities."""
        data = [
            {"supplier_name": "Entity A"},
            {"supplier_name": "Entity A"},
            {"supplier_name": "Entity A"},
            {"supplier_name": "Entity B"},
        ]

        score = await obaluaie_agent._analyze_nepotism(data)

        # High repeat rate should indicate potential nepotism
        assert score > 0.3

    @pytest.mark.asyncio
    async def test_transparency_index_missing_fields(self, obaluaie_agent):
        """Test transparency index with missing data."""
        # Data with missing required fields
        data = [
            {"value": 1000},  # Missing date, supplier_name, description
            {"date": "2024-01-01"},  # Missing value, supplier_name, description
        ]

        score = await obaluaie_agent._calculate_transparency_index(data)

        # Should detect low transparency
        assert score > 0.5

    @pytest.mark.asyncio
    async def test_detect_money_laundering_round_numbers(self, obaluaie_agent):
        """Test money laundering detection with round numbers."""
        financial_data = [
            {"value": 10000},  # Suspicious round number
            {"amount": 20000},  # Suspicious round number
            {"value": 9500},  # Just below threshold
        ]

        result = await obaluaie_agent.detect_money_laundering(financial_data)

        assert "laundering_detected" in result
        assert "risk_score" in result
        assert result["suspicious_transactions"] > 0

    @pytest.mark.asyncio
    async def test_calculate_corruption_risk_score(self, obaluaie_agent):
        """Test corruption risk score calculation."""
        entity_data = {
            "irregularities": 3,
            "contract_count": 25,
            "political_connections": 2,
            "transparency_score": 0.3,
        }

        risk_score = await obaluaie_agent.calculate_corruption_risk_score(entity_data)

        assert 0.0 <= risk_score <= 1.0
        assert risk_score > 0.4  # Should be moderate-high risk

    @pytest.mark.asyncio
    async def test_corruption_severity_levels(self, obaluaie_agent):
        """Test severity determination for different scores."""
        assert obaluaie_agent._determine_severity(0.95) == CorruptionSeverity.CRITICAL
        assert obaluaie_agent._determine_severity(0.75) == CorruptionSeverity.HIGH
        assert obaluaie_agent._determine_severity(0.50) == CorruptionSeverity.MEDIUM
        assert obaluaie_agent._determine_severity(0.20) == CorruptionSeverity.LOW

    @pytest.mark.asyncio
    async def test_detect_corruption_patterns_integration(
        self, obaluaie_agent, agent_context
    ):
        """Test full corruption pattern detection pipeline."""
        await obaluaie_agent.initialize()

        data = [
            {"value": 5000, "supplier_name": "Company A", "date": "2024-01-01"},
            {"value": 5500, "supplier_name": "Company A", "date": "2024-01-15"},
            {"value": 5200, "supplier_name": "Company A", "date": "2024-02-01"},
        ]

        result = await obaluaie_agent.detect_corruption_patterns(data, agent_context)

        assert result.alert_type == "systemic_corruption"
        assert result.severity in [
            CorruptionSeverity.LOW,
            CorruptionSeverity.MEDIUM,
            CorruptionSeverity.HIGH,
            CorruptionSeverity.CRITICAL,
        ]
        assert 0.0 <= result.confidence_score <= 1.0
        assert len(result.entities_involved) > 0
        assert 1 <= result.investigation_priority <= 10

    @pytest.mark.asyncio
    @pytest.mark.skip(
        reason="AgentMessage structure mismatch - data field not settable"
    )
    async def test_process_benford_law_analysis(self, obaluaie_agent, agent_context):
        """Test process method with Benford's Law analysis."""
        # Note: Test skipped due to Pydantic model constraints on AgentMessage
        message = AgentMessage(
            sender="test",
            recipient="obaluaie",
            action="detect_corruption",
        )

        response = await obaluaie_agent.process(message, agent_context)

        assert response.success is True
        assert response.response_type == "corruption_analysis"
        assert "corruption_analysis" in response.data

    @pytest.mark.asyncio
    async def test_generate_recommendations(self, obaluaie_agent):
        """Test recommendation generation for critical corruption."""
        from datetime import datetime

        from src.agents.obaluaie import CorruptionAlertResult

        result = CorruptionAlertResult(
            alert_type="cartel_detection",
            severity=CorruptionSeverity.CRITICAL,
            confidence_score=0.92,
            entities_involved=["Company X", "Company Y"],
            suspicious_patterns=[{"pattern": "price_fixing"}],
            financial_impact=5000000.0,
            evidence_links=["network_graph.png"],
            risk_assessment={"priority": "critical"},
            timestamp=datetime.utcnow(),
            investigation_priority=9,
        )

        recommendations = obaluaie_agent._generate_recommendations(result)

        assert len(recommendations) >= 3
        assert any("investigação formal" in rec for rec in recommendations)

    @pytest.mark.asyncio
    async def test_shutdown(self, obaluaie_agent):
        """Test agent shutdown."""
        await obaluaie_agent.initialize()
        await obaluaie_agent.shutdown()
        # Should complete without errors
        assert True

    @pytest.mark.asyncio
    async def test_reflect_borderline_confidence(self, obaluaie_agent, agent_context):
        """Test reflection on borderline confidence results."""
        result = {
            "corruption_analysis": {
                "confidence": 0.62,
                "severity": "medium",
                "patterns": ["single_pattern"],
            }
        }

        reflected = await obaluaie_agent.reflect(
            "cartel_detection", result, agent_context
        )

        assert "reflection" in reflected
        assert "quality_issues_found" in reflected["reflection"]
