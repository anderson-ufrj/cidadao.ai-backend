"""
Module: api.app
Description: FastAPI application for Cidadão.AI transparency platform
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware  # Disabled for HuggingFace
from fastapi.responses import JSONResponse
# Swagger UI imports removed - using FastAPI defaults now

from src.core import get_logger, settings
from src.core.exceptions import CidadaoAIError, create_error_response
from src.core.audit import audit_logger, AuditEventType, AuditSeverity, AuditContext
from src.api.routes import investigations, analysis, reports, health, auth, oauth, audit, chat, websocket_chat, batch, graphql, cqrs, resilience, observability, notifications, agents, orchestration, agent_metrics, visualization, geographic, tasks, transparency
from src.api.v1 import dados_gov
from src.api.middleware.rate_limiting import RateLimitMiddleware
from src.api.middleware.authentication import AuthenticationMiddleware
from src.api.middleware.logging_middleware import LoggingMiddleware
from src.api.middleware.security import SecurityMiddleware
from src.api.middleware.compression import CompressionMiddleware
from src.api.middleware.metrics_middleware import MetricsMiddleware, setup_http_metrics
from src.api.middleware.ip_whitelist import IPWhitelistMiddleware
from src.api.middleware.rate_limit import RateLimitMiddleware as RateLimitMiddlewareV2
from src.infrastructure.observability import (
    CorrelationMiddleware,
    tracing_manager,
    initialize_app_info
)


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager with enhanced audit logging."""
    # Startup
    logger.info("cidadao_ai_api_starting")
    
    # Log startup event
    await audit_logger.log_event(
        event_type=AuditEventType.SYSTEM_STARTUP,
        message=f"Cidadão.AI API started (env: {settings.app_env})",
        severity=AuditSeverity.LOW,
        details={
            "version": "1.0.0",
            "environment": settings.app_env,
            "debug": settings.debug,
            "security_enabled": True
        }
    )
    
    # Initialize observability
    tracing_manager.initialize()
    initialize_app_info(
        version="1.0.0",
        environment=settings.app_env,
        build_info={"deployment": "huggingface"}
    )
    
    # Setup HTTP metrics
    setup_http_metrics()
    
    # Initialize connection pools
    from src.db.session import init_database
    await init_database()
    
    # Initialize cache warming scheduler
    from src.services.cache_warming_service import cache_warming_service
    warming_task = asyncio.create_task(cache_warming_service.start_warming_scheduler())
    
    # Initialize memory system
    from src.services.memory_startup import setup_memory_on_startup, periodic_memory_optimization
    memory_agent = await setup_memory_on_startup()
    
    # Start periodic memory optimization if enabled
    memory_task = None
    if getattr(settings, "ENABLE_MEMORY_OPTIMIZATION", True):
        memory_task = asyncio.create_task(periodic_memory_optimization())
    
    yield
    
    # Shutdown
    logger.info("cidadao_ai_api_shutting_down")
    
    # Stop cache warming
    warming_task.cancel()
    try:
        await warming_task
    except asyncio.CancelledError:
        pass
    
    # Stop memory optimization
    if memory_task:
        memory_task.cancel()
        try:
            await memory_task
        except asyncio.CancelledError:
            pass
    
    # Cleanup memory system
    from src.services.memory_startup import cleanup_memory_on_shutdown
    await cleanup_memory_on_shutdown()
    
    # Log shutdown event
    await audit_logger.log_event(
        event_type=AuditEventType.SYSTEM_SHUTDOWN,
        message="Cidadão.AI API shutting down",
        severity=AuditSeverity.LOW
    )
    
    # Shutdown observability
    tracing_manager.shutdown()
    
    # Close database connections
    from src.db.session import close_database
    await close_database()


