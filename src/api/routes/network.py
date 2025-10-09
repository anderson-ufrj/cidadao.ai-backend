"""
Network analysis routes for entity relationship graphs.

Provides REST API for frontend visualization of entity networks,
suspicious patterns, and cross-investigation analysis.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from src.core import get_logger
from src.db.session import get_db
from src.models.entity_graph import EntityNode, EntityRelationship, SuspiciousNetwork
from src.services.network_analysis_service import get_network_analysis_service

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/network", tags=["Network Analysis"])


# ==================== REQUEST/RESPONSE MODELS ====================

class EntitySearchResponse(BaseModel):
    """Entity search result."""
    id: str
    entity_type: str
    name: str
    cnpj: Optional[str] = None
    cpf: Optional[str] = None
    total_investigations: int
    total_contracts: int
    total_contract_value: float
    risk_score: float
    is_sanctioned: bool


class NetworkVisualizationResponse(BaseModel):
    """Network visualization data for frontend."""
    nodes: List[dict]
    edges: List[dict]
    node_count: int
    edge_count: int
    center_entity_id: str
    metadata: dict = {}


class SuspiciousNetworkResponse(BaseModel):
    """Suspicious network information."""
    id: str
    network_name: str
    network_type: str
    entity_count: int
    detection_reason: str
    confidence_score: float
    severity: str
    total_contract_value: float
    suspicious_value: float
    investigation_ids: List[str]
    is_active: bool
    reviewed: bool


class NetworkStatisticsResponse(BaseModel):
    """Overall network statistics."""
    total_entities: int
    total_relationships: int
    total_suspicious_networks: int
    entity_types: dict
    top_entities_by_centrality: List[dict]
    recent_suspicious_networks: List[dict]


# ==================== ENDPOINTS ====================

@router.get("/entities/search", response_model=List[EntitySearchResponse])
async def search_entities(
    query: str = Query(..., min_length=3, description="Search query (name, CNPJ, CPF)"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    limit: int = Query(20, le=100, description="Result limit"),
    db: AsyncSession = Depends(get_db),
):
    """
    Search entities in the network graph.

    **Query**: Name, CNPJ, or CPF (minimum 3 characters)
    **Returns**: List of matching entities with statistics
    """
    # Normalize query
    query_normalized = query.lower().strip()

    # Build query
    conditions = [
        or_(
            EntityNode.normalized_name.contains(query_normalized),
            EntityNode.cnpj == query,
            EntityNode.cpf == query,
        )
    ]

    if entity_type:
        conditions.append(EntityNode.entity_type == entity_type)

    stmt = select(EntityNode).where(and_(*conditions)).limit(limit)

    result = await db.execute(stmt)
    entities = list(result.scalars().all())

    return [
        EntitySearchResponse(
            id=e.id,
            entity_type=e.entity_type,
            name=e.name,
            cnpj=e.cnpj,
            cpf=e.cpf,
            total_investigations=e.total_investigations,
            total_contracts=e.total_contracts,
            total_contract_value=e.total_contract_value,
            risk_score=e.risk_score,
            is_sanctioned=e.is_sanctioned,
        )
        for e in entities
    ]


@router.get("/entities/{entity_id}", response_model=dict)
async def get_entity_details(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific entity.

    **Returns**: Complete entity data including statistics and metadata
    """
    entity = await db.get(EntityNode, entity_id)

    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    return entity.to_dict()


