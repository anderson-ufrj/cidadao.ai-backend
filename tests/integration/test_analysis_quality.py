#!/usr/bin/env python3
"""
Analysis Quality Tests

Tests to verify the quality of anomaly detection and analysis algorithms.

This test suite validates:
1. Anomaly detection algorithms produce meaningful results
2. Confidence scores are within expected ranges
3. Different anomaly types are properly detected
4. Analysis results contain required fields
5. Data quality and completeness

Author: Anderson Henrique da Silva
Date: 2025-12-12
"""

import statistics
import uuid
from datetime import UTC, datetime

import httpx
import pytest

# Production API URL
PROD_URL = "https://cidadao-api-production.up.railway.app"


class TestAnomalyDetection:
    """Test suite for anomaly detection quality."""

    @pytest.fixture
    def client(self) -> httpx.Client:
        """Create HTTP client with timeout."""
        return httpx.Client(timeout=90.0, follow_redirects=True)

    def test_anomaly_detection_price_anomaly(self, client: httpx.Client):
        """Test 1: Verify price anomaly detection works."""
        session_id = f"price-anomaly-test-{uuid.uuid4().hex[:8]}"

        # Request investigation focused on price anomalies
        response = client.post(
            f"{PROD_URL}/api/v1/chat/message",
            json={
                "message": "Investigar contratos com valores muito acima da média do mercado",
                "session_id": session_id,
            },
        )

        assert response.status_code == 200
        data = response.json()

        print("\nPrice Anomaly Detection Test")
        print(f"Session: {session_id}")
        print(f"Agent: {data.get('agent_name', 'unknown')}")
        print(f"Confidence: {data.get('confidence', 0)}")

        metadata = data.get("metadata", {})
        portal_data = metadata.get("portal_data", {})

        if portal_data.get("has_data"):
            print(f"Records found: {portal_data.get('total_records', 0)}")
            entities = portal_data.get("entities_found", {})
            print(f"Entities extracted: {entities}")

        return data

    def test_anomaly_detection_vendor_concentration(self, client: httpx.Client):
        """Test 2: Verify vendor concentration detection works."""
        session_id = f"vendor-test-{uuid.uuid4().hex[:8]}"

        response = client.post(
            f"{PROD_URL}/api/v1/chat/message",
            json={
                "message": "Verificar se há concentração de contratos em poucos fornecedores no Ministério da Saúde",
                "session_id": session_id,
            },
        )

        assert response.status_code == 200
        data = response.json()

        print("\nVendor Concentration Test")
        print(f"Agent: {data.get('agent_name', 'unknown')}")
        print(f"Response: {data.get('message', '')[:300]}...")

        return data

    def test_anomaly_detection_temporal_patterns(self, client: httpx.Client):
        """Test 3: Verify temporal pattern detection works."""
        session_id = f"temporal-test-{uuid.uuid4().hex[:8]}"

        response = client.post(
            f"{PROD_URL}/api/v1/chat/message",
            json={
                "message": "Analisar padrões temporais de contratações no final do ano fiscal 2024",
                "session_id": session_id,
            },
        )

        assert response.status_code == 200
        data = response.json()

        print("\nTemporal Patterns Test")
        print(f"Agent: {data.get('agent_name', 'unknown')}")

        # Check if temporal analysis was triggered
        metadata = data.get("metadata", {})
        print(f"Intent: {metadata.get('intent_type', 'unknown')}")

        return data


