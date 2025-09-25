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
    
    # Log startup with version
    print("=" * 60)
    print(f"🚀 Starting Cidadão.AI Full Multi-Agent System v2.0")
    print(f"📅 Deploy timestamp: 2025-09-25 17:46:00 -03")
    print(f"🔧 VERSION: MAIN BRANCH - Full multi-agent system")
    print(f"✅ Fixed: Lazy initialization + MasterAgent import")
    print(f"🤖 All agents available: Drummond, Zumbi, Anita, Tiradentes, and more!")
    print(f"🌐 Running on port {port}")
    print("=" * 60)
    
    # Run the complete API with HuggingFace Spaces compatibility
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        forwarded_allow_ips="*",  # Allow all proxy IPs for HuggingFace
        proxy_headers=True,  # Trust proxy headers from HuggingFace
        root_path="",  # Important for correct URL generation
        access_log=True  # Enable access logging
    )