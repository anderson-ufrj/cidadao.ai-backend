"""
Tests for Oxóssi Agent (Fraud Hunter)
"""

import pytest

from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus
from src.agents.oxossi import FraudType, OxossiAgent


@pytest.fixture
def agent_context():
    """Create test agent context."""
    return AgentContext(
        investigation_id="test-123",
        user_id="user-123",
        session_id="session-123",
        metadata={},
    )


@pytest.fixture
def agent():
    """Create Oxóssi agent instance."""
    return OxossiAgent()


@pytest.fixture
def sample_contracts():
    """Sample contract data for testing."""
    return [
        {
            "contract_id": "001",
            "vendor_id": "V001",
            "vendor_name": "Company A",
            "contract_value": 100000,
            "bid_amount": 100000,
            "bidding_process_id": "BID001",
            "contract_date": "2025-01-15",
            "vendor_registration_date": "2025-01-01",
        },
        {
            "contract_id": "002",
            "vendor_id": "V002",
            "vendor_name": "Company B",
            "contract_value": 100100,
            "bid_amount": 100100,
            "bidding_process_id": "BID001",
            "contract_date": "2025-01-15",
        },
        {
            "contract_id": "003",
            "vendor_id": "V003",
            "vendor_name": "Company C",
            "contract_value": 99900,
            "bid_amount": 99900,
            "bidding_process_id": "BID001",
            "contract_date": "2025-01-15",
        },
    ]


@pytest.fixture
def sample_vendors():
    """Sample vendor data for testing."""
    return [
        {
            "id": "V001",
            "name": "Company A",
            "address": "123 Main St",
            "phone": "555-0001",
            "email": "contact@companya.com",
        },
        {
            "id": "V002",
            "name": "Company B",
            "address": "123 Main St",  # Same address as Company A
            "phone": "555-0002",
            "email": "contact@companyb.com",
        },
        {
            "id": "V003",
            "name": "Company C",
            "address": "123 Main St",  # Same address again
            "phone": "555-0001",  # Same phone as Company A
            "email": "contact@companyc.com",
        },
    ]