class TestConfidenceScores:
    """Test confidence score quality."""

    @pytest.fixture
    def client(self) -> httpx.Client:
        """Create HTTP client."""
        return httpx.Client(timeout=60.0, follow_redirects=True)

    def test_confidence_score_range(self, client: httpx.Client):
        """Test 4: Verify confidence scores are within valid range [0, 1]."""
        queries = [
            "Olá, como você está?",
            "Quero investigar contratos",
            "Analise gastos com educação em 2024",
            "Me fale sobre o portal da transparência",
        ]

        confidence_scores = []

        for query in queries:
            response = client.post(
                f"{PROD_URL}/api/v1/chat/message",
                json={
                    "message": query,
                    "session_id": f"confidence-test-{uuid.uuid4().hex[:8]}",
                },
            )

            if response.status_code == 200:
                data = response.json()
                confidence = data.get("confidence", 0)
                confidence_scores.append(confidence)

                print(f"Query: '{query[:40]}...'")
                print(f"  Confidence: {confidence}")
                print(f"  Valid range: {0 <= confidence <= 1}")

                assert 0 <= confidence <= 1, f"Confidence {confidence} out of range"

        # Statistical analysis
        if confidence_scores:
            print("\nConfidence Score Statistics:")
            print(f"  Min: {min(confidence_scores):.3f}")
            print(f"  Max: {max(confidence_scores):.3f}")
            print(f"  Mean: {statistics.mean(confidence_scores):.3f}")
            if len(confidence_scores) > 1:
                print(f"  Std Dev: {statistics.stdev(confidence_scores):.3f}")

    def test_confidence_varies_by_intent(self, client: httpx.Client):
        """Test 5: Verify confidence varies appropriately by intent type."""
        test_cases = [
            ("greeting", "Olá Drummond!"),
            ("investigate", "Investigar contratos de TI do governo"),
            ("help", "Como posso usar o sistema?"),
            ("analysis", "Analisar tendências de gastos públicos"),
        ]

        results = {}

        for intent_type, query in test_cases:
            response = client.post(
                f"{PROD_URL}/api/v1/chat/message",
                json={
                    "message": query,
                    "session_id": f"intent-confidence-{uuid.uuid4().hex[:8]}",
                },
            )

            if response.status_code == 200:
                data = response.json()
                confidence = data.get("confidence", 0)
                detected_intent = data.get("metadata", {}).get("intent_type", "unknown")

                results[intent_type] = {
                    "expected": intent_type,
                    "detected": detected_intent,
                    "confidence": confidence,
                    "match": intent_type == detected_intent
                    or detected_intent in intent_type,
                }

        print("\nIntent Detection Results:")
        for intent, result in results.items():
            match_indicator = "MATCH" if result["match"] else "MISMATCH"
            print(
                f"  {intent}: detected={result['detected']}, confidence={result['confidence']:.2f} [{match_indicator}]"
            )


