import pytest

#!/usr/bin/env python3
"""
Test the new stable chat endpoint locally
"""

import asyncio
from datetime import datetime

import httpx


@pytest.mark.asyncio
async def test_stable_endpoint():
    """Test the stable chat endpoint"""

    # Test messages covering all scenarios
    test_cases = [
        # Greetings
        {"message": "Olá, tudo bem?", "expected_intent": "greeting"},
        {"message": "Boa tarde!", "expected_intent": "greeting"},
        # Investigations
        {
            "message": "Quero investigar contratos do Ministério da Saúde",
            "expected_intent": "investigation",
        },
        {
            "message": "Buscar licitações suspeitas em São Paulo",
            "expected_intent": "investigation",
        },
        # Analysis
        {
            "message": "Analise os gastos com educação em 2024",
            "expected_intent": "analysis",
        },
        {
            "message": "Faça uma análise dos fornecedores do governo",
            "expected_intent": "analysis",
        },
        # Help
        {"message": "Como você pode me ajudar?", "expected_intent": "help"},
        {"message": "O que você faz?", "expected_intent": "help"},
        # Complex questions
        {
            "message": "Existe algum padrão suspeito nos contratos de TI dos últimos 6 meses?",
            "expected_intent": "investigation/analysis",
        },
        {
            "message": "Quais foram os maiores gastos do governo federal este ano?",
            "expected_intent": "analysis",
        },
    ]

    print("🧪 Testing Stable Chat Endpoint")
    print("=" * 60)

    # Test locally first
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Check if server is running
        try:
            health = await client.get(f"{base_url}/health")
            print(f"✅ Local server is running: {health.status_code}")
        except:
            print("❌ Local server not running. Please start with: make run-dev")
            return

        print("\n📊 Testing various message types:")
        print("-" * 60)

        success_count = 0
        total_tests = len(test_cases)

        for i, test in enumerate(test_cases, 1):
            print(f"\n Test {i}/{total_tests}")
            print(f"📤 Message: {test['message']}")
            print(f"🎯 Expected: {test['expected_intent']}")

            try:
                start_time = datetime.now()
                response = await client.post(
                    f"{base_url}/api/v1/chat/stable",
                    json={"message": test["message"], "session_id": f"test-{i}"},
                )
                duration = (datetime.now() - start_time).total_seconds() * 1000

                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Success in {duration:.0f}ms")
                    print(f"🤖 Agent: {data['agent_name']}")
                    print(f"💬 Response: {data['message'][:100]}...")
                    print(f"📊 Confidence: {data['confidence']:.2f}")
                    print(
                        f"🔧 Backend: {data['metadata'].get('agent_used', 'unknown')}"
                    )
                    success_count += 1
                else:
                    print(f"❌ Failed: {response.status_code}")
                    print(f"Error: {response.text}")

            except Exception as e:
                print(f"❌ Exception: {str(e)}")

        print("\n" + "=" * 60)
        print(
            f"📈 Results: {success_count}/{total_tests} successful ({success_count/total_tests*100:.0f}%)"
        )

        if success_count == total_tests:
            print("🎉 Perfect! 100% success rate!")
        elif success_count >= total_tests * 0.9:
            print("✅ Excellent! Above 90% success rate")
        else:
            print("⚠️  Needs improvement - below 90% success rate")


if __name__ == "__main__":
    asyncio.run(test_stable_endpoint())
