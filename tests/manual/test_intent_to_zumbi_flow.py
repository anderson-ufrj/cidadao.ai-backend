#!/usr/bin/env python3
"""Test complete flow from intent classification to Zumbi investigation."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.orchestration.models.investigation import InvestigationIntent
from src.services.orchestration.query_planner.intent_classifier import IntentClassifier


async def test_intent_classification():
    """Test intent classification with keyword-only mode."""
    print("=" * 80)
    print("🧪 TEST 1: Intent Classification (Keyword-Only Mode)")
    print("=" * 80 + "\n")

    # Initialize in keyword-only mode (like production)
    classifier = IntentClassifier(keyword_only=True)

    test_queries = [
        "Contratos de saúde em MG acima de 1 milhão em 2024",
        "Quero ver contratos de saúde acima de R$ 1 milhão",
        "Como funciona o sistema?",
    ]

    for query in test_queries:
        print(f"📝 Query: {query}")
        try:
            result = await classifier.classify(query)
            print(f"✅ Intent: {result['intent'].value}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Method: {result.get('method', 'unknown')}")
            print(f"   Reasoning: {result.get('reasoning', 'N/A')}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")


async def test_zumbi_initialization():
    """Test if Zumbi can be initialized."""
    print("=" * 80)
    print("🧪 TEST 2: Zumbi Agent Initialization")
    print("=" * 80 + "\n")

    try:
        from src.agents.zumbi import ZumbiAgent

        print("📦 Importing ZumbiAgent...")
        agent = ZumbiAgent()
        print(f"✅ Zumbi initialized successfully")
        print(f"   Name: {agent.name}")
        print(f"   Capabilities: {agent.capabilities}\n")
    except Exception as e:
        print(f"❌ Failed to initialize Zumbi: {e}\n")
        import traceback

        traceback.print_exc()


async def test_entity_extraction():
    """Test entity extraction."""
    print("=" * 80)
    print("🧪 TEST 3: Entity Extraction")
    print("=" * 80 + "\n")

    try:
        from src.services.chat_data_integration import ChatDataIntegration

        chat_integration = ChatDataIntegration()
        query = "Contratos de saúde em Minas Gerais acima de R$ 1 milhão em 2024"

        print(f"📝 Query: {query}")
        entities = await chat_integration._extract_entities(query)

        print(f"✅ Entities extracted:")
        for key, value in entities.items():
            print(f"   {key}: {value}")
        print()
    except Exception as e:
        print(f"❌ Failed to extract entities: {e}\n")
        import traceback

        traceback.print_exc()


async def test_portal_adapter():
    """Test Portal adapter with default orgao."""
    print("=" * 80)
    print("🧪 TEST 4: Portal Adapter (with default orgao fix)")
    print("=" * 80 + "\n")

    try:
        from src.services.transparency_apis.federal_apis.portal_adapter import (
            PortalTransparenciaAdapter,
        )

        adapter = PortalTransparenciaAdapter()

        print("📦 Portal Adapter initialized")
        print(f"   Name: {adapter.name}")
        print(f"   Has API key: {bool(adapter.portal_service.api_key)}\n")

        print("🔍 Testing get_contracts() with NO orgao parameter...")
        # This should now use default orgao=36000
        contracts = await adapter.get_contracts(
            year=2024, start_date="2024-01-01", end_date="2024-01-31"
        )

        print(f"✅ Received {len(contracts)} contracts")
        if contracts:
            print(f"   First contract keys: {list(contracts[0].keys())}\n")
        else:
            print("   (empty result - might be demo mode or no data)\n")

    except Exception as e:
        print(f"❌ Failed Portal test: {e}\n")
        import traceback

        traceback.print_exc()


async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("🚀 COMPLETE FLOW TEST - Intent → Zumbi → Portal")
    print("=" * 80 + "\n")

    await test_intent_classification()
    await test_entity_extraction()
    await test_zumbi_initialization()
    await test_portal_adapter()

    print("=" * 80)
    print("✅ All tests completed")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
