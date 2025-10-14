"""
Entity Graph Implementation

Manages entities and relationships discovered during investigations.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

from collections import defaultdict
from typing import Any

from src.core import get_logger
from src.services.orchestration.models.entities import (
    Entity,
    EntityRelationship,
    EntityType,
)

logger = get_logger(__name__)


class EntityGraph:
    """
    Graph-based storage for entities and relationships.

    Features:
    - Store and retrieve entities by ID or type
    - Track relationships between entities
    - Query entities by attributes
    - Find connected entities (graph traversal)
    - Detect patterns (e.g., supplier concentration)
    """

    def __init__(self) -> None:
        # Entity storage: {entity_id: Entity}
        self._entities: dict[str, Entity] = {}

        # Relationships: {entity_id: [EntityRelationship]}
        self._relationships: dict[str, list[EntityRelationship]] = defaultdict(list)

        # Type index: {EntityType: [entity_ids]}
        self._type_index: dict[EntityType, list[str]] = defaultdict(list)

        # Attribute index: {(attribute, value): [entity_ids]}
        self._attribute_index: dict[tuple[str, str], list[str]] = defaultdict(list)

        self.logger = get_logger(__name__)

    def add_entity(self, entity: Entity) -> None:
        """
        Add or update an entity in the graph.

        Args:
            entity: Entity to add
        """
        entity_id = entity.entity_id

        # Store entity
        self._entities[entity_id] = entity

        # Update type index
        if entity_id not in self._type_index[entity.entity_type]:
            self._type_index[entity.entity_type].append(entity_id)

        # Update attribute index for searchable attributes
        self._index_entity_attributes(entity)

        self.logger.debug(f"Added entity: {entity.entity_type.value} - {entity.name}")

    def _index_entity_attributes(self, entity: Entity) -> None:
        """Index important attributes for quick search."""
        searchable_attrs = ["cnpj", "cpf", "name", "contract_id"]

        for attr in searchable_attrs:
            if attr in entity.attributes and entity.attributes[attr]:
                value = str(entity.attributes[attr])
                key = (attr, value)
                if entity.entity_id not in self._attribute_index[key]:
                    self._attribute_index[key].append(entity.entity_id)

    def add_relationship(self, relationship: EntityRelationship) -> None:
        """
        Add a relationship between two entities.

        Args:
            relationship: Relationship to add
        """
        # Add forward relationship
        self._relationships[relationship.source_entity_id].append(relationship)

        # For bidirectional relationships, add reverse too
        if relationship.bidirectional:
            reverse = EntityRelationship(
                source_entity_id=relationship.target_entity_id,
                target_entity_id=relationship.source_entity_id,
                relationship_type=relationship.relationship_type,
                bidirectional=True,
                metadata=relationship.metadata,
            )
            self._relationships[relationship.target_entity_id].append(reverse)

        self.logger.debug(
            f"Added relationship: {relationship.source_entity_id} "
            f"--{relationship.relationship_type}--> {relationship.target_entity_id}"
        )

    def get_entity(self, entity_id: str) -> Entity | None:
        """Get entity by ID."""
        return self._entities.get(entity_id)

    def get_entities_by_type(self, entity_type: EntityType) -> list[Entity]:
        """Get all entities of a specific type."""
        entity_ids = self._type_index.get(entity_type, [])
        return [self._entities[eid] for eid in entity_ids if eid in self._entities]

    def find_entities_by_attribute(self, attribute: str, value: str) -> list[Entity]:
        """
        Find entities by attribute value.

        Args:
            attribute: Attribute name (e.g., "cnpj", "cpf")
            value: Attribute value to search for

        Returns:
            List of matching entities
        """
        key = (attribute, value)
        entity_ids = self._attribute_index.get(key, [])
        return [self._entities[eid] for eid in entity_ids if eid in self._entities]

    def get_relationships(self, entity_id: str) -> list[EntityRelationship]:
        """Get all relationships for an entity."""
        return self._relationships.get(entity_id, [])

    def get_connected_entities(
        self,
        entity_id: str,
        relationship_type: str | None = None,
        max_depth: int = 1,
    ) -> list[Entity]:
        """
        Get entities connected to this entity.

        Args:
            entity_id: Starting entity ID
            relationship_type: Filter by relationship type (optional)
            max_depth: Maximum traversal depth (default: 1)

        Returns:
            List of connected entities
        """
        visited = set()
        result = []

        def traverse(current_id: str, depth: int) -> None:
            if depth > max_depth or current_id in visited:
                return

            visited.add(current_id)

            # Get relationships
            relationships = self.get_relationships(current_id)

            # Filter by type if specified
            if relationship_type:
                relationships = [
                    r for r in relationships if r.relationship_type == relationship_type
                ]

            # Add connected entities
            for rel in relationships:
                target_entity = self.get_entity(rel.target_entity_id)
                if target_entity and target_entity.entity_id not in visited:
                    result.append(target_entity)
                    traverse(rel.target_entity_id, depth + 1)

        traverse(entity_id, 0)
        return result

    def extract_from_investigation_result(  # noqa: PLR0912
        self, result: dict[str, Any]
    ) -> None:
        """
        Extract entities and relationships from investigation results.

        Args:
            result: Investigation result data
        """
        # This is a simplified extraction
        # In production, use more sophisticated entity recognition

        for stage_name, stage_data in result.items():
            if not isinstance(stage_data, dict):
                continue

            # Extract companies from Minha Receita data
            if "minha_receita" in stage_name.lower():
                self._extract_company_entities(stage_data)

            # Extract contracts from procurement data
            elif (
                "contract" in stage_name.lower() or "procurement" in stage_name.lower()
            ):
                self._extract_contract_entities(stage_data)

            # Extract people from partner/employee data
            elif "partner" in stage_name.lower() or "employee" in stage_name.lower():
                self._extract_person_entities(stage_data)

    def _extract_company_entities(self, data: dict[str, Any]) -> None:
        """Extract company entities from data."""
        if "cnpj" in data:
            entity = Entity(
                entity_type=EntityType.COMPANY,
                name=data.get("name", "Unknown Company"),
                attributes={
                    "cnpj": data.get("cnpj"),
                    "legal_nature": data.get("legal_nature"),
                    "status": data.get("status"),
                    "opening_date": data.get("opening_date"),
                },
                source_api="minha_receita",
            )
            self.add_entity(entity)

    def _extract_contract_entities(self, data: dict[str, Any]) -> None:
        """Extract contract entities from procurement data."""
        # Handle list of contracts
        if isinstance(data, list):
            for contract in data:
                self._create_contract_entity(contract)
        elif "contracts" in data:
            for contract in data["contracts"]:
                self._create_contract_entity(contract)
        else:
            # Single contract
            self._create_contract_entity(data)

    def _create_contract_entity(self, contract: dict[str, Any]) -> None:
        """Create a contract entity."""
        if not contract.get("contract_id"):
            return

        entity = Entity(
            entity_type=EntityType.CONTRACT,
            name=f"Contract {contract.get('contract_id')}",
            attributes={
                "contract_id": contract.get("contract_id"),
                "value": contract.get("value"),
                "supplier_cnpj": contract.get("supplier_cnpj"),
                "agency": contract.get("agency"),
                "date": contract.get("date"),
            },
            source_api=contract.get("source", "unknown"),
        )
        self.add_entity(entity)

        # Create relationship to supplier if we have CNPJ
        if contract.get("supplier_cnpj"):
            supplier_entities = self.find_entities_by_attribute(
                "cnpj", contract["supplier_cnpj"]
            )
            if supplier_entities:
                relationship = EntityRelationship(
                    source_entity_id=supplier_entities[0].entity_id,
                    target_entity_id=entity.entity_id,
                    relationship_type="awarded_contract",
                )
                self.add_relationship(relationship)

    def _extract_person_entities(self, data: dict[str, Any]) -> None:
        """Extract person entities from data."""
        if "partners" in data:
            for partner in data["partners"]:
                if partner.get("name"):
                    entity = Entity(
                        entity_type=EntityType.PERSON,
                        name=partner.get("name"),
                        attributes={
                            "cpf": partner.get("cpf"),
                            "role": partner.get("role"),
                        },
                        source_api="minha_receita",
                    )
                    self.add_entity(entity)

    def get_statistics(self) -> dict[str, Any]:
        """Get graph statistics."""
        total_relationships = sum(len(rels) for rels in self._relationships.values())

        entity_counts = {
            entity_type.value: len(self._type_index.get(entity_type, []))
            for entity_type in EntityType
        }

        return {
            "total_entities": len(self._entities),
            "total_relationships": total_relationships,
            "entities_by_type": entity_counts,
            "indexed_attributes": len(self._attribute_index),
        }


class EntityGraphQuery:
    """
    Query builder for EntityGraph.

    Provides fluent interface for complex graph queries.
    """

    def __init__(self, graph: EntityGraph) -> None:
        self.graph = graph
        self._results: list[Entity] = []
        self._filters: list[callable] = []
        self.logger = get_logger(__name__)

    def of_type(self, entity_type: EntityType) -> "EntityGraphQuery":
        """Filter by entity type."""
        self._results = self.graph.get_entities_by_type(entity_type)
        return self

    def with_attribute(self, attribute: str, value: str) -> "EntityGraphQuery":
        """Filter by attribute value."""
        if not self._results:
            # First filter, search from graph
            self._results = self.graph.find_entities_by_attribute(attribute, value)
        else:
            # Apply to existing results
            self._results = [
                e for e in self._results if e.attributes.get(attribute) == value
            ]
        return self

    def connected_to(
        self,
        entity_id: str,
        relationship_type: str | None = None,
    ) -> "EntityGraphQuery":
        """Filter by connection to another entity."""
        connected = self.graph.get_connected_entities(entity_id, relationship_type)
        if not self._results:
            self._results = connected
        else:
            # Intersection
            connected_ids = {e.entity_id for e in connected}
            self._results = [e for e in self._results if e.entity_id in connected_ids]
        return self

    def filter(self, predicate: callable) -> "EntityGraphQuery":  # noqa: A003
        """Apply custom filter function."""
        self._filters.append(predicate)
        return self

    def execute(self) -> list[Entity]:
        """Execute query and return results."""
        results = self._results

        # Apply custom filters
        for filter_func in self._filters:
            results = [e for e in results if filter_func(e)]

        self.logger.debug(f"Query returned {len(results)} entities")
        return results

    def count(self) -> int:
        """Count results without returning them."""
        return len(self.execute())

    def first(self) -> Entity | None:
        """Get first result or None."""
        results = self.execute()
        return results[0] if results else None
