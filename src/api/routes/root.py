"""API root endpoint - Welcome and system information."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Request

from src.core.config import settings

router = APIRouter()


@router.get("/", tags=["Root"], summary="API Welcome")
async def root(request: Request) -> dict[str, Any]:
    """
    Welcome endpoint for the Cidadão.AI API.

    Returns system information, available endpoints, and quick start guide.
    """
    return {
        "message": "🇧🇷 Welcome to Cidadão.AI API",
        "version": "1.0.0",
        "description": "Multi-agent AI system for Brazilian government transparency analysis",
        "status": "operational",
        "timestamp": datetime.now(UTC).isoformat(),
        "documentation": {
            "swagger_ui": f"{str(request.base_url)}docs",
            "redoc": f"{str(request.base_url)}redoc",
            "openapi_json": f"{str(request.base_url)}openapi.json",
        },
        "endpoints": {
            "health": "/health",
            "metrics": "/health/metrics",
            "agents": "/api/v1/agents",
            "chat": "/api/v1/chat",
            "investigations": "/api/v1/investigations",
            "federal_apis": "/api/v1/federal",
            "orchestration": "/api/v1/orchestration",
        },
        "features": {
            "multi_agent_system": "16 specialized AI agents with Brazilian identities",
            "government_apis": "30+ federal and state transparency APIs integrated",
            "real_time_chat": "Server-Sent Events (SSE) streaming responses",
            "investigation_engine": "Automated anomaly detection and pattern analysis",
            "federal_data": "IBGE, PNCP, Portal da Transparência, and more",
        },
        "agents": {
            "available": 16,
            "tier_1": [
                "Zumbi dos Palmares (Anomaly Detection)",
                "Anita Garibaldi (Pattern Analysis)",
                "Oxóssi (Data Hunting)",
                "Lampião (Regional Analysis)",
                "Ayrton Senna (Semantic Routing)",
            ],
            "tier_2": [
                "Tiradentes (Report Generation)",
                "Oscar Niemeyer (Data Aggregation)",
                "Machado de Assis (Textual Analysis)",
                "José Bonifácio (Legal Analysis)",
                "Maria Quitéria (Security Auditing)",
            ],
            "tier_3": [
                "Abaporu (Master Agent)",
                "Nanã (Memory)",
                "Dandara (Social Equity)",
            ],
        },
        "quick_start": {
            "1_view_agents": "GET /api/v1/agents - List all available agents",
            "2_chat": "POST /api/v1/chat - Chat with an agent (SSE streaming)",
            "3_investigate": "POST /api/v1/investigations - Create investigation",
            "4_federal_data": "GET /api/v1/federal/ibge/states - Example federal API",
        },
        "support": {
            "github": "https://github.com/anderson-ntlabs/cidadao.ai-backend",
            "documentation": "See /docs for interactive API documentation",
            "issues": "https://github.com/anderson-ntlabs/cidadao.ai-backend/issues",
        },
        "production": {
            "environment": settings.app_env,
            "railway": "https://cidadao-api-production.up.railway.app",
            "uptime_since": "2025-10-07",
            "uptime_percentage": "99.9%",
        },
    }