@router.get("/entities/{entity_id}/network", response_model=NetworkVisualizationResponse)
async def get_entity_network(
    entity_id: str,
    depth: int = Query(2, ge=1, le=3, description="Network traversal depth (1-3)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get network visualization data for an entity.

    **Depth**: How many relationship hops to include (1-3)
    **Returns**: Nodes and edges for D3.js/Cytoscape visualization

    **Example Response**:
    ```json
    {
      "nodes": [{"id": "...", "name": "...", "type": "..."}],
      "edges": [{"source": "...", "target": "...", "type": "..."}],
      "node_count": 15,
      "edge_count": 20
    }
    ```
    """
    # Verify entity exists
    entity = await db.get(EntityNode, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Get network analysis service
    network_service = get_network_analysis_service(db)

    # Get network data
    network_data = await network_service.get_entity_network(entity_id, depth)

    return NetworkVisualizationResponse(
        nodes=network_data["nodes"],
        edges=network_data["edges"],
        node_count=network_data["node_count"],
        edge_count=network_data["edge_count"],
        center_entity_id=entity_id,
        metadata={
            "depth": depth,
            "center_entity_name": entity.name,
        },
    )


@router.get("/entities/{entity_id}/investigations", response_model=List[dict])
async def get_entity_investigations(
    entity_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all investigations involving a specific entity.

    **Returns**: List of investigation references with details
    """
    entity = await db.get(EntityNode, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Get investigation references
    references = entity.investigation_references

    return [ref.to_dict() for ref in references]


@router.get("/suspicious-networks", response_model=List[SuspiciousNetworkResponse])
async def get_suspicious_networks(
    network_type: Optional[str] = Query(None, description="Filter by network type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    active_only: bool = Query(True, description="Show only active networks"),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of detected suspicious networks.

    **Network Types**: cartel, shell_network, concentration, fraud_ring, collusion
    **Severity**: low, medium, high, critical
    **Returns**: List of suspicious networks for investigation
    """
    conditions = []

    if network_type:
        conditions.append(SuspiciousNetwork.network_type == network_type)

    if severity:
        conditions.append(SuspiciousNetwork.severity == severity)

    if active_only:
        conditions.append(SuspiciousNetwork.is_active == True)

    stmt = (
        select(SuspiciousNetwork)
        .where(and_(*conditions) if conditions else True)
        .order_by(SuspiciousNetwork.confidence_score.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    networks = list(result.scalars().all())

    return [
        SuspiciousNetworkResponse(
            id=n.id,
            network_name=n.network_name,
            network_type=n.network_type,
            entity_count=n.entity_count,
            detection_reason=n.detection_reason,
            confidence_score=n.confidence_score,
            severity=n.severity,
            total_contract_value=n.total_contract_value,
            suspicious_value=n.suspicious_value,
            investigation_ids=n.investigation_ids,
            is_active=n.is_active,
            reviewed=n.reviewed,
        )
        for n in networks
    ]


@router.get("/suspicious-networks/{network_id}", response_model=dict)
async def get_suspicious_network_details(
    network_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a suspicious network.

    **Returns**: Complete network data including graph visualization
    """
    network = await db.get(SuspiciousNetwork, network_id)

    if not network:
        raise HTTPException(status_code=404, detail="Suspicious network not found")

    return network.to_dict()


@router.get("/statistics", response_model=NetworkStatisticsResponse)
async def get_network_statistics(
    db: AsyncSession = Depends(get_db),
):
    """
    Get overall network statistics.

    **Returns**: Comprehensive statistics about the entity graph
    """
    # Count entities
    entity_count = await db.scalar(select(func.count(EntityNode.id)))

    # Count relationships
    relationship_count = await db.scalar(select(func.count(EntityRelationship.id)))

    # Count suspicious networks
    suspicious_count = await db.scalar(
        select(func.count(SuspiciousNetwork.id)).where(SuspiciousNetwork.is_active == True)
    )

    # Entity type distribution
    entity_types_result = await db.execute(
        select(
            EntityNode.entity_type,
            func.count(EntityNode.id).label("count")
        ).group_by(EntityNode.entity_type)
    )
    entity_types = {row[0]: row[1] for row in entity_types_result}

    # Top entities by centrality
    top_entities_result = await db.execute(
        select(EntityNode)
        .order_by(EntityNode.degree_centrality.desc())
        .limit(10)
    )
    top_entities = [
        {
            "id": e.id,
            "name": e.name,
            "entity_type": e.entity_type,
            "degree_centrality": e.degree_centrality,
            "total_investigations": e.total_investigations,
        }
        for e in top_entities_result.scalars().all()
    ]

    # Recent suspicious networks
    recent_networks_result = await db.execute(
        select(SuspiciousNetwork)
        .where(SuspiciousNetwork.is_active == True)
        .order_by(SuspiciousNetwork.created_at.desc())
        .limit(5)
    )
    recent_networks = [
        {
            "id": n.id,
            "network_name": n.network_name,
            "network_type": n.network_type,
            "severity": n.severity,
            "entity_count": n.entity_count,
        }
        for n in recent_networks_result.scalars().all()
    ]

    return NetworkStatisticsResponse(
        total_entities=entity_count or 0,
        total_relationships=relationship_count or 0,
        total_suspicious_networks=suspicious_count or 0,
        entity_types=entity_types,
        top_entities_by_centrality=top_entities,
        recent_suspicious_networks=recent_networks,
    )


@router.get("/relationships/{relationship_id}", response_model=dict)
async def get_relationship_details(
    relationship_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific relationship.

    **Returns**: Relationship data including evidence and investigations
    """
    relationship = await db.get(EntityRelationship, relationship_id)

    if not relationship:
        raise HTTPException(status_code=404, detail="Relationship not found")

    return relationship.to_dict()


@router.post("/suspicious-networks/{network_id}/review")
async def review_suspicious_network(
    network_id: str,
    review_notes: str = Query(..., description="Investigation review notes"),
    db: AsyncSession = Depends(get_db),
):
    """
    Mark suspicious network as reviewed by investigator.

    **Required**: review_notes (what the investigator concluded)
    **Returns**: Updated network status
    """
    network = await db.get(SuspiciousNetwork, network_id)

    if not network:
        raise HTTPException(status_code=404, detail="Suspicious network not found")

    network.reviewed = True
    network.review_notes = review_notes
    network.is_active = False  # Mark as resolved

    await db.commit()

    logger.info(
        "suspicious_network_reviewed",
        network_id=network_id,
        network_type=network.network_type,
    )

    return {
        "status": "reviewed",
        "network_id": network_id,
        "message": "Rede suspeita marcada como revisada com sucesso",
    }


@router.get("/export/cytoscape/{entity_id}")
async def export_network_cytoscape(
    entity_id: str,
    depth: int = Query(2, ge=1, le=3),
    db: AsyncSession = Depends(get_db),
):
    """
    Export network in Cytoscape.js format for visualization.

    **Returns**: JSON compatible with Cytoscape.js library
    """
    entity = await db.get(EntityNode, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    network_service = get_network_analysis_service(db)
    network_data = await network_service.get_entity_network(entity_id, depth)

    # Convert to Cytoscape format
    cytoscape_data = {
        "elements": {
            "nodes": [
                {
                    "data": {
                        "id": node["id"],
                        "label": node["name"],
                        "type": node["entity_type"],
                        "risk_score": node.get("risk_score", 0),
                        "total_investigations": node.get("total_investigations", 0),
                    }
                }
                for node in network_data["nodes"]
            ],
            "edges": [
                {
                    "data": {
                        "id": edge["id"],
                        "source": edge["source_entity_id"],
                        "target": edge["target_entity_id"],
                        "label": edge["relationship_type"],
                        "strength": edge.get("strength", 1.0),
                    }
                }
                for edge in network_data["edges"]
            ],
        },
        "layout": {
            "name": "cose",  # Force-directed layout
            "animate": True,
        },
        "style": [
            {
                "selector": "node",
                "style": {
                    "label": "data(label)",
                    "background-color": "#009B3A",  # Verde Brasil
                    "color": "#fff",
                },
            },
            {
                "selector": "node[type='empresa']",
                "style": {"background-color": "#002776"},  # Azul Brasil
            },
            {
                "selector": "node[type='pessoa_fisica']",
                "style": {"background-color": "#FFDF00"},  # Amarelo Brasil
            },
            {
                "selector": "edge",
                "style": {
                    "label": "data(label)",
                    "width": "data(strength)",
                    "line-color": "#999",
                    "curve-style": "bezier",
                },
            },
        ],
    }

    return cytoscape_data


@router.get("/export/d3/{entity_id}")
async def export_network_d3(
    entity_id: str,
    depth: int = Query(2, ge=1, le=3),
    db: AsyncSession = Depends(get_db),
):
    """
    Export network in D3.js force graph format.

    **Returns**: JSON compatible with D3.js force-directed graph
    """
    entity = await db.get(EntityNode, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    network_service = get_network_analysis_service(db)
    network_data = await network_service.get_entity_network(entity_id, depth)

    # Convert to D3 format
    d3_data = {
        "nodes": [
            {
                "id": node["id"],
                "name": node["name"],
                "type": node["entity_type"],
                "risk_score": node.get("risk_score", 0),
                "radius": 5 + (node.get("total_investigations", 0) * 2),  # Size by activity
            }
            for node in network_data["nodes"]
        ],
        "links": [
            {
                "source": edge["source_entity_id"],
                "target": edge["target_entity_id"],
                "type": edge["relationship_type"],
                "strength": edge.get("strength", 1.0),
                "value": edge.get("strength", 1.0) * 10,  # Link thickness
            }
            for edge in network_data["edges"]
        ],
    }

    return d3_data
