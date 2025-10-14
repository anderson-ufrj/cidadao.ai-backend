"""
End-to-End Integration Tests for Orchestration System

Tests the complete investigation flow from query to results.

Author: Anderson Henrique da Silva
Created: 2025-10-14
"""

import pytest

from src.services.orchestration import InvestigationOrchestrator
from src.services.orchestration.models.investigation import InvestigationIntent


@pytest.mark.asyncio
async def test_basic_orchestration_flow():
    """
    Test basic orchestration flow.

    This test verifies the complete flow:
    1. Query input
    2. Intent classification
    3. Entity extraction
    4. Execution planning
    5. Result generation
    """
    # Create orchestrator
    orchestrator = InvestigationOrchestrator()

    # Run investigation
    query = "Investigar contratos da empresa 12.345.678/0001-90"
    result = await orchestrator.investigate(query)

    # Verify result structure
    assert result.investigation_id is not None
    assert result.intent in InvestigationIntent
    assert result.context is not None
    assert result.context.user_query == query
    assert result.plan is not None
    assert len(result.plan.stages) > 0
    assert result.status in ["pending", "running", "completed", "failed"]


@pytest.mark.asyncio
async def test_entity_extraction():
    """Test entity extraction from query."""
    orchestrator = InvestigationOrchestrator()

    query = "Contratos da empresa 12.345.678/0001-90 em São Paulo durante 2024"
    result = await orchestrator.investigate(query)

    # Verify entities were extracted
    assert result.context.cnpj is not None
    assert result.context.state is not None
    assert result.context.year is not None


@pytest.mark.asyncio
async def test_entity_graph_population():
    """Test that entity graph is populated during investigation."""
    orchestrator = InvestigationOrchestrator()

    query = "Investigar fornecedor 12.345.678/0001-90"
    await orchestrator.investigate(query)

    # Check entity graph statistics
    stats = orchestrator.get_entity_graph_statistics()

    assert "total_entities" in stats
    assert "total_relationships" in stats
    assert "entities_by_type" in stats


@pytest.mark.asyncio
async def test_multiple_investigations():
    """Test running multiple investigations with shared orchestrator."""
    orchestrator = InvestigationOrchestrator()

    queries = [
        "Contratos em São Paulo",
        "Empresas em Minas Gerais",
        "Despesas federais em 2024",
    ]

    results = []
    for query in queries:
        result = await orchestrator.investigate(query)
        results.append(result)
        assert result.investigation_id is not None

    # Verify all investigations completed
    assert len(results) == len(queries)

    # Verify each has unique ID
    investigation_ids = [r.investigation_id for r in results]
    assert len(set(investigation_ids)) == len(queries)


@pytest.mark.asyncio
async def test_intent_classification_supplier_investigation():
    """Test supplier investigation intent classification."""
    orchestrator = InvestigationOrchestrator()

    query = "Investigar fornecedor ABC Ltda CNPJ 12.345.678/0001-90"
    result = await orchestrator.investigate(query)

    assert result.intent == InvestigationIntent.SUPPLIER_INVESTIGATION


@pytest.mark.asyncio
async def test_intent_classification_anomaly_detection():
    """Test contract anomaly detection intent classification."""
    orchestrator = InvestigationOrchestrator()

    query = "Detectar anomalias em contratos do órgão X"
    result = await orchestrator.investigate(query)

    # Should classify as anomaly detection
    assert result.intent in [
        InvestigationIntent.CONTRACT_ANOMALY_DETECTION,
        InvestigationIntent.CORRUPTION_INDICATORS,
    ]


@pytest.mark.asyncio
async def test_execution_plan_has_stages():
    """Test that execution plans contain stages."""
    orchestrator = InvestigationOrchestrator()

    query = "Contratos federais em 2024"
    result = await orchestrator.investigate(query)

    # Verify plan structure
    assert result.plan is not None
    assert len(result.plan.stages) > 0

    # Verify first stage has required fields
    stage = result.plan.stages[0]
    assert stage.name is not None
    assert stage.apis is not None
    assert stage.method is not None


@pytest.mark.asyncio
async def test_orchestrator_statistics():
    """Test orchestrator provides statistics."""
    orchestrator = InvestigationOrchestrator()

    # Run a investigation
    await orchestrator.investigate("Contratos em São Paulo 2024")

    # Get statistics
    stats = orchestrator.get_entity_graph_statistics()

    # Verify statistics structure
    assert isinstance(stats, dict)
    assert "total_entities" in stats
    assert "total_relationships" in stats
    assert "entities_by_type" in stats
    assert isinstance(stats["total_entities"], int)
    assert isinstance(stats["total_relationships"], int)


@pytest.mark.asyncio
async def test_error_handling():
    """Test that orchestrator handles errors gracefully."""
    orchestrator = InvestigationOrchestrator()

    # Empty query should not crash
    result = await orchestrator.investigate("")

    # Should complete without raising exception
    assert result is not None
    assert result.investigation_id is not None


@pytest.mark.asyncio
async def test_investigation_result_metadata():
    """Test that investigation result contains metadata."""
    orchestrator = InvestigationOrchestrator()

    result = await orchestrator.investigate("Contratos em 2024")

    # Verify metadata structure
    assert result.metadata is not None
    assert isinstance(result.metadata, dict)
    assert result.confidence_score is not None
    assert 0.0 <= result.confidence_score <= 1.0
