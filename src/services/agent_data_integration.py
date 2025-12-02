"""
Agent Data Integration Service

Integrates agents with real government data through orchestrator.
This service ensures agents automatically fetch real data when processing queries.

Author: Anderson Henrique da Silva
Created: 2025-11-21
"""

from typing import Any

from src.core import get_logger
from src.services.orchestration.models.investigation import InvestigationIntent
from src.services.orchestration.orchestrator import InvestigationOrchestrator

logger = get_logger(__name__)


class AgentDataIntegration:
    """
    Service that integrates agents with real government data.

    This is the missing piece that connects agent queries to the orchestrator,
    ensuring agents automatically fetch real data instead of just analyzing.
    """

    def __init__(self):
        self.orchestrator = InvestigationOrchestrator()
        self.logger = get_logger(__name__)

    async def enrich_query_with_real_data(
        self,
        query: str,
        agent_name: str,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Enrich a query with real government data before sending to agent.

        This function:
        1. Uses orchestrator to classify intent
        2. Extracts entities
        3. Fetches real data from appropriate APIs
        4. Returns enriched data for agent processing

        Args:
            query: User query in Portuguese
            agent_name: Name of the agent (zumbi, oxossi, lampiao, etc.)
            user_id: Optional user ID
            session_id: Optional session ID

        Returns:
            Dict with:
                - has_real_data: bool
                - real_data: dict | None (actual data from APIs)
                - intent: str
                - entities: dict
                - should_fetch_data: bool
        """
        self.logger.info(
            f"[{agent_name}] Enriching query with real data: {query[:100]}..."
        )

        try:
            # Step 1: Classify intent to determine if we need to fetch data
            intent_result = await self.orchestrator.intent_classifier.classify(query)
            intent = intent_result["intent"]
            confidence = intent_result["confidence"]

            self.logger.info(
                f"[{agent_name}] Intent: {intent.value} (confidence: {confidence:.2f})"
            )

            # Step 2: Extract entities
            entities = self.orchestrator.entity_extractor.extract(query)
            self.logger.debug(f"[{agent_name}] Entities: {entities}")

            # Step 3: Determine if we should fetch real data based on intent
            should_fetch = self._should_fetch_data_for_intent(intent, agent_name)

            if not should_fetch:
                self.logger.info(
                    f"[{agent_name}] No data fetching needed for intent {intent.value}"
                )
                return {
                    "has_real_data": False,
                    "real_data": None,
                    "intent": intent.value,
                    "entities": entities,
                    "should_fetch_data": False,
                    "reason": "Intent does not require external data",
                }

            # Step 4: Fetch real data using orchestrator
            self.logger.info(
                f"[{agent_name}] Fetching real data for intent {intent.value}..."
            )

            investigation_result = await self.orchestrator.investigate(
                query=query, user_id=user_id, session_id=session_id
            )

            # Extract real data from investigation result
            real_data = self._extract_real_data_from_investigation(investigation_result)

            has_data = real_data is not None and len(real_data) > 0

            self.logger.info(
                f"[{agent_name}] Data fetch completed: "
                f"{'Success' if has_data else 'No data found'}"
            )

            return {
                "has_real_data": has_data,
                "real_data": real_data,
                "intent": intent.value,
                "entities": entities,
                "should_fetch_data": True,
                "investigation_id": investigation_result.investigation_id,
                "confidence": confidence,
                "execution_time": investigation_result.total_duration_seconds,
                # RASTREABILIDADE: Metadados completos de onde os dados vieram
                "traceability": {
                    "data_sources": investigation_result.data_sources_used,
                    "apis_called": [
                        stage.api_calls for stage in investigation_result.stage_results
                    ],
                    "stage_details": [
                        {
                            "stage_name": stage.stage_name,
                            "status": stage.status,
                            "duration_seconds": stage.duration_seconds,
                            "apis": stage.api_calls,
                            "errors": stage.errors,
                        }
                        for stage in investigation_result.stage_results
                    ],
                    "total_api_calls": len(investigation_result.data_sources_used),
                    "timestamp": investigation_result.created_at.isoformat(),
                },
            }

        except Exception as e:
            self.logger.error(
                f"[{agent_name}] Error enriching query with real data: {e}"
            )
            return {
                "has_real_data": False,
                "real_data": None,
                "intent": "UNKNOWN",
                "entities": {},
                "should_fetch_data": False,
                "error": str(e),
            }

    def _should_fetch_data_for_intent(
        self, intent: InvestigationIntent, agent_name: str
    ) -> bool:
        """
        Determine if we should fetch real data for this intent and agent.

        Args:
            intent: Classified investigation intent
            agent_name: Name of the agent

        Returns:
            True if we should fetch data, False otherwise
        """
        # Map intents that require data fetching
        data_fetching_intents = {
            InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
            InvestigationIntent.SUPPLIER_INVESTIGATION,
            InvestigationIntent.BUDGET_ANALYSIS,
            InvestigationIntent.HEALTH_BUDGET_ANALYSIS,
            InvestigationIntent.EDUCATION_PERFORMANCE,
            InvestigationIntent.CORRUPTION_INDICATORS,
        }

        # Map agents that should always fetch data
        data_fetching_agents = {
            "oxossi",  # Data hunter - always fetches
            "lampiao",  # Regional analysis - needs IBGE data
            "zumbi",  # Anomaly detection - needs real contracts
            "anita",  # Pattern analysis - needs real data
            "obaluaie",  # Corruption detection - needs contracts
        }

        should_fetch = (
            intent in data_fetching_intents
            or agent_name.lower() in data_fetching_agents
        )

        return should_fetch

    def _extract_real_data_from_investigation(
        self, investigation_result
    ) -> dict[str, Any] | None:
        """
        Extract real data from investigation result.

        Args:
            investigation_result: InvestigationResult from orchestrator

        Returns:
            Dict with real data or None
        """
        if not investigation_result:
            return None

        real_data = {}

        # Extract stage results (API responses)
        if investigation_result.stage_results:
            for stage_result in investigation_result.stage_results:
                # StageResult is a Pydantic model with .data attribute
                if stage_result.data:
                    # Merge data from all stages
                    if isinstance(stage_result.data, dict):
                        real_data.update(stage_result.data)
                    elif isinstance(stage_result.data, list):
                        # If list, add with stage name as key
                        real_data[stage_result.stage_name] = stage_result.data

        # Extract entities found
        if investigation_result.entities_found:
            real_data["entities"] = investigation_result.entities_found

        # Extract anomalies if any
        if investigation_result.anomalies:
            real_data["anomalies"] = investigation_result.anomalies

        return real_data if real_data else None

    async def fetch_ibge_data_for_location(
        self, location_name: str, uf: str | None = None
    ) -> dict[str, Any] | None:
        """
        Fetch IBGE data for a specific location.

        This is a specialized method for agents like Lampião that need
        regional/demographic data.

        Args:
            location_name: City or state name
            uf: Optional state code (MG, SP, etc.)

        Returns:
            Dict with IBGE data or None
        """
        try:
            from src.services.transparency_apis.federal_apis.ibge_client import (
                IBGEClient,
            )

            ibge_client = IBGEClient()

            # If UF provided, fetch municipalities
            if uf:
                cities = await ibge_client.get_municipalities(uf)
                # Find the specific city
                city_data = next(
                    (
                        c
                        for c in cities
                        if location_name.lower() in c.get("nome", "").lower()
                    ),
                    None,
                )
                return (
                    {"city": city_data, "municipalities": cities} if city_data else None
                )
            # Fetch states
            states = await ibge_client.get_states()
            state_data = next(
                (
                    s
                    for s in states
                    if location_name.lower() in s.get("nome", "").lower()
                ),
                None,
            )
            return {"state": state_data, "states": states} if state_data else None

        except Exception as e:
            self.logger.error(f"Error fetching IBGE data: {e}")
            return None

    async def fetch_contract_data(
        self,
        cnpj: str | None = None,
        value_threshold: float | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Fetch contract data from PNCP/Portal da Transparência.

        This is a specialized method for agents like Oxóssi that hunt for
        contracts and procurement data.

        Args:
            cnpj: Optional company CNPJ
            value_threshold: Optional minimum contract value
            date_from: Optional start date (YYYY-MM-DD)
            date_to: Optional end date (YYYY-MM-DD)

        Returns:
            Dict with contract data or None
        """
        try:
            from src.services.transparency_apis.federal_apis.pncp_client import (
                PNCPClient,
            )

            pncp_client = PNCPClient()

            # Search contracts (implementation depends on PNCP API structure)
            # This is a placeholder - actual implementation needs PNCP API details
            contracts = await pncp_client.search_contracts(
                cnpj=cnpj,
                min_value=value_threshold,
                date_from=date_from,
                date_to=date_to,
            )

            return (
                {"contracts": contracts, "total": len(contracts)} if contracts else None
            )

        except Exception as e:
            self.logger.error(f"Error fetching contract data: {e}")
            return None


# Singleton instance
agent_data_integration = AgentDataIntegration()
