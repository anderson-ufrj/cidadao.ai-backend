"""
Module: agents.anita
Codinome: Anita Garibaldi - Roteadora Semântica
Description: Agent specialized in pattern analysis and correlation detection in government data
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

import numpy as np
import pandas as pd
from pydantic import BaseModel
from pydantic import Field as PydanticField

from src.agents.deodoro import AgentContext, AgentMessage, AgentResponse, BaseAgent
from src.core import AgentStatus
from src.core.exceptions import AgentExecutionError
from src.ml.spectral_analyzer import SpectralAnalyzer, SpectralFeatures
from src.services.transparency_apis import get_transparency_collector


@dataclass
class PatternResult:
    """Result of pattern analysis."""

    pattern_type: str
    description: str
    significance: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    insights: list[str]
    evidence: dict[str, Any]
    recommendations: list[str]
    entities_involved: list[dict[str, Any]]
    trend_direction: Optional[str] = None  # "increasing", "decreasing", "stable"
    correlation_strength: Optional[float] = None


@dataclass
class CorrelationResult:
    """Result of correlation analysis."""

    correlation_type: str
    variables: list[str]
    correlation_coefficient: float
    p_value: Optional[float]
    significance_level: str  # "high", "medium", "low"
    description: str
    business_interpretation: str
    evidence: dict[str, Any]
    recommendations: list[str]


class AnalysisRequest(BaseModel):
    """Request for pattern and correlation analysis."""

    query: str = PydanticField(description="Natural language analysis query")
    analysis_types: Optional[list[str]] = PydanticField(
        default=None, description="Types of analysis to perform"
    )
    time_period: Optional[str] = PydanticField(
        default="12_months", description="Time period for analysis"
    )
    organization_codes: Optional[list[str]] = PydanticField(
        default=None, description="Organizations to analyze"
    )
    focus_areas: Optional[list[str]] = PydanticField(
        default=None, description="Specific areas to focus on"
    )
    comparison_mode: bool = PydanticField(
        default=False, description="Enable comparison between entities"
    )
    max_records: int = PydanticField(
        default=200, description="Maximum records for analysis"
    )


class AnalystAgent(BaseAgent):
    """
    Agent specialized in pattern analysis and correlation detection in government data.

    Capabilities:
    - Spending trend analysis over time
    - Organizational spending pattern comparison
    - Vendor market behavior analysis
    - Seasonal pattern detection
    - Contract value distribution analysis
    - Cross-organizational correlation analysis
    - Performance and efficiency metrics
    - Predictive trend modeling
    """

    def __init__(
        self,
        min_correlation_threshold: float = 0.3,
        significance_threshold: float = 0.05,
        trend_detection_window: int = 6,  # months
    ):
        """
        Initialize the Analyst Agent.

        Args:
            min_correlation_threshold: Minimum correlation coefficient to report
            significance_threshold: P-value threshold for statistical significance
            trend_detection_window: Number of periods for trend analysis
        """
        super().__init__(
            name="Anita",
            description="Anita Garibaldi - Agent specialized in pattern analysis and correlation detection",
            capabilities=[
                "spending_trend_analysis",
                "organizational_comparison",
                "vendor_behavior_analysis",
                "seasonal_pattern_detection",
                "value_distribution_analysis",
                "correlation_analysis",
                "efficiency_metrics",
                "predictive_modeling",
            ],
            max_retries=3,
            timeout=60,
        )
        self.correlation_threshold = min_correlation_threshold
        self.significance_threshold = significance_threshold
        self.trend_window = trend_detection_window

        # Initialize spectral analyzer for frequency-domain analysis
        self.spectral_analyzer = SpectralAnalyzer()

        # Analysis methods registry
        self.analysis_methods = {
            "spending_trends": self._analyze_spending_trends,
            "organizational_patterns": self._analyze_organizational_patterns,
            "vendor_behavior": self._analyze_vendor_behavior,
            "seasonal_patterns": self._analyze_seasonal_patterns,
            "spectral_patterns": self._analyze_spectral_patterns,
            "cross_spectral_analysis": self._perform_cross_spectral_analysis,
            "value_distribution": self._analyze_value_distribution,
            "correlation_analysis": self._perform_correlation_analysis,
            "efficiency_metrics": self._calculate_efficiency_metrics,
        }

        self.logger.info(
            "analyst_agent_initialized",
            agent_name=self.name,
            correlation_threshold=min_correlation_threshold,
            significance_threshold=significance_threshold,
        )

    async def initialize(self) -> None:
        """Initialize agent resources."""
        self.logger.info(f"{self.name} agent initialized")

    async def shutdown(self) -> None:
        """Cleanup agent resources."""
        self.logger.info(f"{self.name} agent shutting down")

    async def process(
        self, message: AgentMessage, context: AgentContext
    ) -> AgentResponse:
        """
        Process pattern analysis request and return insights.

        Args:
            message: Analysis request message
            context: Agent execution context

        Returns:
            AgentResponse with patterns and correlations
        """
        try:
            self.logger.info(
                "analysis_started",
                investigation_id=context.investigation_id,
                agent_name=self.name,
                action=message.action,
            )

            # Parse analysis request
            if message.action == "analyze":
                request = AnalysisRequest(**message.payload)
            else:
                raise AgentExecutionError(
                    f"Unsupported action: {message.action}", agent_id=self.name
                )

            # Fetch data for analysis
            analysis_data = await self._fetch_analysis_data(request, context)

            if not analysis_data:
                return AgentResponse(
                    agent_name=self.name,
                    status=AgentStatus.COMPLETED,
                    result={
                        "status": "no_data",
                        "message": "No data found for the specified criteria",
                        "patterns": [],
                        "correlations": [],
                        "summary": {"total_records": 0, "patterns_found": 0},
                    },
                    metadata={"investigation_id": context.investigation_id},
                )

            # Perform pattern analysis
            patterns = await self._run_pattern_analysis(analysis_data, request, context)

            # Perform correlation analysis
            correlations = await self._run_correlation_analysis(
                analysis_data, request, context
            )

            # Generate insights and recommendations
            insights = self._generate_insights(patterns, correlations, analysis_data)

            # Create result message
            result = {
                "status": "completed",
                "query": request.query,
                "patterns": [self._pattern_to_dict(p) for p in patterns],
                "correlations": [self._correlation_to_dict(c) for c in correlations],
                "insights": insights,
                "summary": self._generate_analysis_summary(
                    analysis_data, patterns, correlations
                ),
                "metadata": {
                    "investigation_id": context.investigation_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent_name": self.name,
                    "records_analyzed": len(analysis_data),
                    "patterns_found": len(patterns),
                    "correlations_found": len(correlations),
                },
            }

            self.logger.info(
                "analysis_completed",
                investigation_id=context.investigation_id,
                records_analyzed=len(analysis_data),
                patterns_found=len(patterns),
                correlations_found=len(correlations),
            )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result=result,
                metadata={"investigation_id": context.investigation_id},
            )

        except Exception as e:
            self.logger.error(
                "analysis_failed",
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
                metadata={"investigation_id": context.investigation_id},
            )

    async def _fetch_analysis_data(
        self, request: AnalysisRequest, context: AgentContext
    ) -> list[dict[str, Any]]:
        """
        Fetch comprehensive data for pattern analysis from multiple transparency sources.

        Uses TransparencyDataCollector to access federal, state, TCE, and CKAN APIs
        across Brazil, enabling comprehensive pattern and correlation analysis.

        Args:
            request: Analysis parameters
            context: Agent context

        Returns:
            List of contract records for analysis with temporal metadata
        """
        collector = get_transparency_collector()
        all_contracts = []

        # Determine year for analysis
        year = 2024

        try:
            # Collect contracts from multiple sources
            # TransparencyDataCollector aggregates data from:
            # - Federal Portal da Transparência
            # - 6 TCE APIs (PE, CE, RJ, SP, MG, BA)
            # - 5 CKAN portals (SP, RJ, RS, SC, BA)
            # - 1 State API (RO)
            result = await collector.collect_contracts(
                state=None,  # Collect from all states
                municipality_code=None,  # All municipalities
                year=year,
                validate=True,  # Enable data validation
            )

            contracts_data = result["contracts"]

            # Enrich contracts with temporal metadata for time-series analysis
            for contract in contracts_data:
                # Extract month from date fields if available
                date_str = (
                    contract.get("dataAssinatura")
                    or contract.get("dataPublicacao")
                    or contract.get("dataInicio")
                )

                if date_str:
                    try:
                        # Parse date (DD/MM/YYYY format)
                        date_parts = date_str.split("/")
                        if len(date_parts) == 3:
                            day, month, year_val = (
                                int(date_parts[0]),
                                int(date_parts[1]),
                                int(date_parts[2]),
                            )
                            contract["_month"] = month
                            contract["_year"] = year_val
                    except (ValueError, IndexError):
                        # Fallback to current year if date parsing fails
                        contract["_month"] = None
                        contract["_year"] = year

                # Add fetch timestamp for tracking
                contract["_fetch_timestamp"] = datetime.utcnow().isoformat()

                # Preserve or add organization code
                if not contract.get("_org_code"):
                    # Extract org code from contract data if available
                    orgao = contract.get("orgao", {})
                    if isinstance(orgao, dict):
                        org_code = orgao.get("codigo") or orgao.get("codigoSIAFI")
                        if org_code:
                            contract["_org_code"] = str(org_code)

            all_contracts.extend(contracts_data)

            # Log multi-source fetch success
            self.logger.info(
                "multi_source_analysis_data_fetched",
                total_contracts=result["total"],
                sources_count=len(result["sources"]),
                sources=result["sources"],
                errors_count=len(result["errors"]),
                contracts_with_dates=len(
                    [c for c in contracts_data if c.get("_month")]
                ),
                investigation_id=context.investigation_id,
            )

            # Log any source failures
            for error in result.get("errors", []):
                self.logger.warning(
                    "source_analysis_fetch_failed",
                    api=error.get("api"),
                    error=error.get("error"),
                    investigation_id=context.investigation_id,
                )

        except Exception as e:
            self.logger.error(
                "multi_source_analysis_fetch_failed",
                error=str(e),
                investigation_id=context.investigation_id,
            )
            # Return empty list on catastrophic failure
            return []

        return all_contracts[: request.max_records]

    async def _run_pattern_analysis(
        self,
        data: list[dict[str, Any]],
        request: AnalysisRequest,
        context: AgentContext,
    ) -> list[PatternResult]:
        """
        Run pattern analysis algorithms on the data.

        Args:
            data: Contract records to analyze
            request: Analysis parameters
            context: Agent context

        Returns:
            List of detected patterns
        """
        all_patterns = []

        # Determine which analysis types to run
        types_to_run = request.analysis_types or list(self.analysis_methods.keys())
        types_to_run = [
            t for t in types_to_run if t != "correlation_analysis"
        ]  # Handle separately

        for analysis_type in types_to_run:
            if analysis_type in self.analysis_methods:
                try:
                    method = self.analysis_methods[analysis_type]
                    patterns = await method(data, context)
                    all_patterns.extend(patterns)

                    self.logger.info(
                        "pattern_analysis_completed",
                        type=analysis_type,
                        patterns_found=len(patterns),
                        investigation_id=context.investigation_id,
                    )

                except Exception as e:
                    self.logger.error(
                        "pattern_analysis_failed",
                        type=analysis_type,
                        error=str(e),
                        investigation_id=context.investigation_id,
                    )

        # Sort patterns by significance
        all_patterns.sort(key=lambda x: x.significance, reverse=True)

        return all_patterns

    async def _run_correlation_analysis(
        self,
        data: list[dict[str, Any]],
        request: AnalysisRequest,
        context: AgentContext,
    ) -> list[CorrelationResult]:
        """
        Run correlation analysis on the data.

        Args:
            data: Contract records to analyze
            request: Analysis parameters
            context: Agent context

        Returns:
            List of detected correlations
        """
        correlations = []

        if "correlation_analysis" in (
            request.analysis_types or ["correlation_analysis"]
        ):
            try:
                correlations = await self._perform_correlation_analysis(data, context)

                self.logger.info(
                    "correlation_analysis_completed",
                    correlations_found=len(correlations),
                    investigation_id=context.investigation_id,
                )

            except Exception as e:
                self.logger.error(
                    "correlation_analysis_failed",
                    error=str(e),
                    investigation_id=context.investigation_id,
                )

        return correlations

    async def _analyze_spending_trends(
        self, data: list[dict[str, Any]], context: AgentContext
    ) -> list[PatternResult]:
        """Analyze spending trends over time."""
        patterns = []

        # Group spending by month
        monthly_spending = defaultdict(float)
        monthly_counts = defaultdict(int)

        for contract in data:
            month = contract.get("_month")
            valor = contract.get("valorInicial") or contract.get("valorGlobal") or 0

            if month and isinstance(valor, (int, float)):
                monthly_spending[month] += float(valor)
                monthly_counts[month] += 1

        if len(monthly_spending) < 3:
            return patterns

        # Calculate trend
        months = sorted(monthly_spending.keys())
        values = [monthly_spending[m] for m in months]

        # Simple linear regression for trend
        x = np.array(range(len(months)))
        y = np.array(values)

        if len(x) > 1 and np.std(y) > 0:
            correlation = np.corrcoef(x, y)[0, 1]
            slope = np.polyfit(x, y, 1)[0]

            # Determine trend direction and significance
            if abs(correlation) > 0.5:
                trend_direction = "increasing" if slope > 0 else "decreasing"
                significance = abs(correlation)

                pattern = PatternResult(
                    pattern_type="spending_trends",
                    description=f"Tendência de gastos {trend_direction} detectada",
                    significance=significance,
                    confidence=abs(correlation),
                    insights=[
                        f"Gastos apresentam tendência {trend_direction} com correlação de {correlation:.2f}",
                        f"Variação média mensal: R$ {slope:,.2f}",
                        f"Período analisado: {len(months)} meses",
                    ],
                    evidence={
                        "monthly_spending": dict(monthly_spending),
                        "trend_correlation": correlation,
                        "monthly_slope": slope,
                        "total_value": sum(values),
                        "average_monthly": np.mean(values),
                    },
                    recommendations=[
                        "Investigar fatores que causam a tendência observada",
                        "Analisar planejamento orçamentário",
                        "Verificar sazonalidade nos gastos",
                        "Monitorar sustentabilidade da tendência",
                    ],
                    entities_involved=[
                        {
                            "type": "monthly_data",
                            "months_analyzed": len(months),
                            "total_contracts": sum(monthly_counts.values()),
                        }
                    ],
                    trend_direction=trend_direction,
                    correlation_strength=abs(correlation),
                )

                patterns.append(pattern)

        return patterns

    async def _analyze_organizational_patterns(
        self, data: list[dict[str, Any]], context: AgentContext
    ) -> list[PatternResult]:
        """Analyze spending patterns across organizations."""
        patterns = []

        # Group by organization
        org_stats = defaultdict(lambda: {"total_value": 0, "count": 0, "contracts": []})

        for contract in data:
            org_code = contract.get("_org_code")
            valor = contract.get("valorInicial") or contract.get("valorGlobal") or 0

            if org_code and isinstance(valor, (int, float)):
                org_stats[org_code]["total_value"] += float(valor)
                org_stats[org_code]["count"] += 1
                org_stats[org_code]["contracts"].append(contract)

        if len(org_stats) < 2:
            return patterns

        # Calculate organization efficiency metrics
        org_efficiency = {}
        for org_code, stats in org_stats.items():
            if stats["count"] > 0:
                avg_contract_value = stats["total_value"] / stats["count"]
                org_efficiency[org_code] = {
                    "avg_contract_value": avg_contract_value,
                    "total_value": stats["total_value"],
                    "contract_count": stats["count"],
                    "efficiency_ratio": stats["total_value"] / stats["count"],
                }

        # Find organizations with unusual patterns
        avg_values = [eff["avg_contract_value"] for eff in org_efficiency.values()]
        mean_avg = np.mean(avg_values)
        std_avg = np.std(avg_values)

        for org_code, efficiency in org_efficiency.items():
            if std_avg > 0:
                z_score = (efficiency["avg_contract_value"] - mean_avg) / std_avg

                if abs(z_score) > 1.5:  # Significant deviation
                    pattern_type = (
                        "high_value_contracts" if z_score > 0 else "low_value_contracts"
                    )
                    significance = min(abs(z_score) / 3.0, 1.0)

                    pattern = PatternResult(
                        pattern_type="organizational_patterns",
                        description=f"Padrão organizacional atípico: {org_code}",
                        significance=significance,
                        confidence=min(abs(z_score) / 2.0, 1.0),
                        insights=[
                            f"Organização {org_code} apresenta padrão atípico de contratação",
                            f"Valor médio por contrato: R$ {efficiency['avg_contract_value']:,.2f}",
                            f"Desvio da média geral: {z_score:.1f} desvios padrão",
                        ],
                        evidence={
                            "organization_code": org_code,
                            "avg_contract_value": efficiency["avg_contract_value"],
                            "total_value": efficiency["total_value"],
                            "contract_count": efficiency["contract_count"],
                            "z_score": z_score,
                            "market_average": mean_avg,
                        },
                        recommendations=[
                            "Investigar critérios de contratação da organização",
                            "Comparar com organizações similares",
                            "Analisar eficiência dos processos",
                            "Verificar adequação dos valores contratados",
                        ],
                        entities_involved=[
                            {
                                "organization": org_code,
                                "total_contracts": efficiency["contract_count"],
                                "total_value": efficiency["total_value"],
                            }
                        ],
                    )

                    patterns.append(pattern)

        return patterns

    async def _analyze_vendor_behavior(
        self, data: list[dict[str, Any]], context: AgentContext
    ) -> list[PatternResult]:
        """Analyze vendor behavior patterns."""
        patterns = []

        # Group by vendor
        vendor_stats = defaultdict(
            lambda: {
                "contracts": [],
                "total_value": 0,
                "organizations": set(),
                "months": set(),
            }
        )

        for contract in data:
            supplier = contract.get("fornecedor", {})
            vendor_name = supplier.get("nome", "Unknown")
            valor = contract.get("valorInicial") or contract.get("valorGlobal") or 0
            org_code = contract.get("_org_code")
            month = contract.get("_month")

            if vendor_name != "Unknown" and isinstance(valor, (int, float)):
                vendor_stats[vendor_name]["contracts"].append(contract)
                vendor_stats[vendor_name]["total_value"] += float(valor)
                if org_code:
                    vendor_stats[vendor_name]["organizations"].add(org_code)
                if month:
                    vendor_stats[vendor_name]["months"].add(month)

        # Analyze multi-organization vendors
        for vendor_name, stats in vendor_stats.items():
            org_count = len(stats["organizations"])
            contract_count = len(stats["contracts"])

            # Check for vendors working with multiple organizations
            if org_count >= 3 and contract_count >= 5:
                significance = min(org_count / 6.0, 1.0)  # Normalize to max 6 orgs

                pattern = PatternResult(
                    pattern_type="vendor_behavior",
                    description=f"Fornecedor multi-organizacional: {vendor_name}",
                    significance=significance,
                    confidence=min(contract_count / 10.0, 1.0),
                    insights=[
                        f"Fornecedor atua em {org_count} organizações diferentes",
                        f"Total de {contract_count} contratos",
                        f"Valor total: R$ {stats['total_value']:,.2f}",
                        f"Presença em {len(stats['months'])} meses diferentes",
                    ],
                    evidence={
                        "vendor_name": vendor_name,
                        "organization_count": org_count,
                        "contract_count": contract_count,
                        "total_value": stats["total_value"],
                        "organizations": list(stats["organizations"]),
                        "months_active": len(stats["months"]),
                    },
                    recommendations=[
                        "Verificar especialização do fornecedor",
                        "Analisar competitividade dos processos",
                        "Investigar relacionamento com múltiplas organizações",
                        "Revisar histórico de performance",
                    ],
                    entities_involved=[
                        {
                            "vendor": vendor_name,
                            "organizations": list(stats["organizations"]),
                            "contract_count": contract_count,
                        }
                    ],
                )

                patterns.append(pattern)

        return patterns

    async def _analyze_seasonal_patterns(
        self, data: list[dict[str, Any]], context: AgentContext
    ) -> list[PatternResult]:
        """Analyze seasonal patterns in contracting."""
        patterns = []

        # Group by month
        monthly_activity = defaultdict(lambda: {"count": 0, "value": 0})

        for contract in data:
            month = contract.get("_month")
            valor = contract.get("valorInicial") or contract.get("valorGlobal") or 0

            if month and isinstance(valor, (int, float)):
                monthly_activity[month]["count"] += 1
                monthly_activity[month]["value"] += float(valor)

        if len(monthly_activity) < 6:  # Need at least half year
            return patterns

        # Calculate monthly averages
        months = sorted(monthly_activity.keys())
        counts = [monthly_activity[m]["count"] for m in months]
        values = [monthly_activity[m]["value"] for m in months]

        # Detect end-of-year rush (December spike)
        if 12 in monthly_activity and len(months) >= 6:
            dec_count = monthly_activity[12]["count"]
            avg_count = np.mean(
                [monthly_activity[m]["count"] for m in months if m != 12]
            )

            if avg_count > 0:
                dec_ratio = dec_count / avg_count

                if dec_ratio > 1.5:  # 50% above average
                    significance = min((dec_ratio - 1) / 2, 1.0)

                    pattern = PatternResult(
                        pattern_type="seasonal_patterns",
                        description="Padrão sazonal: concentração em dezembro",
                        significance=significance,
                        confidence=min(dec_ratio / 2.0, 1.0),
                        insights=[
                            f"Dezembro apresenta {dec_ratio:.1f}x mais contratos que a média",
                            f"Contratos em dezembro: {dec_count}",
                            f"Média mensal: {avg_count:.1f}",
                            "Possível correria de fim de ano orçamentário",
                        ],
                        evidence={
                            "december_count": dec_count,
                            "average_monthly_count": avg_count,
                            "december_ratio": dec_ratio,
                            "monthly_distribution": dict(monthly_activity),
                        },
                        recommendations=[
                            "Melhorar planejamento anual de contratações",
                            "Distribuir contratações ao longo do ano",
                            "Investigar qualidade dos processos de fim de ano",
                            "Implementar cronograma de contratações",
                        ],
                        entities_involved=[
                            {
                                "pattern": "end_of_year_rush",
                                "affected_months": [12],
                                "intensity": dec_ratio,
                            }
                        ],
                    )

                    patterns.append(pattern)

        return patterns

    async def _analyze_value_distribution(
        self, data: list[dict[str, Any]], context: AgentContext
    ) -> list[PatternResult]:
        """Analyze contract value distribution patterns."""
        patterns = []

        # Extract contract values
        values = []
        for contract in data:
            valor = contract.get("valorInicial") or contract.get("valorGlobal") or 0
            if isinstance(valor, (int, float)) and valor > 0:
                values.append(float(valor))

        if len(values) < 10:
            return patterns

        # Calculate distribution statistics
        values_array = np.array(values)

        # Check for unusual distribution patterns
        percentiles = np.percentile(values_array, [25, 50, 75, 90, 95, 99])

        # Detect heavy concentration in specific value ranges
        value_ranges = {
            "micro": (0, 8000),  # Dispensas
            "small": (8000, 176000),  # Convites
            "medium": (176000, 1500000),  # Tomadas de preço
            "large": (1500000, float("inf")),  # Concorrências
        }

        range_counts = {}
        range_values = {}

        for range_name, (min_val, max_val) in value_ranges.items():
            count = sum(1 for v in values if min_val <= v < max_val)
            total_val = sum(v for v in values if min_val <= v < max_val)
            range_counts[range_name] = count
            range_values[range_name] = total_val

        total_contracts = len(values)
        total_value = sum(values)

        # Check for unusual concentrations
        for range_name, count in range_counts.items():
            percentage = count / total_contracts if total_contracts > 0 else 0
            value_percentage = (
                range_values[range_name] / total_value if total_value > 0 else 0
            )

            # Detect if one range dominates
            if percentage > 0.7:  # 70% of contracts in one range
                significance = percentage

                pattern = PatternResult(
                    pattern_type="value_distribution",
                    description=f"Concentração em contratos de valor {range_name}",
                    significance=significance,
                    confidence=percentage,
                    insights=[
                        f"{percentage:.1%} dos contratos estão na faixa {range_name}",
                        f"Representam {value_percentage:.1%} do valor total",
                        f"Total de {count} contratos nesta faixa",
                        f"Faixa de valores: R$ {value_ranges[range_name][0]:,.2f} - R$ {value_ranges[range_name][1]:,.2f}",
                    ],
                    evidence={
                        "range_name": range_name,
                        "concentration_percentage": percentage * 100,
                        "value_percentage": value_percentage * 100,
                        "contract_count": count,
                        "range_limits": value_ranges[range_name],
                        "distribution": range_counts,
                    },
                    recommendations=[
                        "Analisar adequação dos valores contratados",
                        "Verificar se há fracionamento inadequado",
                        "Revisar modalidades licitatórias utilizadas",
                        "Comparar com benchmarks do setor",
                    ],
                    entities_involved=[
                        {
                            "value_range": range_name,
                            "contract_count": count,
                            "percentage": percentage * 100,
                        }
                    ],
                )

                patterns.append(pattern)

        return patterns

    async def _perform_correlation_analysis(
        self, data: list[dict[str, Any]], context: AgentContext
    ) -> list[CorrelationResult]:
        """Perform correlation analysis between variables."""
        correlations = []

        # Prepare data for correlation analysis
        # Group by organization and month for time series
        org_month_data = defaultdict(
            lambda: defaultdict(lambda: {"count": 0, "value": 0})
        )

        for contract in data:
            org_code = contract.get("_org_code")
            month = contract.get("_month")
            valor = contract.get("valorInicial") or contract.get("valorGlobal") or 0

            if org_code and month and isinstance(valor, (int, float)):
                org_month_data[org_code][month]["count"] += 1
                org_month_data[org_code][month]["value"] += float(valor)

        # Analyze correlation between contract count and average value
        if len(org_month_data) >= 3:
            monthly_counts = []
            monthly_avg_values = []

            for org_code, month_data in org_month_data.items():
                for month, stats in month_data.items():
                    if stats["count"] > 0:
                        monthly_counts.append(stats["count"])
                        monthly_avg_values.append(stats["value"] / stats["count"])

            if len(monthly_counts) >= 10 and len(monthly_avg_values) >= 10:
                # Calculate correlation between count and average value
                correlation_coef = np.corrcoef(monthly_counts, monthly_avg_values)[0, 1]

                if abs(correlation_coef) > self.correlation_threshold:
                    significance_level = (
                        "high" if abs(correlation_coef) > 0.7 else "medium"
                    )

                    interpretation = (
                        "Correlação negativa indica que meses com mais contratos tendem a ter valores médios menores"
                        if correlation_coef < 0
                        else "Correlação positiva indica que meses com mais contratos tendem a ter valores médios maiores"
                    )

                    correlation = CorrelationResult(
                        correlation_type="count_vs_value",
                        variables=["monthly_contract_count", "monthly_average_value"],
                        correlation_coefficient=correlation_coef,
                        p_value=None,  # Would need scipy.stats for p-value
                        significance_level=significance_level,
                        description="Correlação entre quantidade e valor médio de contratos",
                        business_interpretation=interpretation,
                        evidence={
                            "correlation_coefficient": correlation_coef,
                            "sample_size": len(monthly_counts),
                            "count_range": [min(monthly_counts), max(monthly_counts)],
                            "value_range": [
                                min(monthly_avg_values),
                                max(monthly_avg_values),
                            ],
                        },
                        recommendations=[
                            "Investigar fatores que influenciam essa correlação",
                            "Analisar estratégias de contratação",
                            "Verificar planejamento orçamentário",
                            "Monitorar tendências futuras",
                        ],
                    )

                    correlations.append(correlation)

        return correlations

    async def _calculate_efficiency_metrics(
        self, data: list[dict[str, Any]], context: AgentContext
    ) -> list[PatternResult]:
        """Calculate efficiency metrics for organizations."""
        patterns = []

        # Calculate metrics by organization
        org_metrics = defaultdict(
            lambda: {
                "total_value": 0,
                "contract_count": 0,
                "unique_vendors": set(),
                "months_active": set(),
            }
        )

        for contract in data:
            org_code = contract.get("_org_code")
            valor = contract.get("valorInicial") or contract.get("valorGlobal") or 0
            supplier = contract.get("fornecedor", {}).get("nome")
            month = contract.get("_month")

            if org_code and isinstance(valor, (int, float)):
                org_metrics[org_code]["total_value"] += float(valor)
                org_metrics[org_code]["contract_count"] += 1
                if supplier:
                    org_metrics[org_code]["unique_vendors"].add(supplier)
                if month:
                    org_metrics[org_code]["months_active"].add(month)

        # Calculate efficiency scores
        efficiency_scores = {}
        for org_code, metrics in org_metrics.items():
            if metrics["contract_count"] > 0:
                vendor_diversity = (
                    len(metrics["unique_vendors"]) / metrics["contract_count"]
                )
                avg_contract_value = metrics["total_value"] / metrics["contract_count"]
                activity_consistency = (
                    len(metrics["months_active"]) / 12
                )  # Normalize to year

                # Composite efficiency score
                efficiency_score = vendor_diversity * 0.4 + activity_consistency * 0.6

                efficiency_scores[org_code] = {
                    "score": efficiency_score,
                    "vendor_diversity": vendor_diversity,
                    "avg_contract_value": avg_contract_value,
                    "activity_consistency": activity_consistency,
                    "metrics": metrics,
                }

        # Find organizations with notably high or low efficiency
        if efficiency_scores:
            scores = [eff["score"] for eff in efficiency_scores.values()]
            mean_score = np.mean(scores)
            std_score = np.std(scores)

            for org_code, efficiency in efficiency_scores.items():
                if std_score > 0:
                    z_score = (efficiency["score"] - mean_score) / std_score

                    if abs(z_score) > 1.0:  # Significant deviation
                        performance_type = (
                            "high_efficiency" if z_score > 0 else "low_efficiency"
                        )
                        significance = min(abs(z_score) / 2.0, 1.0)

                        pattern = PatternResult(
                            pattern_type="efficiency_metrics",
                            description=f"Performance organizacional {performance_type}: {org_code}",
                            significance=significance,
                            confidence=min(abs(z_score) / 1.5, 1.0),
                            insights=[
                                f"Score de eficiência: {efficiency['score']:.2f}",
                                f"Diversidade de fornecedores: {efficiency['vendor_diversity']:.2f}",
                                f"Consistência de atividade: {efficiency['activity_consistency']:.2f}",
                                f"Valor médio por contrato: R$ {efficiency['avg_contract_value']:,.2f}",
                            ],
                            evidence={
                                "organization": org_code,
                                "efficiency_score": efficiency["score"],
                                "vendor_diversity": efficiency["vendor_diversity"],
                                "activity_consistency": efficiency[
                                    "activity_consistency"
                                ],
                                "z_score": z_score,
                                "benchmark_average": mean_score,
                            },
                            recommendations=[
                                "Analisar fatores que contribuem para a performance",
                                "Compartilhar boas práticas com outras organizações",
                                (
                                    "Investigar oportunidades de melhoria"
                                    if z_score < 0
                                    else "Manter padrão de excelência"
                                ),
                                "Monitorar tendências de performance",
                            ],
                            entities_involved=[
                                {
                                    "organization": org_code,
                                    "efficiency_score": efficiency["score"],
                                    "performance_type": performance_type,
                                }
                            ],
                        )

                        patterns.append(pattern)

        return patterns

    async def _analyze_spectral_patterns(
        self,
        data: list[dict[str, Any]],
        request: AnalysisRequest,
        context: AgentContext,
    ) -> list[PatternResult]:
        """
        Analyze spectral patterns using Fourier transforms.

        Args:
            data: Contract data for analysis
            request: Analysis request parameters
            context: Agent context

        Returns:
            List of spectral pattern results
        """
        patterns = []

        try:
            # Group data by organization for spectral analysis
            org_groups = defaultdict(list)
            for contract in data:
                org_code = contract.get("_org_code", "unknown")
                org_groups[org_code].append(contract)

            for org_code, org_contracts in org_groups.items():
                if len(org_contracts) < 30:  # Need sufficient data
                    continue

                # Prepare time series data
                time_series_data = self._prepare_time_series_for_org(org_contracts)
                if len(time_series_data) < 20:
                    continue

                # Extract spending values and timestamps
                spending_data = pd.Series([item["value"] for item in time_series_data])
                timestamps = pd.DatetimeIndex(
                    [item["date"] for item in time_series_data]
                )

                # Perform spectral analysis
                spectral_features = self.spectral_analyzer.analyze_time_series(
                    spending_data, timestamps
                )

                # Find periodic patterns
                periodic_patterns = self.spectral_analyzer.find_periodic_patterns(
                    spending_data, timestamps, entity_name=f"Org_{org_code}"
                )

                # Convert to PatternResult objects
                for i, period_pattern in enumerate(
                    periodic_patterns[:5]
                ):  # Top 5 patterns
                    if period_pattern.amplitude > 0.1:  # Only significant patterns
                        pattern = PatternResult(
                            pattern_type="spectral_periodic",
                            description=f"Padrão periódico detectado: {period_pattern.period_days:.1f} dias",
                            significance=period_pattern.amplitude,
                            confidence=period_pattern.confidence,
                            insights=[
                                f"Período dominante: {period_pattern.period_days:.1f} dias",
                                f"Força do padrão: {period_pattern.amplitude:.1%}",
                                f"Tipo: {period_pattern.pattern_type}",
                                period_pattern.business_interpretation,
                            ],
                            evidence={
                                "period_days": period_pattern.period_days,
                                "frequency_hz": period_pattern.frequency_hz,
                                "amplitude": period_pattern.amplitude,
                                "pattern_type": period_pattern.pattern_type,
                                "confidence": period_pattern.confidence,
                                "spectral_entropy": spectral_features.spectral_entropy,
                                "dominant_frequencies": spectral_features.dominant_frequencies,
                                "seasonal_components": spectral_features.seasonal_components,
                            },
                            recommendations=[
                                f"Investigar causa do padrão de {period_pattern.period_days:.1f} dias",
                                "Verificar se corresponde a processos de negócio conhecidos",
                                "Analisar se há justificativa administrativa",
                                "Considerar otimização do cronograma de contratações",
                            ],
                            entities_involved=[
                                {
                                    "organization_code": org_code,
                                    "contracts_analyzed": len(org_contracts),
                                    "period_days": period_pattern.period_days,
                                    "pattern_strength": period_pattern.amplitude,
                                }
                            ],
                            trend_direction=self._classify_trend_from_spectral(
                                spectral_features
                            ),
                            correlation_strength=period_pattern.amplitude,
                        )
                        patterns.append(pattern)

                # Analyze overall spectral characteristics
                if (
                    spectral_features.spectral_entropy < 0.3
                ):  # Low entropy indicates regular patterns
                    pattern = PatternResult(
                        pattern_type="spectral_regularity",
                        description=f"Padrão de gastos muito regular detectado (entropia: {spectral_features.spectral_entropy:.2f})",
                        significance=1 - spectral_features.spectral_entropy,
                        confidence=0.8,
                        insights=[
                            f"Entropia espectral baixa: {spectral_features.spectral_entropy:.2f}",
                            "Gastos seguem padrão muito regular",
                            "Pode indicar processos automatizados ou planejamento rígido",
                            f"Anomalia score: {spectral_features.anomaly_score:.2f}",
                        ],
                        evidence={
                            "spectral_entropy": spectral_features.spectral_entropy,
                            "anomaly_score": spectral_features.anomaly_score,
                            "dominant_frequencies": spectral_features.dominant_frequencies[
                                :5
                            ],
                            "seasonal_components": spectral_features.seasonal_components,
                        },
                        recommendations=[
                            "Verificar se a regularidade é justificada",
                            "Investigar processos de planejamento orçamentário",
                            "Analisar flexibilidade nos cronogramas",
                            "Considerar diversificação temporal",
                        ],
                        entities_involved=[
                            {
                                "organization_code": org_code,
                                "spectral_entropy": spectral_features.spectral_entropy,
                                "regularity_score": 1
                                - spectral_features.spectral_entropy,
                            }
                        ],
                    )
                    patterns.append(pattern)

            self.logger.info(
                "spectral_analysis_completed",
                patterns_found=len(patterns),
                organizations_analyzed=len(org_groups),
            )

        except Exception as e:
            self.logger.error(f"Error in spectral pattern analysis: {str(e)}")

        return patterns

    async def _perform_cross_spectral_analysis(
        self,
        data: list[dict[str, Any]],
        request: AnalysisRequest,
        context: AgentContext,
    ) -> list[CorrelationResult]:
        """
        Perform cross-spectral analysis between organizations.

        Args:
            data: Contract data for analysis
            request: Analysis request parameters
            context: Agent context

        Returns:
            List of cross-spectral correlation results
        """
        correlations = []

        try:
            # Group data by organization
            org_groups = defaultdict(list)
            for contract in data:
                org_code = contract.get("_org_code", "unknown")
                org_groups[org_code].append(contract)

            # Get organizations with sufficient data
            valid_orgs = {
                org: contracts
                for org, contracts in org_groups.items()
                if len(contracts) >= 30
            }

            if len(valid_orgs) < 2:
                return correlations

            org_list = list(valid_orgs.keys())

            # Perform pairwise cross-spectral analysis
            for i, org1 in enumerate(org_list):
                for org2 in org_list[i + 1 :]:
                    try:
                        # Prepare time series for both organizations
                        ts1 = self._prepare_time_series_for_org(valid_orgs[org1])
                        ts2 = self._prepare_time_series_for_org(valid_orgs[org2])

                        if len(ts1) < 20 or len(ts2) < 20:
                            continue

                        # Create comparable time series (same date range)
                        all_dates = sorted(set([item["date"] for item in ts1 + ts2]))
                        if len(all_dates) < 20:
                            continue

                        # Create aligned series
                        data1 = pd.Series(index=all_dates, dtype=float).fillna(0)
                        data2 = pd.Series(index=all_dates, dtype=float).fillna(0)

                        for item in ts1:
                            data1[item["date"]] += item["value"]
                        for item in ts2:
                            data2[item["date"]] += item["value"]

                        timestamps = pd.DatetimeIndex(all_dates)

                        # Perform cross-spectral analysis
                        cross_spectral_result = (
                            self.spectral_analyzer.cross_spectral_analysis(
                                data1, data2, f"Org_{org1}", f"Org_{org2}", timestamps
                            )
                        )

                        if (
                            cross_spectral_result
                            and cross_spectral_result.get("max_coherence", 0) > 0.5
                        ):
                            correlation = CorrelationResult(
                                correlation_type="cross_spectral",
                                variables=[f"Org_{org1}", f"Org_{org2}"],
                                correlation_coefficient=cross_spectral_result[
                                    "correlation_coefficient"
                                ],
                                p_value=None,  # Not computed in spectral analysis
                                significance_level=self._assess_spectral_significance(
                                    cross_spectral_result["max_coherence"]
                                ),
                                description=f"Correlação espectral entre organizações {org1} e {org2}",
                                business_interpretation=cross_spectral_result[
                                    "business_interpretation"
                                ],
                                evidence={
                                    "max_coherence": cross_spectral_result[
                                        "max_coherence"
                                    ],
                                    "mean_coherence": cross_spectral_result[
                                        "mean_coherence"
                                    ],
                                    "correlated_periods_days": cross_spectral_result[
                                        "correlated_periods_days"
                                    ],
                                    "synchronization_score": cross_spectral_result[
                                        "synchronization_score"
                                    ],
                                    "correlated_frequencies": cross_spectral_result[
                                        "correlated_frequencies"
                                    ],
                                },
                                recommendations=[
                                    "Investigar possível coordenação entre organizações",
                                    "Verificar se há fornecedores em comum",
                                    "Analisar sincronização de processos",
                                    "Revisar independência das contratações",
                                ],
                            )
                            correlations.append(correlation)

                    except Exception as e:
                        self.logger.warning(
                            f"Cross-spectral analysis failed for {org1}-{org2}: {str(e)}"
                        )
                        continue

            self.logger.info(
                "cross_spectral_analysis_completed",
                correlations_found=len(correlations),
                organizations_compared=len(org_list),
            )

        except Exception as e:
            self.logger.error(f"Error in cross-spectral analysis: {str(e)}")

        return correlations

    def _prepare_time_series_for_org(
        self, contracts: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Prepare time series data for a specific organization."""
        time_series = []

        for contract in contracts:
            # Extract date
            date_str = (
                contract.get("dataAssinatura")
                or contract.get("dataPublicacao")
                or contract.get("dataInicio")
            )

            if not date_str:
                continue

            try:
                # Parse date (DD/MM/YYYY format)
                date_parts = date_str.split("/")
                if len(date_parts) == 3:
                    day, month, year = (
                        int(date_parts[0]),
                        int(date_parts[1]),
                        int(date_parts[2]),
                    )
                    date_obj = datetime(year, month, day)

                    # Extract value
                    valor = (
                        contract.get("valorInicial") or contract.get("valorGlobal") or 0
                    )
                    if isinstance(valor, (int, float)) and valor > 0:
                        time_series.append(
                            {
                                "date": date_obj,
                                "value": float(valor),
                                "contract_id": contract.get("id"),
                            }
                        )

            except (ValueError, IndexError):
                continue

        # Sort by date and aggregate by date
        time_series.sort(key=lambda x: x["date"])

        # Aggregate by date
        daily_aggregates = defaultdict(float)
        for item in time_series:
            daily_aggregates[item["date"]] += item["value"]

        return [
            {"date": date, "value": value} for date, value in daily_aggregates.items()
        ]

    def _classify_trend_from_spectral(
        self, features: SpectralFeatures
    ) -> Optional[str]:
        """Classify trend direction from spectral features."""
        # Analyze trend component
        if hasattr(features, "trend_component") and len(features.trend_component) > 10:
            trend_start = np.mean(
                features.trend_component[: len(features.trend_component) // 3]
            )
            trend_end = np.mean(
                features.trend_component[-len(features.trend_component) // 3 :]
            )

            if trend_end > trend_start * 1.1:
                return "increasing"
            elif trend_end < trend_start * 0.9:
                return "decreasing"
            else:
                return "stable"

        return None

    def _assess_spectral_significance(self, coherence: float) -> str:
        """Assess significance level of spectral coherence."""
        if coherence > 0.8:
            return "high"
        elif coherence > 0.6:
            return "medium"
        else:
            return "low"

    def _generate_insights(
        self,
        patterns: list[PatternResult],
        correlations: list[CorrelationResult],
        data: list[dict[str, Any]],
    ) -> list[str]:
        """Generate high-level insights from analysis results."""
        insights = []

        # High-level data insights
        total_contracts = len(data)
        total_value = sum(
            float(c.get("valorInicial") or c.get("valorGlobal") or 0)
            for c in data
            if isinstance(c.get("valorInicial") or c.get("valorGlobal"), (int, float))
        )

        insights.append(
            f"Analisados {total_contracts} contratos totalizando R$ {total_value:,.2f}"
        )

        # Pattern insights
        if patterns:
            high_significance = [p for p in patterns if p.significance > 0.7]
            insights.append(
                f"Identificados {len(patterns)} padrões, sendo {len(high_significance)} de alta significância"
            )

            # Most significant pattern
            if high_significance:
                top_pattern = max(high_significance, key=lambda p: p.significance)
                insights.append(f"Padrão mais significativo: {top_pattern.description}")

        # Correlation insights
        if correlations:
            strong_correlations = [
                c for c in correlations if abs(c.correlation_coefficient) > 0.7
            ]
            insights.append(
                f"Encontradas {len(correlations)} correlações, sendo {len(strong_correlations)} fortes"
            )

        # Risk assessment
        risk_patterns = [
            p
            for p in patterns
            if p.pattern_type in ["spending_trends", "vendor_behavior"]
        ]
        if risk_patterns:
            insights.append(
                f"Identificados {len(risk_patterns)} padrões que requerem atenção especial"
            )

        return insights

    def _generate_analysis_summary(
        self,
        data: list[dict[str, Any]],
        patterns: list[PatternResult],
        correlations: list[CorrelationResult],
    ) -> dict[str, Any]:
        """Generate summary statistics for the analysis."""
        # Calculate basic statistics
        total_value = sum(
            float(c.get("valorInicial") or c.get("valorGlobal") or 0)
            for c in data
            if isinstance(c.get("valorInicial") or c.get("valorGlobal"), (int, float))
        )

        organizations = len(set(c.get("_org_code") for c in data if c.get("_org_code")))
        months_covered = len(set(c.get("_month") for c in data if c.get("_month")))

        # Pattern statistics
        pattern_types = Counter(p.pattern_type for p in patterns)
        high_significance_patterns = len([p for p in patterns if p.significance > 0.7])

        # Calculate overall analysis score
        analysis_score = min(
            (len(patterns) + len(correlations)) / max(len(data) / 10, 1) * 5, 10
        )

        return {
            "total_records": len(data),
            "total_value": total_value,
            "organizations_analyzed": organizations,
            "months_covered": months_covered,
            "patterns_found": len(patterns),
            "correlations_found": len(correlations),
            "pattern_types": dict(pattern_types),
            "high_significance_patterns": high_significance_patterns,
            "analysis_score": analysis_score,
            "avg_contract_value": total_value / len(data) if data else 0,
        }

    def _pattern_to_dict(self, pattern: PatternResult) -> dict[str, Any]:
        """Convert PatternResult to dictionary for serialization."""
        return {
            "type": pattern.pattern_type,
            "description": pattern.description,
            "significance": pattern.significance,
            "confidence": pattern.confidence,
            "insights": pattern.insights,
            "evidence": pattern.evidence,
            "recommendations": pattern.recommendations,
            "entities_involved": pattern.entities_involved,
            "trend_direction": pattern.trend_direction,
            "correlation_strength": pattern.correlation_strength,
        }

    def _correlation_to_dict(self, correlation: CorrelationResult) -> dict[str, Any]:
        """Convert CorrelationResult to dictionary for serialization."""
        return {
            "type": correlation.correlation_type,
            "variables": correlation.variables,
            "correlation_coefficient": correlation.correlation_coefficient,
            "p_value": correlation.p_value,
            "significance_level": correlation.significance_level,
            "description": correlation.description,
            "business_interpretation": correlation.business_interpretation,
            "evidence": correlation.evidence,
            "recommendations": correlation.recommendations,
        }
