#!/usr/bin/env python3
"""
Cidadão.AI Backend - HuggingFace Spaces Entry Point

Enterprise-grade multi-agent AI system for Brazilian government transparency analysis.
Optimized for HuggingFace Spaces deployment with embedded Zumbi investigator agent.

Author: Anderson Henrique da Silva
License: Proprietary - All rights reserved
"""

import asyncio
import logging
import os
import sys
import traceback
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Prometheus metrics - prevent duplicate registration
try:
    REQUEST_COUNT = Counter('cidadao_ai_requests_total', 'Total requests', ['method', 'endpoint'])
    REQUEST_DURATION = Histogram('cidadao_ai_request_duration_seconds', 'Request duration')
    INVESTIGATION_COUNT = Counter('cidadao_ai_investigations_total', 'Total investigations')
except ValueError as e:
    # Handle duplicate registration by reusing existing metrics
    if "Duplicated timeseries" in str(e):
        logger.warning("Prometheus metrics already registered, reusing existing ones")
        from prometheus_client.registry import REGISTRY
        
        # Initialize to None
        REQUEST_COUNT = None
        REQUEST_DURATION = None  
        INVESTIGATION_COUNT = None
        
        # Find existing metrics in registry
        for collector in list(REGISTRY._collector_to_names.keys()):
            if hasattr(collector, '_name'):
                # Counter metrics store name without _total suffix
                if collector._name == 'cidadao_ai_requests':
                    REQUEST_COUNT = collector
                elif collector._name == 'cidadao_ai_request_duration_seconds': 
                    REQUEST_DURATION = collector
                elif collector._name == 'cidadao_ai_investigations':
                    INVESTIGATION_COUNT = collector
        
        # If any metric wasn't found, raise the original error
        if REQUEST_COUNT is None or REQUEST_DURATION is None or INVESTIGATION_COUNT is None:
            logger.error("Could not find all existing metrics in registry")
            raise e
    else:
        raise e
except Exception as e:
    logger.error(f"Failed to setup Prometheus metrics: {e}")
    # Fallback: create mock objects to prevent application crash
    class MockMetric:
        def inc(self): pass
        def labels(self, **kwargs): return self
        def time(self): return self
        def __enter__(self): return self
        def __exit__(self, *args): pass
    
    REQUEST_COUNT = MockMetric()
    REQUEST_DURATION = MockMetric() 
    INVESTIGATION_COUNT = MockMetric()

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = "healthy"
    version: str = "1.0.0"
    agents: Dict[str, str] = Field(default_factory=lambda: {"zumbi": "active"})
    uptime: str = "operational"

class InvestigationRequest(BaseModel):
    """Investigation request model."""
    query: str = Field(..., description="Investigation query")
    data_source: str = Field(default="contracts", description="Data source to investigate")
    max_results: int = Field(default=100, description="Maximum number of results")

class InvestigationResponse(BaseModel):
    """Investigation response model."""
    status: str
    agent: str = "zumbi"
    query: str
    results: List[Dict[str, Any]]
    anomalies_found: int
    confidence_score: float
    processing_time_ms: int

