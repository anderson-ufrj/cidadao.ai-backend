"""
Additional comprehensive tests for Obaluaiê to achieve 80%+ coverage.
Tests Benford's Law, cartel detection, nepotism analysis, and risk scoring.
"""

import pytest

from src.agents.deodoro import AgentContext, AgentStatus
from src.agents.obaluaie import (
    CorruptionAlertResult,
    CorruptionDetectorAgent,
    CorruptionSeverity,
)


@pytest.fixture
def obaluaie_agent():
    """Create Obaluaiê agent."""
    return CorruptionDetectorAgent()


@pytest.fixture
def agent_context():
    """Sample agent context."""
    return AgentContext(
        investigation_id="test_001",
        user_id="user_123",
        session_id="session_456",
    )


@pytest.fixture
def sample_financial_data():
    """Sample financial data for testing Benford's Law."""
    return [
        {"value": 1234.56, "supplier_name": "Company A"},
        {"value": 2345.67, "supplier_name": "Company B"},
        {"value": 3456.78, "supplier_name": "Company C"},
        {"value": 1111.11, "supplier_name": "Company A"},
        {"value": 1987.65, "supplier_name": "Company D"},
        {"value": 2543.21, "supplier_name": "Company B"},
        {"value": 3210.98, "supplier_name": "Company E"},
        {"value": 1456.78, "supplier_name": "Company A"},
        {"value": 2789.01, "supplier_name": "Company F"},
        {"value": 1654.32, "supplier_name": "Company A"},
    ]


@pytest.fixture
def sample_bidding_data():
    """Sample bidding data for cartel detection."""
    return [
        {
            "bidding_id": "BID001",
            "winner": "Company A",
            "value": 100000.0,
            "participants": ["Company A", "Company B", "Company C"],
        },
        {
            "bidding_id": "BID002",
            "winner": "Company B",
            "value": 95000.0,
            "participants": ["Company A", "Company B", "Company C"],
        },
        {
            "bidding_id": "BID003",
            "winner": "Company C",
            "value": 98000.0,
            "participants": ["Company A", "Company B", "Company C"],
        },
        {
            "bidding_id": "BID004",
            "winner": "Company A",
            "value": 102000.0,
            "participants": ["Company A", "Company B", "Company C"],
        },
    ]