# Create FastAPI application
app = FastAPI(
    title="Cidadão.AI API",
    description="""
    # 🏛️ Plataforma de Transparência Pública com IA

    API para investigação inteligente de dados públicos brasileiros usando multi-agente de IA.

    ---

    ## 🎯 Funcionalidades Principais

    ### 🔍 Investigação
    Detecção automática de anomalias e irregularidades em contratos públicos, despesas governamentais e licitações.

    ### 📊 Análise
    Identificação de padrões, correlações e tendências em dados públicos através de algoritmos avançados de ML.

    ### 📝 Relatórios
    Geração automatizada de relatórios detalhados em linguagem natural com insights acionáveis.

    ### 🌐 Transparência
    Acesso democrático e simplificado a informações governamentais complexas.

    ---

    ## 🤖 Sistema Multi-Agente

    ### Agentes Investigadores
    - **Zumbi dos Palmares** 🗡️ - Detecção de anomalias e padrões suspeitos
    - **Anita Garibaldi** 🔍 - Análise de padrões temporais e correlações
    - **Tiradentes** 📋 - Geração de relatórios e documentação

    ### Agentes Especializados
    - **José Bonifácio** 🎭 - Análise de comportamento organizacional
    - **Maria Quitéria** ⚔️ - Detecção de fraudes e irregularidades
    - **Machado de Assis** ✍️ - Processamento de linguagem natural
    - **Drummond** 🎨 - Visualização e apresentação de dados

    ---

    ## 📦 Fontes de Dados

    - Portal da Transparência do Governo Federal
    - Tribunal de Contas dos Estados (TCE)
    - Portais CKAN de dados abertos
    - Dados.gov.br
    - APIs estaduais e municipais (2500+ municípios)

    ---

    ## 🔐 Autenticação

    A API usa autenticação JWT e suporta OAuth2 (Google, GitHub, Microsoft).
    Endpoints públicos disponíveis sem autenticação para demonstração.

    ---

    ## 📚 Versioning

    **Versão Atual**: v1.0.0
    **Base URL**: `/api/v1/`
    **Documentação**: `/docs` (Swagger) ou `/redoc` (ReDoc)

    Futuras versões da API serão disponibilizadas em `/api/v2/` mantendo backward compatibility.

    ---

    ## 🚀 Getting Started

    1. Obtenha uma API key em `/api/v1/api-keys`
    2. Autentique em `/api/v1/auth/login`
    3. Explore os endpoints de investigação em `/api/v1/investigations`
    4. Use o chat inteligente em `/api/v1/chat/message`

    """,
    version="1.0.0",
    contact={
        "name": "Cidadão.AI",
        "url": "https://github.com/anderson-ufrj/cidadao.ai",
        "email": "andersonhs27@gmail.com",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://github.com/anderson-ufrj/cidadao.ai/blob/main/LICENSE",
    },
    terms_of_service="https://github.com/anderson-ufrj/cidadao.ai/blob/main/TERMS.md",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    # Enhanced Swagger UI configuration
    swagger_ui_parameters={
        "syntaxHighlight.theme": "monokai",
        "tryItOutEnabled": True,
        "displayRequestDuration": True,
        "filter": True,
        "showExtensions": True,
        "showCommonExtensions": True,
        "persistAuthorization": True,
        "displayOperationId": False,
        "defaultModelsExpandDepth": 2,
        "defaultModelExpandDepth": 2,
        "docExpansion": "list",  # "list", "full", "none"
    }
)

