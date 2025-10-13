"""
Module: services.graph_integration_service
Description: Integration service to automatically build graphs from investigations
Author: Anderson Henrique da Silva
Date: 2025-10-09
License: Proprietary - All rights reserved

This service automatically integrates network graph analysis into investigations.
"""

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core import get_logger
from src.models.forensic_investigation import ForensicAnomalyResult
from src.services.network_analysis_service import get_network_analysis_service

logger = get_logger(__name__)


class GraphIntegrationService:
    """
    Service to integrate graph analysis with investigations.

    Automatically called after investigation completion to:
    1. Build entity graph from results
    2. Detect suspicious networks
    3. Enrich anomalies with network context
    """

    def __init__(self, db_session: AsyncSession):
        """Initialize graph integration service."""
        self.db = db_session
        self.network_service = get_network_analysis_service(db_session)

    async def integrate_investigation_with_graph(
        self,
        investigation_id: str,
        forensic_results: list[ForensicAnomalyResult],
        contract_data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Integrate investigation results with entity graph.

        Args:
            investigation_id: Investigation UUID
            forensic_results: List of forensic anomaly results
            contract_data: Contract information

        Returns:
            Integration statistics and detected networks
        """
        logger.info("starting_graph_integration", investigation_id=investigation_id)

        # Collect all entities from forensic results
        all_entities = []
        for result in forensic_results:
            all_entities.extend(result.involved_entities)

        # Build graph from entities
        graph_stats = await self.network_service.build_graph_from_investigation(
            investigation_id=investigation_id,
            entities=all_entities,
            contract_data=contract_data,
        )

        # Enrich anomalies with network analysis
        enriched_results = []
        for result in forensic_results:
            enriched = await self.enrich_anomaly_with_network(result, investigation_id)
            enriched_results.append(enriched)

        # Detect suspicious networks
        suspicious_networks = await self.network_service.detect_suspicious_networks(
            investigation_id
        )

        integration_result = {
            "investigation_id": investigation_id,
            "graph_statistics": graph_stats,
            "entities_processed": len(all_entities),
            "suspicious_networks_detected": len(suspicious_networks),
            "suspicious_networks": [
                {
                    "id": net.id,
                    "name": net.network_name,
                    "type": net.network_type,
                    "severity": net.severity,
                    "entity_count": net.entity_count,
                    "confidence": net.confidence_score,
                }
                for net in suspicious_networks
            ],
            "enriched_anomalies": enriched_results,
        }

        logger.info(
            "graph_integration_completed",
            investigation_id=investigation_id,
            entities=len(all_entities),
            networks=len(suspicious_networks),
        )

        return integration_result

    async def enrich_anomaly_with_network(
        self,
        anomaly: ForensicAnomalyResult,
        investigation_id: str,
    ) -> dict[str, Any]:
        """
        Enrich anomaly with network analysis data.

        Adds cross-investigation context:
        - Historical behavior of entities
        - Network connections
        - Suspicious patterns

        Args:
            anomaly: Forensic anomaly result
            investigation_id: Investigation UUID

        Returns:
            Enriched anomaly dict with network data
        """
        enriched_data = anomaly.to_dict()

        # Add network analysis for each entity
        network_analysis = []

        for entity in anomaly.involved_entities:
            # Find entity in graph
            from sqlalchemy import or_, select

            from src.models.entity_graph import EntityNode

            query = select(EntityNode).where(
                or_(
                    EntityNode.cnpj == entity.cnpj if entity.cnpj else False,
                    EntityNode.cpf == entity.cpf if entity.cpf else False,
                )
            )

            result = await self.db.execute(query)
            graph_entity = result.scalars().first()

            if graph_entity:
                # Get entity's network
                entity_network = await self.network_service.get_entity_network(
                    graph_entity.id, depth=1  # Just immediate connections
                )

                # Add network context
                network_analysis.append(
                    {
                        "entity_id": graph_entity.id,
                        "entity_name": graph_entity.name,
                        "entity_type": graph_entity.entity_type,
                        "historical_data": {
                            "total_investigations": graph_entity.total_investigations,
                            "total_contracts": graph_entity.total_contracts,
                            "total_contract_value": graph_entity.total_contract_value,
                            "risk_score": graph_entity.risk_score,
                            "is_sanctioned": graph_entity.is_sanctioned,
                        },
                        "network_metrics": {
                            "degree_centrality": graph_entity.degree_centrality,
                            "betweenness_centrality": graph_entity.betweenness_centrality,
                            "closeness_centrality": graph_entity.closeness_centrality,
                            "eigenvector_centrality": graph_entity.eigenvector_centrality,
                        },
                        "connections": {
                            "node_count": entity_network["node_count"],
                            "edge_count": entity_network["edge_count"],
                            "immediate_connections": [
                                {
                                    "id": node["id"],
                                    "name": node["name"],
                                    "type": node["entity_type"],
                                }
                                for node in entity_network["nodes"][:5]  # Top 5
                            ],
                        },
                    }
                )

        # Add network analysis to enriched data
        enriched_data["network_analysis"] = network_analysis

        # Add cross-investigation insights
        insights = await self._generate_cross_investigation_insights(network_analysis)
        enriched_data["cross_investigation_insights"] = insights

        return enriched_data

    async def _generate_cross_investigation_insights(
        self,
        network_analysis: list[dict[str, Any]],
    ) -> list[str]:
        """Generate insights based on cross-investigation network analysis."""
        insights = []

        for entity_data in network_analysis:
            historical = entity_data.get("historical_data", {})
            metrics = entity_data.get("network_metrics", {})
            entity_name = entity_data.get("entity_name")

            # Insight 1: Recorrência
            if historical.get("total_investigations", 0) >= 3:
                insights.append(
                    f"⚠️ **Entidade Recorrente**: {entity_name} aparece em {historical['total_investigations']} investigações anteriores, "
                    f"totalizando R$ {historical.get('total_contract_value', 0):,.2f} em contratos."
                )

            # Insight 2: Alto risco
            if historical.get("risk_score", 0) >= 7:
                insights.append(
                    f"🚨 **Alto Risco**: {entity_name} tem score de risco {historical['risk_score']:.1f}/10, "
                    f"indicando histórico de irregularidades."
                )

            # Insight 3: Sancionada
            if historical.get("is_sanctioned"):
                insights.append(
                    f"❌ **Sancionada**: {entity_name} consta com sanções administrativas registradas."
                )

            # Insight 4: Alta centralidade (influência)
            if metrics.get("degree_centrality", 0) >= 10:
                insights.append(
                    f"🕸️ **Altamente Conectada**: {entity_name} possui {metrics['degree_centrality']} conexões diretas, "
                    f"indicando posição central na rede."
                )

            # Insight 5: Bridge entre redes
            if metrics.get("betweenness_centrality", 0) >= 0.5:
                insights.append(
                    f"🌉 **Ponte Entre Redes**: {entity_name} atua como intermediária entre diferentes grupos, "
                    f"possível indicador de coordenação."
                )

            # Insight 6: Connections count
            connections = entity_data.get("connections", {})
            if connections.get("node_count", 0) >= 5:
                immediate = connections.get("immediate_connections", [])
                connection_names = [c["name"] for c in immediate[:3]]
                insights.append(
                    f"🔗 **Rede Ampla**: {entity_name} conectada a {connections['node_count']} entidades, "
                    f"incluindo {', '.join(connection_names)}."
                )

        return insights

    async def get_investigation_graph_visualization(
        self,
        investigation_id: str,
    ) -> dict[str, Any]:
        """
        Get graph visualization data for a specific investigation.

        Args:
            investigation_id: Investigation UUID

        Returns:
            Visualization data for frontend (D3.js/Cytoscape compatible)
        """
        # Get all entity references for this investigation
        from sqlalchemy import select

        from src.models.entity_graph import EntityInvestigationReference

        query = select(EntityInvestigationReference).where(
            EntityInvestigationReference.investigation_id == investigation_id
        )

        result = await self.db.execute(query)
        references = list(result.scalars().all())

        if not references:
            return {
                "nodes": [],
                "edges": [],
                "message": "Nenhuma entidade encontrada para esta investigação",
            }

        # Build network from all entities in this investigation
        entity_ids = [ref.entity_id for ref in references]

        nodes = []
        edges = []

        # Get all entities
        from src.models.entity_graph import EntityNode

        for entity_id in entity_ids:
            entity = await self.db.get(EntityNode, entity_id)
            if entity:
                nodes.append(
                    {
                        "id": entity.id,
                        "label": entity.name,
                        "type": entity.entity_type,
                        "risk_score": entity.risk_score,
                        "total_investigations": entity.total_investigations,
                        "is_sanctioned": entity.is_sanctioned,
                        "degree": entity.degree_centrality,
                    }
                )

        # Get relationships between these entities
        from src.models.entity_graph import EntityRelationship

        relationship_query = select(EntityRelationship).where(
            EntityRelationship.source_entity_id.in_(entity_ids)
        )

        rel_result = await self.db.execute(relationship_query)
        relationships = list(rel_result.scalars().all())

        for rel in relationships:
            if (
                rel.target_entity_id in entity_ids
            ):  # Only if target is also in investigation
                edges.append(
                    {
                        "id": rel.id,
                        "source": rel.source_entity_id,
                        "target": rel.target_entity_id,
                        "type": rel.relationship_type,
                        "strength": rel.strength,
                        "is_suspicious": rel.is_suspicious,
                    }
                )

        return {
            "investigation_id": investigation_id,
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "metadata": {
                "has_suspicious_relationships": any(e["is_suspicious"] for e in edges),
                "max_risk_score": max([n["risk_score"] for n in nodes]) if nodes else 0,
                "sanctioned_entities": sum(1 for n in nodes if n["is_sanctioned"]),
            },
        }


# Factory function
def get_graph_integration_service(db_session: AsyncSession) -> GraphIntegrationService:
    """Get graph integration service instance."""
    return GraphIntegrationService(db_session)
