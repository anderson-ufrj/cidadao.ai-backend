#!/usr/bin/env python3
"""
Debug script to trace Drummond import issues.
"""

import sys
import traceback

def test_import_chain():
    """Test the import chain to find where the error occurs."""
    
    print("=== DRUMMOND IMPORT DEBUG ===")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path}")
    print()
    
    # Test 1: Import BaseAgent
    print("1. Testing BaseAgent import...")
    try:
        from src.agents.deodoro import BaseAgent
        print("   ✓ BaseAgent imported successfully")
        
        # Check if shutdown is abstract
        import inspect
        methods = inspect.getmembers(BaseAgent, predicate=inspect.ismethod)
        for name, method in methods:
            if name == 'shutdown':
                print(f"   - shutdown method found: {method}")
                if hasattr(method, '__isabstractmethod__'):
                    print(f"   - Is abstract: {method.__isabstractmethod__}")
    except Exception as e:
        print(f"   ✗ Failed to import BaseAgent: {e}")
        traceback.print_exc()
        return
    
    # Test 2: Import CommunicationAgent directly
    print("\n2. Testing CommunicationAgent import...")
    try:
        from src.agents.drummond import CommunicationAgent
        print("   ✓ CommunicationAgent imported successfully")
        
        # Check if shutdown is implemented
        if hasattr(CommunicationAgent, 'shutdown'):
            print("   ✓ shutdown method exists in CommunicationAgent")
            
            # Check method resolution order
            print(f"   - MRO: {[c.__name__ for c in CommunicationAgent.__mro__]}")
            
            # Check abstract methods
            abstract_methods = getattr(CommunicationAgent, '__abstractmethods__', set())
            print(f"   - Abstract methods: {abstract_methods}")
            
    except Exception as e:
        print(f"   ✗ Failed to import CommunicationAgent: {e}")
        traceback.print_exc()
        return
    
    # Test 3: Try to instantiate
    print("\n3. Testing CommunicationAgent instantiation...")
    try:
        agent = CommunicationAgent()
        print("   ✓ CommunicationAgent instantiated successfully")
    except Exception as e:
        print(f"   ✗ Failed to instantiate CommunicationAgent: {e}")
        traceback.print_exc()
        
        # Additional diagnostics
        print("\n   Additional diagnostics:")
        try:
            from src.agents.drummond import CommunicationAgent
            print(f"   - Class type: {type(CommunicationAgent)}")
            print(f"   - Base classes: {CommunicationAgent.__bases__}")
            
            # List all methods
            print("   - All methods:")
            for attr in dir(CommunicationAgent):
                if not attr.startswith('_'):
                    obj = getattr(CommunicationAgent, attr)
                    if callable(obj):
                        print(f"     * {attr}: {type(obj)}")
                        
        except Exception as e2:
            print(f"   - Failed diagnostics: {e2}")
    
    # Test 4: Test the factory
    print("\n4. Testing chat_drummond_factory...")
    try:
        from src.api.routes.chat_drummond_factory import get_drummond_agent
        print("   ✓ Factory imported successfully")
    except Exception as e:
        print(f"   ✗ Failed to import factory: {e}")
        traceback.print_exc()
    
    print("\n=== END DEBUG ===")

if __name__ == "__main__":
    test_import_chain()