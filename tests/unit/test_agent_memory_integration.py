"""
Unit tests for Agent Memory Integration Service
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.agents.deodoro import AgentContext, AgentMessage, AgentResponse, BaseAgent
from src.agents.nana import (
    ContextMemoryAgent,
    MemoryImportance,
)
from src.services.agent_memory_integration import (
    AgentMemoryIntegration,
    MemoryIntegrationType,
    get_memory_integration,
    initialize_memory_integration,
)


@pytest.fixture
def mock_memory_agent():
    """Create mock memory agent."""
    memory_agent = AsyncMock(spec=ContextMemoryAgent)
    memory_agent.store_episodic = AsyncMock()
    memory_agent.store_semantic = AsyncMock()
    memory_agent.retrieve_episodic = AsyncMock(return_value=[])
    memory_agent.retrieve_by_tag = AsyncMock(return_value=[])
    memory_agent.retrieve_similar = AsyncMock(return_value=[])
    return memory_agent


@pytest.fixture
def memory_integration(mock_memory_agent):
    """Create memory integration service."""
    return AgentMemoryIntegration(mock_memory_agent)


@pytest.fixture
def agent_context():
    """Create test agent context."""
    return AgentContext(
        investigation_id="test-123",
        user_id="user-123",
        session_id="session-123",
        metadata={},
    )


@pytest.fixture
def sample_message():
    """Create sample agent message."""
    return AgentMessage(
        role="user",
        content="Analyze contracts for anomalies",
        data={"contracts": [{"id": "C001", "value": 100000}]},
    )


class TestAgentMemoryIntegration:
    """Test suite for agent memory integration."""

    @pytest.mark.asyncio
    async def test_memory_integration_initialization(self, mock_memory_agent):
        """Test memory integration service initialization."""
        integration = AgentMemoryIntegration(mock_memory_agent)

        assert integration.memory_agent == mock_memory_agent
        assert integration.auto_store is True
        assert integration.auto_retrieve is True
        assert len(integration.agent_configs) > 0
        assert "zumbi" in integration.agent_configs
        assert "oxossi" in integration.agent_configs

    @pytest.mark.asyncio
    async def test_agent_integration(
        self, memory_integration, agent_context, sample_message
    ):
        """Test integrating an agent with memory system."""
        # Create mock agent
        agent = MagicMock(spec=BaseAgent)
        agent.agent_id = "zumbi"
        agent.process = AsyncMock(
            return_value=AgentResponse(
                success=True, data={"anomalies": [{"type": "price", "confidence": 0.8}]}
            )
        )

        # Integrate agent
        await memory_integration.integrate_agent(agent)

        # Test that process method was wrapped
        result = await agent.process(sample_message, agent_context)

        # Verify memory retrieval was attempted
        memory_integration.memory_agent.retrieve_episodic.assert_called()
        memory_integration.memory_agent.retrieve_by_tag.assert_called()

        # Verify result was stored
        memory_integration.memory_agent.store_episodic.assert_called()

    @pytest.mark.asyncio
    async def test_retrieve_relevant_memories(
        self, memory_integration, mock_memory_agent, agent_context
    ):
        """Test retrieving relevant memories for an agent."""
        # Setup mock returns
        mock_memory_agent.retrieve_episodic.return_value = [
            {"id": "mem1", "content": "test1", "relevance": 0.9}
        ]
        mock_memory_agent.retrieve_by_tag.return_value = [
            {"id": "mem2", "content": "test2", "relevance": 0.7}
        ]
        mock_memory_agent.retrieve_similar.return_value = [
            {"id": "mem3", "content": "test3", "relevance": 0.8}
        ]

        # Retrieve memories
        memories = await memory_integration.retrieve_relevant_memories(
            agent_id="zumbi",
            query="test query",
            context=agent_context,
            tags=["anomaly", "fraud"],
            limit=10,
        )

        assert len(memories) > 0
        assert memories[0]["relevance"] == 0.9  # Sorted by relevance
        assert len(memory_integration.access_log) == 1

    @pytest.mark.asyncio
    async def test_store_agent_result(
        self, memory_integration, mock_memory_agent, agent_context, sample_message
    ):
        """Test storing agent results in memory."""
        # Create mock result
        result = MagicMock()
        result.data = {
            "anomalies": [
                {
                    "type": "price",
                    "description": "Price anomaly detected",
                    "confidence": 0.85,
                }
            ]
        }

        # Store result
        success = await memory_integration.store_agent_result(
            agent_id="zumbi",
            message=sample_message,
            context=agent_context,
            result=result,
            importance=MemoryImportance.HIGH,
            tags=["anomaly", "investigation"],
        )

        assert success is True
        mock_memory_agent.store_episodic.assert_called_once()

        # Verify semantic knowledge extraction was attempted
        mock_memory_agent.store_semantic.assert_called()

    @pytest.mark.asyncio
    async def test_importance_determination(self, memory_integration):
        """Test determining importance of results."""
        # High risk result from Oxossi
        high_risk_result = MagicMock()
        high_risk_result.data = {"risk_level": "CRITICAL"}
        importance = memory_integration._determine_importance(
            "oxossi", high_risk_result
        )
        assert importance == MemoryImportance.HIGH

        # Medium importance for analytical findings
        analysis_result = MagicMock()
        analysis_result.data = {"patterns": [{"type": "trend"}]}
        importance = memory_integration._determine_importance("anita", analysis_result)
        assert importance == MemoryImportance.MEDIUM

        # Low importance for routine results
        routine_result = MagicMock()
        routine_result.data = {"status": "ok"}
        importance = memory_integration._determine_importance(
            "tiradentes", routine_result
        )
        assert importance == MemoryImportance.LOW

    @pytest.mark.asyncio
    async def test_memory_caching(
        self, memory_integration, mock_memory_agent, agent_context
    ):
        """Test memory caching mechanism."""
        # Setup mock return
        mock_memory_agent.retrieve_episodic.return_value = [
            {"id": "mem1", "content": "cached"}
        ]

        # First retrieval - should hit memory agent
        memories1 = await memory_integration.retrieve_relevant_memories(
            agent_id="test", query="test query", context=agent_context, tags=["test"]
        )

        assert mock_memory_agent.retrieve_episodic.call_count == 1

        # Second retrieval - should hit cache
        memories2 = await memory_integration.retrieve_relevant_memories(
            agent_id="test", query="test query", context=agent_context, tags=["test"]
        )

        assert mock_memory_agent.retrieve_episodic.call_count == 1  # Not called again
        assert memories1 == memories2

    @pytest.mark.asyncio
    async def test_share_knowledge_between_agents(
        self, memory_integration, mock_memory_agent
    ):
        """Test sharing knowledge between agents."""
        # Setup mock memories
        mock_memory_agent.retrieve_by_tag.return_value = [
            {
                "id": "mem1",
                "tags": ["zumbi", "anomaly"],
                "content": {"pattern": "suspicious"},
            }
        ]

        # Share knowledge
        success = await memory_integration.share_knowledge_between_agents(
            source_agent="zumbi", target_agent="oxossi", knowledge_type="anomaly"
        )

        assert success is True
        mock_memory_agent.retrieve_by_tag.assert_called_with(tag="zumbi", limit=100)

    @pytest.mark.asyncio
    async def test_memory_statistics(self, memory_integration, agent_context):
        """Test getting memory usage statistics."""
        # Add some access logs
        memory_integration.access_log = [
            {
                "agent_id": "zumbi",
                "timestamp": datetime.utcnow(),
                "query": "test1",
                "memories_retrieved": 5,
                "tags": ["anomaly"],
            },
            {
                "agent_id": "zumbi",
                "timestamp": datetime.utcnow(),
                "query": "test2",
                "memories_retrieved": 3,
                "tags": ["anomaly"],
            },
            {
                "agent_id": "oxossi",
                "timestamp": datetime.utcnow(),
                "query": "test3",
                "memories_retrieved": 7,
                "tags": ["fraud"],
            },
        ]

        stats = await memory_integration.get_memory_statistics()

        assert stats["total_accesses"] == 3
        assert "zumbi" in stats["by_agent"]
        assert stats["by_agent"]["zumbi"]["accesses"] == 2
        assert stats["by_agent"]["zumbi"]["memories_retrieved"] == 8
        assert stats["by_agent"]["oxossi"]["accesses"] == 1

    @pytest.mark.asyncio
    async def test_memory_consolidation(self, memory_integration):
        """Test memory consolidation for optimization."""
        memories = [
            {
                "id": f"mem{i}",
                "concept": "anomaly_price",
                "confidence": 0.7 + i * 0.05,
                "evidence": [f"evidence_{i}"],
                "tags": ["anomaly", "price"],
            }
            for i in range(5)
        ]

        consolidated = await memory_integration._consolidate_memories(memories)

        assert consolidated.concept == "anomaly_price"
        assert len(consolidated.evidence) <= 10
        assert consolidated.confidence > 0
        assert "consolidated" in consolidated.tags

    @pytest.mark.asyncio
    async def test_semantic_knowledge_extraction(
        self, memory_integration, mock_memory_agent, agent_context
    ):
        """Test extracting semantic knowledge from agent results."""
        # Test Oxossi fraud patterns
        oxossi_result = MagicMock()
        oxossi_result.data = {
            "fraud_analysis": {
                "patterns": [
                    {
                        "fraud_type": "bid_rigging",
                        "confidence": 0.85,
                        "indicators": [
                            {
                                "type": "identical_bids",
                                "description": "Multiple identical bids",
                            }
                        ],
                    }
                ]
            }
        }

        await memory_integration._extract_semantic_knowledge(
            agent_id="oxossi",
            result=oxossi_result,
            tags=["fraud"],
            context=agent_context,
        )

        # Verify semantic memory was stored
        assert mock_memory_agent.store_semantic.call_count >= 1
        call_args = mock_memory_agent.store_semantic.call_args[1]
        stored_memory = call_args["memory"]
        assert "fraud_bid_rigging" in stored_memory.concept

    @pytest.mark.asyncio
    async def test_access_control(self, memory_integration):
        """Test memory access control based on agent configuration."""
        # Read-only agent should not store
        tiradentes_config = memory_integration.agent_configs["tiradentes"]
        assert tiradentes_config["integration_type"] == MemoryIntegrationType.READ_ONLY
        assert tiradentes_config["auto_store_results"] is False

        # Read-write agent should store
        zumbi_config = memory_integration.agent_configs["zumbi"]
        assert zumbi_config["integration_type"] == MemoryIntegrationType.READ_WRITE
        assert zumbi_config["auto_store_results"] is True

    @pytest.mark.asyncio
    async def test_global_initialization(self, mock_memory_agent):
        """Test global memory integration initialization."""
        # Initialize globally
        integration = await initialize_memory_integration(mock_memory_agent)

        assert integration is not None
        assert get_memory_integration() == integration

        # Test retrieving global instance
        retrieved = get_memory_integration()
        assert retrieved == integration
