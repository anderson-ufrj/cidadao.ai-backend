"""
Unit tests for Tiradentes Agent - Investigation and corruption detection specialist.
Tests anomaly detection, investigation workflows, and data analysis capabilities.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4

from src.agents.tiradentes import (
    TiradentesAgent,
    InvestigationRequest,
    AnomalyReport,
    CorruptionIndicator,
)
from src.agents.deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    AgentStatus,
)
from src.core.exceptions import AgentExecutionError


@pytest.fixture
def mock_data_service():
    """Mock data service for testing."""
    service = AsyncMock()
    service.get_contracts.return_value = [
        {
            "id": "12345",
            "valor": 1000000.0,
            "objeto": "Fornecimento de equipamentos",
            "fornecedor": {"nome": "Tech Corp", "cnpj": "12.345.678/0001-90"},
            "dataAssinatura": "2024-01-15",
            "prazoVigencia": 365
        },
        {
            "id": "67890", 
            "valor": 5000000.0,  # Suspiciously high value
            "objeto": "Consultoria em TI",
            "fornecedor": {"nome": "Consulting Inc", "cnpj": "98.765.432/0001-12"},
            "dataAssinatura": "2024-02-01",
            "prazoVigencia": 180
        }
    ]
    
    service.get_expenses.return_value = [
        {
            "id": "exp001",
            "valor": 250000.0,
            "orgaoSuperior": {"nome": "Ministério da Educação"},
            "modalidadeAplicacao": {"nome": "Aplicação Direta"},
            "dataCompetencia": "2024-01-01"
        }
    ]
    
    service.get_suppliers.return_value = [
        {
            "cnpj": "12.345.678/0001-90",
            "nome": "Tech Corp",
            "situacao": "Ativa",
            "contratos_count": 15,
            "valor_total": 25000000.0
        }
    ]
    
    return service


@pytest.fixture
def mock_ai_service():
    """Mock AI service for anomaly detection."""
    service = AsyncMock()
    service.detect_anomalies.return_value = {
        "anomalies": [
            {
                "type": "price_anomaly",
                "severity": "high", 
                "confidence": 0.92,
                "description": "Price 400% above market average",
                "affected_contracts": ["67890"],
                "evidence": {
                    "market_price": 1250000.0,
                    "contract_price": 5000000.0,
                    "deviation_ratio": 4.0
                }
            },
            {
                "type": "supplier_concentration",
                "severity": "medium",
                "confidence": 0.76,
                "description": "High concentration of contracts with single supplier",
                "affected_supplier": "12.345.678/0001-90",
                "evidence": {
                    "contracts_percentage": 0.35,
                    "value_percentage": 0.42
                }
            }
        ],
        "overall_risk_score": 0.84,
        "processing_metadata": {
            "analysis_time": 2.3,
            "data_points_analyzed": 156,
            "models_used": ["isolation_forest", "statistical_outlier"]
        }
    }
    
    service.classify_corruption_risk.return_value = {
        "risk_level": "high",
        "confidence": 0.88,
        "indicators": [
            "unusual_pricing",
            "supplier_concentration", 
            "rapid_contract_execution"
        ],
        "explanation": "Multiple red flags indicate potential corruption"
    }
    
    return service


@pytest.fixture
def agent_context():
    """Test agent context."""
    return AgentContext(
        investigation_id="investigation-tiradentes-001",
        user_id="investigator-user",
        session_id="investigation-session",
        metadata={
            "investigation_type": "corruption_detection",
            "data_sources": ["contracts", "expenses"],
            "priority": "high"
        },
        trace_id="trace-tiradentes-123"
    )


@pytest.fixture
def tiradentes_agent(mock_data_service, mock_ai_service):
    """Create Tiradentes agent with mocked dependencies."""
    with patch("src.agents.tiradentes.DataService", return_value=mock_data_service), \
         patch("src.agents.tiradentes.AIService", return_value=mock_ai_service):
        
        agent = TiradentesAgent(
            anomaly_threshold=0.7,
            correlation_threshold=0.8,
            max_investigation_depth=3
        )
        return agent


class TestTiradentesAgent:
    """Test suite for Tiradentes (Investigation Agent)."""
    
    @pytest.mark.unit
    def test_agent_initialization(self, tiradentes_agent):
        """Test Tiradentes agent initialization."""
        assert tiradentes_agent.name == "Tiradentes"
        assert tiradentes_agent.anomaly_threshold == 0.7
        assert tiradentes_agent.correlation_threshold == 0.8
        assert tiradentes_agent.max_investigation_depth == 3
        
        # Check capabilities
        expected_capabilities = [
            "anomaly_detection",
            "corruption_analysis", 
            "investigation_planning",
            "pattern_recognition",
            "risk_assessment"
        ]
        
        for capability in expected_capabilities:
            assert capability in tiradentes_agent.capabilities
    
    @pytest.mark.unit
    async def test_detect_contract_anomalies(self, tiradentes_agent, agent_context):
        """Test contract anomaly detection."""
        request = InvestigationRequest(
            investigation_type="contract_anomalies",
            data_sources=["contracts"],
            parameters={
                "period_start": "2024-01-01",
                "period_end": "2024-12-31",
                "min_value": 100000.0
            }
        )
        
        message = AgentMessage(
            sender="master_agent",
            recipient="Tiradentes",
            action="detect_anomalies",
            payload=request.dict()
        )
        
        response = await tiradentes_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "anomalies" in response.result
        assert len(response.result["anomalies"]) > 0
        
        # Check specific anomaly
        price_anomaly = next(
            (a for a in response.result["anomalies"] if a["type"] == "price_anomaly"),
            None
        )
        assert price_anomaly is not None
        assert price_anomaly["severity"] == "high"
        assert price_anomaly["confidence"] > 0.9
    
    @pytest.mark.unit
    async def test_investigate_supplier_patterns(self, tiradentes_agent, agent_context):
        """Test supplier pattern investigation."""
        message = AgentMessage(
            sender="analyst_agent",
            recipient="Tiradentes",
            action="investigate_supplier",
            payload={
                "supplier_cnpj": "12.345.678/0001-90",
                "investigation_scope": "comprehensive",
                "include_network_analysis": True
            }
        )
        
        response = await tiradentes_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "supplier_analysis" in response.result
        assert "risk_indicators" in response.result
        assert "network_connections" in response.result
        
        # Verify comprehensive analysis
        supplier_analysis = response.result["supplier_analysis"]
        assert "contratos_count" in supplier_analysis
        assert "valor_total" in supplier_analysis
        assert "concentration_ratio" in supplier_analysis
    
    @pytest.mark.unit
    async def test_corruption_risk_assessment(self, tiradentes_agent, agent_context):
        """Test corruption risk assessment."""
        message = AgentMessage(
            sender="master_agent",
            recipient="Tiradentes",
            action="assess_corruption_risk",
            payload={
                "target_entities": ["12.345.678/0001-90"],
                "analysis_period": "2024-01-01:2024-12-31",
                "include_predictions": True
            }
        )
        
        response = await tiradentes_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "risk_assessment" in response.result
        assert "corruption_indicators" in response.result
        
        risk_assessment = response.result["risk_assessment"]
        assert risk_assessment["risk_level"] == "high"
        assert risk_assessment["confidence"] > 0.8
        assert len(risk_assessment["indicators"]) > 0
    
    @pytest.mark.unit
    async def test_investigation_planning(self, tiradentes_agent, agent_context):
        """Test investigation plan creation."""
        message = AgentMessage(
            sender="master_agent", 
            recipient="Tiradentes",
            action="create_investigation_plan",
            payload={
                "investigation_objective": "Analyze procurement irregularities in Ministry of Education",
                "available_resources": ["contracts_api", "expenses_api", "suppliers_registry"],
                "urgency_level": "high",
                "expected_timeline_days": 30
            }
        )
        
        response = await tiradentes_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "investigation_plan" in response.result
        
        plan = response.result["investigation_plan"]
        assert "phases" in plan
        assert "timeline" in plan
        assert "required_agents" in plan
        assert "success_criteria" in plan
        assert len(plan["phases"]) > 0
    
    @pytest.mark.unit
    async def test_evidence_collection(self, tiradentes_agent, agent_context):
        """Test evidence collection for investigations."""
        message = AgentMessage(
            sender="reporter_agent",
            recipient="Tiradentes", 
            action="collect_evidence",
            payload={
                "investigation_id": "inv-001",
                "target_contracts": ["12345", "67890"],
                "evidence_types": ["financial", "procedural", "temporal"],
                "verification_level": "high"
            }
        )
        
        response = await tiradentes_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "evidence_collection" in response.result
        
        evidence = response.result["evidence_collection"]
        assert "financial_evidence" in evidence
        assert "procedural_evidence" in evidence
        assert "temporal_evidence" in evidence
        assert "verification_status" in evidence
    
    @pytest.mark.unit
    async def test_anomaly_threshold_configuration(self, mock_data_service, mock_ai_service):
        """Test agent with different anomaly thresholds."""
        with patch("src.agents.tiradentes.DataService", return_value=mock_data_service), \
             patch("src.agents.tiradentes.AIService", return_value=mock_ai_service):
            
            # High threshold agent (strict)
            strict_agent = TiradentesAgent(anomaly_threshold=0.95)
            
            # Low threshold agent (sensitive) 
            sensitive_agent = TiradentesAgent(anomaly_threshold=0.5)
            
            assert strict_agent.anomaly_threshold == 0.95
            assert sensitive_agent.anomaly_threshold == 0.5
    
    @pytest.mark.unit
    async def test_investigation_depth_limits(self, tiradentes_agent, agent_context):
        """Test investigation depth limiting."""
        # Create deep investigation request
        message = AgentMessage(
            sender="master_agent",
            recipient="Tiradentes",
            action="deep_investigation",
            payload={
                "target": "supplier_network",
                "max_depth": 5,  # Exceeds agent limit of 3
                "follow_connections": True
            }
        )
        
        response = await tiradentes_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        # Verify depth was limited
        assert response.result["investigation_metadata"]["actual_depth"] <= 3
        assert response.result["investigation_metadata"]["depth_limited"] is True
    
    @pytest.mark.unit
    async def test_error_handling(self, tiradentes_agent, agent_context):
        """Test error handling in investigation processes."""
        # Mock service to raise exception
        tiradentes_agent.data_service.get_contracts.side_effect = Exception("API Error")
        
        message = AgentMessage(
            sender="test",
            recipient="Tiradentes",
            action="detect_anomalies",
            payload={"investigation_type": "contract_anomalies"}
        )
        
        response = await tiradentes_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.ERROR
        assert response.error is not None
        assert "API Error" in response.error
    
    @pytest.mark.unit
    async def test_concurrent_investigations(self, tiradentes_agent):
        """Test handling multiple concurrent investigations."""
        contexts = [
            AgentContext(investigation_id=f"inv-{i}")
            for i in range(3)
        ]
        
        messages = [
            AgentMessage(
                sender="master",
                recipient="Tiradentes",
                action="detect_anomalies",
                payload={"investigation_type": f"type_{i}"}
            )
            for i in range(3)
        ]
        
        # Process concurrently
        import asyncio
        responses = await asyncio.gather(*[
            tiradentes_agent.process(msg, ctx)
            for msg, ctx in zip(messages, contexts)
        ])
        
        assert len(responses) == 3
        assert all(r.status == AgentStatus.COMPLETED for r in responses)
        assert len(set(r.metadata.get("investigation_id") for r in responses)) == 3
    
    @pytest.mark.unit
    async def test_pattern_correlation_analysis(self, tiradentes_agent, agent_context):
        """Test pattern correlation analysis."""
        message = AgentMessage(
            sender="analyst_agent",
            recipient="Tiradentes", 
            action="analyze_correlations",
            payload={
                "data_dimensions": ["temporal", "financial", "geographical"],
                "correlation_methods": ["pearson", "spearman", "kendall"],
                "significance_level": 0.05
            }
        )
        
        response = await tiradentes_agent.process(message, agent_context)
        
        assert response.status == AgentStatus.COMPLETED
        assert "correlation_analysis" in response.result
        
        correlations = response.result["correlation_analysis"]
        assert "temporal_patterns" in correlations
        assert "financial_patterns" in correlations
        assert "geographical_patterns" in correlations
        assert "cross_correlations" in correlations


class TestInvestigationRequest:
    """Test InvestigationRequest model."""
    
    @pytest.mark.unit
    def test_request_creation(self):
        """Test creating investigation request."""
        request = InvestigationRequest(
            investigation_type="corruption_detection",
            data_sources=["contracts", "expenses"],
            parameters={
                "period": "2024-01-01:2024-12-31",
                "threshold": 0.8
            },
            priority="high"
        )
        
        assert request.investigation_type == "corruption_detection"
        assert len(request.data_sources) == 2
        assert request.parameters["threshold"] == 0.8
        assert request.priority == "high"
    
    @pytest.mark.unit
    def test_request_validation(self):
        """Test request validation."""
        # Valid request
        valid_request = InvestigationRequest(
            investigation_type="anomaly_detection",
            data_sources=["contracts"]
        )
        assert valid_request.investigation_type == "anomaly_detection"
        
        # Test with invalid investigation type
        with pytest.raises(ValueError):
            InvestigationRequest(
                investigation_type="invalid_type",
                data_sources=["contracts"]
            )


class TestAnomalyReport:
    """Test AnomalyReport model."""
    
    @pytest.mark.unit
    def test_report_creation(self):
        """Test creating anomaly report."""
        report = AnomalyReport(
            anomaly_id="anomaly-001",
            anomaly_type="price_deviation",
            severity="high",
            confidence_score=0.92,
            description="Contract price significantly above market rate",
            affected_entities=["contract-123"],
            evidence={
                "market_rate": 100000.0,
                "contract_rate": 400000.0,
                "deviation": 3.0
            },
            recommendations=[
                "Review contract terms",
                "Investigate supplier background",
                "Check approval process"
            ]
        )
        
        assert report.anomaly_id == "anomaly-001"
        assert report.severity == "high"
        assert report.confidence_score == 0.92
        assert len(report.recommendations) == 3
        assert report.evidence["deviation"] == 3.0
    
    @pytest.mark.unit
    def test_report_priority_calculation(self):
        """Test report priority calculation."""
        high_severity = AnomalyReport(
            anomaly_id="high-001",
            anomaly_type="corruption_indicator",
            severity="high",
            confidence_score=0.95
        )
        
        medium_severity = AnomalyReport(
            anomaly_id="medium-001", 
            anomaly_type="price_anomaly",
            severity="medium",
            confidence_score=0.75
        )
        
        assert high_severity.calculate_priority() > medium_severity.calculate_priority()


class TestCorruptionIndicator:
    """Test CorruptionIndicator model."""
    
    @pytest.mark.unit
    def test_indicator_creation(self):
        """Test creating corruption indicator."""
        indicator = CorruptionIndicator(
            indicator_type="supplier_monopoly",
            risk_level="high",
            confidence=0.88,
            description="Single supplier dominates procurement",
            evidence_points=[
                "70% of contracts with same supplier",
                "No competitive bidding records",
                "Supplier connections to officials"
            ],
            impact_assessment="Potential loss of $2M annually"
        )
        
        assert indicator.indicator_type == "supplier_monopoly"
        assert indicator.risk_level == "high"
        assert indicator.confidence == 0.88
        assert len(indicator.evidence_points) == 3
    
    @pytest.mark.unit
    def test_indicator_risk_scoring(self):
        """Test corruption indicator risk scoring."""
        high_risk = CorruptionIndicator(
            indicator_type="bid_rigging",
            risk_level="critical",
            confidence=0.95
        )
        
        low_risk = CorruptionIndicator(
            indicator_type="minor_procedural",
            risk_level="low", 
            confidence=0.60
        )
        
        assert high_risk.calculate_risk_score() > low_risk.calculate_risk_score()
        assert high_risk.calculate_risk_score() > 0.9  # Should be very high
        assert low_risk.calculate_risk_score() < 0.4   # Should be low