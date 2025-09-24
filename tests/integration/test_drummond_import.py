#!/usr/bin/env python3
"""Test Drummond import to debug the issue."""

import inspect

# Test direct import
try:
    from src.agents.drummond import CommunicationAgent
    print("✅ Import successful!")
    
    # Check abstract methods
    abstract_methods = getattr(CommunicationAgent, '__abstractmethods__', set())
    print(f"Abstract methods: {abstract_methods}")
    
    # Check if shutdown is implemented
    if hasattr(CommunicationAgent, 'shutdown'):
        print("✅ shutdown method exists")
        shutdown_method = getattr(CommunicationAgent, 'shutdown')
        print(f"   Is coroutine: {inspect.iscoroutinefunction(shutdown_method)}")
    else:
        print("❌ shutdown method NOT FOUND")
        
    # Check all methods
    all_methods = [m for m in dir(CommunicationAgent) if not m.startswith('_')]
    print(f"\nAll public methods: {all_methods}")
    
except Exception as e:
    print(f"❌ Import failed: {type(e).__name__}: {e}")
    
    # Try simpler import
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from src.agents.deodoro import BaseAgent
        print("\n✅ BaseAgent imported successfully")
        
        # Check BaseAgent abstract methods
        abstract_base = getattr(BaseAgent, '__abstractmethods__', set())
        print(f"BaseAgent abstract methods: {abstract_base}")
    except Exception as e2:
        print(f"❌ BaseAgent import also failed: {e2}")