"""
Execution Planner

Creates execution plans for investigations based on intent and entities.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

from typing import Any

from src.core import get_logger
from src.services.orchestration.api_registry import APICapability, APIRegistry
from src.services.orchestration.models.investigation import (
    ExecutionPlan,
    InvestigationContext,
    InvestigationIntent,
    Stage,
)

logger = get_logger(__name__)


class ExecutionPlanner:
    """
    Creates optimized execution plans for investigations.

    Maps investigation intents to API calls, determines execution order,
    identifies parallelization opportunities, and sets caching strategies.
    """

    def __init__(self, api_registry: APIRegistry | None = None) -> None:
        self.registry = api_registry or APIRegistry()
        self.logger = get_logger(__name__)

    def create_plan(
        self,
        intent: InvestigationIntent,
        entities: dict[str, Any],
        context: InvestigationContext,
    ) -> ExecutionPlan:
        """
        Create execution plan for investigation.

        Args:
            intent: Investigation intent
            entities: Extracted entities
            context: Full investigation context

        Returns:
            ExecutionPlan with stages
        """
        self.logger.info(f"Creating execution plan for intent: {intent}")

        # Get stages based on intent
        stages = self._build_stages_for_intent(intent, entities)

        # Estimate duration
        estimated_duration = sum(stage.timeout_seconds for stage in stages)

        # Determine cache strategy
        cache_strategy = self._determine_cache_strategy(intent)

        plan = ExecutionPlan(
            intent=intent,
            entities=entities,
            stages=stages,
            estimated_duration_seconds=estimated_duration,
            cache_strategy=cache_strategy,
        )

        self.logger.debug(f"Created plan with {len(stages)} stages")
        return plan

    def _build_stages_for_intent(  # noqa: PLR0911
        self, intent: InvestigationIntent, entities: dict[str, Any]
    ) -> list[Stage]:
        """Build execution stages based on investigation intent."""

        if intent == InvestigationIntent.SUPPLIER_INVESTIGATION:
            return self._plan_supplier_investigation(entities)

        if intent == InvestigationIntent.CONTRACT_ANOMALY_DETECTION:
            return self._plan_contract_anomaly_detection(entities)

        if intent == InvestigationIntent.BUDGET_ANALYSIS:
            return self._plan_budget_analysis(entities)

        if intent == InvestigationIntent.HEALTH_BUDGET_ANALYSIS:
            return self._plan_health_budget_analysis(entities)

        if intent == InvestigationIntent.EDUCATION_PERFORMANCE:
            return self._plan_education_performance(entities)

        if intent == InvestigationIntent.CORRUPTION_INDICATORS:
            return self._plan_corruption_indicators(entities)

        # GENERAL_QUERY
        return self._plan_general_query(entities)

    def _plan_supplier_investigation(self, entities: dict[str, Any]) -> list[Stage]:
        """Plan supplier investigation stages."""
        stages = []

        # Stage 1: Get company data
        if entities.get("cnpj"):
            stages.append(
                Stage(
                    name="company_lookup",
                    apis=["minha_receita"],
                    method="get_company",
                    parallel=False,
                    reason="Get company registration and partners data",
                    cache_ttl=86400,  # 24 hours
                )
            )

        # Stage 2: Search contracts (depends on company_lookup for enriched data)
        contract_apis = self._get_apis_for_capability(APICapability.CONTRACT_SEARCH)
        stages.append(
            Stage(
                name="contract_search",
                apis=contract_apis,
                method="search_contracts",
                parallel=True,  # Can query multiple APIs in parallel
                depends_on=["company_lookup"] if stages else [],
                reason="Find all contracts won by supplier",
                cache_ttl=3600,  # 1 hour
            )
        )

        # Stage 3: Get bid details (depends on contracts found)
        bidding_apis = self._get_apis_for_capability(APICapability.BIDDING_SEARCH)
        if bidding_apis:
            stages.append(
                Stage(
                    name="bidding_details",
                    apis=bidding_apis,
                    method="get_bidding",
                    parallel=True,
                    depends_on=["contract_search"],
                    reason="Analyze bidding processes and competition",
                    cache_ttl=3600,
                )
            )

        return stages

    def _plan_contract_anomaly_detection(self, entities: dict[str, Any]) -> list[Stage]:
        """Plan contract anomaly detection stages."""
        stages = []

        # Stage 1: Get contracts
        contract_apis = self._get_apis_for_capability(APICapability.CONTRACT_SEARCH)
        stages.append(
            Stage(
                name="contract_collection",
                apis=contract_apis,
                method="search_contracts",
                parallel=True,
                reason="Collect contracts for analysis",
                cache_ttl=3600,
            )
        )

        # Stage 2: Get economic indicators for price comparison
        econ_apis = self._get_apis_for_capability(APICapability.ECONOMIC_INDICATORS)
        if econ_apis:
            stages.append(
                Stage(
                    name="economic_context",
                    apis=econ_apis,
                    method="get_indicators",
                    parallel=False,  # Sequential, need contract period
                    depends_on=["contract_collection"],
                    reason="Get inflation/indices for price adjustment",
                    cache_ttl=86400,  # Economic data changes daily
                )
            )

        # Stage 3: Analyze patterns (synthetic stage, done by agent)
        stages.append(
            Stage(
                name="anomaly_analysis",
                apis=[],  # No API calls, pure analysis
                method="analyze_anomalies",
                parallel=False,
                depends_on=(
                    ["contract_collection", "economic_context"]
                    if len(stages) > 1
                    else ["contract_collection"]
                ),
                reason="Detect pricing anomalies and suspicious patterns",
                timeout_seconds=60,  # Analysis can take longer
            )
        )

        return stages

    def _plan_budget_analysis(self, entities: dict[str, Any]) -> list[Stage]:
        """Plan budget analysis stages."""
        stages = []

        # Stage 1: Get budget data
        budget_apis = self._get_apis_for_capability(APICapability.BUDGET_DATA)
        expense_apis = self._get_apis_for_capability(APICapability.PUBLIC_EXPENSES)

        all_apis = list(set(budget_apis + expense_apis))
        if all_apis:
            stages.append(
                Stage(
                    name="budget_collection",
                    apis=all_apis,
                    method="get_budget",
                    parallel=True,
                    reason="Collect budget and expense data",
                    cache_ttl=3600,
                )
            )

        # Stage 2: Get demographic context
        demo_apis = self._get_apis_for_capability(APICapability.DEMOGRAPHIC_INDICATORS)
        if demo_apis and entities.get("state"):
            stages.append(
                Stage(
                    name="demographic_context",
                    apis=demo_apis,
                    method="get_demographics",
                    parallel=False,
                    depends_on=["budget_collection"] if stages else [],
                    reason="Get population data for per-capita analysis",
                    cache_ttl=86400,
                )
            )

        return stages

    def _plan_health_budget_analysis(self, entities: dict[str, Any]) -> list[Stage]:
        """Plan health budget analysis stages."""
        stages = []

        # Stage 1: Get health statistics
        health_apis = self._get_apis_for_capability(APICapability.HEALTH_STATISTICS)
        if health_apis:
            stages.append(
                Stage(
                    name="health_statistics",
                    apis=health_apis,
                    method="get_health_stats",
                    parallel=True,
                    reason="Collect health indicators and SUS data",
                    cache_ttl=3600,
                )
            )

        # Stage 2: Get health budget
        budget_apis = self._get_apis_for_capability(APICapability.BUDGET_DATA)
        if budget_apis:
            stages.append(
                Stage(
                    name="health_budget",
                    apis=budget_apis,
                    method="get_health_budget",
                    parallel=False,
                    depends_on=["health_statistics"] if stages else [],
                    reason="Get health sector budget allocation",
                    cache_ttl=3600,
                )
            )

        return stages

    def _plan_education_performance(self, entities: dict[str, Any]) -> list[Stage]:
        """Plan education performance analysis stages."""
        stages = []

        # Stage 1: Get education statistics
        edu_apis = self._get_apis_for_capability(APICapability.EDUCATION_STATISTICS)
        if edu_apis:
            stages.append(
                Stage(
                    name="education_statistics",
                    apis=edu_apis,
                    method="get_education_stats",
                    parallel=True,
                    reason="Collect IDEB, ENEM, and school census data",
                    cache_ttl=86400,  # Education data is annual
                )
            )

        return stages

    def _plan_corruption_indicators(self, entities: dict[str, Any]) -> list[Stage]:
        """Plan corruption indicator analysis stages."""
        # This is a complex investigation combining multiple data sources
        stages = []

        # Stage 1: Collect contracts for pattern analysis
        contract_apis = self._get_apis_for_capability(APICapability.CONTRACT_SEARCH)
        stages.append(
            Stage(
                name="contract_collection",
                apis=contract_apis,
                method="search_contracts",
                parallel=True,
                reason="Collect contracts for pattern detection",
                cache_ttl=3600,
            )
        )

        # Stage 2: Get supplier concentration
        supplier_apis = self._get_apis_for_capability(APICapability.SUPPLIER_SEARCH)
        if supplier_apis:
            stages.append(
                Stage(
                    name="supplier_analysis",
                    apis=supplier_apis,
                    method="analyze_suppliers",
                    parallel=False,
                    depends_on=["contract_collection"],
                    reason="Detect supplier concentration patterns",
                    cache_ttl=3600,
                )
            )

        # Stage 3: Corruption risk analysis (synthetic)
        stages.append(
            Stage(
                name="corruption_risk_analysis",
                apis=[],
                method="analyze_corruption_risk",
                parallel=False,
                depends_on=(
                    ["contract_collection", "supplier_analysis"]
                    if len(stages) > 1
                    else ["contract_collection"]
                ),
                reason="Calculate corruption risk indicators",
                timeout_seconds=60,
            )
        )

        return stages

    def _plan_general_query(self, entities: dict[str, Any]) -> list[Stage]:
        """Plan general query stages (fallback)."""
        # For general queries, create a simple stage
        return [
            Stage(
                name="general_info",
                apis=[],
                method="general_query",
                parallel=False,
                reason="Provide general information about transparency data",
                timeout_seconds=30,
            )
        ]

    def _get_apis_for_capability(self, capability: APICapability) -> list[str]:
        """Get API names that provide a capability."""
        apis = self.registry.find_apis_by_capability(capability)
        return [api.api_name for api in apis]

    def _determine_cache_strategy(self, intent: InvestigationIntent) -> str:
        """Determine caching strategy based on intent."""
        # Real-time investigations: minimal caching
        if intent in [
            InvestigationIntent.CORRUPTION_INDICATORS,
            InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
        ]:
            return "moderate"

        # Historical analysis: aggressive caching
        if intent in [
            InvestigationIntent.EDUCATION_PERFORMANCE,
            InvestigationIntent.BUDGET_ANALYSIS,
        ]:
            return "aggressive"

        # Default: moderate
        return "moderate"
