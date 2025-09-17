#!/usr/bin/env python3
"""
Cidadão.AI Backend - Expanded Version with Multiple Data Sources
Supports: Contracts, Servants, Expenses, Biddings, and more
"""

import asyncio
import logging
import os
import sys
import time
import hashlib
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum

import uvicorn
from fastapi import FastAPI, HTTPException, status, Query
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

# ==================== DATA MODELS ====================

class DataSourceType(str, Enum):
    """Types of data sources available."""
    CONTRACTS = "contratos"
    SERVANTS = "servidores"
    EXPENSES = "despesas"
    BIDDINGS = "licitacoes"
    AGREEMENTS = "convenios"
    SANCTIONS = "empresas-sancionadas"

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = "healthy"
    version: str = "2.0.0"
    agents: Dict[str, str] = Field(default_factory=lambda: {"zumbi": "active"})
    data_sources: List[str] = Field(default_factory=lambda: [e.value for e in DataSourceType])
    uptime: str = "operational"

class UniversalSearchRequest(BaseModel):
    """Universal search request for any data type."""
    query: str = Field(..., description="Search query")
    data_source: DataSourceType = Field(..., description="Type of data to search")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Additional filters")
    max_results: int = Field(default=100, ge=1, le=500, description="Maximum results")
    
class ServantData(BaseModel):
    """Servant/Employee data model."""
    nome: str
    cpf_masked: str
    matricula: str
    orgao: str
    cargo: str
    funcao: Optional[str] = None
    remuneracao: Dict[str, float]
    mes_ano_referencia: str

class ContractData(BaseModel):
    """Contract data model."""
    id: str
    numero: str
    objeto: str
    valor: float
    fornecedor: Dict[str, str]
    orgao: str
    data_assinatura: str
    vigencia: Dict[str, str]
    modalidade: Optional[str] = None

class ExpenseData(BaseModel):
    """Expense data model."""
    id: str
    descricao: str
    valor: float
    favorecido: Dict[str, str]
    orgao: str
    data: str
    programa: Optional[str] = None
    acao: Optional[str] = None

class UniversalSearchResponse(BaseModel):
    """Universal search response."""
    status: str
    data_source: str
    query: str
    results: List[Union[ServantData, ContractData, ExpenseData, Dict[str, Any]]]
    total_found: int
    anomalies_detected: int
    confidence_score: float
    processing_time_ms: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

# ==================== CACHE ====================

class SimpleCache:
    """In-memory cache for API responses with TTL."""
    
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
        self._ttl_cache: Dict[str, datetime] = {}
        self.default_ttl = 3600  # 1 hour
    
    def _generate_key(self, **kwargs) -> str:
        """Generate cache key from parameters."""
        key_string = "&".join([f"{k}={v}" for k, v in sorted(kwargs.items())])
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, **kwargs) -> Optional[Dict]:
        """Get cached value if not expired."""
        key = self._generate_key(**kwargs)
        
        if key not in self._cache:
            return None
        
        if key in self._ttl_cache:
            if datetime.now() > self._ttl_cache[key]:
                del self._cache[key]
                del self._ttl_cache[key]
                return None
        
        return self._cache[key]
    
    def set(self, value: Dict, ttl_seconds: int = None, **kwargs) -> None:
        """Set cached value with TTL."""
        key = self._generate_key(**kwargs)
        self._cache[key] = value
        
        ttl = ttl_seconds or self.default_ttl
        self._ttl_cache[key] = datetime.now() + timedelta(seconds=ttl)

# Global cache instance
api_cache = SimpleCache()

# ==================== ENHANCED ZUMBI AGENT ====================