# Add security middleware (order matters!)
app.add_middleware(SecurityMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Add compression middleware for mobile optimization
app.add_middleware(
    CompressionMiddleware,
    minimum_size=1024  # Compress responses > 1KB
)

# Add trusted host middleware for production
# DISABLED for HuggingFace Spaces - causes issues with proxy headers
# if settings.app_env == "production":
#     app.add_middleware(
#         TrustedHostMiddleware,
#         allowed_hosts=["api.cidadao.ai", "*.cidadao.ai", "*.hf.space", "*.huggingface.co"]
#     )
# else:
#     app.add_middleware(
#         TrustedHostMiddleware,
#         allowed_hosts=["localhost", "127.0.0.1", "*.cidadao.ai", "testserver"]
#     )

# Enhanced CORS middleware for Vercel integration
from src.api.middleware.cors_enhanced import setup_cors
setup_cors(app)

# Add observability middleware
app.add_middleware(CorrelationMiddleware, generate_request_id=True)

# Add metrics middleware for automatic HTTP metrics
app.add_middleware(MetricsMiddleware)

# Add compression middleware (exclude docs to prevent Swagger UI breakage)
from src.api.middleware.compression import add_compression_middleware
add_compression_middleware(
    app,
    minimum_size=settings.compression_min_size,
    gzip_level=settings.compression_gzip_level,
    brotli_quality=settings.compression_brotli_quality,
    exclude_paths={
        "/health", "/metrics", "/health/metrics",
        "/api/v1/ws", "/api/v1/observability",
        "/docs", "/redoc", "/openapi.json"  # Exclude docs to fix Swagger UI
    }
)

# Add streaming compression middleware (exclude docs)
from src.api.middleware.streaming_compression import StreamingCompressionMiddleware
app.add_middleware(
    StreamingCompressionMiddleware,
    minimum_size=256,
    compression_level=settings.compression_gzip_level,
    chunk_size=8192
)

# Add IP whitelist middleware (only in production)
if settings.is_production or settings.app_env == "staging":
    app.add_middleware(
        IPWhitelistMiddleware,
        enabled=True,
        excluded_paths=[
            "/health",
            "/healthz",
            "/ping",
            "/ready",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/metrics",
            "/static",
            "/favicon.ico",
            "/_next",
            "/api/v1/auth/login",
            "/api/v1/auth/register", 
            "/api/v1/auth/refresh",
            "/api/v1/public",
            "/api/v1/webhooks/incoming"
        ],
        strict_mode=False  # Allow requests if IP can't be determined
    )

# Add rate limiting middleware v2
app.add_middleware(
    RateLimitMiddlewareV2,
    default_tier="free",
    strategy="sliding_window"
)

# Add query tracking middleware for cache optimization
from src.api.middleware.query_tracking import QueryTrackingMiddleware
app.add_middleware(
    QueryTrackingMiddleware,
    tracked_paths=[
        "/api/v1/investigations",
        "/api/v1/contracts", 
        "/api/v1/analysis",
        "/api/v1/reports"
    ],
    sample_rate=0.1 if settings.is_production else 1.0  # 10% sampling in production
)


# Documentation endpoints are now handled by FastAPI defaults
# Using standard Swagger UI without customization for better compatibility


# Include routers with security
app.include_router(
    health.router,
    prefix="/health",
    tags=["Health Check"]
)

app.include_router(
    auth.router,
    tags=["Authentication"]
)

app.include_router(
    oauth.router,
    tags=["OAuth2"]
)

app.include_router(
    audit.router,
    tags=["Audit & Security"]
)

app.include_router(
    investigations.router,
    prefix="/api/v1/investigations",
    tags=["Investigations"]
)

app.include_router(
    analysis.router,
    prefix="/api/v1/analysis",
    tags=["Analysis"]
)

app.include_router(
    reports.router,
    prefix="/api/v1/reports",
    tags=["Reports"]
)

from src.api.routes import export
app.include_router(
    export.router,
    prefix="/api/v1/export",
    tags=["Export"]
)

app.include_router(
    chat.router,
    prefix="/api/v1/chat",
    tags=["Chat"]
)

app.include_router(
    websocket_chat.router,
    prefix="/api/v1",
    tags=["WebSocket"]
)

app.include_router(
    batch.router,
    tags=["Batch Operations"]
)

# GraphQL endpoint
app.include_router(
    graphql.router,
    tags=["GraphQL"]
)

# CQRS endpoints
app.include_router(
    cqrs.router,
    tags=["CQRS"]
)

# Resilience monitoring endpoints
app.include_router(
    resilience.router,
    tags=["Resilience"]
)

# Observability monitoring endpoints
app.include_router(
    observability.router,
    tags=["Observability"]
)

app.include_router(
    notifications.router,
    tags=["Notifications"]
)

# Import and include admin routes
from src.api.routes.admin import ip_whitelist as admin_ip_whitelist
from src.api.routes.admin import cache_warming as admin_cache_warming
from src.api.routes.admin import database_optimization as admin_db_optimization
from src.api.routes.admin import compression as admin_compression
from src.api.routes.admin import connection_pools as admin_conn_pools
from src.api.routes.admin import agent_lazy_loading as admin_lazy_loading
from src.api.routes import api_keys

app.include_router(
    admin_ip_whitelist.router,
    prefix="/api/v1/admin",
    tags=["Admin"]
)

app.include_router(
    admin_cache_warming.router,
    prefix="/api/v1/admin",
    tags=["Admin"]
)

app.include_router(
    admin_db_optimization.router,
    prefix="/api/v1/admin",
    tags=["Admin"]
)

app.include_router(
    admin_compression.router,
    prefix="/api/v1/admin",
    tags=["Admin"]
)

app.include_router(
    admin_conn_pools.router,
    prefix="/api/v1/admin",
    tags=["Admin"]
)

app.include_router(
    admin_lazy_loading.router,
    prefix="/api/v1/admin",
    tags=["Admin"]
)

app.include_router(
    api_keys.router,
    prefix="/api/v1",
    tags=["API Keys"]
)

app.include_router(
    dados_gov.router,
    prefix="/api/v1",
    tags=["Dados.gov.br"]
)

app.include_router(
    agents.router,
    prefix="/api/v1/agents",
    tags=["AI Agents"]
)

app.include_router(
    orchestration.router,
    prefix="/api/v1/orchestration",
    tags=["Agent Orchestration"]
)

app.include_router(
    agent_metrics.router,
    prefix="/api/v1/metrics",
    tags=["Agent Metrics"]
)

app.include_router(
    visualization.router,
    tags=["Data Visualization"]
)

app.include_router(
    geographic.router,
    tags=["Geographic Data"]
)

from src.api.routes import ml_pipeline
app.include_router(
    ml_pipeline.router,
    tags=["ML Pipeline"]
)

app.include_router(
    tasks.router,
    tags=["Tasks & Background Jobs"]
)

# Transparency APIs endpoints
app.include_router(
    transparency.router,
    prefix="/api/v1/transparency",
    tags=["Transparency APIs"]
)


# Global exception handler
@app.exception_handler(CidadaoAIError)
async def cidadao_ai_exception_handler(request, exc: CidadaoAIError):
    """Handle CidadãoAI custom exceptions."""
    logger.error(
        "api_exception_occurred",
        error_type=type(exc).__name__,
        error_message=exc.message,
        error_details=exc.details,
        path=request.url.path,
        method=request.method,
    )
    
    # Map exception types to HTTP status codes
    status_code_map = {
        "ValidationError": 400,
        "DataNotFoundError": 404,
        "AuthenticationError": 401,
        "UnauthorizedError": 403,
        "RateLimitError": 429,
        "LLMError": 503,
        "TransparencyAPIError": 502,
        "AgentExecutionError": 500,
    }
    
    status_code = status_code_map.get(exc.error_code, 500)
    error_response = create_error_response(exc, status_code)
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Enhanced HTTP exception handler with audit logging."""
    
    # Create audit context
    context = AuditContext(
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent"),
        host=request.headers.get("host")
    )
    
    # Log security-related errors
    if exc.status_code in [401, 403, 429]:
        await audit_logger.log_event(
            event_type=AuditEventType.UNAUTHORIZED_ACCESS,
            message=f"HTTP {exc.status_code}: {exc.detail}",
            severity=AuditSeverity.MEDIUM if exc.status_code != 429 else AuditSeverity.HIGH,
            success=False,
            error_code=str(exc.status_code),
            error_message=exc.detail,
            context=context
        )
    
    logger.warning(
        "http_exception_occurred",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "status_code": exc.status_code,
            "error": {
                "error": "HTTPException",
                "message": exc.detail,
                "details": {}
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Enhanced general exception handler with audit logging."""
    
    # Log unexpected errors with audit
    context = AuditContext(
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent"),
        host=request.headers.get("host")
    )
    
    await audit_logger.log_event(
        event_type=AuditEventType.API_ERROR,
        message=f"Unhandled exception: {str(exc)}",
        severity=AuditSeverity.HIGH,
        success=False,
        error_message=str(exc),
        details={"error_type": type(exc).__name__},
        context=context
    )
    
    logger.error(
        "unexpected_exception_occurred",
        error_type=type(exc).__name__,
        error_message=str(exc),
        path=request.url.path,
        method=request.method,
    )
    
    # Don't expose internal errors in production
    if settings.app_env == "production":
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "status_code": 500,
                "error": {
                    "error": "InternalServerError",
                    "message": "An unexpected error occurred",
                    "details": {}
                }
            }
        )
    else:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "status_code": 500,
                "error": {
                    "error": "InternalServerError",
                    "message": f"An unexpected error occurred: {str(exc)}",
                    "details": {"error_type": type(exc).__name__}
                }
            }
        )


# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Cidadão.AI - Plataforma de Transparência Pública",
        "version": "1.0.0",
        "description": "API para investigação inteligente de dados públicos brasileiros",
        "documentation": "/docs",
        "health": "/health",
        "status": "operational",
        "portal_integration": "active",
        "last_update": "2025-01-25 15:00:00 UTC"
    }


# Test Portal endpoint
@app.get("/test-portal", include_in_schema=False)
async def test_portal():
    """Test Portal da Transparência integration status."""
    import os
    from src.services.chat_data_integration import chat_data_integration
    
    # Test the service is available
    integration_available = False
    try:
        if chat_data_integration:
            integration_available = True
    except:
        pass
    
    return {
        "portal_integration": "enabled",
        "api_key_configured": bool(os.getenv("TRANSPARENCY_API_KEY")),
        "integration_service_available": integration_available,
        "endpoints": {
            "chat_message": "/api/v1/chat/message",
            "chat_stream": "/api/v1/chat/stream",
            "test_portal": "/api/v1/chat/test-portal/{query}",
            "debug_status": "/api/v1/chat/debug/portal-status"
        },
        "demo_mode": not bool(os.getenv("TRANSPARENCY_API_KEY")),
        "example_queries": [
            "Liste os últimos 3 contratos do ministério da saúde",
            "Mostre contratos com valor acima de 1 milhão",
            "Quais empresas têm mais contratos com o governo?"
        ]
    }

