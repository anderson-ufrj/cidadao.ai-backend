#!/usr/bin/env python3
"""Test production API after Portal fix."""

import asyncio

import httpx

PRODUCTION_URL = "https://cidadao-api-production.up.railway.app"


async def test_chat_endpoint():
    """Test chat endpoint with contract query."""
    print("🧪 Testing Production Chat Endpoint...")
    print(f"URL: {PRODUCTION_URL}/api/v1/chat/message\n")

    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "message": "Contratos de saúde em MG acima de 1 milhão em 2024",
            "user_id": "test-portal-fix",
            "session_id": "test-session-portal-fix",
        }

        print("📤 Request payload:")
        print(f"   {payload}\n")

        try:
            response = await client.post(
                f"{PRODUCTION_URL}/api/v1/chat/message",
                json=payload,
                headers={"Content-Type": "application/json"},
            )

            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response headers: {dict(response.headers)}\n")

            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS!")
                print("Response data:")
                for key, value in data.items():
                    if isinstance(value, str) and len(value) > 200:
                        print(f"  {key}: {value[:200]}...")
                    else:
                        print(f"  {key}: {value}")
            else:
                print(f"❌ ERROR {response.status_code}")
                print(f"Response text: {response.text}")

        except Exception as e:
            print(f"❌ Exception: {e}")


async def test_health_endpoint():
    """Test health endpoint."""
    print("\n" + "=" * 80)
    print("🏥 Testing Health Endpoint...")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{PRODUCTION_URL}/health")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"❌ Exception: {e}")


async def main():
    """Run all tests."""
    print("=" * 80)
    print("🚀 PRODUCTION API TEST - Portal Fix Verification")
    print("=" * 80 + "\n")

    await test_health_endpoint()
    await test_chat_endpoint()

    print("\n" + "=" * 80)
    print("✅ Tests completed")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
