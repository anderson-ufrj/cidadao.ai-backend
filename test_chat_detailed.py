#!/usr/bin/env python3
"""
Detailed test for chat endpoints with exact response format
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://neural-thinker-cidadao-ai-backend.hf.space"

def test_chat_message_detailed():
    """Test main chat endpoint and print full response"""
    print("\n🔍 Testing /api/v1/chat/message with full response...")
    
    payload = {
        "message": "Olá, como você pode me ajudar?",
        "session_id": f"test-{datetime.now().timestamp()}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/message",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print("\nFull Response:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error: {e}")
        print(f"Response Text: {response.text if 'response' in locals() else 'No response'}")

def test_chat_simple_detailed():
    """Test simple chat endpoint"""
    print("\n🔍 Testing /api/v1/chat/simple...")
    
    payload = {
        "message": "Olá, como você pode me ajudar?",
        "session_id": f"test-{datetime.now().timestamp()}"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/simple",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("\nFull Response:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_available_endpoints():
    """Check which endpoints are available"""
    print("\n📋 Checking available endpoints...")
    
    endpoints = [
        "/api/v1/chat/message",
        "/api/v1/chat/simple",
        "/api/v1/chat/agents",
        "/api/v1/chat/suggestions",
        "/api/v1/chat/stream",
        "/docs",
        "/openapi.json"
    ]
    
    for endpoint in endpoints:
        try:
            if endpoint in ["/api/v1/chat/message", "/api/v1/chat/simple", "/api/v1/chat/stream"]:
                # POST endpoints
                response = requests.post(
                    f"{BASE_URL}{endpoint}",
                    json={"message": "test", "session_id": "test"},
                    timeout=5
                )
            else:
                # GET endpoints
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            
            print(f"{endpoint}: {response.status_code} {'✅' if response.status_code != 404 else '❌'}")
        except Exception as e:
            print(f"{endpoint}: Error - {str(e)[:50]}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔬 Detailed Chat Endpoint Test")
    print(f"🌐 URL: {BASE_URL}")
    print("=" * 60)
    
    test_available_endpoints()
    test_chat_message_detailed()
    test_chat_simple_detailed()