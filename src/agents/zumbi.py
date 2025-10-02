"""
Module: agents.zumbi
Codinome: Zumbi - Investigador de Padrões
Description: Agent specialized in detecting anomalies and suspicious patterns in government data
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field as PydanticField

from src.agents.deodoro import BaseAgent, AgentContext, AgentMessage, AgentResponse
from src.core import get_logger, AgentStatus
from src.core.exceptions import AgentExecutionError, DataAnalysisError
from src.core.monitoring import (
    INVESTIGATIONS_TOTAL, ANOMALIES_DETECTED, INVESTIGATION_DURATION,
    DATA_RECORDS_PROCESSED, TRANSPARENCY_API_DATA_FETCHED
)
from src.tools.transparency_api import TransparencyAPIClient, TransparencyAPIFilter
from src.tools.models_client import ModelsClient, get_models_client
from src.ml.spectral_analyzer import SpectralAnalyzer, SpectralAnomaly
from src.tools.dados_gov_tool import DadosGovTool
import time


@dataclass
class AnomalyResult:
    """Result of anomaly detection analysis."""
    
    anomaly_type: str
    severity: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    description: str
    explanation: str
    evidence: Dict[str, Any]
    recommendations: List[str]
    affected_entities: List[Dict[str, Any]]
    financial_impact: Optional[float] = None


class InvestigationRequest(BaseModel):
    """Request for investigation with specific parameters."""
    
    query: str = PydanticField(description="Natural language investigation query")
    organization_codes: Optional[List[str]] = PydanticField(default=None, description="Specific organization codes to investigate")
    date_range: Optional[Tuple[str, str]] = PydanticField(default=None, description="Date range (start, end) in DD/MM/YYYY format")
    value_threshold: Optional[float] = PydanticField(default=None, description="Minimum value threshold for contracts")
    anomaly_types: Optional[List[str]] = PydanticField(default=None, description="Specific types of anomalies to look for")
    max_records: int = PydanticField(default=100, description="Maximum records to analyze")
    enable_open_data_enrichment: bool = PydanticField(default=True, description="Enable enrichment with dados.gov.br open data")


class InvestigatorAgent(BaseAgent):
    """
    Agent specialized in detecting anomalies and suspicious patterns in government data.
    
    Capabilities:
    - Price anomaly detection (overpriced contracts)
    - Temporal pattern analysis (suspicious timing)
    - Vendor concentration analysis (monopolization)
    - Duplicate contract detection
    - Unusual payment patterns
    - Explainable AI for transparency
    """
    
    def __init__(
        self,
        price_anomaly_threshold: float = 2.5,  # Standard deviations
        concentration_threshold: float = 0.7,   # 70% concentration trigger
        duplicate_similarity_threshold: float = 0.85,  # 85% similarity
    ):
        """
        Initialize the Investigator Agent.
        
        Args:
            price_anomaly_threshold: Number of standard deviations for price anomalies
            concentration_threshold: Threshold for vendor concentration (0-1)
            duplicate_similarity_threshold: Threshold for duplicate detection (0-1)
        """
        super().__init__(
            name="Zumbi",
            description="Zumbi dos Palmares - Agent specialized in detecting anomalies and suspicious patterns in government data",
            capabilities=[
                "price_anomaly_detection",
                "temporal_pattern_analysis",
                "vendor_concentration_analysis",
                "duplicate_contract_detection",
                "payment_pattern_analysis",
                "spectral_analysis",
                "explainable_ai",
                "open_data_enrichment"
            ],
            max_retries=3,
            timeout=60
        )
        self.price_threshold = price_anomaly_threshold
        self.concentration_threshold = concentration_threshold
        self.duplicate_threshold = duplicate_similarity_threshold
        
        # Initialize models client for ML inference (only if enabled)
        from src.core import settings
        if settings.models_api_enabled:
            self.models_client = get_models_client()
        else:
            self.models_client = None
            self.logger.info("Models API disabled, using only local ML")
        
        # Initialize spectral analyzer for frequency-domain analysis (fallback)
        self.spectral_analyzer = SpectralAnalyzer()
        
        # Initialize dados.gov.br tool for accessing open data
        self.dados_gov_tool = DadosGovTool()
        
        # Anomaly detection methods registry
        self.anomaly_detectors = {
            "price_anomaly": self._detect_price_anomalies,
            "vendor_concentration": self._detect_vendor_concentration,
            "temporal_patterns": self._detect_temporal_anomalies,
            "spectral_patterns": self._detect_spectral_anomalies,
            "duplicate_contracts": self._detect_duplicate_contracts,
            "payment_patterns": self._detect_payment_anomalies,
        }
        
        self.logger.info(
            "zumbi_initialized",
            agent_name=self.name,
            price_threshold=price_anomaly_threshold,
            concentration_threshold=concentration_threshold,
        )
    
    async def initialize(self) -> None:
        """Initialize agent resources."""
        self.logger.info(f"{self.name} agent initialized")
    
    async def shutdown(self) -> None:
        """Cleanup agent resources."""
        self.logger.info(f"{self.name} agent shutting down")
    
    async def process(
        self,
        message: AgentMessage,
        context: AgentContext
    ) -> AgentResponse:
        """
        Process investigation request and return anomaly detection results.
        
        Args:
            message: Investigation request message
            context: Agent execution context
            
        Returns:
            AgentResponse with detected anomalies
        """
        investigation_start_time = time.time()
        
        try:
            self.logger.info(
                "investigation_started",
                investigation_id=context.investigation_id,
                agent_name=self.name,
                action=message.action,
            )
            
            # Parse investigation request
            if message.action == "investigate":
                request = InvestigationRequest(**message.payload)
                
                # Record investigation start
                INVESTIGATIONS_TOTAL.labels(
                    agent_type="zumbi",
                    investigation_type=request.anomaly_types[0] if request.anomaly_types else "general",
                    status="started"
                ).inc()
                
            else:
                raise AgentExecutionError(
                    f"Unsupported action: {message.action}",
                    agent_id=self.name
                )
            
            # Fetch data for investigation
            contracts_data = await self._fetch_investigation_data(request, context)
            
            # Record data processed
            DATA_RECORDS_PROCESSED.labels(
                data_source="transparency_api",
                agent="zumbi",
                operation="fetch"
            ).inc(len(contracts_data) if contracts_data else 0)
            
            if not contracts_data:
                return AgentResponse(
                    agent_name=self.name,
                    status=AgentStatus.COMPLETED,
                    result={
                        "status": "no_data",
                        "message": "No data found for the specified criteria",
                        "anomalies": [],
                        "summary": {"total_records": 0, "anomalies_found": 0}
                    },
                    metadata={"investigation_id": context.investigation_id}
                )
            
            # Enrich data with open data information if available
            if request.enable_open_data_enrichment:
                contracts_data = await self._enrich_with_open_data(
                    contracts_data,
                    context
                )
            
            # Run anomaly detection
            anomalies = await self._run_anomaly_detection(
                contracts_data, 
                request, 
                context
            )
            
            # Record anomalies detected
            for anomaly in anomalies:
                ANOMALIES_DETECTED.labels(
                    anomaly_type=anomaly.anomaly_type,
                    severity="high" if anomaly.severity > 0.7 else "medium" if anomaly.severity > 0.4 else "low",
                    agent="zumbi"
                ).inc()
            
            # Generate investigation summary
            summary = self._generate_investigation_summary(contracts_data, anomalies)
            
            # Create result message
            result = {
                "status": "completed",
                "query": request.query,
                "anomalies": [self._anomaly_to_dict(a) for a in anomalies],
                "summary": summary,
                "metadata": {
                    "investigation_id": context.investigation_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent_name": self.name,
                    "records_analyzed": len(contracts_data),
                    "anomalies_detected": len(anomalies),
                }
            }
            
            # Record investigation completion and duration
            investigation_duration = time.time() - investigation_start_time
            INVESTIGATION_DURATION.labels(
                agent_type="zumbi",
                investigation_type=request.anomaly_types[0] if request.anomaly_types else "general"
            ).observe(investigation_duration)
            
            INVESTIGATIONS_TOTAL.labels(
                agent_type="zumbi",
                investigation_type=request.anomaly_types[0] if request.anomaly_types else "general",
                status="completed"
            ).inc()
            
            self.logger.info(
                "investigation_completed",
                investigation_id=context.investigation_id,
                records_analyzed=len(contracts_data),
                anomalies_found=len(anomalies),
                duration_seconds=investigation_duration,
            )
            
            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result=result,
                metadata={"investigation_id": context.investigation_id}
            )
            
        except Exception as e:
            # Record investigation failure
            INVESTIGATIONS_TOTAL.labels(
                agent_type="zumbi",
                investigation_type="general",  # Fallback for failed investigations
                status="failed"
            ).inc()
            
            self.logger.error(
                "investigation_failed",
                investigation_id=context.investigation_id,
                error=str(e),
                agent_name=self.name,
            )
            
            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.ERROR,
                error=str(e),
                result={
                    "status": "error",
                    "error": str(e),
                    "investigation_id": context.investigation_id,
                },
                metadata={"investigation_id": context.investigation_id}
            )
    
    async def _fetch_investigation_data(
        self,
        request: InvestigationRequest,
        context: AgentContext
    ) -> List[Dict[str, Any]]:
        """
        Fetch data from Portal da Transparência for investigation.
        
        Args:
            request: Investigation parameters
            context: Agent context
            
        Returns:
            List of contract records for analysis
        """
        all_contracts = []
        
        # Default organization codes if not specified
        org_codes = request.organization_codes or ["26000", "20000", "25000"]  # Health, Presidency, Education
        
        async with TransparencyAPIClient() as client:
            for org_code in org_codes:
                try:
                    # Create filters for this organization
                    filters = TransparencyAPIFilter(
                        codigo_orgao=org_code,
                        ano=2024,  # Current year
                        pagina=1,
                        tamanho_pagina=min(request.max_records // len(org_codes), 50)
                    )
                    
                    # Add date range if specified
                    if request.date_range:
                        filters.data_inicio = request.date_range[0]
                        filters.data_fim = request.date_range[1]
                    
                    # Add value threshold if specified
                    if request.value_threshold:
                        filters.valor_inicial = request.value_threshold
                    
                    # Fetch contracts
                    response = await client.get_contracts(filters)
                    
                    # Record API data fetched
                    TRANSPARENCY_API_DATA_FETCHED.labels(
                        endpoint="contracts",
                        organization=org_code,
                        status="success"
                    ).inc(len(response.data))
                    
                    # Add organization code to each contract
                    for contract in response.data:
                        contract["_org_code"] = org_code
                    
                    all_contracts.extend(response.data)
                    
                    self.logger.info(
                        "data_fetched",
                        org_code=org_code,
                        records=len(response.data),
                        investigation_id=context.investigation_id,
                    )
                    
                except Exception as e:
                    # Record API fetch failure
                    TRANSPARENCY_API_DATA_FETCHED.labels(
                        endpoint="contracts",
                        organization=org_code,
                        status="failed"
                    ).inc()
                    
                    self.logger.warning(
                        "data_fetch_failed",
                        org_code=org_code,
                        error=str(e),
                        investigation_id=context.investigation_id,
                    )
                    continue
        
        return all_contracts[:request.max_records]
    
    async def _enrich_with_open_data(
        self,
        contracts_data: List[Dict[str, Any]],
        context: AgentContext
    ) -> List[Dict[str, Any]]:
        """
        Enrich contract data with information from dados.gov.br.
        
        Args:
            contracts_data: Contract records
            context: Agent context
            
        Returns:
            Enriched contract data
        """
        # Extract unique organizations from contracts
        organizations = set()
        for contract in contracts_data:
            org_name = contract.get("orgao", {}).get("nome", "")
            if org_name:
                organizations.add(org_name)
        
        # Search for related datasets for each organization
        related_datasets = {}
        for org_name in organizations:
            try:
                # Search for datasets from this organization
                result = await self.dados_gov_tool._execute(
                    query=f"{org_name}, licitações, contratos",
                    action="search",
                    limit=5
                )
                
                if result.success and result.data:
                    related_datasets[org_name] = result.data.get("datasets", [])
                    
                    self.logger.info(
                        "open_data_found",
                        organization=org_name,
                        datasets_count=len(related_datasets[org_name]),
                        investigation_id=context.investigation_id,
                    )
            except Exception as e:
                self.logger.warning(
                    "open_data_search_failed",
                    organization=org_name,
                    error=str(e),
                    investigation_id=context.investigation_id,
                )
        
        # Enrich contracts with open data references
        for contract in contracts_data:
            org_name = contract.get("orgao", {}).get("nome", "")
            if org_name in related_datasets:
                contract["_open_data_available"] = True
                contract["_related_datasets"] = related_datasets[org_name]
            else:
                contract["_open_data_available"] = False
                contract["_related_datasets"] = []
        
        return contracts_data
    
    async def _run_anomaly_detection(
        self,
        contracts_data: List[Dict[str, Any]],
        request: InvestigationRequest,
        context: AgentContext
    ) -> List[AnomalyResult]:
        """
        Run all anomaly detection algorithms on the contract data.
        
        Args:
            contracts_data: Contract records to analyze
            request: Investigation parameters
            context: Agent context
            
        Returns:
            List of detected anomalies
        """
        all_anomalies = []
        
        # Determine which anomaly types to run
        types_to_run = request.anomaly_types or list(self.anomaly_detectors.keys())
        
        for anomaly_type in types_to_run:
            if anomaly_type in self.anomaly_detectors:
                try:
                    detector = self.anomaly_detectors[anomaly_type]
                    anomalies = await detector(contracts_data, context)
                    all_anomalies.extend(anomalies)
                    
                    self.logger.info(
                        "anomaly_detection_completed",
                        type=anomaly_type,
                        anomalies_found=len(anomalies),
                        investigation_id=context.investigation_id,
                    )
                    
                except Exception as e:
                    self.logger.error(
                        "anomaly_detection_failed",
                        type=anomaly_type,
                        error=str(e),
                        investigation_id=context.investigation_id,
                    )
        
        # Sort anomalies by severity (descending)
        all_anomalies.sort(key=lambda x: x.severity, reverse=True)
        
        return all_anomalies
    
    async def _detect_price_anomalies(
        self,
        contracts_data: List[Dict[str, Any]],
        context: AgentContext
    ) -> List[AnomalyResult]:
        """
        Detect contracts with anomalous pricing.
        
        Args:
            contracts_data: Contract records
            context: Agent context
            
        Returns:
            List of price anomalies
        """
        anomalies = []
        
        # Extract contract values
        values = []
        valid_contracts = []
        
        for contract in contracts_data:
            valor = contract.get("valorInicial") or contract.get("valorGlobal")
            if valor and isinstance(valor, (int, float)) and valor > 0:
                values.append(float(valor))
                valid_contracts.append(contract)
        
        if len(values) < 10:  # Need minimum samples for statistical analysis
            return anomalies
        
        # Calculate statistical measures
        values_array = np.array(values)
        mean_value = np.mean(values_array)
        std_value = np.std(values_array)
        
        # Detect outliers using z-score
        z_scores = np.abs((values_array - mean_value) / std_value)
        
        for i, (contract, value, z_score) in enumerate(zip(valid_contracts, values, z_scores)):
            if z_score > self.price_threshold:
                severity = min(z_score / 5.0, 1.0)  # Normalize to 0-1
                confidence = min(z_score / 3.0, 1.0)
                
                anomaly = AnomalyResult(
                    anomaly_type="price_anomaly",
                    severity=severity,
                    confidence=confidence,
                    description=f"Contrato com valor suspeito: R$ {value:,.2f}",
                    explanation=(
                        f"O valor deste contrato está {z_score:.1f} desvios padrão acima da média "
                        f"(R$ {mean_value:,.2f}). Valores muito acima do padrão podem indicar "
                        f"superfaturamento ou irregularidades no processo licitatório."
                    ),
                    evidence={
                        "contract_value": value,
                        "mean_value": mean_value,
                        "std_deviation": std_value,
                        "z_score": z_score,
                        "percentile": np.percentile(values_array, 95),
                    },
                    recommendations=[
                        "Investigar justificativas para o valor elevado",
                        "Comparar com contratos similares de outros órgãos",
                        "Verificar processo licitatório e documentação",
                        "Analisar histórico do fornecedor",
                    ],
                    affected_entities=[{
                        "contract_id": contract.get("id"),
                        "object": contract.get("objeto", "")[:100],
                        "supplier": contract.get("fornecedor", {}).get("nome", "N/A"),
                        "organization": contract.get("_org_code"),
                    }],
                    financial_impact=value - mean_value,
                )
                
                anomalies.append(anomaly)
        
        return anomalies
    
    async def _detect_vendor_concentration(
        self,
        contracts_data: List[Dict[str, Any]],
        context: AgentContext
    ) -> List[AnomalyResult]:
        """
        Detect excessive vendor concentration (potential monopolization).
        
        Args:
            contracts_data: Contract records
            context: Agent context
            
        Returns:
            List of vendor concentration anomalies
        """
        anomalies = []
        
        # Group contracts by vendor
        vendor_stats = {}
        total_value = 0
        
        for contract in contracts_data:
            supplier = contract.get("fornecedor", {})
            vendor_name = supplier.get("nome", "Unknown")
            vendor_cnpj = supplier.get("cnpj", "Unknown")
            vendor_key = f"{vendor_name}|{vendor_cnpj}"
            
            valor = contract.get("valorInicial") or contract.get("valorGlobal") or 0
            if isinstance(valor, (int, float)):
                valor = float(valor)
                total_value += valor
                
                if vendor_key not in vendor_stats:
                    vendor_stats[vendor_key] = {
                        "name": vendor_name,
                        "cnpj": vendor_cnpj,
                        "contracts": [],
                        "total_value": 0,
                        "contract_count": 0,
                    }
                
                vendor_stats[vendor_key]["contracts"].append(contract)
                vendor_stats[vendor_key]["total_value"] += valor
                vendor_stats[vendor_key]["contract_count"] += 1
        
        if total_value == 0:
            return anomalies
        
        # Check for concentration anomalies
        for vendor_key, stats in vendor_stats.items():
            concentration = stats["total_value"] / total_value
            
            if concentration > self.concentration_threshold:
                severity = min(concentration * 1.5, 1.0)
                confidence = concentration
                
                anomaly = AnomalyResult(
                    anomaly_type="vendor_concentration",
                    severity=severity,
                    confidence=confidence,
                    description=f"Concentração excessiva de contratos: {stats['name']}",
                    explanation=(
                        f"O fornecedor {stats['name']} concentra {concentration:.1%} do valor total "
                        f"dos contratos analisados ({stats['contract_count']} contratos). "
                        f"Alta concentração pode indicar direcionamento de licitações ou "
                        f"falta de competitividade no processo."
                    ),
                    evidence={
                        "vendor_name": stats["name"],
                        "vendor_cnpj": stats["cnpj"],
                        "concentration_percentage": concentration * 100,
                        "total_value": stats["total_value"],
                        "contract_count": stats["contract_count"],
                        "market_share": concentration,
                    },
                    recommendations=[
                        "Verificar se houve direcionamento nas licitações",
                        "Analisar competitividade do mercado",
                        "Investigar relacionamento entre órgão e fornecedor",
                        "Revisar critérios de seleção de fornecedores",
                    ],
                    affected_entities=[{
                        "vendor_name": stats["name"],
                        "vendor_cnpj": stats["cnpj"],
                        "contract_count": stats["contract_count"],
                        "total_value": stats["total_value"],
                    }],
                    financial_impact=stats["total_value"],
                )
                
                anomalies.append(anomaly)
        
        return anomalies
    
    async def _detect_temporal_anomalies(
        self,
        contracts_data: List[Dict[str, Any]],
        context: AgentContext
    ) -> List[AnomalyResult]:
        """
        Detect suspicious temporal patterns in contracts.
        
        Args:
            contracts_data: Contract records
            context: Agent context
            
        Returns:
            List of temporal anomalies
        """
        anomalies = []
        
        # Group contracts by date
        date_stats = {}
        
        for contract in contracts_data:
            # Try to extract date from different fields
            date_str = (
                contract.get("dataAssinatura") or 
                contract.get("dataPublicacao") or
                contract.get("dataInicio")
            )
            
            if date_str:
                try:
                    # Parse date (assuming DD/MM/YYYY format)
                    date_parts = date_str.split("/")
                    if len(date_parts) == 3:
                        day = int(date_parts[0])
                        month = int(date_parts[1])
                        year = int(date_parts[2])
                        
                        date_key = f"{year}-{month:02d}"
                        
                        if date_key not in date_stats:
                            date_stats[date_key] = {
                                "contracts": [],
                                "count": 0,
                                "total_value": 0,
                            }
                        
                        valor = contract.get("valorInicial") or contract.get("valorGlobal") or 0
                        if isinstance(valor, (int, float)):
                            date_stats[date_key]["total_value"] += float(valor)
                        
                        date_stats[date_key]["contracts"].append(contract)
                        date_stats[date_key]["count"] += 1
                        
                except (ValueError, IndexError):
                    continue
        
        if len(date_stats) < 3:  # Need minimum periods for comparison
            return anomalies
        
        # Calculate average contracts per period
        counts = [stats["count"] for stats in date_stats.values()]
        mean_count = np.mean(counts)
        std_count = np.std(counts)
        
        # Look for periods with unusually high activity
        for date_key, stats in date_stats.items():
            if std_count > 0:
                z_score = (stats["count"] - mean_count) / std_count
                
                if z_score > 2.0:  # More than 2 standard deviations
                    severity = min(z_score / 4.0, 1.0)
                    confidence = min(z_score / 3.0, 1.0)
                    
                    anomaly = AnomalyResult(
                        anomaly_type="temporal_patterns",
                        severity=severity,
                        confidence=confidence,
                        description=f"Atividade contratual suspeita em {date_key}",
                        explanation=(
                            f"Em {date_key} foram assinados {stats['count']} contratos, "
                            f"{z_score:.1f} desvios padrão acima da média ({mean_count:.1f}). "
                            f"Picos de atividade podem indicar direcionamento ou urgência "
                            f"inadequada nos processos."
                        ),
                        evidence={
                            "period": date_key,
                            "contract_count": stats["count"],
                            "mean_count": mean_count,
                            "z_score": z_score,
                            "total_value": stats["total_value"],
                        },
                        recommendations=[
                            "Investigar justificativas para a concentração temporal",
                            "Verificar se houve emergência ou urgência",
                            "Analisar qualidade dos processos licitatórios",
                            "Revisar planejamento de contratações",
                        ],
                        affected_entities=[{
                            "period": date_key,
                            "contract_count": stats["count"],
                            "total_value": stats["total_value"],
                        }],
                        financial_impact=stats["total_value"],
                    )
                    
                    anomalies.append(anomaly)
        
        return anomalies
    
    async def _detect_duplicate_contracts(
        self,
        contracts_data: List[Dict[str, Any]],
        context: AgentContext
    ) -> List[AnomalyResult]:
        """
        Detect potentially duplicate or very similar contracts.
        
        Args:
            contracts_data: Contract records
            context: Agent context
            
        Returns:
            List of duplicate contract anomalies
        """
        anomalies = []
        
        # Simple similarity detection based on object description
        for i, contract1 in enumerate(contracts_data):
            objeto1 = contract1.get("objeto", "").lower()
            if len(objeto1) < 20:  # Skip very short descriptions
                continue
                
            for j, contract2 in enumerate(contracts_data[i+1:], start=i+1):
                objeto2 = contract2.get("objeto", "").lower()
                if len(objeto2) < 20:
                    continue
                
                # Calculate simple similarity (Jaccard similarity of words)
                words1 = set(objeto1.split())
                words2 = set(objeto2.split())
                
                if len(words1) == 0 or len(words2) == 0:
                    continue
                
                intersection = len(words1.intersection(words2))
                union = len(words1.union(words2))
                similarity = intersection / union if union > 0 else 0
                
                if similarity > self.duplicate_threshold:
                    severity = similarity
                    confidence = similarity
                    
                    valor1 = contract1.get("valorInicial") or contract1.get("valorGlobal") or 0
                    valor2 = contract2.get("valorInicial") or contract2.get("valorGlobal") or 0
                    
                    anomaly = AnomalyResult(
                        anomaly_type="duplicate_contracts",
                        severity=severity,
                        confidence=confidence,
                        description="Contratos potencialmente duplicados detectados",
                        explanation=(
                            f"Dois contratos com {similarity:.1%} de similaridade foram "
                            f"encontrados. Contratos similares podem indicar pagamentos "
                            f"duplicados ou direcionamento inadequado."
                        ),
                        evidence={
                            "similarity_score": similarity,
                            "contract1_id": contract1.get("id"),
                            "contract2_id": contract2.get("id"),
                            "contract1_value": valor1,
                            "contract2_value": valor2,
                            "object1": objeto1[:100],
                            "object2": objeto2[:100],
                        },
                        recommendations=[
                            "Verificar se são contratos distintos ou duplicados",
                            "Analisar justificativas para objetos similares",
                            "Investigar fornecedores envolvidos",
                            "Revisar controles internos de contratação",
                        ],
                        affected_entities=[
                            {
                                "contract_id": contract1.get("id"),
                                "object": objeto1[:100],
                                "value": valor1,
                            },
                            {
                                "contract_id": contract2.get("id"),
                                "object": objeto2[:100],
                                "value": valor2,
                            },
                        ],
                        financial_impact=float(valor1) + float(valor2) if isinstance(valor1, (int, float)) and isinstance(valor2, (int, float)) else None,
                    )
                    
                    anomalies.append(anomaly)
        
        return anomalies
    
    async def _detect_payment_anomalies(
        self,
        contracts_data: List[Dict[str, Any]],
        context: AgentContext
    ) -> List[AnomalyResult]:
        """
        Detect unusual payment patterns in contracts.
        
        Args:
            contracts_data: Contract records
            context: Agent context
            
        Returns:
            List of payment anomalies
        """
        anomalies = []
        
        # Look for contracts with unusual value patterns
        for contract in contracts_data:
            valor_inicial = contract.get("valorInicial")
            valor_global = contract.get("valorGlobal")
            
            if valor_inicial and valor_global:
                try:
                    inicial = float(valor_inicial)
                    global_val = float(valor_global)
                    
                    # Check for significant discrepancies
                    if inicial > 0 and global_val > 0:
                        ratio = abs(inicial - global_val) / max(inicial, global_val)
                        
                        if ratio > 0.5:  # 50% discrepancy threshold
                            severity = min(ratio, 1.0)
                            confidence = ratio
                            
                            anomaly = AnomalyResult(
                                anomaly_type="payment_patterns",
                                severity=severity,
                                confidence=confidence,
                                description="Discrepância significativa entre valores do contrato",
                                explanation=(
                                    f"Diferença de {ratio:.1%} entre valor inicial "
                                    f"(R$ {inicial:,.2f}) e valor global (R$ {global_val:,.2f}). "
                                    f"Grandes discrepâncias podem indicar aditivos excessivos "
                                    f"ou irregularidades nos pagamentos."
                                ),
                                evidence={
                                    "valor_inicial": inicial,
                                    "valor_global": global_val,
                                    "discrepancy_ratio": ratio,
                                    "absolute_difference": abs(inicial - global_val),
                                },
                                recommendations=[
                                    "Investigar justificativas para alterações de valor",
                                    "Verificar aditivos contratuais",
                                    "Analisar execução e pagamentos realizados",
                                    "Revisar controles de alteração contratual",
                                ],
                                affected_entities=[{
                                    "contract_id": contract.get("id"),
                                    "object": contract.get("objeto", "")[:100],
                                    "supplier": contract.get("fornecedor", {}).get("nome", "N/A"),
                                }],
                                financial_impact=abs(inicial - global_val),
                            )
                            
                            anomalies.append(anomaly)
                            
                except (ValueError, TypeError):
                    continue
        
        return anomalies
    
    async def _detect_spectral_anomalies(
        self,
        contracts_data: List[Dict[str, Any]],
        context: AgentContext
    ) -> List[AnomalyResult]:
        """
        Detect anomalies using spectral analysis and Fourier transforms.
        
        Args:
            contracts_data: Contract records
            context: Agent context
            
        Returns:
            List of spectral anomalies
        """
        anomalies = []
        
        try:
            # Prepare time series data
            time_series_data = self._prepare_time_series(contracts_data)
            
            if len(time_series_data) < 30:  # Need sufficient data points
                self.logger.warning("insufficient_data_for_spectral_analysis", data_points=len(time_series_data))
                return anomalies
            
            # Extract spending values and timestamps
            spending_data = pd.Series([item['value'] for item in time_series_data])
            timestamps = pd.DatetimeIndex([item['date'] for item in time_series_data])
            
            # Perform spectral anomaly detection
            spectral_anomalies = self.spectral_analyzer.detect_anomalies(
                spending_data, 
                timestamps,
                context={'entity_name': context.investigation_id if hasattr(context, 'investigation_id') else 'Unknown'}
            )
            
            # Convert SpectralAnomaly objects to AnomalyResult objects
            for spec_anomaly in spectral_anomalies:
                anomaly = AnomalyResult(
                    anomaly_type=f"spectral_{spec_anomaly.anomaly_type}",
                    severity=spec_anomaly.anomaly_score,
                    confidence=spec_anomaly.anomaly_score,
                    description=spec_anomaly.description,
                    explanation=self._create_spectral_explanation(spec_anomaly),
                    evidence={
                        "frequency_band": spec_anomaly.frequency_band,
                        "anomaly_score": spec_anomaly.anomaly_score,
                        "timestamp": spec_anomaly.timestamp.isoformat(),
                        **spec_anomaly.evidence
                    },
                    recommendations=spec_anomaly.recommendations,
                    affected_entities=self._extract_affected_entities_from_spectral(spec_anomaly, contracts_data),
                    financial_impact=self._calculate_spectral_financial_impact(spec_anomaly, spending_data)
                )
                anomalies.append(anomaly)
            
            # Find periodic patterns
            periodic_patterns = self.spectral_analyzer.find_periodic_patterns(
                spending_data,
                timestamps,
                entity_name=context.investigation_id if hasattr(context, 'investigation_id') else None
            )
            
            # Convert suspicious periodic patterns to anomalies
            for pattern in periodic_patterns:
                if pattern.pattern_type == "suspicious" or pattern.amplitude > 0.5:
                    anomaly = AnomalyResult(
                        anomaly_type="suspicious_periodic_pattern",
                        severity=pattern.amplitude,
                        confidence=pattern.confidence,
                        description=f"Padrão periódico suspeito detectado (período: {pattern.period_days:.1f} dias)",
                        explanation=(
                            f"Detectado padrão de gastos com periodicidade de {pattern.period_days:.1f} dias "
                            f"e amplitude de {pattern.amplitude:.1%}. {pattern.business_interpretation}"
                        ),
                        evidence={
                            "period_days": pattern.period_days,
                            "frequency_hz": pattern.frequency_hz,
                            "amplitude": pattern.amplitude,
                            "confidence": pattern.confidence,
                            "pattern_type": pattern.pattern_type,
                            "statistical_significance": pattern.statistical_significance
                        },
                        recommendations=[
                            "Investigar causa do padrão periódico",
                            "Verificar se há processos automatizados",
                            "Analisar justificativas para regularidade excessiva",
                            "Revisar cronograma de pagamentos"
                        ],
                        affected_entities=[{
                            "pattern_type": pattern.pattern_type,
                            "period_days": pattern.period_days,
                            "amplitude": pattern.amplitude
                        }],
                        financial_impact=float(spending_data.sum() * pattern.amplitude)
                    )
                    anomalies.append(anomaly)
            
            self.logger.info(
                "spectral_analysis_completed",
                spectral_anomalies_count=len(spectral_anomalies),
                periodic_patterns_count=len(periodic_patterns),
                total_anomalies=len(anomalies)
            )
            
        except Exception as e:
            self.logger.error(f"Error in spectral anomaly detection: {str(e)}")
            # Don't fail the entire investigation if spectral analysis fails
        
        return anomalies
    
    def _prepare_time_series(self, contracts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prepare time series data from contracts for spectral analysis."""
        time_series = []
        
        for contract in contracts_data:
            # Extract date
            date_str = (
                contract.get("dataAssinatura") or 
                contract.get("dataPublicacao") or
                contract.get("dataInicio")
            )
            
            if not date_str:
                continue
                
            try:
                # Parse date (DD/MM/YYYY format)
                date_parts = date_str.split("/")
                if len(date_parts) == 3:
                    day, month, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                    date_obj = datetime(year, month, day)
                    
                    # Extract value
                    valor = contract.get("valorInicial") or contract.get("valorGlobal") or 0
                    if isinstance(valor, (int, float)) and valor > 0:
                        time_series.append({
                            'date': date_obj,
                            'value': float(valor),
                            'contract_id': contract.get('id'),
                            'supplier': contract.get('fornecedor', {}).get('nome', 'N/A')
                        })
                        
            except (ValueError, IndexError):
                continue
        
        # Sort by date
        time_series.sort(key=lambda x: x['date'])
        
        # Aggregate by date (sum values for same dates)
        daily_aggregates = {}
        for item in time_series:
            date_key = item['date'].date()
            if date_key not in daily_aggregates:
                daily_aggregates[date_key] = {
                    'date': datetime.combine(date_key, datetime.min.time()),
                    'value': 0,
                    'contract_count': 0,
                    'suppliers': set()
                }
            daily_aggregates[date_key]['value'] += item['value']
            daily_aggregates[date_key]['contract_count'] += 1
            daily_aggregates[date_key]['suppliers'].add(item['supplier'])
        
        # Convert back to list
        aggregated_series = []
        for date_key in sorted(daily_aggregates.keys()):
            data = daily_aggregates[date_key]
            aggregated_series.append({
                'date': data['date'],
                'value': data['value'],
                'contract_count': data['contract_count'],
                'unique_suppliers': len(data['suppliers'])
            })
        
        return aggregated_series
    
    def _create_spectral_explanation(self, spec_anomaly: SpectralAnomaly) -> str:
        """Create detailed explanation for spectral anomaly."""
        explanations = {
            "high_frequency_pattern": (
                "Detectado padrão de alta frequência nos gastos públicos. "
                "Padrões muito regulares podem indicar manipulação sistemática ou "
                "processos automatizados não documentados."
            ),
            "spectral_regime_change": (
                "Mudança significativa detectada na complexidade dos padrões de gastos. "
                "Alterações bruscas podem indicar mudanças de política, procedimentos "
                "ou possível manipulação."
            ),
            "excessive_quarterly_pattern": (
                "Padrão excessivo de gastos trimestrais detectado. "
                "Concentração de gastos no final de trimestres pode indicar "
                "execução inadequada de orçamento ou 'correria' para gastar verbas."
            ),
            "unusual_weekly_regularity": (
                "Regularidade semanal incomum detectada nos gastos. "
                "Padrões muito regulares em gastos governamentais podem ser suspeitos "
                "se não corresponderem a processos de negócio conhecidos."
            ),
            "high_frequency_noise": (
                "Ruído de alta frequência detectado nos dados de gastos. "
                "Pode indicar problemas na coleta de dados ou manipulação artificial "
                "dos valores reportados."
            )
        }
        
        base_explanation = explanations.get(
            spec_anomaly.anomaly_type,
            f"Anomalia espectral detectada: {spec_anomaly.description}"
        )
        
        return f"{base_explanation} Score de anomalia: {spec_anomaly.anomaly_score:.2f}. {spec_anomaly.description}"
    
    def _extract_affected_entities_from_spectral(
        self, 
        spec_anomaly: SpectralAnomaly, 
        contracts_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract affected entities from spectral anomaly context."""
        affected = []
        
        # For temporal anomalies, find contracts around the anomaly timestamp
        if hasattr(spec_anomaly, 'timestamp') and spec_anomaly.timestamp:
            anomaly_date = spec_anomaly.timestamp.date()
            
            for contract in contracts_data:
                date_str = (
                    contract.get("dataAssinatura") or 
                    contract.get("dataPublicacao") or
                    contract.get("dataInicio")
                )
                
                if date_str:
                    try:
                        date_parts = date_str.split("/")
                        if len(date_parts) == 3:
                            day, month, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
                            contract_date = datetime(year, month, day).date()
                            
                            # Include contracts within a week of the anomaly
                            if abs((contract_date - anomaly_date).days) <= 7:
                                affected.append({
                                    "contract_id": contract.get("id"),
                                    "date": date_str,
                                    "supplier": contract.get("fornecedor", {}).get("nome", "N/A"),
                                    "value": contract.get("valorInicial") or contract.get("valorGlobal") or 0,
                                    "object": contract.get("objeto", "")[:100]
                                })
                    except (ValueError, IndexError):
                        continue
        
        return affected[:10]  # Limit to first 10 to avoid overwhelming
    
    def _calculate_spectral_financial_impact(
        self, 
        spec_anomaly: SpectralAnomaly, 
        spending_data: pd.Series
    ) -> Optional[float]:
        """Calculate financial impact of spectral anomaly."""
        try:
            # For high-amplitude anomalies, estimate impact as percentage of total spending
            if hasattr(spec_anomaly, 'anomaly_score') and spec_anomaly.anomaly_score > 0:
                total_spending = float(spending_data.sum())
                impact_ratio = min(spec_anomaly.anomaly_score, 0.5)  # Cap at 50%
                return total_spending * impact_ratio
        except:
            pass
        
        return None
    
    def _generate_investigation_summary(
        self,
        contracts_data: List[Dict[str, Any]],
        anomalies: List[AnomalyResult]
    ) -> Dict[str, Any]:
        """Generate summary statistics for the investigation."""
        total_value = 0
        suspicious_value = 0
        
        # Calculate total contract value
        for contract in contracts_data:
            valor = contract.get("valorInicial") or contract.get("valorGlobal") or 0
            if isinstance(valor, (int, float)):
                total_value += float(valor)
        
        # Calculate suspicious value
        for anomaly in anomalies:
            if anomaly.financial_impact:
                suspicious_value += anomaly.financial_impact
        
        # Group anomalies by type
        anomaly_counts = {}
        for anomaly in anomalies:
            anomaly_type = anomaly.anomaly_type
            anomaly_counts[anomaly_type] = anomaly_counts.get(anomaly_type, 0) + 1
        
        # Calculate risk score
        risk_score = min(len(anomalies) / max(len(contracts_data), 1) * 10, 10)
        
        return {
            "total_records": len(contracts_data),
            "anomalies_found": len(anomalies),
            "total_value": total_value,
            "suspicious_value": suspicious_value,
            "risk_score": risk_score,
            "anomaly_types": anomaly_counts,
            "high_severity_count": len([a for a in anomalies if a.severity > 0.7]),
            "medium_severity_count": len([a for a in anomalies if 0.3 < a.severity <= 0.7]),
            "low_severity_count": len([a for a in anomalies if a.severity <= 0.3]),
        }
    
    def _anomaly_to_dict(self, anomaly: AnomalyResult) -> Dict[str, Any]:
        """Convert AnomalyResult to dictionary for serialization."""
        return {
            "type": anomaly.anomaly_type,
            "severity": anomaly.severity,
            "confidence": anomaly.confidence,
            "description": anomaly.description,
            "explanation": anomaly.explanation,
            "evidence": anomaly.evidence,
            "recommendations": anomaly.recommendations,
            "affected_entities": anomaly.affected_entities,
            "financial_impact": anomaly.financial_impact,
        }