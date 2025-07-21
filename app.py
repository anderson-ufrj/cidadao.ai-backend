#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - FastAPI Backend for Hugging Face Spaces
Pure REST API for government transparency analysis
"""

import uvicorn
from src.api.app import app  # Import the FastAPI app directly

# HF Spaces entry point
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,  # HF Spaces default port
        log_level="info",
        access_log=True,
        reload=False  # Production mode
    )