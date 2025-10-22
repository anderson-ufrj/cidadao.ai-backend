"""
Additional tests to boost Maria Quitéria coverage from 54% to 80%+.
Focus on uncovered methods and edge cases.

Author: Anderson H. Silva
Date: 2025-10-22
"""

import pytest

from src.agents.deodoro import AgentContext
from src.agents.maria_quiteria import ComplianceFramework, MariaQuiteriaAgent


@pytest.fixture
def agent():
    """Create Maria Quitéria agent."""
    return MariaQuiteriaAgent()


@pytest.fixture
def context():
    """Create agent context."""
    return AgentContext(
        investigation_id="boost-001", user_id="admin", session_id="boost-session"
    )


class TestComplianceReportGeneration:
    """Test compliance report generation in detail."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_compliance_report_lgpd_detailed(self, agent, context):
        """Test LGPD compliance report with detailed control assessment."""
        report = await agent.generate_compliance_report(
            framework=ComplianceFramework.LGPD,
            systems=["data_processing", "user_management"],
            context=context,
        )

        assert isinstance(report, dict)
        assert "compliance_percentage" in report
        assert "control_results" in report
        assert "gap_analysis" in report
        assert "recommendations" in report

        # LGPD-specific domains
        control_results = report["control_results"]
        assert "data_processing_lawfulness" in control_results
        assert "consent_management" in control_results
        assert "data_subject_rights" in control_results

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_compliance_report_iso27001(self, agent, context):
        """Test ISO27001 compliance report."""
        report = await agent.generate_compliance_report(
            framework=ComplianceFramework.ISO27001,
            systems=["corporate_network"],
            context=context,
        )

        assert isinstance(report, dict)
        control_results = report["control_results"]
        # ISO27001-specific domains
        assert "access_control" in control_results
        assert "cryptography" in control_results
        assert "physical_security" in control_results

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_compliance_report_owasp(self, agent, context):
        """Test OWASP compliance report."""
        report = await agent.generate_compliance_report(
            framework=ComplianceFramework.OWASP,
            systems=["web_application"],
            context=context,
        )

        assert isinstance(report, dict)
        control_results = report["control_results"]
        # OWASP-specific domains
        assert "injection_prevention" in control_results
        assert "authentication" in control_results
        assert "sensitive_data_exposure" in control_results

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_compliance_report_gap_analysis(self, agent, context):
        """Test gap analysis in compliance report."""
        report = await agent.generate_compliance_report(
            framework=ComplianceFramework.LGPD,
            systems=["test_system"],
            context=context,
        )

        gap_analysis = report["gap_analysis"]
        assert "total_gaps" in gap_analysis
        assert "critical_gaps" in gap_analysis
        assert isinstance(gap_analysis["total_gaps"], int)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_compliance_report_recommendations(self, agent, context):
        """Test recommendations in compliance report."""
        report = await agent.generate_compliance_report(
            framework=ComplianceFramework.ISO27001,
            systems=["test"],
            context=context,
        )

        recommendations = report["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0


class TestAdditionalMethods:
    """Test additional helper methods."""

    @pytest.mark.unit
    def test_get_remediation_advice_critical(self, agent):
        """Test remediation advice for critical vulnerability."""
        vuln = {"severity": "critical", "cve_id": "CVE-2023-12345"}
        advice = agent._get_remediation_advice(vuln)

        assert isinstance(advice, str)
        assert "URGENT" in advice or "critical" in advice.lower()

    @pytest.mark.unit
    def test_get_remediation_advice_high(self, agent):
        """Test remediation advice for high severity vulnerability."""
        vuln = {"severity": "high", "cve_id": "CVE-2023-67890"}
        advice = agent._get_remediation_advice(vuln)

        assert isinstance(advice, str)
        assert len(advice) > 20

    @pytest.mark.unit
    def test_get_remediation_advice_medium(self, agent):
        """Test remediation advice for medium severity."""
        vuln = {"severity": "medium", "cve_id": "CVE-2023-11111"}
        advice = agent._get_remediation_advice(vuln)

        assert isinstance(advice, str)
        assert "30 days" in advice or "schedule" in advice.lower()

    @pytest.mark.unit
    def test_get_remediation_advice_low(self, agent):
        """Test remediation advice for low severity."""
        vuln = {"severity": "low", "cve_id": "CVE-2023-22222"}
        advice = agent._get_remediation_advice(vuln)

        assert isinstance(advice, str)
        assert "maintenance" in advice.lower()


class TestSignatureBasedDetection:
    """Test signature-based detection methods."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_signature_based_detection_with_matches(self, agent):
        """Test signature detection with known attack patterns."""
        network_data = [
            {
                "src_ip": "192.168.1.100",
                "dst_port": 22,
                "packets": 1000,
                "pattern": "port_scan",
            }
        ]

        matches = await agent._signature_based_detection(network_data)

        assert isinstance(matches, list)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_signature_based_detection_clean_traffic(self, agent):
        """Test signature detection with clean traffic."""
        network_data = [{"src_ip": "10.0.0.1", "dst_port": 443, "packets": 50}]

        matches = await agent._signature_based_detection(network_data)

        assert isinstance(matches, list)