class EnhancedZumbiAgent:
    """Enhanced Zumbi agent that can investigate multiple data sources."""
    
    def __init__(self):
        self.name = "Zumbi dos Palmares"
        self.role = "Universal Investigator"
        self.specialty = "Multi-source anomaly detection"
        logger.info(f"🏹 {self.name} - Enhanced {self.role} initialized")
    
    async def investigate_universal(self, request: UniversalSearchRequest) -> UniversalSearchResponse:
        """Investigate any data source."""
        start_time = time.time()
        
        try:
            # Get API key
            api_key = os.getenv("TRANSPARENCY_API_KEY")
            if not api_key:
                logger.warning("⚠️ No API key, using demo data")
                return await self._get_demo_data(request, start_time)
            
            # Route to appropriate handler
            if request.data_source == DataSourceType.SERVANTS:
                return await self._search_servants(request, api_key, start_time)
            elif request.data_source == DataSourceType.CONTRACTS:
                return await self._search_contracts(request, api_key, start_time)
            elif request.data_source == DataSourceType.EXPENSES:
                return await self._search_expenses(request, api_key, start_time)
            elif request.data_source == DataSourceType.BIDDINGS:
                return await self._search_biddings(request, api_key, start_time)
            else:
                return await self._search_generic(request, api_key, start_time)
                
        except Exception as e:
            logger.error(f"Investigation error: {str(e)}")
            return UniversalSearchResponse(
                status="error",
                data_source=request.data_source.value,
                query=request.query,
                results=[],
                total_found=0,
                anomalies_detected=0,
                confidence_score=0.0,
                processing_time_ms=int((time.time() - start_time) * 1000),
                metadata={"error": str(e)}
            )
    
    async def _search_servants(self, request: UniversalSearchRequest, api_key: str, start_time: float) -> UniversalSearchResponse:
        """Search for government servants."""
        import httpx
        
        # Check cache first
        cache_key = f"servants_{request.query}_{request.max_results}"
        cached = api_cache.get(source=cache_key)
        if cached:
            logger.info("📦 Using cached servants data")
            return cached
        
        results = []
        anomalies = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = "https://api.portaldatransparencia.gov.br/api-de-dados/servidores"
            headers = {
                "chave-api-dados": api_key,
                "Accept": "application/json"
            }
            params = {
                "nome": request.query.upper(),
                "pagina": 1,
                "tamanhoPagina": min(request.max_results, 50)
            }
            
            # Add filters from request
            if "orgao" in request.filters:
                params["orgao"] = request.filters["orgao"]
            if "funcao" in request.filters:
                params["funcao"] = request.filters["funcao"]
            
            response = await client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process servants
                for item in data:
                    servant_info = item.get("servidor", {})
                    org_info = item.get("unidadeOrganizacional", {})
                    
                    # Extract salary info
                    salary = item.get("remuneracaoBasicaBruta", 0)
                    total = item.get("remuneracaoAposDeducoes", 0)
                    
                    # Detect anomalies (e.g., very high salaries)
                    if salary > 40000:  # Above R$ 40k is unusual
                        anomalies += 1
                    
                    servant = ServantData(
                        nome=servant_info.get("nome", "N/A"),
                        cpf_masked=servant_info.get("cpf", "***.***.***-**"),
                        matricula=servant_info.get("matricula", "N/A"),
                        orgao=org_info.get("nomeUnidade", "N/A"),
                        cargo=item.get("cargo", {}).get("descricao", "N/A"),
                        funcao=item.get("funcao", {}).get("descricao"),
                        remuneracao={
                            "basica": salary,
                            "total_liquido": total,
                            "gratificacoes": item.get("gratificacoes", 0),
                            "auxilios": item.get("auxilios", 0)
                        },
                        mes_ano_referencia=f"{item.get('mesReferencia', 'N/A')}/{item.get('anoReferencia', 'N/A')}"
                    )
                    results.append(servant.dict())
                
                response_data = UniversalSearchResponse(
                    status="success",
                    data_source=request.data_source.value,
                    query=request.query,
                    results=results,
                    total_found=len(results),
                    anomalies_detected=anomalies,
                    confidence_score=0.95,
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    metadata={"source": "real_api", "anomaly_threshold": 40000}
                )
                
                # Cache the response
                api_cache.set(response_data.dict(), source=cache_key)
                
                return response_data
            else:
                raise HTTPException(status_code=response.status_code, detail="API request failed")
    
    async def _search_contracts(self, request: UniversalSearchRequest, api_key: str, start_time: float) -> UniversalSearchResponse:
        """Search for contracts with anomaly detection."""
        import httpx
        import numpy as np
        
        results = []
        anomalies = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Search multiple organizations
            org_codes = request.filters.get("orgaos", ["26000", "25000", "44000"])
            
            all_contracts = []
            for org_code in org_codes[:3]:  # Limit to 3 orgs
                url = "https://api.portaldatransparencia.gov.br/api-de-dados/contratos"
                headers = {
                    "chave-api-dados": api_key,
                    "Accept": "application/json"
                }
                params = {
                    "codigoOrgao": org_code,
                    "ano": request.filters.get("ano", 2024),
                    "tamanhoPagina": 50
                }
                
                # Add search term if provided
                if request.query and request.query.lower() != "todos":
                    params["descricao"] = request.query
                
                response = await client.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    contracts = response.json()
                    all_contracts.extend(contracts)
            
            # Analyze contracts for anomalies
            if all_contracts:
                values = [c.get("valorInicial", 0) for c in all_contracts if c.get("valorInicial", 0) > 0]
                
                if len(values) > 3:
                    mean_val = np.mean(values)
                    std_val = np.std(values)
                    
                    for contract in all_contracts[:request.max_results]:
                        valor = contract.get("valorInicial", 0)
                        z_score = abs((valor - mean_val) / std_val) if std_val > 0 else 0
                        
                        # Flag as anomaly if z-score > 1.5
                        is_anomaly = z_score > 1.5
                        if is_anomaly:
                            anomalies += 1
                        
                        contract_data = {
                            "id": contract.get("id", "N/A"),
                            "numero": contract.get("numero", "N/A"),
                            "objeto": contract.get("objeto", "N/A")[:200],
                            "valor": valor,
                            "fornecedor": {
                                "nome": contract.get("nomeFornecedor", "N/A"),
                                "cnpj": contract.get("cnpjFornecedor", "N/A")
                            },
                            "orgao": contract.get("nomeOrgao", org_code),
                            "data_assinatura": contract.get("dataAssinatura", "N/A"),
                            "vigencia": {
                                "inicio": contract.get("dataInicioVigencia", "N/A"),
                                "fim": contract.get("dataFimVigencia", "N/A")
                            },
                            "modalidade": contract.get("modalidadeCompra", "N/A"),
                            "_anomaly": is_anomaly,
                            "_z_score": z_score
                        }
                        results.append(contract_data)
            
            return UniversalSearchResponse(
                status="success",
                data_source=request.data_source.value,
                query=request.query,
                results=results,
                total_found=len(results),
                anomalies_detected=anomalies,
                confidence_score=0.87,
                processing_time_ms=int((time.time() - start_time) * 1000),
                metadata={
                    "organizations_searched": org_codes[:3],
                    "anomaly_method": "z_score",
                    "threshold": 1.5
                }
            )
    
    async def _search_expenses(self, request: UniversalSearchRequest, api_key: str, start_time: float) -> UniversalSearchResponse:
        """Search for government expenses."""
        import httpx
        
        results = []
        anomalies = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = "https://api.portaldatransparencia.gov.br/api-de-dados/despesas"
            headers = {
                "chave-api-dados": api_key,
                "Accept": "application/json"
            }
            params = {
                "ano": request.filters.get("ano", 2024),
                "mes": request.filters.get("mes", 12),
                "pagina": 1,
                "tamanhoPagina": min(request.max_results, 50)
            }
            
            if "orgao" in request.filters:
                params["orgao"] = request.filters["orgao"]
            
            response = await client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                for expense in data:
                    valor = expense.get("valor", 0)
                    
                    # Simple anomaly detection for high values
                    if valor > 1000000:  # Above 1M
                        anomalies += 1
                    
                    expense_data = ExpenseData(
                        id=expense.get("id", "N/A"),
                        descricao=expense.get("descricao", "N/A"),
                        valor=valor,
                        favorecido={
                            "nome": expense.get("nomeFavorecido", "N/A"),
                            "codigo": expense.get("codigoFavorecido", "N/A")
                        },
                        orgao=expense.get("nomeOrgao", "N/A"),
                        data=expense.get("data", "N/A"),
                        programa=expense.get("nomePrograma"),
                        acao=expense.get("nomeAcao")
                    )
                    results.append(expense_data.dict())
                
                return UniversalSearchResponse(
                    status="success",
                    data_source=request.data_source.value,
                    query=request.query,
                    results=results,
                    total_found=len(results),
                    anomalies_detected=anomalies,
                    confidence_score=0.85,
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    metadata={"high_value_threshold": 1000000}
                )
            else:
                raise HTTPException(status_code=response.status_code, detail="API request failed")
    
    async def _search_biddings(self, request: UniversalSearchRequest, api_key: str, start_time: float) -> UniversalSearchResponse:
        """Search for biddings/licitações."""
        # Implementation similar to contracts
        # For brevity, returning a simplified response
        return UniversalSearchResponse(
            status="success",
            data_source=request.data_source.value,
            query=request.query,
            results=[],
            total_found=0,
            anomalies_detected=0,
            confidence_score=0.8,
            processing_time_ms=int((time.time() - start_time) * 1000),
            metadata={"note": "Biddings endpoint to be implemented"}
        )
    
    async def _search_generic(self, request: UniversalSearchRequest, api_key: str, start_time: float) -> UniversalSearchResponse:
        """Generic search for other data types."""
        return UniversalSearchResponse(
            status="success",
            data_source=request.data_source.value,
            query=request.query,
            results=[],
            total_found=0,
            anomalies_detected=0,
            confidence_score=0.7,
            processing_time_ms=int((time.time() - start_time) * 1000),
            metadata={"note": f"Generic handler for {request.data_source.value}"}
        )
    
    async def _get_demo_data(self, request: UniversalSearchRequest, start_time: float) -> UniversalSearchResponse:
        """Return demo data when no API key is available."""
        demo_results = []
        
        if request.data_source == DataSourceType.SERVANTS:
            demo_results = [{
                "nome": "MARIA DA SILVA",
                "cpf_masked": "***.***.***-**",
                "matricula": "1234567",
                "orgao": "MINISTERIO DA SAUDE",
                "cargo": "ANALISTA",
                "funcao": "ANALISTA TECNICO",
                "remuneracao": {
                    "basica": 8500.00,
                    "total_liquido": 9876.54,
                    "gratificacoes": 2000.00,
                    "auxilios": 458.00
                },
                "mes_ano_referencia": "12/2024"
            }]
        elif request.data_source == DataSourceType.CONTRACTS:
            demo_results = [{
                "id": "demo-001",
                "numero": "2024/001",
                "objeto": "Contrato demonstrativo para testes",
                "valor": 150000.00,
                "fornecedor": {
                    "nome": "EMPRESA DEMO LTDA",
                    "cnpj": "00.000.000/0001-00"
                },
                "orgao": "ORGAO DEMONSTRATIVO",
                "data_assinatura": "01/01/2024",
                "vigencia": {
                    "inicio": "01/01/2024",
                    "fim": "31/12/2024"
                },
                "modalidade": "Pregão Eletrônico",
                "_anomaly": False,
                "_z_score": 0.5
            }]
        
        return UniversalSearchResponse(
            status="demo",
            data_source=request.data_source.value,
            query=request.query,
            results=demo_results,
            total_found=len(demo_results),
            anomalies_detected=0,
            confidence_score=0.5,
            processing_time_ms=int((time.time() - start_time) * 1000),
            metadata={"mode": "demo", "message": "Configure TRANSPARENCY_API_KEY for real data"}
        )

