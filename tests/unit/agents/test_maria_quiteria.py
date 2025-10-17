"""
Unit tests for Maria Quitéria Agent - Security auditor and system guardian.
Tests security auditing, threat detection, and compliance verification capabilities.
"""

from unittest.mock import patch

import pytest

from src.agents.deodoro import AgentContext, AgentMessage
from src.agents.maria_quiteria import (
    ComplianceFramework,
    MariaQuiteriaAgent,
    SecurityThreatLevel,
)


@pytest.fixture
def agent_context():
    """Test agent context for security analysis."""
    return AgentContext(
        investigation_id="security-audit-001",
        user_id="security-admin",
        session_id="security-session",
        metadata={
            "analysis_type": "security_audit",
            "scope": "system_wide",
            "compliance_required": ["LGPD", "ISO27001"],
        },
        trace_id="trace-maria-789",
    )


@pytest.fixture
def maria_quiteria_agent():
    """Create Maria Quitéria agent."""
    agent = MariaQuiteriaAgent()
    return agent


class TestMariaQuiteriaAgent:
    """Test suite for Maria Quitéria (Security Agent)."""

    @pytest.mark.unit
    def test_agent_initialization(self, maria_quiteria_agent):
        """Test Maria Quitéria agent initialization."""
        assert maria_quiteria_agent.name == "MariaQuiteriaAgent"
        assert "security_audit" in maria_quiteria_agent.capabilities
        assert "threat_detection" in maria_quiteria_agent.capabilities
        assert "compliance_verification" in maria_quiteria_agent.capabilities
        assert "intrusion_detection" in maria_quiteria_agent.capabilities
        assert len(maria_quiteria_agent.capabilities) == 8

        # Check security configurations
        assert maria_quiteria_agent.security_config["max_failed_attempts"] == 5
        assert maria_quiteria_agent.security_config["threat_detection_threshold"] == 0.7

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_security_analysis_with_dict(
        self, maria_quiteria_agent, agent_context
    ):
        """Test security analysis with dictionary input."""
        message = AgentMessage(
            type="security_audit",
            data={
                "system_name": "Production Server",
                "audit_scope": "full_system",
                "compliance_frameworks": ["LGPD", "ISO27001"],
            },
            sender="security_manager",
            metadata={},
        )

        response = await maria_quiteria_agent.process(message, agent_context)

        assert response.success is True
        assert response.response_type == "security_analysis"
        assert "security_assessment" in response.data

        assessment = response.data["security_assessment"]
        assert "overall_threat_level" in assessment
        assert "security_score" in assessment
        assert "vulnerabilities_found" in assessment
        assert "compliance_status" in assessment

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_security_analysis_with_string(
        self, maria_quiteria_agent, agent_context
    ):
        """Test security analysis with simple string input."""
        message = AgentMessage(
            type="security_audit",
            data="Check system security status",
            sender="admin",
            metadata={},
        )

        response = await maria_quiteria_agent.process(message, agent_context)

        assert response.success is True
        assert response.data is not None

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_threat_level_classification(
        self, maria_quiteria_agent, agent_context
    ):
        """Test threat level classification."""
        message = AgentMessage(
            type="security_audit",
            data={"system_name": "Test System"},
            sender="test",
            metadata={},
        )

        response = await maria_quiteria_agent.process(message, agent_context)

        threat_level = response.data["security_assessment"]["overall_threat_level"]
        assert threat_level in ["minimal", "low", "medium", "high", "critical"]

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_compliance_verification(self, maria_quiteria_agent, agent_context):
        """Test compliance verification for multiple frameworks."""
        message = AgentMessage(
            type="security_audit",
            data={
                "system_name": "Data Processing System",
                "compliance_frameworks": ["LGPD", "ISO27001", "OWASP"],
            },
            sender="compliance_officer",
            metadata={},
        )

        response = await maria_quiteria_agent.process(message, agent_context)

        compliance_status = response.data["security_assessment"]["compliance_status"]
        assert "LGPD" in compliance_status
        assert "ISO27001" in compliance_status
        assert "OWASP" in compliance_status

        # All compliance scores should be between 0 and 1
        for framework, score in compliance_status.items():
            assert 0 <= score <= 1

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_vulnerability_detection(self, maria_quiteria_agent, agent_context):
        """Test vulnerability detection and reporting."""
        message = AgentMessage(
            type="vulnerability_scan",
            data={"system_name": "Web Application", "scan_depth": "comprehensive"},
            sender="security_scanner",
            metadata={},
        )

        response = await maria_quiteria_agent.process(message, agent_context)

        # Should have vulnerability count
        vulnerabilities = response.data.get("security_assessment", {}).get(
            "vulnerabilities_found", 0
        )
        assert isinstance(vulnerabilities, int)
        assert vulnerabilities >= 0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_security_recommendations(self, maria_quiteria_agent, agent_context):
        """Test security recommendations generation."""
        message = AgentMessage(
            type="security_audit",
            data={"system_name": "Corporate Network"},
            sender="ciso",
            metadata={},
        )

        response = await maria_quiteria_agent.process(message, agent_context)

        recommendations = response.data.get("recommendations", [])
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # Check recommendation quality
        for rec in recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 10  # Non-trivial recommendation

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_intrusion_detection_mode(self, maria_quiteria_agent, agent_context):
        """Test intrusion detection functionality."""
        message = AgentMessage(
            type="intrusion_detection",
            data={
                "network_data": [
                    {"src_ip": "192.168.1.100", "dst_port": 22, "packets": 1000},
                    {"src_ip": "10.0.0.50", "dst_port": 80, "packets": 500},
                ],
                "time_window_minutes": 30,
            },
            sender="network_monitor",
            metadata={},
        )

        # Mock the detect_intrusions method for this test
        mock_result = {
            "intrusions_detected": 1,
            "threat_level": "medium",
            "suspicious_ips": ["192.168.1.100"],
        }

        with patch.object(
            maria_quiteria_agent, "detect_intrusions", return_value=mock_result
        ) as mock_detect:
            response = await maria_quiteria_agent.process(message, agent_context)

            assert response.success is True
            assert mock_detect.called
            mock_detect.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_security_score_calculation(
        self, maria_quiteria_agent, agent_context
    ):
        """Test security score calculation."""
        message = AgentMessage(
            type="security_audit",
            data={"system_name": "Secure System"},
            sender="auditor",
            metadata={},
        )

        response = await maria_quiteria_agent.process(message, agent_context)

        security_score = response.data["security_assessment"]["security_score"]
        assert isinstance(security_score, float)
        assert 0 <= security_score <= 1

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_analysis_confidence(self, maria_quiteria_agent, agent_context):
        """Test analysis confidence scoring."""
        message = AgentMessage(
            type="security_audit",
            data={"system_name": "Test Environment"},
            sender="qa_team",
            metadata={},
        )

        response = await maria_quiteria_agent.process(message, agent_context)

        confidence = response.data.get("analysis_confidence", 0)
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1
        assert confidence >= 0.85  # High confidence for security assessments

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_error_handling(self, maria_quiteria_agent, agent_context):
        """Test error handling for invalid requests."""
        message = AgentMessage(
            type="invalid_security_action",
            data={"invalid": "data"},
            sender="test",
            metadata={},
        )

        # Mock to force an error
        with patch.object(
            maria_quiteria_agent,
            "_perform_comprehensive_security_analysis",
            side_effect=Exception("Security analysis failed"),
        ):
            response = await maria_quiteria_agent.process(message, agent_context)

            assert response.success is False
            assert response.response_type == "error"
            assert "error" in response.data


class TestSecurityThreatLevel:
    """Test SecurityThreatLevel enum."""

    @pytest.mark.unit
    def test_threat_levels(self):
        """Test threat level definitions."""
        assert SecurityThreatLevel.MINIMAL.value == "minimal"
        assert SecurityThreatLevel.LOW.value == "low"
        assert SecurityThreatLevel.MEDIUM.value == "medium"
        assert SecurityThreatLevel.HIGH.value == "high"
        assert SecurityThreatLevel.CRITICAL.value == "critical"


class TestComplianceFramework:
    """Test ComplianceFramework enum."""

    @pytest.mark.unit
    def test_compliance_frameworks(self):
        """Test compliance framework definitions."""
        assert ComplianceFramework.LGPD.value == "lgpd"
        assert ComplianceFramework.ISO27001.value == "iso27001"
        assert ComplianceFramework.OWASP.value == "owasp"
        assert ComplianceFramework.GDPR.value == "gdpr"
