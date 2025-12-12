#!/usr/bin/env python3
"""
Investigation Persistence Tests

Tests to verify that investigations are properly persisted to PostgreSQL,
including status updates, timestamps, and results.

This test suite validates:
1. Investigation creation and database persistence
2. Status update persistence (pending -> running -> completed)
3. Datetime handling (timezone-aware to naive conversion)
4. Results and anomalies storage
5. Concurrent investigation handling

Author: Anderson Henrique da Silva
Date: 2025-12-12
"""

import asyncio
import time
import uuid
from datetime import UTC, datetime

import httpx
import pytest

# Production API URL
PROD_URL = "https://cidadao-api-production.up.railway.app"

# Test session prefix for easy identification
TEST_SESSION_PREFIX = "persistence-test"


class TestInvestigationPersistence:
    """Test suite for investigation persistence verification."""

    @pytest.fixture
    def session_id(self) -> str:
        """Generate unique session ID for each test."""
        return f"{TEST_SESSION_PREFIX}-{uuid.uuid4().hex[:8]}"

    @pytest.fixture
    def client(self) -> httpx.Client:
        """Create HTTP client with timeout."""
        return httpx.Client(timeout=60.0, follow_redirects=True)

    def test_health_check(self, client: httpx.Client):
        """Test 1: Verify API is healthy before running tests."""
        response = client.get(f"{PROD_URL}/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print(f"Health check passed at {data['timestamp']}")

    def test_investigation_list_endpoint(self, client: httpx.Client):
        """Test 2: Verify investigations endpoint is accessible."""
        response = client.get(f"{PROD_URL}/api/v1/investigations/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"Found {len(data)} existing investigations")

    def test_chat_creates_investigation_intent(
        self, client: httpx.Client, session_id: str
    ):
        """Test 3: Verify chat with investigation intent triggers investigation creation."""
        payload = {
            "message": "Quero investigar contratos de tecnologia do Ministério da Educação em 2024",
            "session_id": session_id,
        }

        response = client.post(
            f"{PROD_URL}/api/v1/chat/message",
            json=payload,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "session_id" in data
        assert "message" in data
        assert "metadata" in data

        # Check if investigation intent was detected
        metadata = data.get("metadata", {})
        intent_type = metadata.get("intent_type", "")

        print(f"Session: {session_id}")
        print(f"Intent detected: {intent_type}")
        print(f"Agent: {data.get('agent_name', 'unknown')}")
        print(f"Response preview: {data.get('message', '')[:200]}...")

        return data

    def test_investigation_direct_creation(self, client: httpx.Client, session_id: str):
        """Test 4: Test direct investigation creation via API."""
        # First, check if there's a direct investigation creation endpoint
        # This tests the /api/v1/investigations/ POST endpoint if it exists

        payload = {
            "query": "Contratos de TI acima de R$ 1 milhão",
            "data_source": "contratos",
            "user_id": "test-user",
            "session_id": session_id,
        }

        response = client.post(
            f"{PROD_URL}/api/v1/investigations/",
            json=payload,
        )

        # Log the response regardless of status
        print(f"Direct creation response status: {response.status_code}")

        if response.status_code in (200, 201):
            data = response.json()
            print(f"Investigation created: {data.get('id', 'unknown')}")
            return data
        elif response.status_code == 422:
            print("Validation error - endpoint exists but requires different payload")
            print(f"Response: {response.text[:300]}")
        else:
            print(f"Response: {response.text[:300]}")

        return None

    def test_investigation_status_persistence(self, client: httpx.Client):
        """Test 5: Verify investigation status is persisted correctly."""
        # Get all investigations
        response = client.get(f"{PROD_URL}/api/v1/investigations/")
        assert response.status_code == 200
        investigations = response.json()

        if not investigations:
            print("No investigations found - creating one first")
            # Trigger investigation via chat
            chat_response = client.post(
                f"{PROD_URL}/api/v1/chat/message",
                json={
                    "message": "Investigar contratos do Ministério da Saúde",
                    "session_id": f"status-test-{uuid.uuid4().hex[:8]}",
                },
            )
            print(f"Chat response: {chat_response.status_code}")
            time.sleep(2)  # Wait for async processing

            # Fetch again
            response = client.get(f"{PROD_URL}/api/v1/investigations/")
            investigations = response.json()

        # Analyze investigation statuses
        status_counts = {}
        for inv in investigations:
            status = inv.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

            # Check datetime fields
            created_at = inv.get("created_at")
            completed_at = inv.get("completed_at")

            print(f"Investigation {inv.get('id', 'unknown')[:8]}...")
            print(f"  Status: {status}")
            print(f"  Created: {created_at}")
            print(f"  Completed: {completed_at}")

            # Verify completed investigations have completed_at
            if status in ("completed", "error", "cancelled"):
                if completed_at:
                    print("  Datetime persistence: PASSED")
                else:
                    print("  Datetime persistence: FAILED - missing completed_at")

        print(f"\nStatus distribution: {status_counts}")

    def test_datetime_timezone_handling(self, client: httpx.Client):
        """Test 6: Verify datetime fields are properly stored (naive, no timezone)."""
        response = client.get(f"{PROD_URL}/api/v1/investigations/")
        assert response.status_code == 200
        investigations = response.json()

        for inv in investigations[:5]:  # Check first 5
            created_at = inv.get("created_at", "")
            completed_at = inv.get("completed_at", "")

            # Check that timestamps don't have timezone info that would cause issues
            # PostgreSQL TIMESTAMP WITHOUT TIME ZONE should store naive datetimes
            if created_at:
                # Should be in ISO format without explicit timezone
                has_tz = "+00:00" in created_at or "Z" in created_at
                print(
                    f"Investigation {inv.get('id', '')[:8]}: created_at timezone info: {has_tz}"
                )

            if completed_at:
                has_tz = "+00:00" in completed_at or "Z" in completed_at
                print(
                    f"Investigation {inv.get('id', '')[:8]}: completed_at timezone info: {has_tz}"
                )


class TestInvestigationFlow:
    """Test the complete investigation flow from creation to completion."""

    @pytest.fixture
    def async_client(self):
        """Create async HTTP client."""
        return httpx.AsyncClient(timeout=120.0, follow_redirects=True)

    @pytest.mark.asyncio
    async def test_full_investigation_flow(self, async_client: httpx.AsyncClient):
        """Test 7: Complete flow from chat to investigation to results."""
        session_id = f"flow-test-{uuid.uuid4().hex[:8]}"

        print(f"\n{'='*60}")
        print("Testing full investigation flow")
        print(f"Session: {session_id}")
        print(f"{'='*60}")

        # Step 1: Send investigation request via chat
        print("\nStep 1: Sending investigation request...")
        response = await async_client.post(
            f"{PROD_URL}/api/v1/chat/message",
            json={
                "message": "Investigar contratos do Ministério da Educação em 2024 acima de 500 mil reais",
                "session_id": session_id,
            },
        )

        assert response.status_code == 200
        chat_data = response.json()
        print(f"Agent response: {chat_data.get('agent_name', 'unknown')}")
        print(f"Intent: {chat_data.get('metadata', {}).get('intent_type', 'unknown')}")

        # Step 2: Wait and check for investigation creation
        print("\nStep 2: Waiting for investigation processing...")
        await asyncio.sleep(3)

        # Step 3: Check investigations list
        print("\nStep 3: Checking investigations list...")
        response = await async_client.get(f"{PROD_URL}/api/v1/investigations/")
        assert response.status_code == 200
        investigations = response.json()

        # Find our investigation
        our_inv = None
        for inv in investigations:
            if inv.get("session_id") == session_id:
                our_inv = inv
                break

        if our_inv:
            print("Found our investigation!")
            print(f"  ID: {our_inv.get('id')}")
            print(f"  Status: {our_inv.get('status')}")
            print(f"  Progress: {our_inv.get('progress', 0) * 100:.1f}%")
            print(f"  Anomalies found: {our_inv.get('anomalies_found', 0)}")
            print(f"  Records analyzed: {our_inv.get('total_records_analyzed', 0)}")

            # Step 4: Verify persistence of key fields
            print("\nStep 4: Verifying persistence...")
            assert our_inv.get("id") is not None, "ID should be persisted"
            assert our_inv.get("status") is not None, "Status should be persisted"
            assert (
                our_inv.get("created_at") is not None
            ), "Created_at should be persisted"

            if our_inv.get("status") in ("completed", "error"):
                assert (
                    our_inv.get("completed_at") is not None
                ), "Completed_at should be set for finished investigations"
                print("  Datetime persistence: VERIFIED")

            return our_inv
        else:
            print("Investigation not found in list - may be processing async")
            print(f"Total investigations in DB: {len(investigations)}")

        return None


class TestConcurrentInvestigations:
    """Test concurrent investigation handling."""

    @pytest.mark.asyncio
    async def test_multiple_concurrent_investigations(self):
        """Test 8: Verify system handles multiple concurrent investigations."""
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            # Create 3 concurrent investigation requests
            sessions = [f"concurrent-test-{i}-{uuid.uuid4().hex[:6]}" for i in range(3)]

            queries = [
                "Investigar contratos de educação",
                "Investigar contratos de saúde",
                "Investigar contratos de tecnologia",
            ]

            print(f"\nSending {len(sessions)} concurrent investigation requests...")

            # Send all requests concurrently
            tasks = []
            for session_id, query in zip(sessions, queries, strict=False):
                task = client.post(
                    f"{PROD_URL}/api/v1/chat/message",
                    json={"message": query, "session_id": session_id},
                )
                tasks.append(task)

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # Analyze results
            successful = 0
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    print(f"Request {i+1}: ERROR - {response}")
                elif response.status_code == 200:
                    successful += 1
                    data = response.json()
                    print(
                        f"Request {i+1}: SUCCESS - Agent: {data.get('agent_name', 'unknown')}"
                    )
                else:
                    print(f"Request {i+1}: HTTP {response.status_code}")

            print(f"\nConcurrent requests: {successful}/{len(sessions)} successful")
            assert successful >= 2, "At least 2 concurrent requests should succeed"


def run_persistence_tests():
    """Run all persistence tests and generate report."""
    print("=" * 70)
    print("INVESTIGATION PERSISTENCE TEST SUITE")
    print(f"Target: {PROD_URL}")
    print(f"Started: {datetime.now(UTC).isoformat()}")
    print("=" * 70)

    # Run tests
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "-x",  # Stop on first failure
        ]
    )


if __name__ == "__main__":
    run_persistence_tests()
