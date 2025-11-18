#!/usr/bin/env python3
"""Debug Maritaca provider initialization error"""

import os
import sys
import traceback

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set test environment variables
os.environ["JWT_SECRET_KEY"] = "test"
os.environ["SECRET_KEY"] = "test"
os.environ["LLM_PROVIDER"] = "maritaca"

try:
    print("1. Importing LLM providers...")
    from src.llm.providers import create_llm_manager

    print("2. Creating LLM Manager with maritaca...")
    manager = create_llm_manager(primary_provider="maritaca", enable_fallback=False)

    print("✅ Success! LLM Manager created")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

    print("\n\n3. Checking settings...")
    from src.core import settings

    print(f"   llm_provider: {settings.llm_provider}")
    print(f"   maritaca_api_key: {settings.maritaca_api_key}")
    print(f"   maritaca_model: {settings.maritaca_model}")
