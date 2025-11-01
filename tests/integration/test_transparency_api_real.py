# TODO: Mock Portal da Transparência API responses for integration tests
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

#!/usr/bin/env python3
"""
Test script to validate real API integration
Run this to test if the Portal da Transparência integration is working
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


@pytest.mark.asyncio
async def test_real_api_integration():
    """Test the real API integration"""
    print("🧪 Testing Real API Integration")
    print("=" * 50)

    # Test 1: Check API key availability
    api_key = os.getenv("TRANSPARENCY_API_KEY")
    print(f"1. API Key Status: {'✅ Available' if api_key else '❌ Not found'}")

    if not api_key:
        print("   ⚠️  Set TRANSPARENCY_API_KEY environment variable to test real API")
        print("   🔄 Will use fallback mock data\n")
    else:
        print(f"   🔑 API Key: {api_key[:20]}...{api_key[-10:]}\n")

    # Test 2: Import and test API client
    try:
        from tools.transparency_api import TransparencyAPIClient, TransparencyAPIFilter

        print("2. API Client Import: ✅ Success")

        if api_key:
            # Test real API call
            try:
                async with TransparencyAPIClient(api_key=api_key) as client:
                    filters = TransparencyAPIFilter(
                        codigo_orgao="26000",  # Health Ministry
                        ano=2024,
                        tamanho_pagina=5,
                    )

                    response = await client.get_contracts(filters)
                    print(
                        f"3. Real API Test: ✅ Success - {len(response.data)} contracts fetched"
                    )

                    if response.data:
                        sample = response.data[0]
                        print(
                            f"   📄 Sample contract: {sample.get('objeto', 'N/A')[:60]}..."
                        )
                        print(f"   💰 Value: R$ {sample.get('valorInicial', 0):,.2f}")

            except Exception as e:
                print(f"3. Real API Test: ❌ Failed - {str(e)}")
        else:
            print("3. Real API Test: ⏭️  Skipped (no API key)")

    except ImportError as e:
        print(f"2. API Client Import: ❌ Failed - {str(e)}")
        return

    # Test 3: Test embedded Zumbi agent
    try:
        # Import the ZumbiAgent from app.py
        import importlib.util

        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)

        zumbi = app_module.ZumbiAgent()
        print("4. Zumbi Agent: ✅ Initialized")

        # Test investigation
        request = app_module.InvestigationRequest(
            query="Analisar contratos de informática com valores suspeitos",
            data_source="contracts",
            max_results=50,
        )

        result = await zumbi.investigate(request)
        print("5. Investigation Test: ✅ Success")
        print(f"   🔍 Status: {result.status}")
        print(f"   📊 Anomalies found: {result.anomalies_found}")
        print(f"   ⏱️  Processing time: {result.processing_time_ms}ms")
        print(f"   🎯 Confidence: {result.confidence_score:.2f}")

        if result.results:
            print("\n📋 Sample anomalies:")
            for i, anomaly in enumerate(result.results[:3], 1):
                print(f"   {i}. {anomaly.get('description', 'N/A')[:50]}...")
                print(f"      💰 Value: R$ {anomaly.get('value', 0):,.2f}")
                print(f"      🚨 Risk: {anomaly.get('risk_level', 'unknown')}")

    except Exception as e:
        print(f"4. Zumbi Agent Test: ❌ Failed - {str(e)}")
        return

    print("\n" + "=" * 50)
    print("🎉 Integration test completed!")

    if api_key and result.status == "completed":
        print("✅ System is using REAL Portal da Transparência data")
    elif result.status == "completed_fallback":
        print("🔄 System is using fallback demo data (API key needed for real data)")
    else:
        print("❌ System encountered errors")


if __name__ == "__main__":
    asyncio.run(test_real_api_integration())
