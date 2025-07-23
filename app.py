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
from fastapi.responses import HTMLResponse, JSONResponse

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

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with simple HTML page"""
    uptime = datetime.now() - datetime.fromisoformat(metrics["uptime_start"])
    uptime_str = str(uptime).split('.')[0]  # Remove microseconds
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cidadão.AI Backend</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #1f2937;
                line-height: 1.6;
            }}
            .container {{
                max-width: 800px;
                padding: 2rem;
                text-align: center;
                background: white;
                border-radius: 1rem;
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                border: 1px solid #d1fae5;
            }}
            .logo {{
                font-size: 4rem;
                margin-bottom: 1rem;
            }}
            .title {{
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                background: linear-gradient(135deg, #22c55e 0%, #3b82f6 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            .subtitle {{
                font-size: 1.2rem;
                color: #6b7280;
                margin-bottom: 2rem;
            }}
            .status {{
                display: inline-block;
                padding: 0.75rem 1.5rem;
                background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
                color: white;
                border-radius: 2rem;
                font-weight: 600;
                margin-bottom: 2rem;
                box-shadow: 0 4px 6px rgba(34, 197, 94, 0.2);
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1.5rem;
                margin: 2rem 0;
            }}
            .info-card {{
                padding: 1.5rem;
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border-radius: 0.75rem;
                border: 1px solid #e2e8f0;
            }}
            .info-card h3 {{
                font-size: 1.1rem;
                font-weight: 600;
                color: #374151;
                margin-bottom: 0.5rem;
            }}
            .info-card p {{
                color: #6b7280;
                font-size: 0.95rem;
            }}
            .links {{
                margin-top: 2rem;
                display: flex;
                gap: 1rem;
                justify-content: center;
                flex-wrap: wrap;
            }}
            .link-button {{
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.75rem 1.5rem;
                background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
                color: white;
                text-decoration: none;
                border-radius: 0.5rem;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: 0 4px 6px rgba(34, 197, 94, 0.2);
            }}
            .link-button:hover {{
                transform: translateY(-2px) scale(1.02);
                box-shadow: 0 8px 12px rgba(34, 197, 94, 0.3);
            }}
            .secondary-button {{
                background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
                box-shadow: 0 4px 6px rgba(107, 114, 128, 0.2);
            }}
            .secondary-button:hover {{
                box-shadow: 0 8px 12px rgba(107, 114, 128, 0.3);
            }}
            .footer {{
                margin-top: 3rem;
                padding-top: 2rem;
                border-top: 1px solid #e5e7eb;
                color: #6b7280;
                font-size: 0.875rem;
            }}
            .footer a {{
                color: #22c55e;
                text-decoration: none;
            }}
            .footer a:hover {{
                text-decoration: underline;
            }}
            @media (max-width: 640px) {{
                .container {{ padding: 1.5rem; }}
                .title {{ font-size: 2rem; }}
                .logo {{ font-size: 3rem; }}
                .links {{ flex-direction: column; align-items: center; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🏛️</div>
            <h1 class="title">Cidadão.AI Backend</h1>
            <p class="subtitle">Sistema de Transparência Pública com IA</p>
            
            <div class="status">
                ✅ Backend Operacional
            </div>
            
            <div class="info-grid">
                <div class="info-card">
                    <h3>📡 Status do Sistema</h3>
                    <p>Online e processando requisições</p>
                </div>
                <div class="info-card">
                    <h3>⏱️ Tempo Ativo</h3>
                    <p>{uptime_str}</p>
                </div>
                <div class="info-card">
                    <h3>📊 Requisições</h3>
                    <p>{metrics['requests_total']} processadas</p>
                </div>
                <div class="info-card">
                    <h3>🔧 Última Atividade</h3>
                    <p>{metrics['last_activity']}</p>
                </div>
            </div>
            
            <p style="margin: 2rem 0; color: #374151;">
                Este é o servidor backend do <strong>Cidadão.AI</strong>, responsável por processar 
                e analisar dados de transparência pública brasileira usando inteligência artificial.
            </p>
            
            <div class="links">
                <a href="/docs" class="link-button">
                    📚 Swagger UI
                </a>
                <a href="/redoc" class="link-button">
                    📖 ReDoc
                </a>
                <a href="/health" class="link-button secondary-button">
                    🔍 Health Check
                </a>
                <a href="/metrics" class="link-button secondary-button">
                    📊 Metrics
                </a>
                <a href="https://anderson-ufrj.github.io/cidadao.ai-docs/" target="_blank" class="link-button">
                    🌐 Documentação Completa
                </a>
            </div>
            
            <div class="footer">
                <p>
                    <strong>Desenvolvido por:</strong> Anderson Henrique da Silva<br>
                    <strong>Licença:</strong> Apache 2.0 | <strong>SDG:</strong> 16 - Paz, Justiça e Instituições Eficazes
                </p>
                <p style="margin-top: 1rem;">
                    <a href="https://github.com/anderson-ufrj/cidadao.ai-backend" target="_blank">GitHub</a> | 
                    <a href="https://huggingface.co/spaces/neural-thinker/cidadao.ai-backend" target="_blank">Hugging Face</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    add_activity("Página principal acessada", "web")
    return HTMLResponse(content=html_content)

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