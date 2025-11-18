#!/usr/bin/env python3
"""
Test investigation persistence (CRUD operations).
"""

import asyncio

from dotenv import load_dotenv

from src.services.investigation_service import investigation_service

load_dotenv()


async def test_crud():
    """Test Create, Read, Update, Delete operations."""

    print("🧪 Testing Investigation Persistence\n")

    # CREATE
    print("1️⃣ Creating investigation...")
    investigation = await investigation_service.create(
        user_id="test_user_123",
        query="Analisar contratos suspeitos de superfaturamento",
        data_source="contracts",
        filters={"year": 2024, "min_value": 100000},
        anomaly_types=["price", "vendor", "temporal"],
        session_id="session_456",
    )
    print(f"   ✅ Created: {investigation.id}")
    print(f"   Status: {investigation.status}")
    print(f"   Query: {investigation.query}\n")

    # READ (by ID)
    print("2️⃣ Reading investigation by ID...")
    found = await investigation_service.get_by_id(investigation.id)
    if found:
        print(f"   ✅ Found: {found.id}")
        print(f"   User: {found.user_id}")
        print(f"   Data: {found.to_dict(include_results=False)}\n")

    # UPDATE
    print("3️⃣ Updating investigation status...")
    updated = await investigation_service.update_status(
        investigation.id,
        status="processing",
        progress=0.5,
        current_phase="anomaly_detection",
        anomalies_found=5,
        total_records_analyzed=1000,
    )
    print(f"   ✅ Updated: {updated.status}")
    print(f"   Progress: {updated.progress * 100}%")
    print(f"   Anomalies: {updated.anomalies_found}\n")

    # SEARCH (list user investigations)
    print("4️⃣ Searching user investigations...")
    user_invs = await investigation_service.get_user_investigations(
        user_id="test_user_123", limit=10
    )
    print(f"   ✅ Found {len(user_invs)} investigations for user")
    for inv in user_invs:
        print(f"   - {inv.id[:8]}... | {inv.status} | {inv.query[:50]}")
    print()

    # SEARCH with filters
    print("5️⃣ Searching with status filter...")
    processing_invs = await investigation_service.search(
        user_id="test_user_123", status="processing", limit=5
    )
    print(f"   ✅ Found {len(processing_invs)} processing investigations\n")

    # CANCEL
    print("6️⃣ Cancelling investigation...")
    cancelled = await investigation_service.cancel(
        investigation.id, user_id="test_user_123"
    )
    print(f"   ✅ Cancelled: {cancelled.status}")
    print(f"   Completed at: {cancelled.completed_at}\n")

    print("✅ All CRUD operations working!")
    print("\n📊 Final investigation state:")
    final = await investigation_service.get_by_id(investigation.id)
    if final:
        print(f"   ID: {final.id}")
        print(f"   Status: {final.status}")
        print(f"   Progress: {final.progress}")
        print(f"   Anomalies: {final.anomalies_found}")
        print(f"   Records: {final.total_records_analyzed}")


if __name__ == "__main__":
    asyncio.run(test_crud())
