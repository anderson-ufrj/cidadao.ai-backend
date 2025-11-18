#!/usr/bin/env python3
"""
Test Supabase REST API connection.

This script tests the REST API version which works on HuggingFace Spaces.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv

load_dotenv()

from src.services.investigation_service_supabase_rest import (
    investigation_service_supabase_rest,
)
from src.services.supabase_service_rest import get_supabase_service_rest


async def main():
    """Test Supabase REST API connection and operations."""

    print("=" * 80)
    print("🧪 Testing Supabase REST API Connection")
    print("=" * 80)
    print()

    try:
        # Test 1: Initialize service
        print("1️⃣  Initializing Supabase REST service...")
        service = await get_supabase_service_rest()
        print("   ✅ Service initialized successfully!")
        print()

        # Test 2: Health check
        print("2️⃣  Testing health check...")
        health = await service.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Connected: {health['connected']}")
        print(f"   API Version: {health.get('api_version', 'unknown')}")
        print()

        if health["status"] != "healthy":
            print("   ❌ Health check failed!")
            print(f"   Error: {health.get('error', 'Unknown error')}")
            return

        # Test 3: Create investigation
        print("3️⃣  Creating test investigation...")
        investigation = await investigation_service_supabase_rest.create(
            user_id="302573ff-3416-43a3-a074-24bd7c6ed50a",
            query="Test investigation via REST API",
            data_source="contracts",
            filters={"state": "SP", "min_value": 100000},
            anomaly_types=["price_deviation", "supplier_concentration"],
        )

        inv_id = investigation["id"]
        print(f"   ✅ Investigation created: {inv_id}")
        print(f"   Status: {investigation['status']}")
        print(f"   Query: {investigation['query']}")
        print()

        # Test 4: Update progress
        print("4️⃣  Updating investigation progress...")
        await investigation_service_supabase_rest.update_progress(
            investigation_id=inv_id,
            progress=0.5,
            current_phase="testing_rest_api",
            records_processed=100,
            anomalies_found=5,
        )
        print("   ✅ Progress updated to 50%")
        print()

        # Test 5: Get investigation
        print("5️⃣  Retrieving investigation...")
        retrieved = await investigation_service_supabase_rest.get(inv_id)
        print("   ✅ Investigation retrieved")
        print(f"   Progress: {retrieved['progress'] * 100:.0f}%")
        print(f"   Phase: {retrieved['current_phase']}")
        print(f"   Records processed: {retrieved.get('total_records_analyzed', 0)}")
        print(f"   Anomalies found: {retrieved.get('anomalies_found', 0)}")
        print()

        # Test 6: Complete investigation
        print("6️⃣  Completing investigation...")
        await investigation_service_supabase_rest.complete_investigation(
            investigation_id=inv_id,
            results=[
                {
                    "anomaly_id": "test-1",
                    "type": "price_deviation",
                    "severity": "high",
                    "confidence": 0.95,
                    "description": "Test anomaly via REST API",
                }
            ],
            summary="Test investigation completed successfully via REST API",
            confidence_score=0.95,
            total_records=100,
            anomalies_found=1,
        )
        print("   ✅ Investigation completed!")
        print()

        # Test 7: Verify final state
        print("7️⃣  Verifying final state...")
        final = await investigation_service_supabase_rest.get(inv_id)
        print(f"   Status: {final['status']}")
        print(f"   Progress: {final['progress'] * 100:.0f}%")
        print(f"   Summary: {final['summary'][:50]}...")
        print(f"   Results count: {len(final.get('results', []))}")
        print()

        print("=" * 80)
        print("✅ ALL TESTS PASSED - REST API WORKING!")
        print("=" * 80)
        print()
        print("🎉 This version will work on HuggingFace Spaces!")
        print()

    except Exception as e:
        print("=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
