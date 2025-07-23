#!/usr/bin/env python3
"""
🇧🇷 Cidadão.AI - Optimized FastAPI Backend for Hugging Face Spaces
Enhanced performance with caching, connection pooling, and async operations
"""

import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import redis.asyncio as redis
from prometheus_client import Counter, Histogram, generate_latest
import structlog

# Configure structured logging
logger = structlog.get_logger()

# Metrics
request_count = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('app_request_duration_seconds', 'Request duration')

# Global connections
redis_client: Optional[redis.Redis] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global redis_client
    
    # Startup
    logger.info("Starting Cidadão.AI backend...")
    
    # Initialize Redis with connection pool
    try:
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True,
            max_connections=50,
            socket_keepalive=True,
            socket_keepalive_options={
                1: 1,  # TCP_KEEPIDLE
                2: 1,  # TCP_KEEPINTVL
                3: 5,  # TCP_KEEPCNT
            }
        )
        await redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Running without cache.")
        redis_client = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down Cidadão.AI backend...")
    if redis_client:
        await redis_client.close()

# Create optimized FastAPI application
app = FastAPI(
    title="Cidadão.AI API",
    description="🏛️ High-performance API for Brazilian public transparency",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Middleware stack (order matters!)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,  # Cache CORS preflight
)

# Request tracking middleware
@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Track request metrics"""
    start_time = asyncio.get_event_loop().time()
    
    # Process request
    response = await call_next(request)
    
    # Record metrics
    duration = asyncio.get_event_loop().time() - start_time
    request_count.labels(
        method=request.method,
        endpoint=request.url.path
    ).inc()
    request_duration.observe(duration)
    
    # Add performance headers
    response.headers["X-Process-Time"] = str(duration)
    response.headers["X-Server"] = "Cidadao.AI/2.0"
    
    return response

# Cache decorator
def cache(expire: int = 300):
    """Simple cache decorator with Redis"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if not redis_client:
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = f"cache:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            try:
                cached = await redis_client.get(cache_key)
                if cached:
                    logger.debug(f"Cache hit: {cache_key}")
                    return JSONResponse(content=eval(cached))
            except Exception as e:
                logger.warning(f"Cache get error: {e}")
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            try:
                await redis_client.setex(
                    cache_key,
                    expire,
                    str(result)
                )
            except Exception as e:
                logger.warning(f"Cache set error: {e}")
            
            return result
        return wrapper
    return decorator

# Routes
@app.get("/")
@cache(expire=3600)
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Cidadão.AI Backend",
        "version": "2.0.0",
        "status": "operational",
        "description": "High-performance API for intelligent investigation of Brazilian public data",
        "features": [
            "Multi-agent AI system",
            "Real-time data analysis",
            "Advanced caching",
            "WebSocket support",
            "Prometheus metrics"
        ],
        "endpoints": {
            "documentation": "/docs",
            "health": "/health",
            "metrics": "/metrics",
            "api": {
                "investigations": "/api/v1/investigations",
                "analysis": "/api/v1/analysis",
                "reports": "/api/v1/reports"
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with dependencies."""
    health_status = {
        "status": "healthy",
        "service": "cidadao-ai-backend",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "calculating...",
        "dependencies": {}
    }
    
    # Check Redis
    if redis_client:
        try:
            await redis_client.ping()
            health_status["dependencies"]["redis"] = "healthy"
        except Exception:
            health_status["dependencies"]["redis"] = "unhealthy"
            health_status["status"] = "degraded"
    else:
        health_status["dependencies"]["redis"] = "not configured"
    
    return health_status

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        generate_latest(),
        media_type="text/plain"
    )

# API v1 routes
@app.get("/api/v1/investigations")
@cache(expire=60)
async def list_investigations(
    limit: int = 10,
    offset: int = 0,
    status: Optional[str] = None
):
    """List recent investigations with caching."""
    # Mock data for HF Spaces demo
    investigations = []
    for i in range(offset, min(offset + limit, 100)):
        investigations.append({
            "id": f"inv-{i:04d}",
            "title": f"Investigation {i}",
            "status": status or "active",
            "created_at": (datetime.utcnow() - timedelta(days=i)).isoformat(),
            "agents_assigned": ["bonifacio", "dandara", "machado"],
            "anomaly_score": 0.75 - (i * 0.01)
        })
    
    return {
        "total": 100,
        "limit": limit,
        "offset": offset,
        "data": investigations
    }

@app.get("/api/v1/analysis/{entity_id}")
@cache(expire=300)
async def get_analysis(entity_id: str):
    """Get analysis results for an entity."""
    # Mock analysis data
    return {
        "entity_id": entity_id,
        "entity_type": "contract",
        "analysis": {
            "risk_score": 0.72,
            "anomalies_detected": 3,
            "patterns": [
                "Unusual payment frequency",
                "Above average contract value",
                "Vendor concentration"
            ],
            "recommendations": [
                "Review payment schedule",
                "Verify vendor credentials",
                "Compare with similar contracts"
            ]
        },
        "metadata": {
            "analyzed_at": datetime.utcnow().isoformat(),
            "agents_used": ["investigator", "analyst"],
            "data_sources": ["portal_transparencia", "tce", "siafi"]
        }
    }

@app.post("/api/v1/reports/generate")
async def generate_report(request: Dict[str, Any]):
    """Generate investigation report."""
    # Mock report generation
    report_id = f"rpt-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "report_id": report_id,
        "status": "generating",
        "estimated_completion": (datetime.utcnow() + timedelta(minutes=2)).isoformat(),
        "message": "Report generation started. Check status endpoint for updates."
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with proper formatting."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

# HF Spaces optimized entry point
if __name__ == "__main__":
    # Configure for HF Spaces
    port = int(os.getenv("PORT", 7860))
    
    # Use multiple workers if available
    workers = int(os.getenv("WEB_CONCURRENCY", 1))
    
    if workers > 1:
        # Multi-worker mode
        uvicorn.run(
            "app-optimized:app",
            host="0.0.0.0",
            port=port,
            workers=workers,
            loop="uvloop",  # Faster event loop
            log_level="info",
            access_log=True,
            reload=False
        )
    else:
        # Single worker mode (default for HF free tier)
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            loop="uvloop",
            log_level="info",
            access_log=True,
            reload=False
        )