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

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

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
        """Execute investigation with anomaly detection using REAL API data."""
        import time
        import os
        import numpy as np
        from collections import defaultdict
        start_time = time.time()
        
        try:
            # Get API key from environment (HuggingFace Secrets)
            api_key = os.getenv("TRANSPARENCY_API_KEY")
            if not api_key:
                logger.warning("⚠️ TRANSPARENCY_API_KEY not found, using fallback data")
                return await self._get_fallback_investigation(request, start_time)
            
            logger.info(f"🔍 Investigating with REAL DATA: {request.query}")
            
            # Use direct HTTP calls to avoid complex configuration dependencies
            results = []
            
            # Direct API call to Portal da Transparência
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Define organization codes for investigation
                org_codes = ["26000", "20000", "25000"]  # Health, Presidency, Education
                
                for org_code in org_codes[:2]:  # Limit to 2 orgs to avoid timeout
                    try:
                        # Direct API call to Portal da Transparência
                        url = "https://api.portaldatransparencia.gov.br/api-de-dados/contratos"
                        headers = {
                            "chave-api-dados": api_key,
                            "Accept": "application/json"
                        }
                        params = {
                            "codigoOrgao": org_code,
                            "ano": 2024,
                            "tamanhoPagina": 20,
                            "valorInicial": 50000
                        }
                        
                        response = await client.get(url, headers=headers, params=params)
                        
                        if response.status_code == 200:
                            contracts_data = response.json()
                            
                            # Process real contracts for anomalies
                            anomalies = await self._detect_anomalies_in_real_data(contracts_data, org_code)
                            results.extend(anomalies)
                            
                            logger.info(f"✅ Fetched {len(contracts_data)} contracts from org {org_code}, found {len(anomalies)} anomalies")
                        else:
                            logger.warning(f"⚠️ API returned status {response.status_code} for org {org_code}")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to fetch data from org {org_code}: {str(e)}")
                        continue
            
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
    
    async def _detect_anomalies_in_real_data(self, contracts_data: list, org_code: str) -> list:
        """Detect anomalies in real Portal da Transparência data."""
        anomalies = []
        
        if not contracts_data:
            return anomalies
        
        # Extract contract values for statistical analysis
        values = []
        for contract in contracts_data:
            valor = contract.get("valorInicial") or contract.get("valorGlobal") or contract.get("valor", 0)
            if isinstance(valor, (int, float)) and valor > 0:
                values.append(float(valor))
        
        if len(values) < 5:  # Need minimum samples
            return anomalies
        
        # Calculate statistical measures
        import numpy as np
        mean_value = np.mean(values)
        std_value = np.std(values) 
        
        # Analyze each contract
        for contract in contracts_data:
            valor = contract.get("valorInicial") or contract.get("valorGlobal") or contract.get("valor", 0)
            if not isinstance(valor, (int, float)) or valor <= 0:
                continue
            
            valor = float(valor)
            
            # Price anomaly detection (Z-score > 2)
            z_score = abs((valor - mean_value) / std_value) if std_value > 0 else 0
            
            if z_score > 2.0:  # Suspicious price
                anomaly = {
                    "contract_id": contract.get("id", "unknown"),
                    "description": contract.get("objeto", "")[:100],
                    "value": valor,
                    "supplier": self._extract_supplier_name(contract),
                    "organization": org_code,
                    "anomaly_type": "price_suspicious" if z_score < 3 else "price_critical",
                    "risk_level": "high" if z_score > 3 else "medium",
                    "explanation": f"Valor R$ {valor:,.2f} está {z_score:.1f} desvios padrão acima da média (R$ {mean_value:,.2f})",
                    "z_score": z_score,
                    "mean_value": mean_value
                }
                anomalies.append(anomaly)
        
        # Vendor concentration analysis
        vendor_analysis = self._analyze_vendor_concentration(contracts_data, org_code)
        anomalies.extend(vendor_analysis)
        
        return anomalies[:10]  # Limit to top 10 anomalies
    
    def _extract_supplier_name(self, contract: dict) -> str:
        """Extract supplier name from contract data."""
        fornecedor = contract.get("fornecedor", {})
        if isinstance(fornecedor, dict):
            return fornecedor.get("nome", "N/A")
        elif isinstance(fornecedor, str):
            return fornecedor
        return "N/A"
    
    def _analyze_vendor_concentration(self, contracts_data: list, org_code: str) -> list:
        """Analyze vendor concentration in contracts."""
        anomalies = []
        vendor_stats = {}
        total_value = 0
        
        for contract in contracts_data:
            supplier_name = self._extract_supplier_name(contract)
            valor = contract.get("valorInicial") or contract.get("valorGlobal") or contract.get("valor", 0)
            
            if isinstance(valor, (int, float)) and valor > 0:
                total_value += float(valor)
                
                if supplier_name not in vendor_stats:
                    vendor_stats[supplier_name] = {"contracts": 0, "total_value": 0}
                
                vendor_stats[supplier_name]["contracts"] += 1
                vendor_stats[supplier_name]["total_value"] += float(valor)
        
        if total_value == 0:
            return anomalies
        
        # Check for excessive concentration (>40% of total value)
        for supplier, stats in vendor_stats.items():
            concentration = stats["total_value"] / total_value
            
            if concentration > 0.4 and stats["contracts"] > 1:  # 40% threshold
                anomaly = {
                    "contract_id": f"concentration_{org_code}_{supplier}",
                    "description": f"Concentração excessiva de contratos",
                    "value": stats["total_value"],
                    "supplier": supplier,
                    "organization": org_code,
                    "anomaly_type": "vendor_concentration",
                    "risk_level": "high" if concentration > 0.6 else "medium",
                    "explanation": f"Fornecedor {supplier} concentra {concentration:.1%} do valor total ({stats['contracts']} contratos)",
                    "concentration": concentration,
                    "contract_count": stats["contracts"]
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    async def _get_fallback_investigation(self, request: InvestigationRequest, start_time: float) -> InvestigationResponse:
        """Fallback investigation with mock data when API is unavailable."""
        logger.info("🔄 Using fallback mock data for investigation")
        
        results = [
            {
                "contract_id": "FALLBACK_001",
                "description": "Aquisição de equipamentos de informática (DADOS DEMO)",
                "value": 150000.00,
                "supplier": "Tech Solutions LTDA",
                "anomaly_type": "price_suspicious",
                "risk_level": "medium",
                "explanation": "[DEMO] Preço 25% acima da média de mercado para equipamentos similares"
            },
            {
                "contract_id": "FALLBACK_002", 
                "description": "Serviços de consultoria especializada (DADOS DEMO)",
                "value": 280000.00,
                "supplier": "Consulting Group SA",
                "anomaly_type": "vendor_concentration",
                "risk_level": "high",
                "explanation": "[DEMO] Fornecedor concentra 40% dos contratos do órgão no período"
            }
        ]
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return InvestigationResponse(
            status="completed_fallback",
            query=request.query,
            results=results,
            anomalies_found=len(results),
            confidence_score=0.75,  # Lower confidence for mock data
            processing_time_ms=processing_time
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
    """API status endpoint with data source information."""
    REQUEST_COUNT.labels(method="GET", endpoint="/api/status").inc()
    
    # Check if we have real API access
    api_key_available = bool(os.getenv("TRANSPARENCY_API_KEY"))
    
    return {
        "api": "Cidadão.AI Backend",
        "version": "1.1.0",
        "status": "operational",
        "data_source": {
            "type": "real_api" if api_key_available else "fallback_demo",
            "portal_transparencia": {
                "enabled": api_key_available,
                "status": "connected" if api_key_available else "using_fallback"
            }
        },
        "agents": {
            "zumbi": {
                "name": "Zumbi dos Palmares",
                "role": "InvestigatorAgent",
                "specialty": "Real-time anomaly detection in government contracts",
                "status": "active",
                "data_source": "Portal da Transparência API" if api_key_available else "Demo data"
            }
        },
        "endpoints": {
            "health": "/health",
            "investigate": "/api/agents/zumbi/investigate",
            "test_data": "/api/agents/zumbi/test",
            "metrics": "/metrics",
            "docs": "/docs",
            "status": "/api/status"
        },
        "capabilities": [
            "Price anomaly detection (Z-score analysis)",
            "Vendor concentration analysis", 
            "Statistical outlier detection",
            "Real-time government data processing" if api_key_available else "Demo data analysis"
        ]
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