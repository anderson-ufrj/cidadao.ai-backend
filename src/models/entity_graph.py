"""
Module: models.entity_graph
Description: Entity relationship graph models for cross-investigation analysis
Author: Anderson Henrique da Silva
Date: 2025-10-09
License: Proprietary - All rights reserved

This module defines the graph database structure for tracking relationships
between companies, people, and government agencies across multiple investigations.
"""

from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from src.models.base import BaseModel


class EntityNode(BaseModel):
    """
    Entity node in the relationship graph.

    Represents companies, people, or government agencies that appear
    across multiple investigations. Tracks all occurrences and connections.
    """

    __tablename__ = "entity_nodes"

    # Entity identification
    entity_type = Column(
        String(50), nullable=False, index=True
    )  # company, person, agency
    name = Column(String(500), nullable=False, index=True)
    normalized_name = Column(
        String(500), nullable=False, index=True
    )  # Lowercase, no accents

    # Official identifiers
    cnpj = Column(String(18), nullable=True, index=True)
    cpf = Column(String(14), nullable=True, index=True)
    agency_code = Column(String(50), nullable=True, index=True)

    # Contact information
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)

    # External references
    transparency_portal_url = Column(String(500), nullable=True)
    receita_federal_url = Column(String(500), nullable=True)
    company_website = Column(String(500), nullable=True)

    # Statistics (updated automatically)
    total_investigations = Column(Integer, default=0)
    total_contracts = Column(Integer, default=0)
    total_contract_value = Column(Float, default=0.0)
    total_anomalies = Column(Integer, default=0)

    # Risk scoring
    risk_score = Column(Float, default=0.0)  # 0-10 scale
    is_sanctioned = Column(Boolean, default=False)
    sanction_details = Column(JSON, default={})

    # Network metrics (calculated by NetworkAnalysisService)
    degree_centrality = Column(Float, default=0.0)  # Number of connections
    betweenness_centrality = Column(Float, default=0.0)  # Bridge between networks
    closeness_centrality = Column(Float, default=0.0)  # Average distance to others
    eigenvector_centrality = Column(Float, default=0.0)  # Influence score

    # Extra data
    first_detected = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    last_detected = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    extra_data = Column(JSON, default={})

    # Relationships
    source_relationships = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.source_entity_id",
        back_populates="source_entity",
        cascade="all, delete-orphan",
    )
    target_relationships = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.target_entity_id",
        back_populates="target_entity",
        cascade="all, delete-orphan",
    )
    investigation_references = relationship(
        "EntityInvestigationReference",
        back_populates="entity",
        cascade="all, delete-orphan",
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_entity_cnpj", "cnpj"),
        Index("idx_entity_cpf", "cpf"),
        Index("idx_entity_type_name", "entity_type", "normalized_name"),
        Index("idx_entity_risk", "risk_score"),
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "entity_type": self.entity_type,
            "name": self.name,
            "cnpj": self.cnpj,
            "cpf": self.cpf,
            "agency_code": self.agency_code,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "transparency_portal_url": self.transparency_portal_url,
            "receita_federal_url": self.receita_federal_url,
            "company_website": self.company_website,
            "statistics": {
                "total_investigations": self.total_investigations,
                "total_contracts": self.total_contracts,
                "total_contract_value": self.total_contract_value,
                "total_anomalies": self.total_anomalies,
            },
            "risk_score": self.risk_score,
            "is_sanctioned": self.is_sanctioned,
            "sanction_details": self.sanction_details,
            "network_metrics": {
                "degree_centrality": self.degree_centrality,
                "betweenness_centrality": self.betweenness_centrality,
                "closeness_centrality": self.closeness_centrality,
                "eigenvector_centrality": self.eigenvector_centrality,
            },
            "first_detected": (
                self.first_detected.isoformat() if self.first_detected else None
            ),
            "last_detected": (
                self.last_detected.isoformat() if self.last_detected else None
            ),
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class EntityRelationship(BaseModel):
    """
    Relationship edge between two entities in the graph.

    Represents connections like "company A is owned by person B",
    "company C contracts with agency D", etc.
    """

    __tablename__ = "entity_relationships"

    # Relationship endpoints
    source_entity_id = Column(
        String(36),
        ForeignKey("entity_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_entity_id = Column(
        String(36),
        ForeignKey("entity_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationship type
    relationship_type = Column(String(100), nullable=False, index=True)
    # Types: owns, manages, partners_with, contracts_with, employs, related_to

    # Relationship strength and confidence
    strength = Column(Float, default=1.0)  # 0-1, based on frequency and evidence
    confidence = Column(Float, default=1.0)  # 0-1, confidence in the relationship

    # Evidence and detection
    first_detected = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    last_detected = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    detection_count = Column(Integer, default=1)  # How many times detected

    # Investigation references (which investigations found this relationship)
    investigation_ids = Column(JSON, default=[])  # List of investigation UUIDs

    # Evidence details
    evidence = Column(JSON, default={})  # Links to documents, contracts, etc.

    # Risk flags
    is_suspicious = Column(Boolean, default=False)
    suspicion_reasons = Column(JSON, default=[])

    # Extra data
    extra_data = Column(JSON, default={})

    # SQLAlchemy relationships
    source_entity = relationship(
        "EntityNode",
        foreign_keys=[source_entity_id],
        back_populates="source_relationships",
    )
    target_entity = relationship(
        "EntityNode",
        foreign_keys=[target_entity_id],
        back_populates="target_relationships",
    )

    # Indexes
    __table_args__ = (
        Index("idx_relationship_source_target", "source_entity_id", "target_entity_id"),
        Index("idx_relationship_type", "relationship_type"),
        Index("idx_relationship_suspicious", "is_suspicious"),
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "source_entity_id": self.source_entity_id,
            "target_entity_id": self.target_entity_id,
            "relationship_type": self.relationship_type,
            "strength": self.strength,
            "confidence": self.confidence,
            "first_detected": (
                self.first_detected.isoformat() if self.first_detected else None
            ),
            "last_detected": (
                self.last_detected.isoformat() if self.last_detected else None
            ),
            "detection_count": self.detection_count,
            "investigation_ids": self.investigation_ids,
            "evidence": self.evidence,
            "is_suspicious": self.is_suspicious,
            "suspicion_reasons": self.suspicion_reasons,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class EntityInvestigationReference(BaseModel):
    """
    Reference linking an entity to a specific investigation.

    Tracks exactly where and how an entity appeared in each investigation.
    """

    __tablename__ = "entity_investigation_references"

    # References
    entity_id = Column(
        String(36),
        ForeignKey("entity_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    investigation_id = Column(
        String(36), nullable=False, index=True
    )  # UUID from investigations table

    # Context of appearance
    role = Column(
        String(100), nullable=False
    )  # supplier, contractor, owner, beneficiary
    contract_id = Column(
        String(100), nullable=True
    )  # If related to a specific contract
    contract_value = Column(Float, nullable=True)

    # Anomaly involvement
    involved_in_anomalies = Column(Boolean, default=False)
    anomaly_ids = Column(JSON, default=[])  # List of anomaly IDs from the investigation

    # Evidence
    evidence_data = Column(JSON, default={})  # Full entity data from that investigation

    # Extra data
    detected_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    extra_data = Column(JSON, default={})

    # SQLAlchemy relationship
    entity = relationship("EntityNode", back_populates="investigation_references")

    # Indexes
    __table_args__ = (
        Index("idx_reference_entity_investigation", "entity_id", "investigation_id"),
        Index("idx_reference_investigation", "investigation_id"),
        Index("idx_reference_anomalies", "involved_in_anomalies"),
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "entity_id": self.entity_id,
            "investigation_id": self.investigation_id,
            "role": self.role,
            "contract_id": self.contract_id,
            "contract_value": self.contract_value,
            "involved_in_anomalies": self.involved_in_anomalies,
            "anomaly_ids": self.anomaly_ids,
            "evidence_data": self.evidence_data,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SuspiciousNetwork(BaseModel):
    """
    Detected suspicious network of entities.

    Represents groups of entities with suspicious patterns like:
    - Cartels (multiple companies with same ownership)
    - Shell company networks
    - Concentration patterns
    """

    __tablename__ = "suspicious_networks"

    # Network identification
    network_name = Column(String(255), nullable=False)
    network_type = Column(String(100), nullable=False, index=True)
    # Types: cartel, shell_network, concentration, fraud_ring, collusion

    # Member entities
    entity_ids = Column(JSON, default=[])  # List of entity IDs in this network
    entity_count = Column(Integer, default=0)

    # Detection details
    detection_reason = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.0)  # 0-1
    severity = Column(String(50), default="medium")  # low, medium, high, critical

    # Investigation references
    investigation_ids = Column(JSON, default=[])  # Investigations that detected this
    first_detected = Column(DateTime, default=lambda: datetime.now(UTC))
    last_detected = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Financial impact
    total_contract_value = Column(Float, default=0.0)
    suspicious_value = Column(Float, default=0.0)

    # Evidence
    evidence = Column(JSON, default={})
    graph_data = Column(JSON, default={})  # Network structure for visualization

    # Status
    is_active = Column(Boolean, default=True)
    reviewed = Column(Boolean, default=False)
    review_notes = Column(Text, nullable=True)

    # Extra data
    extra_data = Column(JSON, default={})

    # Indexes
    __table_args__ = (
        Index("idx_network_type", "network_type"),
        Index("idx_network_severity", "severity"),
        Index("idx_network_active", "is_active"),
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "network_name": self.network_name,
            "network_type": self.network_type,
            "entity_ids": self.entity_ids,
            "entity_count": self.entity_count,
            "detection_reason": self.detection_reason,
            "confidence_score": self.confidence_score,
            "severity": self.severity,
            "investigation_ids": self.investigation_ids,
            "first_detected": (
                self.first_detected.isoformat() if self.first_detected else None
            ),
            "last_detected": (
                self.last_detected.isoformat() if self.last_detected else None
            ),
            "financial_impact": {
                "total_contract_value": self.total_contract_value,
                "suspicious_value": self.suspicious_value,
            },
            "evidence": self.evidence,
            "graph_data": self.graph_data,
            "is_active": self.is_active,
            "reviewed": self.reviewed,
            "review_notes": self.review_notes,
            "extra_data": self.extra_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
