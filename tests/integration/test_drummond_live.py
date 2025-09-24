#!/usr/bin/env python3
"""Test Drummond agent on live HuggingFace deployment"""
import requests
import json

# Test the chat endpoint with a greeting
url = "https://neural-thinker-cidadao-ai-backend.hf.space/api/v1/chat/message"
headers = {"Content-Type": "application/json"}

# Test 1: Simple greeting (should route to Drummond)
print("Test 1: Testing greeting message...")
data = {"message": "Olá, pode me ajudar?"}
try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(response, 'text'):
        print(f"Raw response: {response.text}")

print("\n" + "="*50 + "\n")

# Test 2: Literary analysis request
print("Test 2: Testing literary analysis...")
data = {"message": "Analise o poema 'No meio do caminho tinha uma pedra' de Drummond"}
try:
    response = requests.post(url, json=data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(response, 'text'):
        print(f"Raw response: {response.text}")

print("\n" + "="*50 + "\n")

# Test 3: Check health endpoint
print("Test 3: Checking health endpoint...")
health_url = "https://neural-thinker-cidadao-ai-backend.hf.space/health"
try:
    response = requests.get(health_url)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")