#!/usr/bin/env python3
"""
Minimal test to verify CommunicationAgent can be imported and instantiated.
This simulates what happens on HuggingFace Spaces.
"""

import os
import sys

# Add src to path like HuggingFace does
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_minimal_import():
    print("=== MINIMAL DRUMMOND TEST ===")

    # Step 1: Try importing just the class
    try:
        print("1. Importing CommunicationAgent class...")
        from src.agents.drummond import CommunicationAgent

        print("   ✓ Import successful")
    except Exception as e:
        print(f"   ✗ Import failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Step 2: Check if it's a proper class
    print("\n2. Checking class structure...")
    print(f"   - Type: {type(CommunicationAgent)}")
    print(f"   - Base classes: {CommunicationAgent.__bases__}")
    print(f"   - Module: {CommunicationAgent.__module__}")

    # Check abstract methods
    abstract_methods = getattr(CommunicationAgent, "__abstractmethods__", None)
    if abstract_methods:
        print(f"   - Abstract methods remaining: {abstract_methods}")
    else:
        print("   - No abstract methods remaining")

    # Step 3: Try instantiation without any dependencies
    print("\n3. Testing instantiation...")
    try:
        # Mock the logger to avoid dependency issues
        import logging

        logging.basicConfig(level=logging.INFO)

        # Try to create instance
        agent = CommunicationAgent()
        print("   ✓ Instantiation successful")
        return True
    except Exception as e:
        print(f"   ✗ Instantiation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_minimal_import()
    print(f"\n=== TEST {'PASSED' if success else 'FAILED'} ===")
    sys.exit(0 if success else 1)
