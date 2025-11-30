"""
Module: api.app
Description: FastAPI application for Cidadão.AI transparency platform
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.docs import get_swagger_ui_html

# from fastapi.middleware.trustedhost import TrustedHostMiddleware  # Disabled for HuggingFace
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.middleware.compression import CompressionMiddleware
from src.api.middleware.logging_middleware import LoggingMiddleware
from src.api.middleware.metrics_middleware import MetricsMiddleware, setup_http_metrics
from src.api.middleware.rate_limit import RateLimitMiddleware
from src.api.routes import (
    agent_metrics,
    agents,
    analysis,
    audit,
    auth,
    batch,
    chat,
    chat_investigative,
    cqrs,
    debug,
    federal_apis,
    geographic,
    graphql,
    health,
    investigations,
    network,
    notifications,
    oauth,
    observability,
    orchestration,
    reports,
    resilience,
    root,
    tasks,
    transparency,
    transparency_coverage,
    visualization,
    voice,
    websocket_chat,
)
from src.api.v1 import dados_gov
from src.core import get_logger, settings
from src.core.audit import AuditContext, AuditEventType, AuditSeverity, audit_logger
from src.core.exceptions import CidadaoAIError, create_error_response
from src.infrastructure.observability import (
    CorrelationMiddleware,
    initialize_app_info,
    tracing_manager,
)
from src.infrastructure.observability.grafana_cloud_pusher import grafana_pusher

# Swagger UI imports removed - using FastAPI defaults now


logger = get_logger(__name__)

# HTTP status code constants
HTTP_RATE_LIMIT = 429


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
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
            "security_enabled": True,
        },
    )

    # Initialize observability
    tracing_manager.initialize()
    initialize_app_info(
        version="1.0.0",
        environment=settings.app_env,
        build_info={"deployment": "huggingface"},
    )

    # Setup HTTP metrics
    setup_http_metrics()

    # Initialize connection pools
    from src.db.session import init_database

    await init_database()

    # Run database migrations at startup (Railway runtime has access to internal network)
    try:
        logger.info("running_alembic_migrations")
        from alembic import command
        from alembic.config import Config

        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("alembic_migrations_completed")
    except Exception as e:
        logger.error(
            "alembic_migrations_failed", error=str(e), error_type=type(e).__name__
        )
        # Don't fail startup if migrations fail - allow app to start with existing schema
        # This prevents blocking the app if migrations are already applied
        logger.warning("continuing_startup_despite_migration_failure")

    # Initialize cache warming scheduler
    from src.services.cache_warming_service import cache_warming_service

    warming_task = asyncio.create_task(cache_warming_service.start_warming_scheduler())

    # Initialize memory system
    from src.services.memory_startup import (
        periodic_memory_optimization,
        setup_memory_on_startup,
    )

    # Setup memory agent (return value not used but initialization is needed)
    await setup_memory_on_startup()

    # Start periodic memory optimization if enabled
    memory_task = None
    if getattr(settings, "ENABLE_MEMORY_OPTIMIZATION", True):
        memory_task = asyncio.create_task(periodic_memory_optimization())

    # Start Grafana Cloud metrics push
    await grafana_pusher.start()

    yield

    # Shutdown
    logger.info("cidadao_ai_api_shutting_down")

    # Stop cache warming
    warming_task.cancel()
    with suppress(asyncio.CancelledError):
        await warming_task

    # Stop memory optimization
    if memory_task:
        memory_task.cancel()
        with suppress(asyncio.CancelledError):
            await memory_task

    # Stop Grafana Cloud metrics push
    await grafana_pusher.stop()

    # Cleanup memory system
    from src.services.memory_startup import cleanup_memory_on_shutdown

    await cleanup_memory_on_shutdown()

    # Log shutdown event
    await audit_logger.log_event(
        event_type=AuditEventType.SYSTEM_SHUTDOWN,
        message="Cidadão.AI API shutting down",
        severity=AuditSeverity.LOW,
    )

    # Shutdown observability
    tracing_manager.shutdown()

    # Close database connections
    from src.db.session import close_database

    await close_database()


# Create FastAPI application
app = FastAPI(
    title="🏛️ Cidadão.AI - Plataforma de Transparência Pública",
    description="API para investigação inteligente de dados públicos brasileiros usando sistema multi-agente de IA. Inspirado na obra 'Operários' de Tarsila do Amaral, representando a diversidade do povo brasileiro.",
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
    docs_url=None,  # Disable default docs, using custom endpoint below
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    # Enhanced Swagger UI configuration with Brazilian theme
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
    },
    swagger_ui_init_oauth=None,
)


# Custom Swagger UI endpoint with Brazilian theme
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html() -> HTMLResponse:
    """Custom Swagger UI with Brazilian theme CSS."""
    html_response = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Documentação",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_favicon_url="🏛️",
        init_oauth=app.swagger_ui_init_oauth,
        swagger_ui_parameters=app.swagger_ui_parameters,
    )

    # Inject custom CSS
    html_content = html_response.body.decode()
    html_content = html_content.replace(
        "</head>",
        '<link rel="stylesheet" type="text/css" href="/static/custom.css"></head>',
    )

    return HTMLResponse(content=html_content)


# Add security middleware (order matters!)
# TEMPORARILY DISABLED FOR FRONTEND INTEGRATION
# The SecurityMiddleware has its own IP blocklist that blocks external access
# TODO: Configure proper IP whitelist for production after frontend integration
# app.add_middleware(SecurityMiddleware)  # RE-ENABLE AFTER CONFIGURING WHITELIST
app.add_middleware(LoggingMiddleware)

# Add compression middleware for mobile optimization
app.add_middleware(CompressionMiddleware, minimum_size=1024)  # Compress responses > 1KB

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
        "/health",
        "/metrics",
        "/health/metrics",
        "/api/v1/ws",
        "/api/v1/observability",
        "/docs",
        "/redoc",
        "/openapi.json",  # Exclude docs to fix Swagger UI
    },
)

# Add streaming compression middleware (exclude docs)
from src.api.middleware.streaming_compression import StreamingCompressionMiddleware

app.add_middleware(
    StreamingCompressionMiddleware,
    minimum_size=256,
    compression_level=settings.compression_gzip_level,
    chunk_size=8192,
)

# Add IP whitelist middleware (only in production)
# Enhanced with API key authentication as fallback
# TEMPORARILY DISABLED FOR TESTING AND FRONTEND INTEGRATION
ENABLE_IP_WHITELIST = False  # Set to True to re-enable IP whitelist
if ENABLE_IP_WHITELIST and (settings.is_production or settings.app_env == "staging"):
    from src.api.middleware.ip_whitelist import IPWhitelistMiddleware

    # Configure Vercel and known service IP ranges
    ALLOWED_IP_RANGES = [
        # Vercel Edge Network
        "76.76.21.0/24",
        "76.223.126.0/24",
        # Add Railway internal IPs if needed
        # Add monitoring service IPs
    ]

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
            "/api/v1/webhooks/incoming",
        ],
        strict_mode=False,  # Allow requests if IP can't be determined
    )

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware, default_tier="free", strategy="sliding_window")

# Add query tracking middleware for cache optimization
from src.api.middleware.query_tracking import QueryTrackingMiddleware

app.add_middleware(
    QueryTrackingMiddleware,
    tracked_paths=[
        "/api/v1/investigations",
        "/api/v1/contracts",
        "/api/v1/analysis",
        "/api/v1/reports",
    ],
    sample_rate=0.1 if settings.is_production else 1.0,  # 10% sampling in production
)


# Mount static files for images and CSS
import os

static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Documentation endpoints are now handled by FastAPI defaults
# Using standard Swagger UI without customization for better compatibility


# Include routers with security
app.include_router(health.router, prefix="/health", tags=["Health Check"])

# API root endpoint - Welcome message
app.include_router(root.router, prefix="/api/v1", tags=["Root"])

# Debug endpoints for troubleshooting
app.include_router(debug.router, prefix="/api/v1/debug", tags=["Debug"])

app.include_router(auth.router, tags=["Authentication"])

app.include_router(oauth.router, tags=["OAuth2"])

app.include_router(audit.router, tags=["Audit & Security"])

app.include_router(
    investigations.router, prefix="/api/v1/investigations", tags=["Investigations"]
)

app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])

app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

from src.api.routes import export

app.include_router(export.router, prefix="/api/v1/export", tags=["Export"])

app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])

# Chat Investigative - Real-time contract search with streaming
app.include_router(
    chat_investigative.router, prefix="/api/v1/chat", tags=["Chat Investigativo"]
)

app.include_router(websocket_chat.router, prefix="/api/v1", tags=["WebSocket"])

# Voice API endpoints for Speech-to-Text and Text-to-Speech
app.include_router(voice.router, prefix="/api/v1/voice", tags=["Voice AI"])

app.include_router(batch.router, tags=["Batch Operations"])

# GraphQL endpoint
app.include_router(graphql.router, tags=["GraphQL"])

# CQRS endpoints
app.include_router(cqrs.router, tags=["CQRS"])

# Resilience monitoring endpoints
app.include_router(resilience.router, tags=["Resilience"])

# Observability monitoring endpoints
app.include_router(observability.router, tags=["Observability"])

app.include_router(notifications.router, tags=["Notifications"])

from src.api.routes import api_keys

# Import and include admin routes
from src.api.routes.admin import agent_lazy_loading as admin_lazy_loading
from src.api.routes.admin import cache_warming as admin_cache_warming
from src.api.routes.admin import compression as admin_compression
from src.api.routes.admin import connection_pools as admin_conn_pools
from src.api.routes.admin import database_optimization as admin_db_optimization
from src.api.routes.admin import ip_whitelist as admin_ip_whitelist

app.include_router(admin_ip_whitelist.router, prefix="/api/v1/admin", tags=["Admin"])

app.include_router(admin_cache_warming.router, prefix="/api/v1/admin", tags=["Admin"])

app.include_router(admin_db_optimization.router, prefix="/api/v1/admin", tags=["Admin"])

app.include_router(admin_compression.router, prefix="/api/v1/admin", tags=["Admin"])

app.include_router(admin_conn_pools.router, prefix="/api/v1/admin", tags=["Admin"])

app.include_router(admin_lazy_loading.router, prefix="/api/v1/admin", tags=["Admin"])

app.include_router(api_keys.router, prefix="/api/v1", tags=["API Keys"])

# LLM Cost Tracking endpoints
from src.api.routes import llm_costs

app.include_router(llm_costs.router, tags=["LLM Cost Tracking"])

app.include_router(dados_gov.router, prefix="/api/v1", tags=["Dados.gov.br"])

app.include_router(agents.router, prefix="/api/v1/agents", tags=["AI Agents"])

app.include_router(
    orchestration.router, prefix="/api/v1/orchestration", tags=["Agent Orchestration"]
)

app.include_router(
    agent_metrics.router, prefix="/api/v1/metrics", tags=["Agent Metrics"]
)

app.include_router(visualization.router, tags=["Data Visualization"])

app.include_router(geographic.router, tags=["Geographic Data"])

from src.api.routes import ml_pipeline

app.include_router(ml_pipeline.router, tags=["ML Pipeline"])

app.include_router(tasks.router, tags=["Tasks & Background Jobs"])

# Transparency APIs endpoints
app.include_router(
    transparency.router, prefix="/api/v1/transparency", tags=["Transparency APIs"]
)

# Transparency Coverage Map endpoints (hybrid cache with 6-hour updates)
app.include_router(
    transparency_coverage.router, prefix="/api/v1", tags=["Transparency Coverage"]
)

# Federal APIs REST endpoints
app.include_router(federal_apis.router, tags=["Federal APIs"])

# Network Graph Analysis endpoints
app.include_router(network.router, tags=["Network Analysis"])

# Agent Dashboard endpoints
from src.api.routes import dashboard, dashboard_view

app.include_router(dashboard.router, prefix="/api/v1", tags=["Agent Dashboard"])
app.include_router(dashboard_view.router, tags=["Dashboard View"])


# Global exception handler
@app.exception_handler(CidadaoAIError)
async def cidadao_ai_exception_handler(
    request: Request, exc: CidadaoAIError
) -> JSONResponse:
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

    return JSONResponse(status_code=status_code, content=error_response)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Enhanced HTTP exception handler with audit logging."""

    # Create audit context
    context = AuditContext(
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent"),
        host=request.headers.get("host"),
    )

    # Log security-related errors
    if exc.status_code in [401, 403, HTTP_RATE_LIMIT]:
        await audit_logger.log_event(
            event_type=AuditEventType.UNAUTHORIZED_ACCESS,
            message=f"HTTP {exc.status_code}: {exc.detail}",
            severity=(
                AuditSeverity.MEDIUM
                if exc.status_code != HTTP_RATE_LIMIT
                else AuditSeverity.HIGH
            ),
            success=False,
            error_code=str(exc.status_code),
            error_message=exc.detail,
            context=context,
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
            "error": {"error": "HTTPException", "message": exc.detail, "details": {}},
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Enhanced general exception handler with audit logging."""

    # Log unexpected errors with audit
    context = AuditContext(
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent"),
        host=request.headers.get("host"),
    )

    await audit_logger.log_event(
        event_type=AuditEventType.API_ERROR,
        message=f"Unhandled exception: {str(exc)}",
        severity=AuditSeverity.HIGH,
        success=False,
        error_message=str(exc),
        details={"error_type": type(exc).__name__},
        context=context,
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
                    "details": {},
                },
            },
        )
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "status_code": 500,
            "error": {
                "error": "InternalServerError",
                "message": f"An unexpected error occurred: {str(exc)}",
                "details": {"error_type": type(exc).__name__},
            },
        },
    )


# Root endpoint
@app.get("/", include_in_schema=False)
async def root() -> dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "message": "Cidadão.AI - Plataforma de Transparência Pública",
        "version": "1.0.0",
        "description": "API para investigação inteligente de dados públicos brasileiros",
        "documentation": "/docs",
        "health": "/health",
        "status": "operational",
        "portal_integration": "active",
        "last_update": "2025-01-25 15:00:00 UTC",
    }


# Test Portal endpoint
@app.get("/test-portal", include_in_schema=False)
async def test_portal() -> dict[str, Any]:
    """Test Portal da Transparência integration status."""
    import os

    from src.services.chat_data_integration import chat_data_integration

    # Test the service is available
    integration_available = False
    try:
        if chat_data_integration:
            integration_available = True
    except Exception:
        # Service not available
        integration_available = False

    return {
        "portal_integration": "enabled",
        "api_key_configured": bool(os.getenv("TRANSPARENCY_API_KEY")),
        "integration_service_available": integration_available,
        "endpoints": {
            "chat_message": "/api/v1/chat/message",
            "chat_stream": "/api/v1/chat/stream",
            "test_portal": "/api/v1/chat/test-portal/{query}",
            "debug_status": "/api/v1/chat/debug/portal-status",
        },
        "demo_mode": not bool(os.getenv("TRANSPARENCY_API_KEY")),
        "example_queries": [
            "Liste os últimos 3 contratos do ministério da saúde",
            "Mostre contratos com valor acima de 1 milhão",
            "Quais empresas têm mais contratos com o governo?",
        ],
    }


# API info endpoint
@app.get("/api/v1/info", tags=["General"])
async def api_info() -> dict[str, Any]:
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
                    "Irregularidades de pagamento",
                ],
            },
            "analyst": {
                "description": "Análise de padrões e correlações",
                "capabilities": [
                    "Tendências de gastos",
                    "Padrões organizacionais",
                    "Comportamento de fornecedores",
                    "Análise sazonal",
                    "Métricas de eficiência",
                ],
            },
            "reporter": {
                "description": "Geração de relatórios inteligentes",
                "capabilities": [
                    "Relatórios executivos",
                    "Análise detalhada",
                    "Múltiplos formatos",
                    "Linguagem natural",
                ],
            },
        },
        "data_sources": [
            "Portal da Transparência",
            "Contratos públicos",
            "Despesas governamentais",
            "Licitações",
            "Convênios",
            "Servidores públicos",
        ],
        "formats": ["JSON", "Markdown", "HTML", "PDF (planned)"],
    }


def create_app() -> FastAPI:
    """
    Factory function to create the FastAPI application.

    This function exists for backward compatibility with tests that expect
    a create_app() factory function. The actual app is created at module level
    above for direct import.

    Returns:
        FastAPI: The application instance
    """
    return app


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