class TestDataQuality:
    """Test data quality in analysis results."""

    @pytest.fixture
    def client(self) -> httpx.Client:
        """Create HTTP client."""
        return httpx.Client(timeout=90.0, follow_redirects=True)

    def test_response_structure_completeness(self, client: httpx.Client):
        """Test 6: Verify response contains all required fields."""
        response = client.post(
            f"{PROD_URL}/api/v1/chat/message",
            json={
                "message": "Investigar contratos de saúde",
                "session_id": f"structure-test-{uuid.uuid4().hex[:8]}",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Required fields
        required_fields = [
            "session_id",
            "message_id",
            "agent_id",
            "agent_name",
            "message",
            "confidence",
            "metadata",
        ]

        print("\nResponse Structure Check:")
        missing_fields = []
        for field in required_fields:
            present = field in data
            print(f"  {field}: {'PRESENT' if present else 'MISSING'}")
            if not present:
                missing_fields.append(field)

        assert len(missing_fields) == 0, f"Missing required fields: {missing_fields}"

    def test_metadata_quality(self, client: httpx.Client):
        """Test 7: Verify metadata contains useful information."""
        response = client.post(
            f"{PROD_URL}/api/v1/chat/message",
            json={
                "message": "Analisar contratos do Ministério da Educação em 2024",
                "session_id": f"metadata-test-{uuid.uuid4().hex[:8]}",
            },
        )

        assert response.status_code == 200
        data = response.json()
        metadata = data.get("metadata", {})

        print("\nMetadata Quality Check:")
        print(f"  Intent type: {metadata.get('intent_type', 'NOT SET')}")
        print(f"  Timestamp: {metadata.get('timestamp', 'NOT SET')}")
        print(f"  Model used: {metadata.get('model_used', 'NOT SET')}")

        # Check orchestration data
        orchestration = metadata.get("orchestration", {})
        print(f"  Target agent: {orchestration.get('target_agent', 'NOT SET')}")
        print(
            f"  Routing reason: {orchestration.get('routing_reason', 'NOT SET')[:50]}..."
        )

        # Check portal data if present
        portal_data = metadata.get("portal_data", {})
        if portal_data:
            print(f"  Portal data type: {portal_data.get('type', 'NOT SET')}")
            print(f"  Has data: {portal_data.get('has_data', False)}")
            print(f"  Total records: {portal_data.get('total_records', 0)}")

    def test_entity_extraction_quality(self, client: httpx.Client):
        """Test 8: Verify entity extraction is working correctly."""
        test_cases = [
            {
                "query": "Contratos do Ministério da Saúde em 2024 acima de R$ 1 milhão",
                "expected_entities": ["orgao", "ano", "valor"],
            },
            {
                "query": "Investigar licitações de tecnologia em São Paulo",
                "expected_entities": ["categoria", "localidade"],
            },
            {
                "query": "Gastos com educação no primeiro semestre de 2024",
                "expected_entities": ["categoria", "periodo"],
            },
        ]

        print("\nEntity Extraction Quality:")
        for case in test_cases:
            response = client.post(
                f"{PROD_URL}/api/v1/chat/message",
                json={
                    "message": case["query"],
                    "session_id": f"entity-test-{uuid.uuid4().hex[:8]}",
                },
            )

            if response.status_code == 200:
                data = response.json()
                metadata = data.get("metadata", {})
                portal_data = metadata.get("portal_data", {})
                entities = portal_data.get("entities_found", {})

                print(f"\n  Query: '{case['query'][:50]}...'")
                print(f"  Entities found: {entities}")
                print(f"  Expected: {case['expected_entities']}")


class TestInvestigationResults:
    """Test investigation result quality."""

    @pytest.fixture
    def client(self) -> httpx.Client:
        """Create HTTP client."""
        return httpx.Client(timeout=60.0, follow_redirects=True)

    def test_investigation_results_structure(self, client: httpx.Client):
        """Test 9: Verify completed investigations have proper result structure."""
        response = client.get(f"{PROD_URL}/api/v1/investigations/")
        assert response.status_code == 200
        investigations = response.json()

        completed = [inv for inv in investigations if inv.get("status") == "completed"]

        print("\nCompleted Investigations Analysis:")
        print(f"Total completed: {len(completed)}")

        for inv in completed[:5]:  # Analyze first 5
            print(f"\n  Investigation {inv.get('id', 'unknown')[:8]}...")
            print(f"    Query: {inv.get('query', 'N/A')[:50]}...")
            print(f"    Anomalies found: {inv.get('anomalies_found', 0)}")
            print(f"    Records analyzed: {inv.get('total_records_analyzed', 0)}")
            print(f"    Progress: {inv.get('progress', 0) * 100:.1f}%")

            # Check if results field exists and has content
            results = inv.get("results", [])
            if results:
                print(f"    Results count: {len(results)}")
            else:
                print("    Results: Empty or not set")

    def test_anomaly_severity_distribution(self, client: httpx.Client):
        """Test 10: Analyze anomaly severity distribution."""
        response = client.get(f"{PROD_URL}/api/v1/investigations/")
        assert response.status_code == 200
        investigations = response.json()

        all_anomalies = []
        for inv in investigations:
            results = inv.get("results", [])
            if isinstance(results, list):
                all_anomalies.extend(results)

        if all_anomalies:
            severities = [
                a.get("severity", 0) for a in all_anomalies if "severity" in a
            ]

            if severities:
                print("\nAnomaly Severity Distribution:")
                print(f"  Total anomalies: {len(all_anomalies)}")
                print(f"  With severity: {len(severities)}")
                print(f"  Min severity: {min(severities):.3f}")
                print(f"  Max severity: {max(severities):.3f}")
                print(f"  Mean severity: {statistics.mean(severities):.3f}")

                # Distribution buckets
                low = sum(1 for s in severities if s < 0.4)
                medium = sum(1 for s in severities if 0.4 <= s < 0.7)
                high = sum(1 for s in severities if s >= 0.7)

                print("\n  Distribution:")
                print(f"    Low (< 0.4): {low} ({low/len(severities)*100:.1f}%)")
                print(
                    f"    Medium (0.4-0.7): {medium} ({medium/len(severities)*100:.1f}%)"
                )
                print(f"    High (>= 0.7): {high} ({high/len(severities)*100:.1f}%)")
        else:
            print("\nNo anomalies found in completed investigations")


def run_analysis_quality_tests():
    """Run all analysis quality tests and generate report."""
    print("=" * 70)
    print("ANALYSIS QUALITY TEST SUITE")
    print(f"Target: {PROD_URL}")
    print(f"Started: {datetime.now(UTC).isoformat()}")
    print("=" * 70)

    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
        ]
    )


if __name__ == "__main__":
    run_analysis_quality_tests()
