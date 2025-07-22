#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Simple FastAPI Backend for Hugging Face Spaces
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create simple FastAPI application
app = FastAPI(
    title="Cidadão.AI API",
    description="🏛️ API para transparência pública brasileira",
    version="1.0.0"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Cidadão.AI - Plataforma de Transparência Pública",
        "version": "1.0.0",
        "description": "API para investigação inteligente de dados públicos brasileiros",
        "documentation": "/docs",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "cidadao-ai-backend"}

# HF Spaces entry point
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
        log_level="info",
        access_log=True,
        reload=False
    )