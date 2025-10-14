"""
Entity Models

Data models for entity graph.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EntityType(str, Enum):
    """Types of entities in the graph."""

    COMPANY = "company"
    PERSON = "person"
    CONTRACT = "contract"
    BIDDING = "bidding"
    AGENCY = "agency"
    POLITICIAN = "politician"
    DONATION = "donation"
    BUDGET_ITEM = "budget_item"


class Entity(BaseModel):
    """Entity in the knowledge graph."""

    entity_id: str
    entity_type: EntityType
    data: dict[str, Any]
    source_api: str
    confidence_score: float = 1.0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def get_node_id(self) -> str:
        """Get node ID for graph."""
        return f"{self.entity_type.value}:{self.entity_id}"


class EntityRelationship(BaseModel):
    """Relationship between entities."""

    from_entity: str  # node_id format: "entity_type:entity_id"
    to_entity: str
    relationship_type: str  # won_contract, is_partner_of, donated_to, etc
    metadata: dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = 1.0
    created_at: datetime = Field(default_factory=datetime.now)
