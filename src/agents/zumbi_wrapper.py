"""
Wrapper methods for InvestigatorAgent (Zumbi) to provide backward compatibility
"""

from datetime import UTC, datetime
from typing import Optional

from src.agents.deodoro import AgentContext, AgentMessage
from src.agents.zumbi import AnomalyResult


async def investigate_anomalies_wrapper(
    self,
    query: str,
    data_source: str = "contracts",
    filters: Optional[dict] = None,
    anomaly_types: Optional[list[str]] = None,
    context: Optional[AgentContext] = None,
) -> list[AnomalyResult]:
    """
    Wrapper method to provide investigate_anomalies interface for InvestigatorAgent.

    Converts the parameters to the format expected by the process method.
    """
    # Create investigation request payload
    payload = {
        "query": query,
        "data_source": data_source,
        "filters": filters or {},
        "anomaly_types": anomaly_types or ["price", "temporal", "vendor", "duplicate"],
        "confidence_threshold": 0.7,
        "enable_explainability": True,
        "enable_open_data_enrichment": False,  # Set to False for faster processing
        "max_results": 100,
    }

    # Create agent message
    message = AgentMessage(
        sender="investigations_route",
        recipient="zumbi",
        action="investigate",
        payload=payload,
        context=context.to_dict() if context else {},
        requires_response=True,
    )

    # If no context provided, create one
    if context is None:
        context = AgentContext(
            investigation_id=f"inv_{datetime.now(UTC).isoformat()}", user_id="system"
        )

    # Call the process method
    response = await self.process(message, context)

    # Extract anomalies from response
    if response.result and isinstance(response.result, dict):
        anomalies_data = response.result.get("anomalies", [])

        # Convert dict anomalies back to AnomalyResult objects if needed
        anomalies = []
        for anomaly_dict in anomalies_data:
            if isinstance(anomaly_dict, dict):
                anomaly = AnomalyResult(
                    anomaly_type=anomaly_dict.get(
                        "type", anomaly_dict.get("anomaly_type", "unknown")
                    ),
                    severity=anomaly_dict.get("severity", 0.5),
                    confidence=anomaly_dict.get("confidence", 0.5),
                    description=anomaly_dict.get("description", ""),
                    explanation=anomaly_dict.get("explanation", ""),
                    affected_entities=anomaly_dict.get("affected_entities", []),
                    financial_impact=anomaly_dict.get("financial_impact"),
                    recommendations=anomaly_dict.get("recommendations", []),
                    evidence=anomaly_dict.get("evidence", {}),
                    metadata=anomaly_dict.get("metadata", {}),
                )
                anomalies.append(anomaly)
            elif isinstance(anomaly_dict, AnomalyResult):
                anomalies.append(anomaly_dict)

        return anomalies

    return []


# Monkey-patch the method onto InvestigatorAgent
def patch_investigator_agent():
    """Add the wrapper method to InvestigatorAgent class"""
    from src.agents.zumbi import InvestigatorAgent

    InvestigatorAgent.investigate_anomalies = investigate_anomalies_wrapper
