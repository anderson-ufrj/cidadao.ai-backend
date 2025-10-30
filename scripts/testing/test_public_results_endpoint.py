#!/usr/bin/env python3
"""
Test script for the public results endpoint.

This script tests the new GET /api/v1/investigations/public/results/{id} endpoint
to verify it works correctly with both in-memory and database investigations.
"""

import asyncio
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, "/home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend")

from src.api.routes.investigations import (  # noqa: E402
    _active_investigations,
    get_public_investigation_results,
)


async def test_in_memory_investigation():
    """Test endpoint with in-memory investigation."""
    print("\n=== Test 1: In-Memory Investigation (Completed) ===")

    # Create a mock completed investigation
    test_id = "test-inv-001"
    _active_investigations[test_id] = {
        "status": "completed",
        "query": "Test query for contracts analysis",
        "data_source": "contracts",
        "started_at": datetime(2025, 10, 30, 10, 0, 0),
        "completed_at": datetime(2025, 10, 30, 10, 5, 30),
        "records_processed": 150,
        "results": [
            {
                "anomaly_type": "price_deviation",
                "severity": "high",
                "confidence": 0.92,
                "description": "Contract price 3.5x higher than average",
                "contract_id": "C001",
            },
            {
                "anomaly_type": "supplier_concentration",
                "severity": "medium",
                "confidence": 0.85,
                "description": "Single supplier won 85% of contracts",
                "contract_id": "C002",
            },
        ],
        "summary": "Found 2 significant anomalies requiring review",
        "confidence_score": 0.88,
    }

    try:
        response = await get_public_investigation_results(test_id)
        print(f"✅ SUCCESS: Retrieved results for {test_id}")
        print(f"   Status: {response.status}")
        print(f"   Anomalies Found: {response.anomalies_found}")
        print(f"   Records Analyzed: {response.total_records_analyzed}")
        print(f"   Processing Time: {response.processing_time:.2f}s")
        print(f"   Confidence Score: {response.confidence_score:.2f}")
        print(f"   Results: {len(response.results)} anomalies")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False
    finally:
        # Clean up
        if test_id in _active_investigations:
            del _active_investigations[test_id]


async def test_pending_investigation():
    """Test endpoint with pending investigation (should return 409)."""
    print("\n=== Test 2: Pending Investigation (Should Return 409) ===")

    test_id = "test-inv-002"
    _active_investigations[test_id] = {
        "status": "running",
        "query": "Analyzing contracts...",
        "data_source": "contracts",
        "started_at": datetime.now(),
        "records_processed": 50,
        "results": [],
    }

    try:
        await get_public_investigation_results(test_id)
        print("❌ FAILED: Should have returned 409 for pending investigation")
        return False
    except Exception as e:
        if "409" in str(e) or "not yet completed" in str(e).lower():
            print("✅ SUCCESS: Correctly returned 409 for pending investigation")
            return True
        print(f"❌ FAILED: Wrong error: {str(e)}")
        return False
    finally:
        # Clean up
        if test_id in _active_investigations:
            del _active_investigations[test_id]


async def test_not_found():
    """Test endpoint with non-existent investigation (should return 404)."""
    print("\n=== Test 3: Non-Existent Investigation (Should Return 404) ===")

    test_id = "nonexistent-inv-999"

    try:
        await get_public_investigation_results(test_id)
        print("❌ FAILED: Should have returned 404 for non-existent investigation")
        return False
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            print("✅ SUCCESS: Correctly returned 404 for non-existent investigation")
            return True
        print(f"❌ FAILED: Wrong error: {str(e)}")
        return False


async def main():
    """Run all tests."""
    print("=" * 70)
    print("🔬 Testing Public Results Endpoint")
    print("=" * 70)

    results = []

    # Run tests
    results.append(await test_in_memory_investigation())
    results.append(await test_pending_investigation())
    results.append(await test_not_found())

    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("✅ All tests passed!")
        return 0
    print(f"❌ {total - passed} test(s) failed")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
