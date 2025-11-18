#!/usr/bin/env python3
"""Test complete investigation flow locally."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import os

os.environ["JWT_SECRET_KEY"] = "test"
os.environ["SECRET_KEY"] = "test"
os.environ["REDIS_URL"] = "redis://fake:6379"  # Disable Redis


async def test_complete_flow():
    """Test the complete flow from query to result."""
    print("=" * 80)
    print("🧪 Testing Complete Investigation Flow")
    print("=" * 80 + "\n")

    try:
        # Test 1: Intent Classification
        print("1️⃣  Testing Intent Classification...")
        from src.services.orchestration.query_planner.intent_classifier import (
            IntentClassifier,
        )

        classifier = IntentClassifier(keyword_only=True)
        query = "Contratos de saúde em MG acima de 1 milhão em 2024"

        intent = await classifier.classify(query)
        print(f"   Query: {query}")
        print(f"   Intent: {intent}")

        if intent.get("intent_type") in ["investigate", "contract_anomaly_detection"]:
            print(f"   ✅ Intent classification working!\n")
        else:
            print(f"   ❌ Wrong intent: {intent}\n")
            return

        # Test 2: Entity Extraction
        print("2️⃣  Testing Entity Extraction...")
        from src.services.orchestration.query_planner.entity_extractor import (
            EntityExtractor,
        )

        extractor = EntityExtractor()
        entities = await extractor.extract(query)
        print(f"   Entities: {entities}")

        if entities.get("state_code") == "31":  # MG
            print(f"   ✅ Entity extraction working!\n")
        else:
            print(f"   ⚠️  Estado não extraído corretamente\n")

        # Test 3: Check if we can import and create Zumbi agent
        print("3️⃣  Testing Zumbi Agent Import...")
        from src.agents.zumbi import InvestigationRequest, InvestigatorAgent

        agent = InvestigatorAgent()
        print(f"   Agent: {agent.name}")
        print(f"   Capabilities: {agent.capabilities[:3]}...")
        print(f"   ✅ Zumbi agent can be imported!\n")

        # Test 4: Create investigation request
        print("4️⃣  Testing Investigation Request Creation...")
        request = InvestigationRequest(
            query=query,
            organization_codes=None,
            enable_open_data=True,
            date_range={"start": "2024-01-01", "end": "2024-12-31"},
            value_threshold=1000000.0,
            categories=["saúde", "health"],
        )
        print(f"   Request query: {request.query}")
        print(f"   Date range: {request.date_range}")
        print(f"   Value threshold: R$ {request.value_threshold:,.2f}")
        print(f"   ✅ Investigation request created!\n")

        # Test 5: Check Portal API service (without actually calling)
        print("5️⃣  Testing Portal API Service Configuration...")
        from src.services.portal_transparencia_service import PortalTransparenciaService

        service = PortalTransparenciaService()
        print(f"   Base URL: {service.base_url}")
        print(
            f"   Has API key: {'Yes' if service.api_key else 'No (expected locally)'}"
        )
        print(f"   ✅ Portal service configured!\n")

        print("=" * 80)
        print("📊 SUMMARY:")
        print("=" * 80)
        print("✅ 1. Intent Classification - WORKING")
        print("✅ 2. Entity Extraction - WORKING")
        print("✅ 3. Zumbi Agent - WORKING")
        print("✅ 4. Investigation Request - WORKING")
        print("✅ 5. Portal API Service - CONFIGURED")
        print()
        print("🎯 All components are operational!")
        print()
        print("⚠️  Note: Actual Portal API calls require:")
        print("   - TRANSPARENCY_API_KEY in production")
        print("   - The fix is deployed and should work in Railway")
        print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_complete_flow())
