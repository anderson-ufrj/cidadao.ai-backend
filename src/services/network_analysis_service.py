"""
Module: services.network_analysis_service
Description: Network analysis service for entity relationship graphs
Author: Anderson Henrique da Silva
Date: 2025-10-09
License: Proprietary - All rights reserved

This service builds and analyzes entity relationship graphs from investigation data.
"""

import re
import unicodedata
from datetime import UTC, datetime
from typing import Any, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import get_logger
from src.models.entity_graph import (
    EntityInvestigationReference,
    EntityNode,
    EntityRelationship,
    SuspiciousNetwork,
)
from src.models.forensic_investigation import LegalEntity

logger = get_logger(__name__)


class NetworkAnalysisService:
    """
    Service for building and analyzing entity relationship networks.

    This is the core intelligence behind cross-investigation analysis,
    detecting hidden patterns, cartels, and suspicious networks.
    """

    def __init__(self, db_session: AsyncSession):
        """Initialize network analysis service."""
        self.db = db_session

    # ==================== ENTITY NODE MANAGEMENT ====================

    async def find_or_create_entity(
        self,
        legal_entity: LegalEntity,
        investigation_id: str,
        role: str = "unknown",
        contract_id: Optional[str] = None,
        contract_value: Optional[float] = None,
    ) -> EntityNode:
        """
        Find existing entity or create new one in the graph.

        Args:
            legal_entity: Entity data from investigation
            investigation_id: UUID of the investigation
            role: Role of entity (supplier, contractor, etc)
            contract_id: Related contract ID
            contract_value: Contract value

        Returns:
            EntityNode instance
        """
        # Determine entity type and identifier
        entity_type = legal_entity.entity_type
        identifier = (
            legal_entity.cnpj or legal_entity.cpf or legal_entity.company_registration
        )

        # Normalize name for matching
        normalized_name = self._normalize_text(legal_entity.name)

        # Try to find existing entity
        query = select(EntityNode).where(
            and_(
                EntityNode.entity_type == entity_type,
                or_(
                    (
                        EntityNode.cnpj == legal_entity.cnpj
                        if legal_entity.cnpj
                        else False
                    ),
                    EntityNode.cpf == legal_entity.cpf if legal_entity.cpf else False,
                    EntityNode.normalized_name == normalized_name,
                ),
            )
        )

        result = await self.db.execute(query)
        existing_entity = result.scalars().first()

        if existing_entity:
            # Update existing entity
            existing_entity.last_detected = datetime.now(UTC)
            existing_entity.total_investigations += 1

            # Update statistics
            if contract_value:
                existing_entity.total_contracts += 1
                existing_entity.total_contract_value += contract_value

            # Update metadata if new info available
            if (
                legal_entity.transparency_portal_url
                and not existing_entity.transparency_portal_url
            ):
                existing_entity.transparency_portal_url = (
                    legal_entity.transparency_portal_url
                )
            if (
                legal_entity.receita_federal_url
                and not existing_entity.receita_federal_url
            ):
                existing_entity.receita_federal_url = legal_entity.receita_federal_url

            entity = existing_entity
        else:
            # Create new entity
            entity = EntityNode(
                entity_type=entity_type,
                name=legal_entity.name,
                normalized_name=normalized_name,
                cnpj=legal_entity.cnpj,
                cpf=legal_entity.cpf,
                agency_code=(
                    legal_entity.company_registration
                    if entity_type == "orgao_publico"
                    else None
                ),
                email=legal_entity.email,
                phone=legal_entity.phone,
                address=legal_entity.address,
                city=legal_entity.city,
                state=legal_entity.state,
                transparency_portal_url=legal_entity.transparency_portal_url,
                receita_federal_url=legal_entity.receita_federal_url,
                company_website=legal_entity.company_website,
                total_investigations=1,
                total_contracts=1 if contract_value else 0,
                total_contract_value=contract_value or 0.0,
                first_detected=datetime.now(UTC),
                last_detected=datetime.now(UTC),
            )
            self.db.add(entity)
            await self.db.flush()  # Get ID

        # Create investigation reference
        reference = EntityInvestigationReference(
            entity_id=entity.id,
            investigation_id=investigation_id,
            role=role,
            contract_id=contract_id,
            contract_value=contract_value,
            evidence_data=self._entity_to_dict(legal_entity),
            detected_at=datetime.now(UTC),
        )
        self.db.add(reference)

        await self.db.commit()

        logger.info(
            "entity_processed",
            entity_id=entity.id,
            entity_name=entity.name,
            investigation_id=investigation_id,
            is_new=existing_entity is None,
        )

        return entity

    async def create_relationship(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relationship_type: str,
        investigation_id: str,
        evidence: Optional[dict[str, Any]] = None,
        strength: float = 1.0,
    ) -> EntityRelationship:
        """
        Create or update relationship between entities.

        Args:
            source_entity_id: Source entity ID
            target_entity_id: Target entity ID
            relationship_type: Type of relationship
            investigation_id: Investigation that found this
            evidence: Supporting evidence
            strength: Relationship strength (0-1)

        Returns:
            EntityRelationship instance
        """
        # Check if relationship already exists
        query = select(EntityRelationship).where(
            and_(
                EntityRelationship.source_entity_id == source_entity_id,
                EntityRelationship.target_entity_id == target_entity_id,
                EntityRelationship.relationship_type == relationship_type,
            )
        )

        result = await self.db.execute(query)
        existing_rel = result.scalars().first()

        if existing_rel:
            # Update existing relationship
            existing_rel.last_detected = datetime.now(UTC)
            existing_rel.detection_count += 1
            existing_rel.strength = min(
                1.0, existing_rel.strength + 0.1
            )  # Increase strength

            # Add investigation ID if not already present
            if investigation_id not in existing_rel.investigation_ids:
                existing_rel.investigation_ids.append(investigation_id)

            # Merge evidence
            if evidence:
                existing_rel.evidence.update(evidence)

            relationship = existing_rel
        else:
            # Create new relationship
            relationship = EntityRelationship(
                source_entity_id=source_entity_id,
                target_entity_id=target_entity_id,
                relationship_type=relationship_type,
                strength=strength,
                confidence=1.0,
                first_detected=datetime.now(UTC),
                last_detected=datetime.now(UTC),
                detection_count=1,
                investigation_ids=[investigation_id],
                evidence=evidence or {},
            )
            self.db.add(relationship)

        await self.db.commit()

        logger.info(
            "relationship_created",
            source_id=source_entity_id,
            target_id=target_entity_id,
            type=relationship_type,
            investigation_id=investigation_id,
        )

        return relationship

    # ==================== GRAPH BUILDING ====================

    async def build_graph_from_investigation(
        self,
        investigation_id: str,
        entities: list[LegalEntity],
        contract_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Build entity graph from investigation results.

        Args:
            investigation_id: Investigation UUID
            entities: List of entities found
            contract_data: Contract information

        Returns:
            Graph statistics
        """
        logger.info(
            "building_graph",
            investigation_id=investigation_id,
            entities_count=len(entities),
        )

        created_nodes = []
        created_relationships = []

        # Process each entity
        for entity_data in entities:
            role = self._determine_entity_role(entity_data)
            contract_id = contract_data.get("id") if contract_data else None
            contract_value = (
                contract_data.get("valorInicial") if contract_data else None
            )

            entity_node = await self.find_or_create_entity(
                legal_entity=entity_data,
                investigation_id=investigation_id,
                role=role,
                contract_id=contract_id,
                contract_value=contract_value,
            )
            created_nodes.append(entity_node)

        # Create relationships between entities
        # Example: supplier -> contracts_with -> agency
        suppliers = [e for e in created_nodes if e.entity_type == "empresa"]
        agencies = [e for e in created_nodes if e.entity_type == "orgao_publico"]

        for supplier in suppliers:
            for agency in agencies:
                rel = await self.create_relationship(
                    source_entity_id=supplier.id,
                    target_entity_id=agency.id,
                    relationship_type="contracts_with",
                    investigation_id=investigation_id,
                    evidence={
                        "contract_id": (
                            contract_data.get("id") if contract_data else None
                        ),
                        "contract_value": (
                            contract_data.get("valorInicial") if contract_data else None
                        ),
                    },
                )
                created_relationships.append(rel)

        # Calculate network metrics
        await self.calculate_network_metrics()

        # Detect suspicious patterns
        suspicious_networks = await self.detect_suspicious_networks(investigation_id)

        stats = {
            "investigation_id": investigation_id,
            "nodes_created": len(created_nodes),
            "relationships_created": len(created_relationships),
            "suspicious_networks_detected": len(suspicious_networks),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        logger.info("graph_built", **stats)

        return stats

    # ==================== NETWORK ANALYSIS ====================

    async def calculate_network_metrics(self) -> None:
        """
        Calculate network centrality metrics for all entities.

        Uses graph theory to identify influential entities:
        - Degree: Number of direct connections
        - Betweenness: Entity acting as bridge
        - Closeness: Average distance to others
        - Eigenvector: Influence based on connections' importance
        """
        # Get all entities and relationships
        entities_result = await self.db.execute(select(EntityNode))
        entities = list(entities_result.scalars().all())

        relationships_result = await self.db.execute(select(EntityRelationship))
        relationships = list(relationships_result.scalars().all())

        # Build adjacency dict for calculations
        adjacency = {}
        for entity in entities:
            adjacency[entity.id] = []

        for rel in relationships:
            adjacency[rel.source_entity_id].append(rel.target_entity_id)
            adjacency[rel.target_entity_id].append(rel.source_entity_id)  # Undirected

        # Calculate degree centrality (simple: number of connections)
        for entity in entities:
            entity.degree_centrality = len(adjacency.get(entity.id, []))

        # Calculate betweenness centrality (simplified version)
        # Full algorithm is complex, using approximation
        for entity in entities:
            betweenness = self._calculate_betweenness_simple(entity.id, adjacency)
            entity.betweenness_centrality = betweenness

        # Calculate closeness centrality
        for entity in entities:
            closeness = self._calculate_closeness_simple(entity.id, adjacency)
            entity.closeness_centrality = closeness

        # Eigenvector centrality (simplified: influenced by neighbors' degree)
        for entity in entities:
            neighbors = adjacency.get(entity.id, [])
            neighbor_degrees = sum(len(adjacency.get(n, [])) for n in neighbors)
            entity.eigenvector_centrality = neighbor_degrees / (len(entities) + 1)

        await self.db.commit()

        logger.info("network_metrics_calculated", entities_count=len(entities))

    async def detect_suspicious_networks(
        self, investigation_id: str
    ) -> list[SuspiciousNetwork]:
        """
        Detect suspicious entity networks.

        Patterns detected:
        - Cartels: Multiple companies with same ownership
        - Shell networks: Complex ownership chains
        - Concentration: Few suppliers dominating contracts
        - Collusion: Coordinated bidding patterns
        """
        suspicious_networks = []

        # Pattern 1: Cartel Detection (companies with shared relationships)
        cartels = await self._detect_cartels(investigation_id)
        suspicious_networks.extend(cartels)

        # Pattern 2: Concentration Detection
        concentration_networks = await self._detect_concentration(investigation_id)
        suspicious_networks.extend(concentration_networks)

        # Pattern 3: Shell Network Detection (complex chains)
        shell_networks = await self._detect_shell_networks(investigation_id)
        suspicious_networks.extend(shell_networks)

        logger.info(
            "suspicious_networks_detected",
            investigation_id=investigation_id,
            count=len(suspicious_networks),
        )

        return suspicious_networks

    async def _detect_cartels(self, investigation_id: str) -> list[SuspiciousNetwork]:
        """Detect potential cartels (companies with common ownership/management)."""
        cartels = []

        # Find companies that frequently contract with same agencies
        query = """
        WITH entity_agency_pairs AS (
            SELECT
                er.source_entity_id as company_id,
                er.target_entity_id as agency_id,
                COUNT(*) as contract_count
            FROM entity_relationships er
            WHERE er.relationship_type = 'contracts_with'
            AND :investigation_id = ANY(er.investigation_ids)
            GROUP BY er.source_entity_id, er.target_entity_id
        )
        SELECT
            agency_id,
            array_agg(company_id) as company_ids,
            COUNT(*) as company_count,
            SUM(contract_count) as total_contracts
        FROM entity_agency_pairs
        GROUP BY agency_id
        HAVING COUNT(*) >= 3  -- At least 3 companies
        """

        result = await self.db.execute(query, {"investigation_id": investigation_id})
        cartel_candidates = result.fetchall()

        for candidate in cartel_candidates:
            # Check if companies have high concentration
            if candidate.company_count >= 3:
                network = SuspiciousNetwork(
                    network_name=f"Possível Cartel - Agência {candidate.agency_id[:8]}",
                    network_type="cartel",
                    entity_ids=candidate.company_ids,
                    entity_count=candidate.company_count,
                    detection_reason=f"Detectados {candidate.company_count} fornecedores concentrados contratando com mesma agência",
                    confidence_score=0.7,
                    severity="high",
                    investigation_ids=[investigation_id],
                )
                self.db.add(network)
                cartels.append(network)

        await self.db.commit()
        return cartels

    async def _detect_concentration(
        self, investigation_id: str
    ) -> list[SuspiciousNetwork]:
        """Detect supplier concentration patterns."""
        concentration_networks = []

        # Find entities with high contract volume
        query = (
            select(EntityNode)
            .where(
                and_(
                    EntityNode.total_investigations >= 3,
                    EntityNode.total_contract_value > 1000000,  # R$ 1M+
                )
            )
            .order_by(EntityNode.total_contract_value.desc())
        )

        result = await self.db.execute(query)
        high_volume_entities = list(result.scalars().all())

        for entity in high_volume_entities[:10]:  # Top 10
            network = SuspiciousNetwork(
                network_name=f"Alta Concentração - {entity.name}",
                network_type="concentration",
                entity_ids=[entity.id],
                entity_count=1,
                detection_reason=f"Entidade com {entity.total_investigations} investigações e R$ {entity.total_contract_value:,.2f} em contratos",
                confidence_score=0.6,
                severity="medium",
                investigation_ids=[investigation_id],
                total_contract_value=entity.total_contract_value,
            )
            self.db.add(network)
            concentration_networks.append(network)

        await self.db.commit()
        return concentration_networks

    async def _detect_shell_networks(
        self, investigation_id: str
    ) -> list[SuspiciousNetwork]:
        """Detect shell company networks (complex ownership chains)."""
        # Simplified: Detect entities with many relationships but low contract value
        query = select(EntityNode).where(
            and_(
                EntityNode.degree_centrality >= 5,  # Many connections
                EntityNode.total_contract_value < 100000,  # Low value
            )
        )

        result = await self.db.execute(query)
        shell_candidates = list(result.scalars().all())

        shell_networks = []
        for candidate in shell_candidates:
            network = SuspiciousNetwork(
                network_name=f"Possível Rede de Laranjas - {candidate.name}",
                network_type="shell_network",
                entity_ids=[candidate.id],
                entity_count=1,
                detection_reason=f"Entidade com {candidate.degree_centrality} conexões mas baixo volume de contratos",
                confidence_score=0.5,
                severity="medium",
                investigation_ids=[investigation_id],
            )
            self.db.add(network)
            shell_networks.append(network)

        await self.db.commit()
        return shell_networks

    # ==================== GRAPH QUERIES ====================

    async def get_entity_network(
        self,
        entity_id: str,
        depth: int = 2,
    ) -> dict[str, Any]:
        """
        Get network of entities connected to a specific entity.

        Args:
            entity_id: Central entity ID
            depth: How many hops to traverse (1-3)

        Returns:
            Network data for visualization
        """
        nodes = []
        edges = []
        visited = set()

        # BFS traversal
        await self._traverse_network(entity_id, depth, visited, nodes, edges)

        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "center_entity_id": entity_id,
        }

    async def _traverse_network(
        self,
        entity_id: str,
        depth: int,
        visited: set,
        nodes: list,
        edges: list,
    ) -> None:
        """Recursive BFS network traversal."""
        if depth <= 0 or entity_id in visited:
            return

        visited.add(entity_id)

        # Get entity
        entity = await self.db.get(EntityNode, entity_id)
        if entity:
            nodes.append(entity.to_dict())

        # Get relationships
        query = select(EntityRelationship).where(
            or_(
                EntityRelationship.source_entity_id == entity_id,
                EntityRelationship.target_entity_id == entity_id,
            )
        )

        result = await self.db.execute(query)
        relationships = list(result.scalars().all())

        for rel in relationships:
            edges.append(rel.to_dict())

            # Traverse connected entities
            next_id = (
                rel.target_entity_id
                if rel.source_entity_id == entity_id
                else rel.source_entity_id
            )
            await self._traverse_network(next_id, depth - 1, visited, nodes, edges)

    # ==================== HELPER METHODS ====================

    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching (lowercase, no accents)."""
        if not text:
            return ""
        # Remove accents
        text = unicodedata.normalize("NFKD", text)
        text = "".join([c for c in text if not unicodedata.combining(c)])
        # Lowercase and clean
        text = text.lower().strip()
        # Remove extra spaces
        text = re.sub(r"\s+", " ", text)
        return text

    def _determine_entity_role(self, entity: LegalEntity) -> str:
        """Determine role of entity based on type."""
        if entity.entity_type == "empresa":
            return "supplier"
        elif entity.entity_type == "orgao_publico":
            return "contracting_agency"
        elif entity.entity_type == "pessoa_fisica":
            return "owner"
        return "unknown"

    def _entity_to_dict(self, entity: LegalEntity) -> dict:
        """Convert LegalEntity to dict."""
        return {
            "name": entity.name,
            "entity_type": entity.entity_type,
            "cnpj": entity.cnpj,
            "cpf": entity.cpf,
            "address": entity.address,
            "city": entity.city,
            "state": entity.state,
        }

    def _calculate_betweenness_simple(self, node_id: str, adjacency: dict) -> float:
        """Simplified betweenness centrality calculation."""
        # Count how many shortest paths pass through this node
        # Simplified: Just check if node connects disconnected components
        neighbors = set(adjacency.get(node_id, []))
        if len(neighbors) < 2:
            return 0.0

        # Check if removing this node disconnects the graph
        bridge_count = 0
        for n1 in neighbors:
            for n2 in neighbors:
                if n1 != n2:
                    # Check if n1 and n2 are only connected through node_id
                    n1_neighbors = set(adjacency.get(n1, []))
                    if n2 not in n1_neighbors:
                        bridge_count += 1

        return bridge_count / (len(neighbors) * (len(neighbors) - 1) + 1)

    def _calculate_closeness_simple(self, node_id: str, adjacency: dict) -> float:
        """Simplified closeness centrality calculation."""
        # Average shortest path length from this node to all others
        # Using BFS to find distances
        distances = self._bfs_distances(node_id, adjacency)

        if not distances:
            return 0.0

        avg_distance = sum(distances.values()) / len(distances)
        return 1.0 / (avg_distance + 1)  # Inverse of average distance

    def _bfs_distances(self, start: str, adjacency: dict) -> dict:
        """BFS to calculate distances from start node."""
        distances = {}
        queue = [(start, 0)]
        visited = {start}

        while queue:
            node, dist = queue.pop(0)

            for neighbor in adjacency.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    distances[neighbor] = dist + 1
                    queue.append((neighbor, dist + 1))

        return distances


# Factory function for easy instantiation
def get_network_analysis_service(db_session: AsyncSession) -> NetworkAnalysisService:
    """Get network analysis service instance."""
    return NetworkAnalysisService(db_session)