@pytest.mark.unit
class TestObaluaieCompleteCoverage:
    """Test suite for complete Obaluaiê coverage."""

    @pytest.mark.asyncio
    async def test_apply_benford_law_with_valid_data(
        self, obaluaie_agent, sample_financial_data
    ):
        """Test Benford's Law analysis with valid financial data."""
        score = await obaluaie_agent._apply_benford_law(sample_financial_data)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_apply_benford_law_empty_data(self, obaluaie_agent):
        """Test Benford's Law with empty data."""
        score = await obaluaie_agent._apply_benford_law([])

        assert score == 0.0

    @pytest.mark.asyncio
    async def test_apply_benford_law_no_valid_values(self, obaluaie_agent):
        """Test Benford's Law with no valid values."""
        data = [{"value": 0}, {"value": -100}, {"amount": 0}]
        score = await obaluaie_agent._apply_benford_law(data)

        assert score == 0.0

    @pytest.mark.asyncio
    async def test_detect_cartels_with_bidding_data(
        self, obaluaie_agent, sample_bidding_data
    ):
        """Test cartel detection with bidding data."""
        score = await obaluaie_agent._detect_cartels(sample_bidding_data)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_analyze_nepotism_with_concentration(
        self, obaluaie_agent, sample_financial_data
    ):
        """Test nepotism detection with entity concentration."""
        score = await obaluaie_agent._analyze_nepotism(sample_financial_data)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        # Company A appears 4 times out of 10 - should detect concentration
        assert score > 0.0

    @pytest.mark.asyncio
    async def test_analyze_nepotism_empty_data(self, obaluaie_agent):
        """Test nepotism analysis with empty data."""
        score = await obaluaie_agent._analyze_nepotism([])

        assert score == 0.0

    @pytest.mark.asyncio
    async def test_analyze_nepotism_no_entities(self, obaluaie_agent):
        """Test nepotism analysis with no entity information."""
        data = [{"value": 1000}, {"amount": 2000}]
        score = await obaluaie_agent._analyze_nepotism(data)

        # When no supplier_name or entity_id, it returns None values
        # which are treated as entities, so score > 0
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_calculate_transparency_index(
        self, obaluaie_agent, sample_financial_data
    ):
        """Test transparency index calculation."""
        score = await obaluaie_agent._calculate_transparency_index(
            sample_financial_data
        )

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_calculate_transparency_index_empty(self, obaluaie_agent):
        """Test transparency index with empty data."""
        score = await obaluaie_agent._calculate_transparency_index([])

        assert score == 0.0

    @pytest.mark.asyncio
    async def test_determine_severity_levels(self, obaluaie_agent):
        """Test severity determination for different scores."""
        assert obaluaie_agent._determine_severity(0.2) == CorruptionSeverity.LOW
        assert obaluaie_agent._determine_severity(0.5) == CorruptionSeverity.MEDIUM
        assert obaluaie_agent._determine_severity(0.75) == CorruptionSeverity.HIGH
        assert obaluaie_agent._determine_severity(0.95) == CorruptionSeverity.CRITICAL

    @pytest.mark.asyncio
    async def test_calculate_priority(self, obaluaie_agent):
        """Test investigation priority calculation."""
        high_risk_result = {
            "corruption_detected": True,
            "confidence": 0.95,
            "severity": "critical",
            "financial_impact": 1000000.0,
        }

        priority = obaluaie_agent._calculate_priority(high_risk_result)

        assert isinstance(priority, int)
        assert 1 <= priority <= 10
        assert priority >= 8  # High risk should get high priority

    @pytest.mark.asyncio
    async def test_calculate_priority_low_risk(self, obaluaie_agent):
        """Test priority for low risk case."""
        low_risk_result = {
            "corruption_detected": False,
            "confidence": 0.3,
            "severity": "low",
            "financial_impact": 1000.0,
        }

        priority = obaluaie_agent._calculate_priority(low_risk_result)

        assert isinstance(priority, int)
        assert 1 <= priority <= 10
        assert priority <= 3  # Low risk should get low priority

    @pytest.mark.asyncio
    async def test_benford_law_analysis_method(self, obaluaie_agent, agent_context):
        """Test _benford_law_analysis method directly."""
        data = {"financial_data": [{"value": 1234}, {"value": 2345}, {"value": 3456}]}

        result = await obaluaie_agent._benford_law_analysis(data, agent_context)

        assert isinstance(result, dict)
        assert "corruption_detected" in result
        assert "confidence" in result
        assert "severity" in result
        assert "patterns" in result

    @pytest.mark.asyncio
    async def test_cartel_detection_method(self, obaluaie_agent, agent_context):
        """Test _cartel_detection method directly."""
        data = {"bidding_data": [{"winner": "Company A", "value": 100000}]}

        result = await obaluaie_agent._cartel_detection(data, agent_context)

        assert isinstance(result, dict)
        assert "corruption_detected" in result
        assert "confidence" in result
        assert "severity" in result
        assert "patterns" in result

    @pytest.mark.asyncio
    async def test_nepotism_detection_method(self, obaluaie_agent, agent_context):
        """Test _nepotism_detection method directly."""
        data = {"entity_data": [{"supplier_name": "Company A", "value": 1000}]}

        result = await obaluaie_agent._nepotism_detection(data, agent_context)

        assert isinstance(result, dict)
        assert "corruption_detected" in result
        assert "confidence" in result
        assert "severity" in result
        assert "patterns" in result

    @pytest.mark.asyncio
    async def test_financial_flow_analysis_method(self, obaluaie_agent, agent_context):
        """Test _financial_flow_analysis method directly."""
        data = {"transaction_data": [{"from": "A", "to": "B", "amount": 10000}]}

        result = await obaluaie_agent._financial_flow_analysis(data, agent_context)

        assert isinstance(result, dict)
        assert "corruption_detected" in result
        assert "confidence" in result
        assert "severity" in result
        assert "patterns" in result

    @pytest.mark.asyncio
    async def test_shutdown(self, obaluaie_agent):
        """Test agent shutdown."""
        await obaluaie_agent.initialize()
        await obaluaie_agent.shutdown()

        assert obaluaie_agent.status == AgentStatus.IDLE

    @pytest.mark.asyncio
    async def test_generate_recommendations(self, obaluaie_agent):
        """Test recommendation generation."""
        alert_result = CorruptionAlertResult(
            alert_type="benford_law",
            severity=CorruptionSeverity.HIGH,
            confidence_score=0.85,
            entities_involved=["Entity A"],
            suspicious_patterns=["Pattern 1"],
            financial_impact=500000.0,
            evidence_links=["evidence1.pdf"],
            risk_assessment={"risk_level": "high"},
            timestamp="2025-10-30T12:00:00",
            investigation_priority=8,
        )

        recommendations = obaluaie_agent._generate_recommendations(alert_result)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    @pytest.mark.asyncio
    async def test_generate_recommendations_critical_severity(self, obaluaie_agent):
        """Test recommendations for critical severity alert."""
        alert_result = CorruptionAlertResult(
            alert_type="cartel_detection",
            severity=CorruptionSeverity.CRITICAL,
            confidence_score=0.95,
            entities_involved=["Entity A", "Entity B"],
            suspicious_patterns=["Pattern 1", "Pattern 2"],
            financial_impact=5000000.0,
            evidence_links=["evidence1.pdf", "evidence2.pdf"],
            risk_assessment={"risk_level": "critical"},
            timestamp="2025-10-30T12:00:00",
            investigation_priority=10,
        )

        recommendations = obaluaie_agent._generate_recommendations(alert_result)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    @pytest.mark.asyncio
    async def test_apply_benford_law_with_large_numbers(self, obaluaie_agent):
        """Test Benford's Law with large financial values."""
        large_values = [
            {"value": 123456.78, "supplier_name": "Company A"},
            {"value": 234567.89, "supplier_name": "Company B"},
            {"value": 345678.90, "supplier_name": "Company C"},
            {"value": 156789.01, "supplier_name": "Company D"},
            {"value": 267890.12, "supplier_name": "Company E"},
        ]

        score = await obaluaie_agent._apply_benford_law(large_values)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_detect_cartels_with_single_winner(self, obaluaie_agent):
        """Test cartel detection with single repeated winner."""
        bidding_data = [
            {
                "bidding_id": f"BID{i:03d}",
                "winner": "Company A",
                "value": 100000.0 + i * 1000,
                "participants": ["Company A", "Company B", "Company C"],
            }
            for i in range(10)
        ]

        score = await obaluaie_agent._detect_cartels(bidding_data)

        assert isinstance(score, float)
        # High concentration should give high score
        assert score > 0.5

    @pytest.mark.asyncio
    async def test_analyze_nepotism_high_concentration(self, obaluaie_agent):
        """Test nepotism with high supplier concentration."""
        concentrated_data = [
            {"value": 10000 + i * 100, "supplier_name": "Company A"} for i in range(15)
        ] + [{"value": 5000, "supplier_name": "Company B"}]

        score = await obaluaie_agent._analyze_nepotism(concentrated_data)

        assert isinstance(score, float)
        # 15/16 = 93.75% concentration, should be high score
        assert score > 0.8

    @pytest.mark.asyncio
    async def test_calculate_transparency_index_complete_data(self, obaluaie_agent):
        """Test transparency index with complete data."""
        complete_data = [
            {
                "value": 1000,
                "supplier_name": "Company A",
                "contract_id": "CTR001",
                "description": "Service contract",
                "date": "2025-01-01",
            }
            for i in range(10)
        ]

        score = await obaluaie_agent._calculate_transparency_index(complete_data)

        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_calculate_priority_edge_cases(self, obaluaie_agent):
        """Test priority calculation with edge cases."""
        # Zero confidence
        zero_conf_result = {
            "corruption_detected": False,
            "confidence": 0.0,
            "severity": "low",
            "financial_impact": 0.0,
        }
        priority_zero = obaluaie_agent._calculate_priority(zero_conf_result)
        assert 1 <= priority_zero <= 10

        # Maximum values
        max_result = {
            "corruption_detected": True,
            "confidence": 1.0,
            "severity": "critical",
            "financial_impact": 100000000.0,
        }
        priority_max = obaluaie_agent._calculate_priority(max_result)
        assert priority_max == 10

    @pytest.mark.asyncio
    async def test_detect_cartels_empty_data(self, obaluaie_agent):
        """Test cartel detection with empty data."""
        score = await obaluaie_agent._detect_cartels([])
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_analyze_nepotism_single_entity(self, obaluaie_agent):
        """Test nepotism with single entity (100% concentration)."""
        single_entity_data = [
            {"value": 10000, "supplier_name": "Company A"},
            {"value": 20000, "supplier_name": "Company A"},
            {"value": 30000, "supplier_name": "Company A"},
        ]

        score = await obaluaie_agent._analyze_nepotism(single_entity_data)
        assert isinstance(score, float)
        assert score > 0.0

    @pytest.mark.asyncio
    async def test_calculate_transparency_index_missing_fields(self, obaluaie_agent):
        """Test transparency with incomplete data (missing fields)."""
        incomplete_data = [
            {"value": 1000},  # Missing supplier_name, contract_id, etc.
            {"supplier_name": "Company B"},  # Missing value
            {},  # Completely empty
        ]

        score = await obaluaie_agent._calculate_transparency_index(incomplete_data)
        assert isinstance(score, float)
        # Should have low transparency score due to missing fields
        assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_determine_severity_boundary_values(self, obaluaie_agent):
        """Test severity determination at exact boundary values."""
        # LOW: score < 0.4
        assert obaluaie_agent._determine_severity(0.0) == CorruptionSeverity.LOW
        assert obaluaie_agent._determine_severity(0.3) == CorruptionSeverity.LOW
        # MEDIUM: 0.4 <= score < 0.7
        assert obaluaie_agent._determine_severity(0.4) == CorruptionSeverity.MEDIUM
        assert obaluaie_agent._determine_severity(0.5) == CorruptionSeverity.MEDIUM
        assert obaluaie_agent._determine_severity(0.65) == CorruptionSeverity.MEDIUM
        # HIGH: 0.7 <= score < 0.9
        assert obaluaie_agent._determine_severity(0.7) == CorruptionSeverity.HIGH
        assert obaluaie_agent._determine_severity(0.85) == CorruptionSeverity.HIGH
        # CRITICAL: score >= 0.9
        assert obaluaie_agent._determine_severity(0.9) == CorruptionSeverity.CRITICAL
        assert obaluaie_agent._determine_severity(1.0) == CorruptionSeverity.CRITICAL

    @pytest.mark.asyncio
    async def test_apply_benford_law_single_digit_values(self, obaluaie_agent):
        """Test Benford's Law with single-digit values."""
        single_digit_data = [
            {"value": 1.0, "supplier_name": "A"},
            {"value": 2.0, "supplier_name": "B"},
            {"value": 3.0, "supplier_name": "C"},
        ]

        score = await obaluaie_agent._apply_benford_law(single_digit_data)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_detect_cartels_perfect_distribution(self, obaluaie_agent):
        """Test cartel detection with perfect winner distribution."""
        perfect_distribution = [
            {
                "bidding_id": "BID001",
                "winner": "Company A",
                "value": 100000.0,
            },
            {
                "bidding_id": "BID002",
                "winner": "Company B",
                "value": 105000.0,
            },
            {
                "bidding_id": "BID003",
                "winner": "Company C",
                "value": 102000.0,
            },
        ]

        score = await obaluaie_agent._detect_cartels(perfect_distribution)
        assert isinstance(score, float)
        # Should be low since distribution is perfect
        assert score < 0.5
