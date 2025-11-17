"""
Agent Adapter

Adapters for integrating existing agents with the orchestration system.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

import uuid
from typing import Any

from src.agents.deodoro import AgentContext, AgentMessage
from src.agents.zumbi import InvestigationRequest, InvestigatorAgent
from src.core import get_logger

logger = get_logger(__name__)


class AgentAdapter:
    """
    Base adapter for integrating agents with orchestration.

    Provides common functionality for calling agents and
    transforming results.
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    async def call_agent(
        self, agent: Any, message: AgentMessage, context: AgentContext  # noqa: ANN401
    ) -> dict[str, Any]:
        """
        Call an agent with a message and context.

        Args:
            agent: Agent instance to call
            message: Message with action and payload
            context: Agent execution context

        Returns:
            Dict with agent response data
        """
        try:
            response = await agent.process(message, context)

            return {
                "agent_name": response.agent_name,
                "status": (
                    response.status.value
                    if hasattr(response.status, "value")
                    else str(response.status)
                ),
                "result": response.result,
                "error": response.error,
                "metadata": response.metadata,
            }

        except Exception as e:
            self.logger.error(f"Agent call failed: {e}")
            raise


class InvestigationAgentAdapter(AgentAdapter):
    """
    Adapter for Zumbi anomaly detection agent.

    Integrates the InvestigatorAgent (Zumbi) with the
    orchestration system.
    """

    def __init__(
        self,
        price_anomaly_threshold: float = 2.5,
        concentration_threshold: float = 0.7,
        duplicate_similarity_threshold: float = 0.85,
    ) -> None:
        super().__init__()
        self.agent = InvestigatorAgent(
            price_anomaly_threshold=price_anomaly_threshold,
            concentration_threshold=concentration_threshold,
            duplicate_similarity_threshold=duplicate_similarity_threshold,
        )

    async def detect_anomalies(  # noqa: PLR0913
        self,
        query: str,
        organization_codes: list[str] | None = None,
        date_range: tuple[str, str] | None = None,
        value_threshold: float | None = None,
        anomaly_types: list[str] | None = None,
        max_records: int = 100,
        investigation_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Detect anomalies in government contracts.

        Args:
            query: Natural language investigation query
            organization_codes: Organization codes to investigate
            date_range: (start, end) date range in DD/MM/YYYY
            value_threshold: Minimum contract value
            anomaly_types: Specific anomaly types to check
            max_records: Maximum records to analyze
            investigation_id: Optional investigation ID

        Returns:
            Dict with anomaly detection results
        """
        # Create investigation request
        request = InvestigationRequest(
            query=query,
            organization_codes=organization_codes,
            date_range=date_range,
            value_threshold=value_threshold,
            anomaly_types=anomaly_types,
            max_records=max_records,
        )

        # Create agent message
        message = AgentMessage(
            sender="orchestrator",
            recipient="investigator_agent",
            message_id=str(uuid.uuid4()),
            action="investigate",
            payload=request.model_dump(),
        )

        # Create agent context
        context = AgentContext(
            investigation_id=investigation_id or str(uuid.uuid4()),
            user_id="orchestrator",
            session_id="orchestrator",
        )

        # Call agent
        return await self.call_agent(self.agent, message, context)

    async def analyze_investigation_results(
        self, investigation_results: dict[str, Any], investigation_id: str | None = None
    ) -> dict[str, Any]:
        """
        Analyze investigation results for anomalies.

        Takes the results from a multi-API investigation and
        runs anomaly detection on the aggregated data.

        Args:
            investigation_results: Results from data federation
            investigation_id: Investigation ID

        Returns:
            Dict with anomaly analysis
        """
        # Extract key information for query
        query_parts = []

        # Check for companies in results
        if "company_lookup" in investigation_results:
            company_data = investigation_results["company_lookup"]
            if isinstance(company_data, dict) and "name" in company_data:
                query_parts.append(f"Empresa: {company_data['name']}")

        # Check for contracts
        if "contract_search" in investigation_results:
            query_parts.append("Contratos encontrados")

        query = " | ".join(query_parts) if query_parts else "Análise de dados agregados"

        # Call detection
        return await self.detect_anomalies(
            query=query, investigation_id=investigation_id, max_records=200
        )
