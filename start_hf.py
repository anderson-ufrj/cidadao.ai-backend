#!/usr/bin/env python3
"""
HuggingFace Spaces Entry Point for Full API
Runs the complete Cidadão.AI API with WebSocket support
"""
import os
import sys
import uvicorn
from pathlib import Path

# Load HuggingFace-specific environment
env_file = Path(__file__).parent / ".env.hf"
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file, override=True)

# Force HuggingFace port
os.environ["PORT"] = "7860"
os.environ["DATABASE_URL"] = os.environ.get("DATABASE_URL", "sqlite:///./cidadao.db")

# Import the FastAPI app
from src.api.app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("="*60)
    print("🚀 Starting Cidadão.AI Full API - VERSION 2025-09-20 13:46:00")
    print("🔧 FIXED: Lazy initialization for chat service")
    print("🔧 FIXED: MasterAgent import added")
    print(f"🌐 Running on {host}:{port}")
    print("✅ WebSocket support enabled")
    print("✅ All API endpoints available")
    print("="*60)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=False,
        forwarded_allow_ips="*",  # Allow all proxy IPs for HuggingFace
        proxy_headers=True  # Trust proxy headers from HuggingFace
    )