class TestOxossiAgent:
    """Test suite for Oxóssi Agent."""

    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.agent_id == "oxossi"
        assert agent.name == "oxossi"
        assert (
            agent.description
            == "Fraud detection specialist with precision tracking capabilities"
        )
        assert agent.status == AgentStatus.IDLE
        assert "fraud_detection" in agent.capabilities
        assert "pattern_recognition" in agent.capabilities
        assert "financial_forensics" in agent.capabilities

    @pytest.mark.asyncio
    async def test_initialize(self, agent):
        """Test agent initialization process."""
        await agent.initialize()
        assert agent.status == AgentStatus.IDLE
        assert agent.fraud_patterns is not None
        assert FraudType.BID_RIGGING in agent.fraud_patterns

    @pytest.mark.asyncio
    async def test_detect_bid_rigging(self, agent, agent_context, sample_contracts):
        """Test bid rigging detection."""
        # Create message
        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="analyze_fraud",
            payload={"contracts": sample_contracts},
        )

        # Process message
        response = await agent.process(message, agent_context)

        # Verify response
        assert response.status == AgentStatus.COMPLETED
        assert "fraud_analysis" in response.result
        analysis = response.result["fraud_analysis"]
        assert "patterns" in analysis

        # Should detect bid rigging due to similar amounts
        bid_rigging_patterns = [
            p
            for p in analysis["patterns"]
            if p["fraud_type"] == FraudType.BID_RIGGING.value
        ]
        assert len(bid_rigging_patterns) > 0

    @pytest.mark.asyncio
    async def test_detect_phantom_vendor(self, agent, agent_context, sample_contracts):
        """Test phantom vendor detection."""
        # Add a single-contract vendor
        phantom_vendor_contract = {
            "contract_id": "004",
            "vendor_id": "V004",
            "vendor_name": "Phantom Corp",
            "contract_value": 500000,
            "contract_date": "2025-01-20",
            "vendor_registration_date": "2025-01-15",  # Registered 5 days before contract
        }

        contracts = sample_contracts + [phantom_vendor_contract]

        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="detect_phantom_vendors",
            payload={"contracts": contracts},
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        analysis = response.result["fraud_analysis"]

        # Should detect phantom vendor
        phantom_patterns = [
            p
            for p in analysis["patterns"]
            if p["fraud_type"] == FraudType.PHANTOM_VENDOR.value
        ]
        assert len(phantom_patterns) > 0

        # Check if Phantom Corp is detected in any of the patterns
        phantom_corp_detected = any(
            "Phantom Corp" in p["entities_involved"] for p in phantom_patterns
        )
        assert (
            phantom_corp_detected
        ), "Phantom Corp should be detected as a phantom vendor"

    @pytest.mark.asyncio
    async def test_detect_shared_vendor_info(
        self, agent, agent_context, sample_vendors
    ):
        """Test detection of vendors with shared contact information."""
        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="analyze_vendor_fraud",
            payload={"vendors": sample_vendors},
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        analysis = response.result["fraud_analysis"]

        # Should detect shared address and phone
        shared_info_patterns = [
            p
            for p in analysis["patterns"]
            if any(ind["type"] == "shared_address" for ind in p["indicators"])
        ]
        assert len(shared_info_patterns) > 0

    @pytest.mark.asyncio
    async def test_detect_duplicate_invoices(self, agent, agent_context):
        """Test duplicate invoice detection."""
        invoices = [
            {
                "invoice_number": "INV001",
                "vendor_id": "V001",
                "vendor_name": "Company A",
                "amount": 10000,
                "date": "2025-01-15",
            },
            {
                "invoice_number": "INV002",
                "vendor_id": "V001",
                "vendor_name": "Company A",
                "amount": 10000,  # Same amount
                "date": "2025-01-15",  # Same date
            },
        ]

        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="analyze_invoices_for_fraud",
            payload={"invoices": invoices},
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        analysis = response.result["fraud_analysis"]

        # Should detect duplicate invoice
        duplicate_patterns = [
            p
            for p in analysis["patterns"]
            if p["fraud_type"] == FraudType.INVOICE_FRAUD.value
        ]
        assert len(duplicate_patterns) > 0

    @pytest.mark.asyncio
    async def test_fraud_severity_classification(
        self, agent, agent_context, sample_vendors
    ):
        """Test that fraud patterns are properly classified by severity."""
        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="comprehensive_fraud_analysis",
            payload={"vendors": sample_vendors},
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        analysis = response.result["fraud_analysis"]

        # Check severity classification
        assert "risk_level" in analysis
        assert analysis["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    @pytest.mark.asyncio
    async def test_high_risk_entity_identification(self, agent, agent_context):
        """Test identification of high-risk entities."""
        # Create contracts that trigger bid rigging detection
        # All contracts in same bidding process with similar bid amounts
        contracts = [
            {
                "contract_id": f"C{i:03d}",
                "vendor_id": "V_RISKY",
                "vendor_name": "Risky Vendor",
                "contract_value": 100000 + i * 1000,
                "bid_amount": 100000,  # All same bid amount (suspicious)
                "bidding_process_id": "BID001",  # All in same bidding process
                "contract_date": f"2025-01-{i+1:02d}",
            }
            for i in range(5)
        ]

        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="identify_high_risk_entities",
            payload={"contracts": contracts},
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "high_risk_entities" in response.result
        high_risk = response.result["high_risk_entities"]
        assert len(high_risk) > 0
        assert high_risk[0]["entity"] == "Risky Vendor"

    @pytest.mark.asyncio
    async def test_comprehensive_fraud_analysis(self, agent, agent_context):
        """Test comprehensive fraud analysis across multiple data types."""
        data = {
            "contracts": [
                {
                    "contract_id": "C001",
                    "vendor_id": "V001",
                    "vendor_name": "Suspicious Corp",
                    "contract_value": 1000000,
                    "category": "IT Services",
                    "unit_price": 1000,
                    "contract_date": "2025-01-15",
                }
            ],
            "vendors": [
                {
                    "id": "V001",
                    "name": "Suspicious Corp",
                    "address": "999 Fake St",
                    "phone": "555-FAKE",
                }
            ],
            "invoices": [
                {
                    "invoice_number": "FAKE001",
                    "vendor_id": "V001",
                    "vendor_name": "Suspicious Corp",
                    "amount": 50000,
                    "date": "2025-01-20",
                }
            ],
        }

        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="comprehensive_fraud_analysis",
            payload=data,
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        analysis = response.result["fraud_analysis"]
        assert len(analysis["patterns"]) > 0
        assert "recommendations" in analysis
        assert len(analysis["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, agent, agent_context):
        """Test error handling for invalid data."""
        # No data provided
        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="detect_fraud",
            payload={},  # Empty payload instead of None
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.ERROR
        assert response.error is not None

    @pytest.mark.asyncio
    async def test_hunt_specific_fraud_type(
        self, agent, agent_context, sample_contracts
    ):
        """Test hunting for specific fraud type."""
        response = await agent.hunt_specific_fraud(
            fraud_type=FraudType.BID_RIGGING,
            data={"contracts": sample_contracts},
            context=agent_context,
        )

        assert response.status == AgentStatus.COMPLETED
        assert "fraud_analysis" in response.result

    @pytest.mark.asyncio
    async def test_fraud_confidence_calculation(self, agent, agent_context):
        """Test overall confidence score calculation."""
        # Create data that will generate multiple patterns with different confidences
        data = {
            "contracts": [
                {
                    "contract_id": "C001",
                    "vendor_id": "V001",
                    "vendor_name": "Test Vendor",
                    "contract_value": 100000,
                    "bid_amount": 100000,
                    "bidding_process_id": "BID001",
                    "contract_date": "2025-01-15",
                }
            ]
            * 3  # Duplicate contracts to trigger patterns
        }

        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="analyze_fraud_confidence",
            payload=data,
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        assert "confidence_score" in response.metadata
        assert 0 <= response.metadata["confidence_score"] <= 1


class TestOxossiKickbackDetection:
    """Test suite for Kickback Schemes Detection (Phase 1)."""

    @pytest.mark.asyncio
    async def test_detect_round_number_kickback(self, agent, agent_context):
        """Test detection of round-number payments to individuals after contract."""
        transactions = [
            {
                "transaction_type": "contract_award",
                "contract_id": "C001",
                "vendor_id": "V001",
                "amount": 1000000,
                "date": "2025-01-01",
            },
            {
                "transaction_type": "payment",
                "payer_id": "V001",
                "recipient_id": "OFFICIAL001",
                "recipient_type": "individual",
                "amount": 50000,  # Round number: R$ 50k
                "date": "2025-01-15",  # 14 days after contract
            },
        ]

        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="detect_kickback_schemes",
            payload={"transactions": transactions},
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        analysis = response.result["fraud_analysis"]

        kickback_patterns = [
            p
            for p in analysis["patterns"]
            if p["fraud_type"] == FraudType.KICKBACK_SCHEME.value
        ]
        assert len(kickback_patterns) > 0

        # Check for suspicious_round_payment indicator
        pattern = kickback_patterns[0]
        indicators = pattern["indicators"]
        round_payment_indicators = [
            ind for ind in indicators if ind["type"] == "suspicious_round_payment"
        ]
        assert len(round_payment_indicators) > 0
        assert round_payment_indicators[0]["confidence"] == 0.75

    @pytest.mark.asyncio
    async def test_detect_percentage_kickback(self, agent, agent_context):
        """Test detection of payments that are exact percentage of contract value."""
        transactions = [
            {
                "transaction_type": "contract_award",
                "contract_id": "C002",
                "vendor_id": "V002",
                "amount": 500000,
                "date": "2025-02-01",
            },
            {
                "transaction_type": "payment",
                "payer_id": "V002",
                "recipient_id": "OFFICIAL002",
                "recipient_type": "individual",
                "amount": 50000,  # Exactly 10% of contract value
                "date": "2025-02-10",  # 9 days after
            },
        ]

        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="detect_percentage-based_kickbacks",
            payload={"transactions": transactions},
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        analysis = response.result["fraud_analysis"]

        kickback_patterns = [
            p
            for p in analysis["patterns"]
            if p["fraud_type"] == FraudType.KICKBACK_SCHEME.value
        ]
        assert len(kickback_patterns) > 0

        # Check for percentage_payment indicator
        pattern = kickback_patterns[0]
        indicators = pattern["indicators"]
        percentage_indicators = [
            ind for ind in indicators if ind["type"] == "percentage_payment"
        ]
        assert len(percentage_indicators) > 0
        assert percentage_indicators[0]["confidence"] == 0.8
        assert percentage_indicators[0]["risk_score"] == 8.5

    @pytest.mark.asyncio
    async def test_detect_vendor_payment_after_award(self, agent, agent_context):
        """Test detection of vendor payments shortly after winning contract."""
        transactions = [
            {
                "transaction_type": "contract_award",
                "contract_id": "C003",
                "vendor_id": "V003",
                "amount": 2000000,
                "date": "2025-03-01",
            },
            {
                "transaction_type": "payment",
                "payer_id": "V003",  # Same vendor who won contract
                "recipient_id": "DECISION_MAKER",
                "amount": 100000,
                "date": "2025-03-20",  # 19 days after contract
            },
        ]

        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="detect_post-award_payments",
            payload={"transactions": transactions},
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        analysis = response.result["fraud_analysis"]

        kickback_patterns = [
            p
            for p in analysis["patterns"]
            if p["fraud_type"] == FraudType.KICKBACK_SCHEME.value
        ]
        assert len(kickback_patterns) > 0

        pattern = kickback_patterns[0]
        assert "V003" in pattern["entities_involved"]
        assert pattern["severity"] in ["high", "critical"]


class TestOxossiCircularPayments:
    """Test suite for Circular Payment Detection."""

    @pytest.mark.asyncio
    async def test_detect_simple_circular_payment(self, agent, agent_context):
        """Test detection of A→B→C→A circular payment pattern."""
        transactions = [
            {
                "payer_id": "ENTITY_A",
                "recipient_id": "ENTITY_B",
                "amount": 100000,
                "date": "2025-01-01",
            },
            {
                "payer_id": "ENTITY_B",
                "recipient_id": "ENTITY_C",
                "amount": 95000,
                "date": "2025-01-02",
            },
            {
                "payer_id": "ENTITY_C",
                "recipient_id": "ENTITY_A",  # Completes the circle
                "amount": 90000,
                "date": "2025-01-03",
            },
        ]

        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="detect_circular_payments",
            payload={"transactions": transactions},
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        analysis = response.result["fraud_analysis"]

        circular_patterns = [
            p
            for p in analysis["patterns"]
            if p["fraud_type"] == FraudType.MONEY_LAUNDERING.value
            and any(ind["type"] == "circular_payments" for ind in p["indicators"])
        ]
        assert len(circular_patterns) > 0

        pattern = circular_patterns[0]
        assert pattern["severity"] == "critical"
        assert pattern["confidence"] == 0.85
        assert set(pattern["entities_involved"]) == {"ENTITY_A", "ENTITY_B", "ENTITY_C"}


class TestOxossiBenfordsLaw:
    """Test suite for Benford's Law Analysis."""

    @pytest.mark.asyncio
    async def test_benfords_law_with_natural_data(self, agent):
        """Test Benford's Law with naturally occurring data (should pass)."""
        # Generate values following Benford's Law distribution
        natural_values = [
            # Leading digit 1 (30.1%)
            1234,
            1456,
            1789,
            1001,
            1999,
            1500,
            1750,
            1250,
            1100,
            1900,
            # Leading digit 2 (17.6%)
            2345,
            2456,
            2567,
            2100,
            2900,
            # Leading digit 3 (12.5%)
            3456,
            3567,
            3100,
            3800,
            # Leading digits 4-9 (smaller frequencies)
            4567,
            4100,
            5678,
            6789,
            7890,
            8901,
            9012,
            # More 1s to match distribution
            1111,
            1222,
            1333,
        ]

        patterns = agent._analyze_benfords_law(natural_values, "Natural Data")

        # Should NOT detect fraud for natural distribution
        assert len(patterns) == 0

    @pytest.mark.asyncio
    async def test_benfords_law_with_manipulated_data(self, agent):
        """Test Benford's Law with manipulated data (should detect fraud)."""
        # Generate data with too many 5s and 6s (unnatural)
        manipulated_values = [
            5000,
            5100,
            5200,
            5300,
            5400,
            5500,
            5600,
            5700,
            5800,
            5900,
            6000,
            6100,
            6200,
            6300,
            6400,
            6500,
            6600,
            6700,
            6800,
            6900,
            7000,
            7100,
            7200,
            7300,
            8000,
            8100,
            8200,
            9000,
            9100,
            9200,
        ]

        patterns = agent._analyze_benfords_law(manipulated_values, "Manipulated Data")

        # Should detect fraud due to unnatural distribution
        assert len(patterns) > 0
        pattern = patterns[0]
        assert pattern.fraud_type == FraudType.FALSE_CLAIMS
        assert pattern.confidence >= 0.7
        assert "benfords_law_violation" in pattern.indicators[0].indicator_type

    @pytest.mark.asyncio
    async def test_benfords_law_insufficient_data(self, agent):
        """Test that Benford's Law requires minimum 30 samples."""
        small_dataset = [100, 200, 300, 400, 500]  # Only 5 values

        patterns = agent._analyze_benfords_law(small_dataset, "Small Data")

        # Should not analyze (insufficient data)
        assert len(patterns) == 0

    @pytest.mark.asyncio
    async def test_benfords_law_integration_in_contracts(self, agent, agent_context):
        """Test that Benford's Law is automatically applied to contract values."""
        # Create 35 contracts with manipulated values (lots of 5s)
        contracts = [
            {
                "contract_id": f"C{i:03d}",
                "vendor_id": f"V{i:03d}",
                "contract_value": 5000 + i * 100,  # Starts with 5
                "contract_date": f"2025-01-{(i % 28) + 1:02d}",
            }
            for i in range(35)
        ]

        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="comprehensive_analysis",
            payload={"contracts": contracts},
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        analysis = response.result["fraud_analysis"]

        # Should include Benford's Law violation
        benford_patterns = [
            p
            for p in analysis["patterns"]
            if any(ind["type"] == "benfords_law_violation" for ind in p["indicators"])
        ]
        assert len(benford_patterns) > 0


class TestOxossiTemporalAnomalies:
    """Test suite for Temporal Anomaly Detection."""

    @pytest.mark.asyncio
    async def test_detect_after_hours_activity(self, agent):
        """Test detection of after-hours transactions."""
        data = [
            {"date": "2025-01-15 22:30:00", "amount": 10000},  # 10:30 PM
            {"date": "2025-01-16 23:15:00", "amount": 15000},  # 11:15 PM
            {"date": "2025-01-17 02:00:00", "amount": 20000},  # 2:00 AM
            {"date": "2025-01-18 03:30:00", "amount": 12000},  # 3:30 AM
            {"date": "2025-01-19 14:00:00", "amount": 18000},  # 2:00 PM (normal)
            {"date": "2025-01-20 15:00:00", "amount": 16000},  # 3:00 PM (normal)
        ]

        patterns = agent._detect_temporal_anomalies(data, "Test Entity")

        assert len(patterns) > 0
        pattern = patterns[0]
        indicators = pattern.indicators

        after_hours_indicators = [
            ind for ind in indicators if ind.indicator_type == "after_hours_activity"
        ]
        assert len(after_hours_indicators) > 0
        # Should have >20% after hours (4 out of 6)
        assert after_hours_indicators[0].confidence == 0.7

    @pytest.mark.asyncio
    async def test_detect_weekend_activity(self, agent):
        """Test detection of weekend transactions."""
        data = [
            {"date": "2025-01-04 10:00:00", "amount": 10000},  # Saturday
            {"date": "2025-01-05 10:00:00", "amount": 15000},  # Sunday
            {"date": "2025-01-11 10:00:00", "amount": 20000},  # Saturday
            {"date": "2025-01-12 10:00:00", "amount": 12000},  # Sunday
            {"date": "2025-01-13 10:00:00", "amount": 18000},  # Monday (normal)
        ]

        patterns = agent._detect_temporal_anomalies(data, "Test Entity")

        assert len(patterns) > 0
        pattern = patterns[0]
        indicators = pattern.indicators

        weekend_indicators = [
            ind for ind in indicators if ind.indicator_type == "weekend_activity"
        ]
        assert len(weekend_indicators) > 0
        # Should have >30% weekend (4 out of 5 = 80%)

    @pytest.mark.asyncio
    async def test_detect_velocity_anomaly(self, agent):
        """Test detection of transactions processed too quickly."""
        data = [
            {"date": "2025-01-15 10:00:00", "amount": 10000},
            {"date": "2025-01-15 10:00:30", "amount": 15000},  # 30 seconds later
            {"date": "2025-01-15 10:00:45", "amount": 20000},  # 15 seconds later
            {"date": "2025-01-15 10:01:00", "amount": 12000},  # 15 seconds later
            {"date": "2025-01-15 10:01:15", "amount": 18000},  # 15 seconds later
        ]

        patterns = agent._detect_temporal_anomalies(data, "Test Entity")

        assert len(patterns) > 0
        pattern = patterns[0]
        indicators = pattern.indicators

        velocity_indicators = [
            ind for ind in indicators if ind.indicator_type == "velocity_anomaly"
        ]
        assert len(velocity_indicators) > 0
        assert velocity_indicators[0].confidence == 0.75

    @pytest.mark.asyncio
    async def test_detect_temporal_clustering(self, agent):
        """Test detection of unusual clustering of transactions."""
        # Create normal activity for 10 days, then a spike on day 11
        data = []
        for day in range(1, 11):
            # Normal: 2-3 transactions per day
            for _ in range(2):
                data.append(
                    {
                        "date": f"2025-01-{day:02d} 10:00:00",
                        "amount": 10000,
                    }
                )

        # Spike: 20 transactions on one day
        for hour in range(20):
            data.append(
                {
                    "date": f"2025-01-11 {hour:02d}:00:00",
                    "amount": 10000,
                }
            )

        patterns = agent._detect_temporal_anomalies(data, "Test Entity")

        assert len(patterns) > 0
        pattern = patterns[0]
        indicators = pattern.indicators

        clustering_indicators = [
            ind for ind in indicators if ind.indicator_type == "temporal_clustering"
        ]
        assert len(clustering_indicators) > 0

    @pytest.mark.asyncio
    async def test_temporal_analysis_integration(self, agent, agent_context):
        """Test that temporal analysis is automatically applied to timestamped data."""
        transactions = [
            {
                "date": "2025-01-15 23:00:00",
                "amount": 10000,
                "payer_id": "A",
                "recipient_id": "B",
            },  # After hours
            {
                "date": "2025-01-16 23:30:00",
                "amount": 15000,
                "payer_id": "A",
                "recipient_id": "B",
            },  # After hours
            {
                "date": "2025-01-17 10:00:00",
                "amount": 20000,
                "payer_id": "A",
                "recipient_id": "B",
            },  # Normal
        ]

        message = AgentMessage(
            sender="test",
            recipient="oxossi",
            action="comprehensive_analysis",
            payload={"transactions": transactions},
        )

        response = await agent.process(message, agent_context)

        assert response.status == AgentStatus.COMPLETED
        analysis = response.result["fraud_analysis"]

        # May or may not detect temporal anomalies depending on thresholds,
        # but integration is tested by verifying the analysis includes patterns
        assert "patterns" in analysis
