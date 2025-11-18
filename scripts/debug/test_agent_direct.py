#!/usr/bin/env python3
"""
Test agent directly to diagnose issues
"""

import asyncio
import json
from datetime import datetime

import httpx

# Production API
API_URL = "https://cidadao-api-production.up.railway.app"


async def test_agent_direct():
    """Test Zumbi agent directly"""

    print("\n" + "=" * 60)
    print("🔍 TESTING ZUMBI AGENT DIRECTLY")
    print("=" * 60)
    print(f"API: {API_URL}")
    print(f"Time: {datetime.now()}")
    print("-" * 60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test the Zumbi agent directly
        print("\n📝 Calling Zumbi agent directly...")

        payload = {
            "query": "Analyze contracts for anomalies",
            "context": {
                "data_source": "contracts",
                "filters": {"ano": 2024, "codigo_orgao": "26000"},
                "investigation_id": "test_direct_001",
                "user_id": "test_user",
            },
        }

        print(f"   Payload: {json.dumps(payload, indent=2)}")

        try:
            response = await client.post(
                f"{API_URL}/api/agents/zumbi/analyze",
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            print(f"\n📊 Response Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print("\n✅ Agent Response!")
                print(f"   Status: {result.get('status')}")
                print(f"   Message: {result.get('message')}")
                if result.get("result"):
                    print(
                        f"   Results: {json.dumps(result.get('result'), indent=2)[:500]}..."
                    )
            else:
                print("\n❌ Agent call failed!")
                print(f"   Response: {response.text[:500]}")

        except Exception as e:
            print(f"\n❌ Exception occurred: {e}")
            import traceback

            traceback.print_exc()

    print("\n" + "=" * 60)


async def test_health_check():
    """Test health endpoints"""

    print("\n📍 Testing health endpoints...")

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test main health
        response = await client.get(f"{API_URL}/health/")
        print(f"   /health/: {response.status_code} - {response.text}")

        # Test metrics
        try:
            response = await client.get(f"{API_URL}/health/metrics")
            print(f"   /health/metrics: {response.status_code}")
        except:
            print("   /health/metrics: Not available")


async def main():
    """Run all tests"""
    await test_health_check()
    await test_agent_direct()


if __name__ == "__main__":
    asyncio.run(main())