class ZumbiAgent:
    """Embedded Zumbi dos Palmares - Investigator Agent for HuggingFace deployment."""
    
    def __init__(self):
        self.name = "Zumbi dos Palmares"
        self.role = "InvestigatorAgent" 
        self.specialty = "Anomaly detection in government contracts"
        self.active = True
        logger.info(f"🏹 {self.name} - {self.role} initialized")
    
    async def investigate(self, request: InvestigationRequest) -> InvestigationResponse:
        """Execute investigation with anomaly detection."""
        import time
        start_time = time.time()
        
        try:
            # Simulate investigation process
            logger.info(f"🔍 Investigating: {request.query}")
            
            # Mock investigation results for demonstration
            results = [
                {
                    "contract_id": "2024001",
                    "description": "Aquisição de equipamentos de informática",
                    "value": 150000.00,
                    "supplier": "Tech Solutions LTDA",
                    "anomaly_type": "price_suspicious",
                    "risk_level": "medium",
                    "explanation": "Preço 25% acima da média de mercado para equipamentos similares"
                },
                {
                    "contract_id": "2024002", 
                    "description": "Serviços de consultoria especializada",
                    "value": 280000.00,
                    "supplier": "Consulting Group SA",
                    "anomaly_type": "vendor_concentration",
                    "risk_level": "high",
                    "explanation": "Fornecedor concentra 40% dos contratos do órgão no período"
                }
            ]
            
            processing_time = int((time.time() - start_time) * 1000)
            
            response = InvestigationResponse(
                status="completed",
                query=request.query,
                results=results,
                anomalies_found=len(results),
                confidence_score=0.87,
                processing_time_ms=processing_time
            )
            
            INVESTIGATION_COUNT.inc()
            logger.info(f"✅ Investigation completed: {len(results)} anomalies found")
            return response
            
        except Exception as e:
            logger.error(f"❌ Investigation failed: {str(e)}")
            return InvestigationResponse(
                status="error",
                query=request.query,
                results=[],
                anomalies_found=0,
                confidence_score=0.0,
                processing_time_ms=int((time.time() - start_time) * 1000)
            )

# Initialize Zumbi Agent
zumbi_agent = ZumbiAgent()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🏛️ Cidadão.AI Backend starting up...")
    logger.info("🏹 Zumbi dos Palmares agent ready for investigations")
    yield
    logger.info("🏛️ Cidadão.AI Backend shutting down...")

# Create FastAPI application
app = FastAPI(
    title="🏛️ Cidadão.AI Backend",
    description="Enterprise-grade multi-agent AI system for Brazilian government transparency analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with system status."""
    REQUEST_COUNT.labels(method="GET", endpoint="/").inc()
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        agents={"zumbi": "active"},
        uptime="operational"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    REQUEST_COUNT.labels(method="GET", endpoint="/health").inc()
    return HealthResponse()

@app.get("/api/agents/zumbi/test")
async def get_test_data():
    """Get test data for Zumbi agent."""
    REQUEST_COUNT.labels(method="GET", endpoint="/api/agents/zumbi/test").inc()
    
    test_data = {
        "description": "Dados de teste para investigação de contratos públicos",
        "sample_query": "Analisar contratos de informática com valores suspeitos",
        "expected_anomalies": ["price_suspicious", "vendor_concentration"],
        "data_source": "Portal da Transparência (simulado)",
        "agent": "Zumbi dos Palmares - InvestigatorAgent"
    }
    
    return JSONResponse(content=test_data)

@app.post("/api/agents/zumbi/investigate", response_model=InvestigationResponse)
async def investigate_contracts(request: InvestigationRequest):
    """Execute investigation using Zumbi agent."""
    REQUEST_COUNT.labels(method="POST", endpoint="/api/agents/zumbi/investigate").inc()
    
    try:
        with REQUEST_DURATION.time():
            result = await zumbi_agent.investigate(request)
        return result
        
    except Exception as e:
        logger.error(f"Investigation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation failed: {str(e)}"
        )

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return generate_latest().decode('utf-8')

@app.get("/api/status")
async def api_status():
    """API status endpoint."""
    REQUEST_COUNT.labels(method="GET", endpoint="/api/status").inc()
    
    return {
        "api": "Cidadão.AI Backend",
        "version": "1.0.0",
        "status": "operational",
        "agents": {
            "zumbi": {
                "name": "Zumbi dos Palmares",
                "role": "InvestigatorAgent",
                "specialty": "Anomaly detection in government contracts",
                "status": "active"
            }
        },
        "endpoints": {
            "health": "/health",
            "investigate": "/api/agents/zumbi/investigate",
            "test_data": "/api/agents/zumbi/test",
            "metrics": "/metrics",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    # Configuration for different environments
    port = int(os.getenv("PORT", 7860))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting Cidadão.AI Backend on {host}:{port}")
    
    try:
        uvicorn.run(
            "app:app",
            host=host,
            port=port,
            log_level="info",
            reload=False
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        traceback.print_exc()
        sys.exit(1)