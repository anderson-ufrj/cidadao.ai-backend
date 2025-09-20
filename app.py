#!/usr/bin/env python3
"""
Cidadão.AI Backend - Full Multi-Agent System for HuggingFace Spaces
This imports the complete API with all agents including Drummond
"""

import os
import sys

# Add src to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the complete FastAPI application with all agents
from src.api.app import app
import uvicorn

if __name__ == "__main__":
    # Get port from environment (HuggingFace uses 7860)
    port = int(os.getenv("PORT", 7860))
    
    # Log startup
    print(f"🚀 Starting Cidadão.AI Full Multi-Agent System on port {port}")
    print("🤖 All agents available: Drummond, Zumbi, Anita, Tiradentes, and more!")
    
    # Run the complete API
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        forwarded_allow_ips="*",  # Allow all proxy IPs for HuggingFace
        proxy_headers=True  # Trust proxy headers from HuggingFace
    )