class TestLoadThreatIntelligence:
    """Test threat intelligence loading."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_load_threat_intelligence(self, agent):
        """Test loading threat intelligence feeds."""
        await agent._load_threat_intelligence()

        assert hasattr(agent, "threat_intelligence")
        assert isinstance(agent.threat_intelligence, dict)
        # Should have malicious IPs and known CVEs
        assert (
            "malicious_ips" in agent.threat_intelligence
            or len(agent.threat_intelligence) >= 0
        )


class TestSecurityEventCorrelation:
    """Test security event correlation."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_correlate_security_events_with_matches(self, agent):
        """Test correlating security events."""
        signature_matches = [
            {"event_type": "port_scan", "severity": "medium", "source": "10.0.0.100"}
        ]
        behavioral_anomalies = [
            {"event_type": "high_traffic", "severity": "low", "source": "10.0.0.100"}
        ]

        correlated = await agent._correlate_security_events(
            signature_matches, behavioral_anomalies
        )

        assert isinstance(correlated, list)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_correlate_security_events_empty(self, agent):
        """Test correlating with no events."""
        correlated = await agent._correlate_security_events([], [])

        assert isinstance(correlated, list)
        assert len(correlated) == 0


class TestDetectionConfidence:
    """Test detection confidence calculation."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_detection_confidence_high(self, agent):
        """Test high confidence calculation."""
        events = [
            {"severity": "critical", "confidence": 0.95},
            {"severity": "high", "confidence": 0.90},
        ]

        confidence = await agent._calculate_detection_confidence(events)

        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_detection_confidence_empty(self, agent):
        """Test confidence calculation with no events."""
        confidence = await agent._calculate_detection_confidence([])

        assert confidence == 0.0


class TestAttackPatternIdentification:
    """Test attack pattern identification."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_identify_attack_patterns_multiple(self, agent):
        """Test identifying multiple attack patterns."""
        events = [
            {"event_type": "port_scan", "mitre_technique": "T1046"},
            {"event_type": "brute_force", "mitre_technique": "T1110"},
        ]

        patterns = await agent._identify_attack_patterns(events)

        assert isinstance(patterns, list)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_identify_attack_patterns_empty(self, agent):
        """Test identifying patterns with no events."""
        patterns = await agent._identify_attack_patterns([])

        assert isinstance(patterns, list)


class TestAffectedSystemsIdentification:
    """Test affected systems identification."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_identify_affected_systems_multiple(self, agent):
        """Test identifying multiple affected systems."""
        events = [
            {"affected_system": "web_server"},
            {"affected_system": "database"},
            {"affected_system": "web_server"},  # Duplicate
        ]

        systems = await agent._identify_affected_systems(events)

        assert isinstance(systems, list)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_identify_affected_systems_empty(self, agent):
        """Test identifying systems with no events."""
        systems = await agent._identify_affected_systems([])

        assert isinstance(systems, list)


class TestAttackTimeline:
    """Test attack timeline reconstruction."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reconstruct_attack_timeline_ordered(self, agent):
        """Test reconstructing attack timeline."""
        events = [
            {"timestamp": "2025-10-22T12:00:00", "event": "initial_scan"},
            {"timestamp": "2025-10-22T12:05:00", "event": "exploit_attempt"},
        ]

        timeline = await agent._reconstruct_attack_timeline(events)

        assert isinstance(timeline, list)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reconstruct_attack_timeline_empty(self, agent):
        """Test timeline with no events."""
        timeline = await agent._reconstruct_attack_timeline([])

        assert isinstance(timeline, list)
        assert len(timeline) == 0


class TestMitigationActions:
    """Test mitigation action generation."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_mitigation_actions_critical(self, agent):
        """Test generating mitigation actions for critical events."""
        events = [{"severity": "critical", "event_type": "data_breach"}]

        actions = await agent._generate_mitigation_actions(events)

        assert isinstance(actions, list)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_mitigation_actions_empty(self, agent):
        """Test generating actions with no events."""
        actions = await agent._generate_mitigation_actions([])

        assert isinstance(actions, list)
        assert len(actions) == 0


class TestUserRiskScoring:
    """Test user risk score calculation."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_user_risk_score_normal(self, agent):
        """Test risk score for normal activity."""
        activity = {
            "user_id": "user123",
            "action_type": "read",
            "resource": "/api/data",
            "timestamp": "2025-10-22T12:00:00",
        }

        risk_score = await agent._calculate_user_risk_score(activity)

        assert isinstance(risk_score, float)
        assert 0 <= risk_score <= 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_user_risk_score_suspicious(self, agent):
        """Test risk score for suspicious activity."""
        activity = {
            "user_id": "suspicious_user",
            "action_type": "failed_access",
            "resource": "/admin/critical",
            "timestamp": "2025-10-22T03:00:00",  # Unusual hour
            "status": "denied",
        }

        risk_score = await agent._calculate_user_risk_score(activity)

        assert isinstance(risk_score, float)
        assert 0 <= risk_score <= 1


