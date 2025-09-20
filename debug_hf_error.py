#!/usr/bin/env python3
"""Debug script to understand the HuggingFace error"""

print("=== Debugging HuggingFace Import Error ===\n")

# Check if we can find where the error is really coming from
import re

log_line = '{"event": "Failed to initialize Drummond agent: Can\'t instantiate abstract class CommunicationAgent with abstract method shutdown", "logger": "src.api.routes.chat", "level": "error", "timestamp": "2025-09-20T16:17:42.475125Z", "filename": "chat.py", "func_name": "<module>", "lineno": 33}'

print("Log says:")
print(f"- File: chat.py")
print(f"- Line: 33")
print(f"- Function: <module> (module-level code)")
print(f"- Error: Can't instantiate abstract class CommunicationAgent with abstract method shutdown")

print("\nThis suggests that somewhere at the module level (not inside a function),")
print("there's an attempt to instantiate CommunicationAgent directly.")
print("\nBut line 33 is just a comment. Possible explanations:")
print("1. Line numbers are off due to imports or preprocessing")
print("2. There's a hidden try/except block wrapping an import")
print("3. The error is actually from a different file that's imported")
print("4. MasterAgent (line 35) might be trying to instantiate CommunicationAgent")

print("\nLet's check if MasterAgent exists...")

try:
    from src.agents.abaporu import MasterAgent
    print("✓ MasterAgent found in abaporu.py")
except ImportError as e:
    print(f"✗ MasterAgent not found: {e}")
    print("  This would cause an error at line 35!")
    
print("\nThe real issue might be that MasterAgent is not imported in chat.py!")