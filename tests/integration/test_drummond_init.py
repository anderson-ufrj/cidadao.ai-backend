#!/usr/bin/env python3
"""Test Drummond initialization locally"""
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set necessary environment variables for testing
os.environ["GROQ_API_KEY"] = "dummy_key_for_test"
os.environ["JWT_SECRET_KEY"] = "test_secret"
os.environ["SECRET_KEY"] = "test_secret"

try:
    print("Testing Drummond agent initialization...")
    from src.agents.drummond import CommunicationAgent
    
    # Try to create agent
    print("Creating CommunicationAgent...")
    agent = CommunicationAgent()
    print("✓ Agent created successfully!")
    
    # Check if it has the necessary methods
    print(f"Has process method: {hasattr(agent, 'process')}")
    print(f"Has shutdown method: {hasattr(agent, 'shutdown')}")
    
except Exception as e:
    print(f"✗ Error creating agent: {e}")
    import traceback
    traceback.print_exc()