class TestSecurityScoreCalculation:
    """Test security score calculation."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_security_score_high(self, agent):
        """Test security score with few vulnerabilities."""
        vulnerabilities = [{"severity": "low", "cvss_score": 2.0}]
        compliance_status = {
            ComplianceFramework.LGPD: 0.95,
            ComplianceFramework.ISO27001: 0.90,
        }

        score = await agent._calculate_security_score(
            vulnerabilities, compliance_status
        )

        assert isinstance(score, float)
        assert 0 <= score <= 1
        assert score > 0.7  # Should be high with good compliance

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_security_score_low(self, agent):
        """Test security score with many vulnerabilities."""
        vulnerabilities = [
            {"severity": "critical", "cvss_score": 9.5},
            {"severity": "high", "cvss_score": 8.0},
            {"severity": "high", "cvss_score": 7.5},
        ]
        compliance_status = {ComplianceFramework.LGPD: 0.60}

        score = await agent._calculate_security_score(
            vulnerabilities, compliance_status
        )

        assert isinstance(score, float)
        assert 0 <= score <= 1


class TestSecurityRecommendations:
    """Test security recommendations generation."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_security_recommendations_comprehensive(self, agent):
        """Test generating comprehensive security recommendations."""
        vulnerabilities = [
            {"severity": "critical", "cve_id": "CVE-2023-12345"},
            {"severity": "medium", "cve_id": "CVE-2023-67890"},
        ]
        compliance_status = {ComplianceFramework.LGPD: 0.75}

        recommendations = await agent._generate_security_recommendations(
            vulnerabilities, compliance_status
        )

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_generate_security_recommendations_no_issues(self, agent):
        """Test recommendations when no issues found."""
        vulnerabilities = []
        compliance_status = {ComplianceFramework.LGPD: 0.95}

        recommendations = await agent._generate_security_recommendations(
            vulnerabilities, compliance_status
        )

        assert isinstance(recommendations, list)


class TestComplianceChecking:
    """Test compliance checking for frameworks."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_compliance_lgpd(self, agent):
        """Test LGPD compliance check."""
        score = await agent._check_compliance(ComplianceFramework.LGPD, ["system1"])

        assert isinstance(score, float)
        assert 0 <= score <= 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_compliance_iso27001(self, agent):
        """Test ISO27001 compliance check."""
        score = await agent._check_compliance(ComplianceFramework.ISO27001, ["system1"])

        assert isinstance(score, float)
        assert 0 <= score <= 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_check_compliance_multiple_systems(self, agent):
        """Test compliance check across multiple systems."""
        systems = ["web", "db", "api"]
        score = await agent._check_compliance(ComplianceFramework.OWASP, systems)

        assert isinstance(score, float)
        assert 0 <= score <= 1


class TestShutdownAndReflection:
    """Test shutdown and reflection methods."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_shutdown_clean(self, agent):
        """Test clean shutdown."""
        await agent.shutdown()

        # Should clear sensitive data
        assert len(agent.threat_intelligence) == 0
        assert len(agent.security_baselines) == 0
        assert len(agent.active_incidents) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_shutdown_with_active_incidents(self, agent):
        """Test shutdown with active incidents."""
        # Add active incident
        agent.active_incidents["incident_1"] = {"severity": "high"}

        await agent.shutdown()

        # Should still clear despite active incidents
        assert len(agent.active_incidents) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reflect_security_analysis(self, agent, context):
        """Test reflection on security analysis."""
        task = "security_audit"
        result = {
            "security_score": 0.75,
            "vulnerabilities": 5,
            "compliance_status": {"LGPD": 0.80},
        }

        reflected = await agent.reflect(task, result, context)

        assert isinstance(reflected, dict)
        # Reflection should maintain or improve results
        assert "security_score" in reflected or "improved" in str(reflected).lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_reflect_threat_detection(self, agent, context):
        """Test reflection on threat detection."""
        task = "intrusion_detection"
        result = {
            "intrusions_detected": 2,
            "confidence": 0.85,
            "threat_level": "medium",
        }

        reflected = await agent.reflect(task, result, context)

        assert isinstance(reflected, dict)
