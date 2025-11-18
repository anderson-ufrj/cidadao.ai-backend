#!/usr/bin/env python3
"""
Test Direct Supabase Investigation Creation
Author: Anderson Henrique da Silva
Date: 2025-10-09
"""

import asyncio
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


async def test_supabase_connection():
    """Test direct connection to Supabase."""

    print("🔍 Testing Supabase REST API Connection")
    print("=" * 60)
    print()

    # Set environment variables
    os.environ["SUPABASE_URL"] = "https://pbsiyuattnwgohvkkkks.supabase.co"
    os.environ["SUPABASE_SERVICE_ROLE_KEY"] = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBic2l5dWF0dG53Z29odmtra2tzIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNzU1NTg3MCwiZXhwIjoyMDUzMTMxODcwfQ.aCtc21nAF5aw23FiP9z-fmUQMfjptW93gXD9oZfqRoE"
    )

    # Import service
    from src.services.investigation_service_supabase_rest import (
        InvestigationServiceSupabaseRest,
    )

    service = InvestigationServiceSupabaseRest()

    print(f"✅ Service initialized")
    print(f"   URL: {os.getenv('SUPABASE_URL')}")
    print(f"   API Key: {os.getenv('SUPABASE_SERVICE_ROLE_KEY')[:20]}...")
    print()

    # Test 1: Create investigation
    print("📝 Test 1: Creating investigation...")
    try:
        investigation = await service.create(
            user_id="test_user_anderson",
            query="🧪 TESTE DIRETO PYTHON - Supabase REST - 2025-10-09 14:20",
            data_source="contracts",
            filters={"test": True, "direct_python": True},
        )

        print(f"✅ Investigation created!")
        print(f"   ID: {investigation.id}")
        print(f"   Query: {investigation.query}")
        print(f"   Status: {investigation.status}")
        print(f"   Created: {investigation.created_at}")
        print()

        investigation_id = investigation.id

    except Exception as e:
        print(f"❌ Error creating investigation: {e}")
        import traceback

        traceback.print_exc()
        return

    # Test 2: Get investigation
    print("🔍 Test 2: Retrieving investigation...")
    try:
        retrieved = await service.get(investigation_id)

        if retrieved:
            print(f"✅ Investigation retrieved!")
            print(f"   ID: {retrieved.id}")
            print(f"   Query: {retrieved.query}")
            print(f"   Status: {retrieved.status}")
        else:
            print(f"❌ Investigation not found!")
        print()

    except Exception as e:
        print(f"❌ Error retrieving investigation: {e}")
        import traceback

        traceback.print_exc()

    # Test 3: List all investigations
    print("📋 Test 3: Listing all investigations...")
    try:
        all_investigations = await service.list(limit=10)

        print(f"✅ Found {len(all_investigations)} investigations")
        for inv in all_investigations:
            print(f"   - {inv.id[:8]}... | {inv.query[:50]} | {inv.created_at}")
        print()

    except Exception as e:
        print(f"❌ Error listing investigations: {e}")
        import traceback

        traceback.print_exc()

    # Test 4: Update investigation
    print("🔄 Test 4: Updating investigation...")
    try:
        await service.update(
            investigation_id,
            status="completed",
            results=[{"test": "result", "timestamp": datetime.now().isoformat()}],
        )

        updated = await service.get(investigation_id)
        print(f"✅ Investigation updated!")
        print(f"   Status: {updated.status}")
        print(f"   Results: {len(updated.results)} items")
        print()

    except Exception as e:
        print(f"❌ Error updating investigation: {e}")
        import traceback

        traceback.print_exc()

    print("=" * 60)
    print("✅ All tests completed!")
    print()
    print("🌐 Check Supabase Dashboard:")
    print("   https://supabase.com/dashboard/project/pbsiyuattnwgohvkkkks/editor")
    print()


if __name__ == "__main__":
    asyncio.run(test_supabase_connection())