# ==================== FASTAPI APP ====================

# Create agent instance
enhanced_zumbi = EnhancedZumbiAgent()

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🏛️ Cidadão.AI Enhanced Backend starting up...")
    logger.info("🏹 Enhanced Zumbi agent ready for multi-source investigations")
    yield
    logger.info("👋 Cidadão.AI Enhanced Backend shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Cidadão.AI Enhanced Backend",
    description="Multi-source government transparency analysis with AI",
    version="2.0.0",
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

# ==================== ENDPOINTS ====================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with system status."""
    return HealthResponse()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse()

@app.post("/api/investigate", response_model=UniversalSearchResponse)
async def investigate_universal(request: UniversalSearchRequest):
    """
    Universal investigation endpoint for any data source.
    
    Example queries:
    - Servants: {"query": "João Silva", "data_source": "servidores"}
    - Contracts: {"query": "informática", "data_source": "contratos"}
    - Expenses: {"query": "todos", "data_source": "despesas", "filters": {"mes": 12}}
    """
    try:
        result = await enhanced_zumbi.investigate_universal(request)
        return result
    except Exception as e:
        logger.error(f"Investigation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Investigation failed: {str(e)}"
        )

@app.get("/api/data-sources")
async def list_data_sources():
    """List all available data sources."""
    return {
        "sources": [
            {
                "id": ds.value,
                "name": ds.name,
                "description": {
                    DataSourceType.CONTRACTS: "Government contracts and procurements",
                    DataSourceType.SERVANTS: "Public servants and their salaries",
                    DataSourceType.EXPENSES: "Government expenses and payments",
                    DataSourceType.BIDDINGS: "Public biddings and auctions",
                    DataSourceType.AGREEMENTS: "Government agreements and partnerships",
                    DataSourceType.SANCTIONS: "Sanctioned companies"
                }.get(ds, "Data source")
            }
            for ds in DataSourceType
        ]
    }

@app.get("/api/search/servants")
async def search_servants_quick(
    nome: str = Query(..., description="Nome do servidor"),
    orgao: Optional[str] = Query(None, description="Código do órgão"),
    limit: int = Query(10, ge=1, le=50, description="Limite de resultados")
):
    """Quick endpoint to search servants by name."""
    request = UniversalSearchRequest(
        query=nome,
        data_source=DataSourceType.SERVANTS,
        filters={"orgao": orgao} if orgao else {},
        max_results=limit
    )
    return await investigate_universal(request)

@app.get("/api/search/contracts")
async def search_contracts_quick(
    query: str = Query("todos", description="Termo de busca"),
    orgao: Optional[str] = Query(None, description="Código do órgão"),
    ano: int = Query(2024, description="Ano"),
    limit: int = Query(50, ge=1, le=100, description="Limite de resultados")
):
    """Quick endpoint to search contracts."""
    request = UniversalSearchRequest(
        query=query,
        data_source=DataSourceType.CONTRACTS,
        filters={"orgaos": [orgao] if orgao else ["26000", "25000"], "ano": ano},
        max_results=limit
    )
    return await investigate_universal(request)

@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    return {
        "cache_size": len(api_cache._cache),
        "active_entries": len([k for k, v in api_cache._ttl_cache.items() if v > datetime.now()]),
        "ttl_seconds": api_cache.default_ttl
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    logger.info(f"🚀 Starting Enhanced Cidadão.AI Backend on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)