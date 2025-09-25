"""
Tests for Oxóssi Agent (Fraud Hunter)
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.oxossi import (
    OxossiAgent, 
    FraudType, 
    FraudSeverity, 
    FraudIndicator, 
    FraudPattern
)
from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus
from src.core.exceptions import AgentExecutionError


@pytest.fixture
def agent_context():
    """Create test agent context."""
    return AgentContext(
        investigation_id="test-123",
        user_id="user-123",
        session_id="session-123",
        metadata={}
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
            "vendor_registration_date": "2025-01-01"
        },
        {
            "contract_id": "002", 
            "vendor_id": "V002",
            "vendor_name": "Company B",
            "contract_value": 100100,
            "bid_amount": 100100,
            "bidding_process_id": "BID001",
            "contract_date": "2025-01-15"
        },
        {
            "contract_id": "003",
            "vendor_id": "V003",
            "vendor_name": "Company C",
            "contract_value": 99900,
            "bid_amount": 99900,
            "bidding_process_id": "BID001",
            "contract_date": "2025-01-15"
        }
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
            "email": "contact@companya.com"
        },
        {
            "id": "V002",
            "name": "Company B",
            "address": "123 Main St",  # Same address as Company A
            "phone": "555-0002",
            "email": "contact@companyb.com"
        },
        {
            "id": "V003",
            "name": "Company C",
            "address": "123 Main St",  # Same address again
            "phone": "555-0001",  # Same phone as Company A
            "email": "contact@companyc.com"
        }
    ]


class TestOxossiAgent:
    """Test suite for Oxóssi Agent."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.agent_id == "oxossi"
        assert agent.name == "Oxóssi"
        assert agent.description == "Fraud detection specialist with precision tracking capabilities"
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
            role="user",
            content="Analyze contracts for fraud",
            data={"contracts": sample_contracts}
        )
        
        # Process message
        response = await agent.process(message, agent_context)
        
        # Verify response
        assert response.success
        assert "fraud_analysis" in response.data
        analysis = response.data["fraud_analysis"]
        assert "patterns" in analysis
        
        # Should detect bid rigging due to similar amounts
        bid_rigging_patterns = [
            p for p in analysis["patterns"] 
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
            "vendor_registration_date": "2025-01-15"  # Registered 5 days before contract
        }
        
        contracts = sample_contracts + [phantom_vendor_contract]
        
        message = AgentMessage(
            role="user",
            content="Detect phantom vendors",
            data={"contracts": contracts}
        )
        
        response = await agent.process(message, agent_context)
        
        assert response.success
        analysis = response.data["fraud_analysis"]
        
        # Should detect phantom vendor
        phantom_patterns = [
            p for p in analysis["patterns"]
            if p["fraud_type"] == FraudType.PHANTOM_VENDOR.value
        ]
        assert len(phantom_patterns) > 0
        assert "Phantom Corp" in phantom_patterns[0]["entities_involved"]
    
    @pytest.mark.asyncio
    async def test_detect_shared_vendor_info(self, agent, agent_context, sample_vendors):
        """Test detection of vendors with shared contact information."""
        message = AgentMessage(
            role="user",
            content="Analyze vendor fraud",
            data={"vendors": sample_vendors}
        )
        
        response = await agent.process(message, agent_context)
        
        assert response.success
        analysis = response.data["fraud_analysis"]
        
        # Should detect shared address and phone
        shared_info_patterns = [
            p for p in analysis["patterns"]
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
                "date": "2025-01-15"
            },
            {
                "invoice_number": "INV002",
                "vendor_id": "V001", 
                "vendor_name": "Company A",
                "amount": 10000,  # Same amount
                "date": "2025-01-15"  # Same date
            }
        ]
        
        message = AgentMessage(
            role="user",
            content="Analyze invoices for fraud",
            data={"invoices": invoices}
        )
        
        response = await agent.process(message, agent_context)
        
        assert response.success
        analysis = response.data["fraud_analysis"]
        
        # Should detect duplicate invoice
        duplicate_patterns = [
            p for p in analysis["patterns"]
            if p["fraud_type"] == FraudType.INVOICE_FRAUD.value
        ]
        assert len(duplicate_patterns) > 0
    
    @pytest.mark.asyncio
    async def test_fraud_severity_classification(self, agent, agent_context, sample_vendors):
        """Test that fraud patterns are properly classified by severity."""
        message = AgentMessage(
            role="user",
            content="Comprehensive fraud analysis",
            data={"vendors": sample_vendors}
        )
        
        response = await agent.process(message, agent_context)
        
        assert response.success
        analysis = response.data["fraud_analysis"]
        
        # Check severity classification
        assert "risk_level" in analysis
        assert analysis["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    @pytest.mark.asyncio
    async def test_high_risk_entity_identification(self, agent, agent_context):
        """Test identification of high-risk entities."""
        contracts = [
            {
                "contract_id": f"C{i:03d}",
                "vendor_id": "V_RISKY",
                "vendor_name": "Risky Vendor",
                "contract_value": 100000 + i * 1000,
                "bid_amount": 100000,
                "bidding_process_id": f"BID{i:03d}",
                "contract_date": f"2025-01-{i+1:02d}"
            }
            for i in range(5)
        ]
        
        message = AgentMessage(
            role="user",
            content="Identify high risk entities",
            data={"contracts": contracts}
        )
        
        response = await agent.process(message, agent_context)
        
        assert response.success
        assert "high_risk_entities" in response.data
        high_risk = response.data["high_risk_entities"]
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
                    "contract_date": "2025-01-15"
                }
            ],
            "vendors": [
                {
                    "id": "V001",
                    "name": "Suspicious Corp",
                    "address": "999 Fake St",
                    "phone": "555-FAKE"
                }
            ],
            "invoices": [
                {
                    "invoice_number": "FAKE001",
                    "vendor_id": "V001",
                    "vendor_name": "Suspicious Corp",
                    "amount": 50000,
                    "date": "2025-01-20"
                }
            ]
        }
        
        message = AgentMessage(
            role="user",
            content="Comprehensive fraud analysis",
            data=data
        )
        
        response = await agent.process(message, agent_context)
        
        assert response.success
        analysis = response.data["fraud_analysis"]
        assert len(analysis["patterns"]) > 0
        assert "recommendations" in analysis
        assert len(analysis["recommendations"]) > 0
    
    @pytest.mark.asyncio
    async def test_error_handling(self, agent, agent_context):
        """Test error handling for invalid data."""
        # No data provided
        message = AgentMessage(
            role="user",
            content="Detect fraud",
            data=None
        )
        
        response = await agent.process(message, agent_context)
        
        assert not response.success
        assert "error" in response.data
    
    @pytest.mark.asyncio
    async def test_hunt_specific_fraud_type(self, agent, agent_context, sample_contracts):
        """Test hunting for specific fraud type."""
        response = await agent.hunt_specific_fraud(
            fraud_type=FraudType.BID_RIGGING,
            data={"contracts": sample_contracts},
            context=agent_context
        )
        
        assert response.success
        assert "fraud_analysis" in response.data
    
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
                    "contract_date": "2025-01-15"
                }
            ] * 3  # Duplicate contracts to trigger patterns
        }
        
        message = AgentMessage(
            role="user",
            content="Analyze fraud confidence",
            data=data
        )
        
        response = await agent.process(message, agent_context)
        
        assert response.success
        assert "confidence_score" in response.metadata
        assert 0 <= response.metadata["confidence_score"] <= 1