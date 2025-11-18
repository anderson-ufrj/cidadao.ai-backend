#!/usr/bin/env python3
"""Test if we can import InvestigatorAgent from zumbi.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("Testing InvestigatorAgent Import")
print("=" * 80 + "\n")

# Test 1: Direct import from zumbi.py
print("Test 1: Direct import from zumbi.py")
try:
    from src.agents.zumbi import InvestigatorAgent

    print(f"✅ SUCCESS: InvestigatorAgent imported")
    print(f"   Class name: {InvestigatorAgent.__name__}")
    print(f"   Module: {InvestigatorAgent.__module__}\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")

# Test 2: Try importing ZumbiAgent (should fail or use alias)
print("Test 2: Try importing ZumbiAgent from zumbi.py")
try:
    from src.agents.zumbi import ZumbiAgent  # This should fail

    print(f"✅ ZumbiAgent exists in zumbi.py (unexpected!)")
    print(f"   Class name: {ZumbiAgent.__name__}\n")
except ImportError as e:
    print(f"❌ EXPECTED FAILURE: {e}")
    print(f"   (This is correct - zumbi.py only exports InvestigatorAgent)\n")

# Test 3: Import from src.agents (should use lazy loading)
print("Test 3: Import from src.agents using lazy loading")
try:
    from src.agents import InvestigatorAgent as LazyInvestigator

    print(f"✅ SUCCESS: InvestigatorAgent via lazy loading")
    print(f"   Class name: {LazyInvestigator.__name__}\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")

# Test 4: Try ZumbiAgent alias from src.agents
print("Test 4: Try ZumbiAgent alias from src.agents")
try:
    from src.agents import ZumbiAgent as AliasedZumbi

    print(f"✅ SUCCESS: ZumbiAgent alias works")
    print(f"   Class name: {AliasedZumbi.__name__}")
    print(f"   Is same as InvestigatorAgent: {AliasedZumbi is InvestigatorAgent}\n")
except Exception as e:
    print(f"❌ FAILED: {e}\n")

print("=" * 80)
print("Summary:")
print("- InvestigatorAgent is the real class in zumbi.py")
print("- ZumbiAgent should be an alias in src.agents.__init__.py")
print("- chat.py AGENT_MAP should use 'InvestigatorAgent' not 'ZumbiAgent'")
print("=" * 80)
