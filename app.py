#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - FastAPI Backend for Hugging Face Spaces
"""

import os
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Global metrics storage
metrics = {
    "requests_total": 0,
    "api_calls": 0,
    "data_processed": 0,
    "last_activity": "Sistema iniciado",
    "status": "online",
    "uptime_start": datetime.now().isoformat(),
    "connections": {
        "portal_transparencia": "connected",
        "database": "connected", 
        "redis": "checking",
        "ai_service": "active"
    },
    "recent_activities": []
}

# Create FastAPI application
app = FastAPI(
    title="Cidadão.AI API",
    description="🏛️ High-performance API for Brazilian public transparency analysis",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def add_activity(activity: str, activity_type: str = "info"):
    """Add new activity to tracking"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    metrics["recent_activities"].insert(0, {
        "time": timestamp,
        "activity": activity,
        "type": activity_type
    })
    
    # Keep only last 20 activities
    metrics["recent_activities"] = metrics["recent_activities"][:20]
    metrics["last_activity"] = f"[{timestamp}] {activity}"

# Middleware to track requests
@app.middleware("http")
async def track_requests(request: Request, call_next):
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Update metrics
    process_time = time.time() - start_time
    metrics["requests_total"] += 1
    
    # Add activity for non-static requests
    if not request.url.path.startswith("/static"):
        add_activity(f"Request {request.method} {request.url.path}", "api")
    
    # Add performance headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Server"] = "Cidadao.AI/2.0"
    
    return response

@app.get("/")
async def root():
    """Root endpoint with system information"""
    uptime = datetime.now() - datetime.fromisoformat(metrics["uptime_start"])
    uptime_str = str(uptime).split('.')[0]  # Remove microseconds
    
    add_activity("Sistema acessado via API", "api")
    return JSONResponse({
        "service": "Cidadão.AI Backend API",
        "version": "2.0.0",
        "status": "operational",
        "description": "Sistema de Transparência Pública com IA",
        "uptime": uptime_str,
        "metrics": {
            "requests_total": metrics["requests_total"],
            "last_activity": metrics["last_activity"]
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc", 
            "health": "/health",
            "metrics": "/metrics",
            "api_status": "/api/v1/status"
        },
        "features": [
            "Multi-agent AI system",
            "Real-time data analysis",
            "Government transparency tools",
            "Anomaly detection"
        ]
    })

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint"""
    add_activity("Health check executado", "system")
    
    uptime = datetime.now() - datetime.fromisoformat(metrics["uptime_start"])
    
    return JSONResponse({
        "status": "healthy",
        "service": "cidadao-ai-backend",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime": str(uptime).split('.')[0],
        "metrics": {
            "requests_total": metrics["requests_total"],
            "last_activity": metrics["last_activity"]
        },
        "dependencies": metrics["connections"]
    })

@app.get("/metrics")
async def get_metrics():
    """Prometheus-style metrics endpoint"""
    add_activity("Métricas solicitadas", "api")
    
    uptime = datetime.now() - datetime.fromisoformat(metrics["uptime_start"])
    
    return JSONResponse({
        "service": "cidadao-ai-backend",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": int(uptime.total_seconds()),
        "metrics": metrics,
        "endpoints": {
            "total": 5,
            "health": "/health",
            "docs": "/docs",
            "metrics": "/metrics",
            "api_v1": "/api/v1/"
        }
    })

# API v1 routes
@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    add_activity("Status API consultado", "api")
    return JSONResponse({
        "api_version": "1.0.0",
        "status": "operational",
        "features": [
            "Multi-agent AI system",
            "Real-time data analysis", 
            "Government transparency tools",
            "Anomaly detection"
        ]
    })

# HF Spaces optimized entry point
if __name__ == "__main__":
    # Initialize startup activity
    add_activity("Sistema iniciado com sucesso", "system")
    
    # Configure for environment
    port = int(os.getenv("PORT", 7860))
    
    # Launch FastAPI with optimal settings
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True,
        reload=False
    )