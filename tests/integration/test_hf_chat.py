#!/usr/bin/env python3
"""
Test script for HuggingFace Spaces chat endpoints
Tests both main and simple chat endpoints with Maritaca AI
"""

from datetime import datetime

import requests

# HuggingFace Spaces URL
BASE_URL = "https://neural-thinker-cidadao-ai-backend.hf.space"


def test_health():
    """Test if API is running"""
    print("\n1️⃣ Testing API Health...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ API Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_docs():
    """Test if API docs are accessible"""
    print("\n2️⃣ Testing API Documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"✅ Docs Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Docs check failed: {e}")
        return False


def test_simple_chat():
    """Test simple chat endpoint with Maritaca AI"""
    print("\n3️⃣ Testing Simple Chat Endpoint (Maritaca AI direct)...")

    test_messages = [
        "Olá, como você pode me ajudar?",
        "Quais são os gastos públicos mais recentes?",
        "Me explique sobre transparência governamental",
    ]

    for message in test_messages:
        print(f"\n📤 Sending: {message}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/chat/simple",
                json={
                    "message": message,
                    "session_id": f"test-session-{datetime.now().timestamp()}",
                },
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response Status: {response.status_code}")
                print(f"📥 Assistant: {data['response'][:200]}...")
                print(f"🤖 Agent Used: {data.get('agent_used', 'Unknown')}")
            else:
                print(f"⚠️ Status: {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"❌ Error: {e}")


def test_main_chat():
    """Test main chat endpoint with full agent system"""
    print("\n4️⃣ Testing Main Chat Endpoint (Full Agent System)...")

    test_messages = [
        {"message": "Oi, tudo bem?", "expected_agent": "Drummond"},
        {
            "message": "Investigue contratos suspeitos em São Paulo",
            "expected_agent": "Abaporu/Zumbi",
        },
        {"message": "Análise de gastos com educação", "expected_agent": "Abaporu"},
    ]

    for test in test_messages:
        print(f"\n📤 Sending: {test['message']}")
        print(f"🎯 Expected Agent: {test['expected_agent']}")

        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/chat/message",
                json={
                    "message": test["message"],
                    "session_id": f"test-session-{datetime.now().timestamp()}",
                },
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response Status: {response.status_code}")
                print(f"📥 Response: {data['response'][:200]}...")
                print(f"🤖 Agent: {data.get('agent_name', 'Unknown')}")
                print(f"💬 Type: {data.get('response_type', 'Unknown')}")
            else:
                print(f"⚠️ Status: {response.status_code}")
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"❌ Error: {e}")


def test_chat_suggestions():
    """Test chat suggestions endpoint"""
    print("\n5️⃣ Testing Chat Suggestions...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/chat/suggestions", params={"limit": 5}
        )

        if response.status_code == 200:
            suggestions = response.json()
            print(f"✅ Found {len(suggestions)} suggestions:")
            for idx, suggestion in enumerate(suggestions[:3], 1):
                print(f"  {idx}. {suggestion['text']}")
        else:
            print(f"⚠️ Status: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all tests"""
    print("🚀 Testing Cidadão.AI Backend on HuggingFace Spaces")
    print("=" * 60)
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"🕐 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Run tests
    if test_health():
        test_docs()
        test_simple_chat()
        test_main_chat()
        test_chat_suggestions()

    print("\n" + "=" * 60)
    print("✅ Tests completed!")
    print("\n💡 Integration Tips for Frontend:")
    print("1. Use /api/v1/chat/simple for reliable Maritaca AI responses")
    print("2. Use /api/v1/chat/message for full agent capabilities")
    print("3. Handle both 200 (success) and 500 (fallback) responses")
    print("4. Check the 'agent_used' field to know which agent responded")


if __name__ == "__main__":
    main()
