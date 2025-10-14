"""
Investigation Orchestrator

Main orchestration component that coordinates the entire investigation flow.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

import uuid
from typing import Any

from src.core import get_logger
from src.services.orchestration.api_registry import APIRegistry
from src.services.orchestration.data_federation import DataFederationExecutor
from src.services.orchestration.entity_graph import EntityGraph
from src.services.orchestration.models.investigation import (
    InvestigationContext,
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
    ) -> None:
        self.registry = api_registry or APIRegistry()
        self.intent_classifier = intent_classifier or IntentClassifier()
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.execution_planner = execution_planner or ExecutionPlanner(self.registry)
        self.data_executor = data_executor or DataFederationExecutor(self.registry)
        self.entity_graph = entity_graph or EntityGraph()
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
            # (This would be more sophisticated in production)
            result.entities_found = self._extract_entities_from_results(
                execution_result["results"]
            )

            result.mark_completed()
            self.logger.info(
                f"Investigation {investigation_id} completed in "
                f"{result.total_duration_seconds:.2f}s"
            )

        except Exception as e:
            self.logger.error(f"Investigation {investigation_id} failed: {e}")
            result.mark_failed(str(e))

        return result

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