# API info endpoint
@app.get("/api/v1/info", tags=["General"])
async def api_info():
    """Get API information and capabilities."""
    return {
        "api": {
            "name": "Cidadão.AI API",
            "version": "1.0.0",
            "description": "Plataforma de transparência pública com IA",
        },
        "agents": {
            "investigator": {
                "description": "Detecção de anomalias e irregularidades",
                "capabilities": [
                    "Anomalias de preço",
                    "Concentração de fornecedores", 
                    "Padrões temporais suspeitos",
                    "Contratos duplicados",
                    "Irregularidades de pagamento"
                ]
            },
            "analyst": {
                "description": "Análise de padrões e correlações",
                "capabilities": [
                    "Tendências de gastos",
                    "Padrões organizacionais",
                    "Comportamento de fornecedores",
                    "Análise sazonal",
                    "Métricas de eficiência"
                ]
            },
            "reporter": {
                "description": "Geração de relatórios inteligentes",
                "capabilities": [
                    "Relatórios executivos",
                    "Análise detalhada",
                    "Múltiplos formatos",
                    "Linguagem natural"
                ]
            }
        },
        "data_sources": [
            "Portal da Transparência",
            "Contratos públicos",
            "Despesas governamentais",
            "Licitações",
            "Convênios",
            "Servidores públicos"
        ],
        "formats": [
            "JSON",
            "Markdown", 
            "HTML",
            "PDF (planned)"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers if not settings.debug else 1,
        log_level=settings.log_level.lower(),
    )