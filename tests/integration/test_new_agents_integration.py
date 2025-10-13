"""
Integration tests for José Bonifácio and Maria Quitéria agents.
Tests agent interactions, coordination, and complete workflows.
"""

import asyncio
from datetime import datetime
from unittest.mock import patch
from uuid import uuid4

import pytest

from src.agents import (
    AgentContext,
    AgentMessage,
    BonifacioAgent,
    MariaQuiteriaAgent,
    MasterAgent,
    ZumbiAgent,
)
from src.services.investigation_service import InvestigationService


@pytest.fixture
async def investigation_service():
    """Create investigation service for tests."""
    service = InvestigationService()
    return service


@pytest.fixture
def investigation_context():
    """Create investigation context for integration tests."""
    return AgentContext(
        investigation_id=str(uuid4()),
        user_id="integration-tester",
        session_id=str(uuid4()),
        metadata={
            "test_type": "integration",
            "agents": ["bonifacio", "maria_quiteria"],
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


class TestBonifacioMariaQuiteriaIntegration:
    """Integration tests for Bonifácio and Maria Quitéria agents."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_policy_security_compliance_workflow(self, investigation_context):
        """Test complete workflow: policy analysis + security compliance check."""
        # Initialize agents
        bonifacio = BonifacioAgent()
        maria_quiteria = MariaQuiteriaAgent()

        # Step 1: Analyze policy with Bonifácio
        policy_message = AgentMessage(
            type="policy_analysis",
            data={
                "policy_name": "Sistema Nacional de Dados Sensíveis",
                "policy_area": "security",
                "budget_data": {"planned": 10_000_000, "executed": 9_500_000},
            },
            sender="master",
            metadata={"step": "policy_analysis"},
        )

        policy_response = await bonifacio.process(policy_message, investigation_context)

        assert policy_response.success is True
        assert "policy_evaluation" in policy_response.data

        # Step 2: Check security compliance based on policy
        security_message = AgentMessage(
            type="security_audit",
            data={
                "system_name": "Sistema Nacional de Dados Sensíveis",
                "policy_requirements": policy_response.data["policy_evaluation"],
                "compliance_frameworks": ["LGPD", "ISO27001"],
            },
            sender="bonifacio",
            metadata={"step": "security_verification"},
        )

        security_response = await maria_quiteria.process(
            security_message, investigation_context
        )

        assert security_response.success is True
        assert "security_assessment" in security_response.data

        # Verify cross-agent data flow
        compliance_status = security_response.data["security_assessment"][
            "compliance_status"
        ]
        assert "LGPD" in compliance_status
        assert compliance_status["LGPD"] > 0.7  # Policy should ensure good compliance

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multi_agent_investigation_with_new_agents(
        self, investigation_service, investigation_context
    ):
        """Test complete investigation involving all agents including new ones."""

        # Mock external data sources
        with patch("src.services.data_service.TransparencyAPIClient") as mock_api:
            mock_api.return_value.search_contracts.return_value = [
                {
                    "id": "contract-123",
                    "valor": 5_000_000,
                    "objeto": "Sistema de Segurança Digital com Compliance LGPD",
                    "fornecedor": "TechSec Solutions",
                    "modalidade": "Pregão Eletrônico",
                    "data_assinatura": "2024-01-15",
                }
            ]

            # Create investigation request
            investigation_request = {
                "query": "Investigar contrato de sistema de segurança com compliance",
                "investigation_type": "comprehensive",
                "include_agents": ["zumbi", "bonifacio", "maria_quiteria"],
            }

            # Execute investigation
            result = await investigation_service.create_investigation(
                request=investigation_request, user_id=investigation_context.user_id
            )

            investigation_id = result["investigation_id"]

            # Wait for investigation to complete (with timeout)
            max_attempts = 30
            for _ in range(max_attempts):
                status = await investigation_service.get_investigation_status(
                    investigation_id
                )
                if status["status"] in ["completed", "failed"]:
                    break
                await asyncio.sleep(1)

            # Verify investigation results
            assert status["status"] == "completed"
            assert "agents_involved" in status

            # Check that all requested agents participated
            agents_involved = status["agents_involved"]
            assert "zumbi" in agents_involved
            assert "bonifacio" in agents_involved
            assert "maria_quiteria" in agents_involved

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_security_driven_policy_recommendations(self, investigation_context):
        """Test workflow: security issues trigger policy recommendations."""

        bonifacio = BonifacioAgent()
        maria_quiteria = MariaQuiteriaAgent()

        # Step 1: Security audit finds vulnerabilities
        security_audit_msg = AgentMessage(
            type="security_audit",
            data={
                "system_name": "Portal Transparência",
                "audit_scope": "comprehensive",
            },
            sender="master",
            metadata={},
        )

        security_result = await maria_quiteria.process(
            security_audit_msg, investigation_context
        )

        # Step 2: Based on security findings, get policy recommendations
        policy_request_msg = AgentMessage(
            type="policy_analysis",
            data={
                "policy_name": "Política de Segurança Digital",
                "security_findings": security_result.data["security_assessment"],
                "focus_area": "security_improvements",
            },
            sender="maria_quiteria",
            metadata={"triggered_by": "security_audit"},
        )

        policy_result = await bonifacio.process(
            policy_request_msg, investigation_context
        )

        # Verify recommendations address security issues
        recommendations = policy_result.data["strategic_recommendations"]
        assert len(recommendations) > 0

        # At least one recommendation should address security
        security_related = any(
            "security" in rec.get("area", "").lower()
            or "compliance" in rec.get("area", "").lower()
            for rec in recommendations
        )
        assert security_related is True

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_parallel_agent_execution(self, investigation_context):
        """Test parallel execution of Bonifácio and Maria Quitéria."""

        bonifacio = BonifacioAgent()
        maria_quiteria = MariaQuiteriaAgent()

        # Create messages for parallel execution
        policy_msg = AgentMessage(
            type="policy_analysis",
            data="Programa Nacional de Cibersegurança",
            sender="master",
            metadata={},
        )

        security_msg = AgentMessage(
            type="security_audit",
            data="Sistema Nacional de Cibersegurança",
            sender="master",
            metadata={},
        )

        # Execute agents in parallel
        start_time = datetime.utcnow()

        policy_task = asyncio.create_task(
            bonifacio.process(policy_msg, investigation_context)
        )
        security_task = asyncio.create_task(
            maria_quiteria.process(security_msg, investigation_context)
        )

        # Wait for both to complete
        policy_response, security_response = await asyncio.gather(
            policy_task, security_task
        )

        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()

        # Verify both completed successfully
        assert policy_response.success is True
        assert security_response.success is True

        # Verify parallel execution (should take less time than sequential)
        # Both agents have ~2-3 second simulated delays
        assert execution_time < 5  # Should complete in under 5 seconds if parallel

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_agent_error_recovery(self, investigation_context):
        """Test error handling and recovery between agents."""

        bonifacio = BonifacioAgent()
        maria_quiteria = MariaQuiteriaAgent()

        # Force an error in Bonifácio
        with patch.object(
            bonifacio,
            "_evaluate_policy",
            side_effect=Exception("Policy database error"),
        ):
            policy_msg = AgentMessage(
                type="policy_analysis",
                data={"policy_name": "Test Policy"},
                sender="master",
                metadata={},
            )

            policy_response = await bonifacio.process(policy_msg, investigation_context)
            assert policy_response.success is False

        # Maria Quitéria should still work independently
        security_msg = AgentMessage(
            type="security_audit",
            data={"system_name": "Test System"},
            sender="master",
            metadata={"note": "bonifacio_failed"},
        )

        security_response = await maria_quiteria.process(
            security_msg, investigation_context
        )
        assert security_response.success is True

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_comprehensive_compliance_workflow(self, investigation_context):
        """Test complete compliance verification workflow."""

        # This tests the full cycle:
        # 1. Zumbi detects anomaly
        # 2. Maria Quitéria performs security audit
        # 3. Bonifácio analyzes policy compliance
        # 4. Results are consolidated

        zumbi = ZumbiAgent()
        maria_quiteria = MariaQuiteriaAgent()
        bonifacio = BonifacioAgent()

        # Step 1: Anomaly detection
        anomaly_msg = AgentMessage(
            type="analyze",
            data={
                "contract_data": {
                    "valor": 10_000_000,
                    "objeto": "Sistema de Compliance Integrado",
                    "fornecedor": "ComplianceTech",
                }
            },
            sender="master",
            metadata={},
        )

        with patch("src.agents.zumbi.ZumbiAgent._fetch_contract_details") as mock_fetch:
            mock_fetch.return_value = {
                "id": "123",
                "valor": 10_000_000,
                "objeto": "Sistema de Compliance Integrado",
            }

            anomaly_response = await zumbi.process(anomaly_msg, investigation_context)

        # Step 2: Security audit based on anomaly
        if anomaly_response.data.get("anomalies_detected", 0) > 0:
            security_msg = AgentMessage(
                type="security_audit",
                data={
                    "system_name": "Sistema de Compliance Integrado",
                    "triggered_by": "anomaly_detection",
                    "anomaly_details": anomaly_response.data,
                },
                sender="zumbi",
                metadata={},
            )

            security_response = await maria_quiteria.process(
                security_msg, investigation_context
            )

            # Step 3: Policy compliance check
            policy_msg = AgentMessage(
                type="policy_analysis",
                data={
                    "policy_name": "Política de Compliance e Segurança",
                    "security_assessment": security_response.data,
                    "contract_value": 10_000_000,
                },
                sender="maria_quiteria",
                metadata={},
            )

            policy_response = await bonifacio.process(policy_msg, investigation_context)

            # Verify complete workflow
            assert anomaly_response.success is True
            assert security_response.success is True
            assert policy_response.success is True

            # Results should be interconnected
            assert "security_assessment" in security_response.data
            assert "policy_evaluation" in policy_response.data


class TestAgentCoordinationPatterns:
    """Test various agent coordination patterns."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_sequential_agent_pipeline(self, investigation_context):
        """Test sequential processing pipeline with data passing."""

        agents = [ZumbiAgent(), MariaQuiteriaAgent(), BonifacioAgent()]

        # Initial data
        current_data = {
            "investigation_subject": "Contrato de Software de Segurança",
            "initial_value": 5_000_000,
        }

        # Process through pipeline
        for i, agent in enumerate(agents):
            message = AgentMessage(
                type="analyze",
                data=current_data,
                sender=f"agent_{i-1}" if i > 0 else "master",
                metadata={"pipeline_step": i},
            )

            response = await agent.process(message, investigation_context)
            assert response.success is True

            # Pass data forward
            current_data.update({f"{agent.name}_result": response.data})

        # Verify all agents contributed
        assert "InvestigatorAgent_result" in current_data
        assert "MariaQuiteriaAgent_result" in current_data
        assert "BonifacioAgent_result" in current_data

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_fan_out_fan_in_pattern(self, investigation_context):
        """Test fan-out/fan-in pattern with result aggregation."""

        # Master coordinates multiple specialized agents
        master = MasterAgent()

        # Create complex investigation request
        investigation_msg = AgentMessage(
            type="investigate",
            data={
                "query": "Análise completa de contrato com aspectos de segurança e compliance",
                "contract_id": "complex-123",
                "include_analysis": ["anomaly", "security", "policy"],
            },
            sender="user",
            metadata={},
        )

        # Mock the investigation service to control agent responses
        with patch("src.agents.abaporu.InvestigationService") as mock_service:
            mock_service.return_value.create_investigation.return_value = {
                "investigation_id": "test-123",
                "status": "completed",
            }

            response = await master.process(investigation_msg, investigation_context)

            assert response.success is True
            assert "investigation_id" in response.data
