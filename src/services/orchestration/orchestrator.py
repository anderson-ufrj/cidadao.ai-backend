"""
Investigation Orchestrator

Main orchestration component that coordinates the entire investigation flow.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

import uuid
from typing import Any

from src.core import get_logger
from src.services.orchestration.agents import InvestigationAgentAdapter
from src.services.orchestration.api_registry import APIRegistry
from src.services.orchestration.data_federation import DataFederationExecutor
from src.services.orchestration.entity_graph import EntityGraph
from src.services.orchestration.models.investigation import (
    InvestigationContext,
    InvestigationIntent,
    InvestigationResult,
)
from src.services.orchestration.query_planner import (
    EntityExtractor,
    ExecutionPlanner,
    IntentClassifier,
)

logger = get_logger(__name__)


class InvestigationOrchestrator:
    """
    Main orchestrator for transparency investigations.

    Coordinates the complete flow:
    1. Classify intent from user query
    2. Extract entities (CNPJ, dates, locations)
    3. Create execution plan
    4. Execute plan across multiple APIs
    5. Return structured results
    """

    def __init__(  # noqa: PLR0913
        self,
        api_registry: APIRegistry | None = None,
        intent_classifier: IntentClassifier | None = None,
        entity_extractor: EntityExtractor | None = None,
        execution_planner: ExecutionPlanner | None = None,
        data_executor: DataFederationExecutor | None = None,
        entity_graph: EntityGraph | None = None,
        investigation_agent: InvestigationAgentAdapter | None = None,
    ) -> None:
        self.registry = api_registry or APIRegistry()
        self.intent_classifier = intent_classifier or IntentClassifier()
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.execution_planner = execution_planner or ExecutionPlanner(self.registry)
        self.data_executor = data_executor or DataFederationExecutor(self.registry)
        self.entity_graph = entity_graph or EntityGraph()
        self.investigation_agent = investigation_agent or InvestigationAgentAdapter()
        self.logger = get_logger(__name__)

    async def investigate(
        self,
        query: str,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> InvestigationResult:
        """
        Run a complete investigation from a user query.

        Args:
            query: User query in Portuguese
            user_id: Optional user ID
            session_id: Optional session ID

        Returns:
            InvestigationResult with complete investigation data
        """
        investigation_id = str(uuid.uuid4())
        self.logger.info(f"Starting investigation {investigation_id}: {query[:100]}...")

        # Step 1: Extract entities from query
        entities = self.entity_extractor.extract(query)
        self.logger.debug(f"Extracted entities: {entities}")

        # Step 2: Classify intent
        intent_result = await self.intent_classifier.classify(query)
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        self.logger.info(f"Classified as {intent.value} (confidence: {confidence:.2f})")

        # Step 3: Create investigation context
        context = InvestigationContext(
            user_query=query,
            user_id=user_id,
            session_id=session_id,
            **entities,  # Spread extracted entities
        )

        # Step 4: Create execution plan
        plan = self.execution_planner.create_plan(intent, entities, context)
        self.logger.info(
            f"Created plan with {len(plan.stages)} stages, "
            f"estimated duration: {plan.estimated_duration_seconds}s"
        )

        # Step 5: Create investigation result (initially pending)
        result = InvestigationResult(
            investigation_id=investigation_id,
            intent=intent,
            context=context,
            plan=plan,
            confidence_score=confidence,
        )

        # Step 6: Execute plan
        result.mark_running()
        try:
            execution_result = await self.data_executor.execute_plan(plan, entities)

            # Add results to investigation
            result.stage_results = list(execution_result["stage_results"].values())
            result.total_duration_seconds = execution_result["duration_seconds"]

            # Extract entities and relationships from results
            result.entities_found = self._extract_entities_from_results(
                execution_result["results"]
            )

            # Step 7: Run anomaly detection if applicable
            if self._should_run_anomaly_detection(intent):
                try:
                    self.logger.info(
                        f"Running anomaly detection for investigation {investigation_id}"
                    )
                    anomaly_results = (
                        await self.investigation_agent.analyze_investigation_results(
                            execution_result["results"], investigation_id
                        )
                    )

                    # Add anomaly results to investigation
                    if anomaly_results and "result" in anomaly_results:
                        anomaly_data = anomaly_results["result"]
                        # Store anomalies directly in the anomalies field (not metadata)
                        result.anomalies = anomaly_data.get("anomalies", [])
                        # Add summary to context metadata
                        result.context.metadata["anomaly_detection"] = {
                            "status": anomaly_results.get("status"),
                            "summary": anomaly_data.get("summary", {}),
                        }
                        self.logger.info(
                            f"Anomaly detection completed: "
                            f"{len(result.anomalies)} anomalies found"
                        )

                except Exception as e:
                    self.logger.warning(
                        f"Anomaly detection failed for {investigation_id}: {e}"
                    )
                    # Don't fail the entire investigation if anomaly detection fails

            result.mark_completed()
            self.logger.info(
                f"Investigation {investigation_id} completed in "
                f"{result.total_duration_seconds:.2f}s"
            )

        except Exception as e:
            self.logger.error(f"Investigation {investigation_id} failed: {e}")
            result.mark_failed(str(e))

        return result

    def _should_run_anomaly_detection(self, intent: InvestigationIntent) -> bool:
        """
        Determine if anomaly detection should run for this intent.

        Args:
            intent: Investigation intent

        Returns:
            True if anomaly detection should run
        """
        # Run anomaly detection for these intents
        anomaly_detection_intents = {
            InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
            InvestigationIntent.SUPPLIER_INVESTIGATION,
            InvestigationIntent.CORRUPTION_INDICATORS,
            InvestigationIntent.BUDGET_ANALYSIS,
        }

        return intent in anomaly_detection_intents

    def _extract_entities_from_results(
        self, results: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Extract entities from investigation results using Entity Graph.

        Builds a graph of entities and their relationships,
        then returns a summary for the investigation result.
        """
        # Extract entities and relationships into graph
        self.entity_graph.extract_from_investigation_result(results)

        # Get statistics
        stats = self.entity_graph.get_statistics()
        self.logger.info(
            f"Entity graph: {stats['total_entities']} entities, "
            f"{stats['total_relationships']} relationships"
        )

        # Return entity summaries
        entities = []
        for stage_name, stage_data in results.items():
            if isinstance(stage_data, dict):
                entity = {
                    "source_stage": stage_name,
                    "data_summary": self._summarize_data(stage_data),
                }
                entities.append(entity)

        return entities

    def _summarize_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a summary of data for quick viewing."""
        summary = {}

        for key, value in data.items():
            if isinstance(value, str | int | float | bool):
                summary[key] = value
            elif isinstance(value, list):
                summary[f"{key}_count"] = len(value)
            elif isinstance(value, dict):
                summary[f"{key}_keys"] = list(value.keys())[:5]  # First 5 keys

        return summary

    def get_entity_graph(self) -> EntityGraph:
        """
        Get the entity graph.

        Returns:
            EntityGraph instance
        """
        return self.entity_graph

    def get_entity_graph_statistics(self) -> dict[str, Any]:
        """
        Get statistics about the entity graph.

        Returns:
            Dict with graph statistics
        """
        return self.entity_graph.get_statistics()
