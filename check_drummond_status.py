#!/usr/bin/env python3
"""Check Drummond debug status"""
import requests
import json

url = "https://neural-thinker-cidadao-ai-backend.hf.space/api/v1/chat/debug/drummond-status"

try:
    response = requests.get(url)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")