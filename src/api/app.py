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

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware  # Disabled for HuggingFace
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from src.core import get_logger, settings
from src.core.exceptions import CidadaoAIError, create_error_response
from src.core.audit import audit_logger, AuditEventType, AuditSeverity, AuditContext
from src.api.routes import investigations, analysis, reports, health, auth, oauth, audit, chat, websocket_chat, batch, graphql, cqrs, resilience, observability, chat_simple, chat_stable, chat_optimized, chat_emergency
from src.api.middleware.rate_limiting import RateLimitMiddleware
from src.api.middleware.authentication import AuthenticationMiddleware
from src.api.middleware.logging_middleware import LoggingMiddleware
from src.api.middleware.security import SecurityMiddleware
from src.api.middleware.compression import CompressionMiddleware
from src.api.middleware.metrics_middleware import MetricsMiddleware, setup_http_metrics
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
        build_info={"deployment": "hf-fastapi"}
    )
    
    # Setup HTTP metrics
    setup_http_metrics()
    
    # Initialize global resources here
    # - Database connections
    # - Background tasks
    # - Cache connections
    
    yield
    
    # Shutdown
    logger.info("cidadao_ai_api_shutting_down")
    
    # Log shutdown event
    await audit_logger.log_event(
        event_type=AuditEventType.SYSTEM_SHUTDOWN,
        message="Cidadão.AI API shutting down",
        severity=AuditSeverity.LOW
    )
    
    # Shutdown observability
    tracing_manager.shutdown()
    
    # Cleanup resources here
    # - Close database connections
    # - Stop background tasks
    # - Clean up cache


# Create FastAPI application
app = FastAPI(
    title="Cidadão.AI API",
    description="""
    **Plataforma de Transparência Pública com IA**
    
    API para investigação inteligente de dados públicos brasileiros.
    
    ## Funcionalidades
    
    * **Investigação** - Detecção de anomalias e irregularidades
    * **Análise** - Padrões e correlações em dados públicos
    * **Relatórios** - Geração de relatórios em linguagem natural
    * **Transparência** - Acesso democrático a informações governamentais
    
    ## Agentes Especializados
    
    * **InvestigatorAgent** - Detecção de anomalias com IA explicável
    * **AnalystAgent** - Análise de padrões e correlações
    * **ReporterAgent** - Geração de relatórios inteligentes
    
    ## Fontes de Dados
    
    * Portal da Transparência do Governo Federal
    * Contratos, despesas, licitações e convênios públicos
    * Dados de servidores e empresas sancionadas
    """,
    version="1.0.0",
    contact={
        "name": "Cidadão.AI",
        "url": "https://github.com/anderson-ufrj/cidadao.ai",
        "email": "contato@cidadao.ai",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://github.com/anderson-ufrj/cidadao.ai/blob/main/LICENSE",
    },
    lifespan=lifespan,
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable redoc
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

# CORS middleware with secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"]
)

# Add observability middleware
app.add_middleware(CorrelationMiddleware, generate_request_id=True)

# Add metrics middleware for automatic HTTP metrics
app.add_middleware(MetricsMiddleware)

# Add compression middleware
from src.api.middleware.compression import add_compression_middleware
add_compression_middleware(
    app,
    minimum_size=1024,
    gzip_level=6,
    brotli_quality=4,
    exclude_paths={"/health", "/metrics", "/health/metrics", "/api/v1/ws", "/api/v1/observability"}
)


# Custom OpenAPI schema
def custom_openapi():
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom API info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://cidadao.ai/logo.png"
    }
    
    # Add servers
    openapi_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "Development server"},
        {"url": "https://api.cidadao.ai", "description": "Production server"},
    ]
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Custom documentation endpoint
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI with branding."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Documentação",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://cidadao.ai/favicon.ico",
    )


# Include routers with security
app.include_router(
    health.router,
    prefix="/health",
    tags=["Health Check"]
)

app.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    oauth.router,
    prefix="/auth/oauth",
    tags=["OAuth2"]
)

app.include_router(
    audit.router,
    prefix="/audit",
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

app.include_router(
    chat.router,
    prefix="/api/v1/chat",
    tags=["Chat"]
)

app.include_router(
    chat_simple.router,
    prefix="/api/v1/chat",
    tags=["Chat Simple"]
)

app.include_router(
    chat_stable.router,
    tags=["Chat Stable"]
)

app.include_router(
    chat_optimized.router,
    tags=["Chat Optimized"]
)

app.include_router(
    chat_emergency.router,
    tags=["Chat Emergency"]
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
        "status": "operational"
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