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
    
    print(f"🚀 Starting Cidadão.AI Full API on {host}:{port}")
    print("✅ WebSocket support enabled")
    print("✅ All API endpoints available")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=False
    )