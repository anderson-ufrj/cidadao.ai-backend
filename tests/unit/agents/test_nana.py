"""
Complete unit tests for Nanã Agent - Context Memory and Knowledge Management specialist.
Tests episodic memory, semantic memory, conversation tracking, and memory consolidation.
"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from src.agents.deodoro import AgentContext, AgentMessage, AgentStatus
from src.agents.nana import ContextMemoryAgent


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    client = AsyncMock()
    client.ping.return_value = True
    client.get.return_value = None
    client.set.return_value = True
    client.hset.return_value = 1
    client.hget.return_value = None
    client.hgetall.return_value = {}
    client.incr.return_value = 1
    client.sadd.return_value = 1
    client.smembers.return_value = set()
    return client


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing."""
    store = AsyncMock()
    store.initialize = AsyncMock()
    store.add_documents = AsyncMock()
    store.similarity_search = AsyncMock(return_value=[])
    store.delete_documents = AsyncMock()
    store.count = AsyncMock(return_value=0)
    return store


@pytest_asyncio.fixture
async def nana_agent(mock_redis_client, mock_vector_store):
    """Create Nanã agent with mocked dependencies."""
    agent = ContextMemoryAgent(
        redis_client=mock_redis_client,
        vector_store=mock_vector_store,
        max_episodic_memories=1000,
        max_conversation_turns=50,
        memory_decay_days=30,
    )
    await agent.initialize()
    return agent


@pytest.fixture
def sample_context():
    """Sample agent context for testing."""
    return AgentContext(
        investigation_id="test_investigation_001",
        user_id="test_user",
        session_id="test_session",
    )


class TestNanaAgentInitialization:
    """Test agent initialization and configuration."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_agent_basic_info(self, nana_agent):
        """Test basic agent information."""
        assert nana_agent.name == "ContextMemoryAgent"
        assert "store_episodic" in nana_agent.capabilities
        assert "retrieve_episodic" in nana_agent.capabilities
        assert "store_semantic" in nana_agent.capabilities
        assert "consolidate_memories" in nana_agent.capabilities

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_agent_configuration(self, nana_agent):
        """Test agent configuration parameters."""
        assert nana_agent.max_episodic_memories == 1000
        assert nana_agent.max_conversation_turns == 50
        assert nana_agent.memory_decay_days == 30

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_agent_initialization_success(
        self, mock_redis_client, mock_vector_store
    ):
        """Test successful agent initialization."""
        agent = ContextMemoryAgent(
            redis_client=mock_redis_client,
            vector_store=mock_vector_store,
        )
        await agent.initialize()

        # Verify vector store was initialized
        mock_vector_store.initialize.assert_called_once()


class TestEpisodicMemory:
    """Test episodic memory operations."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_episodic_memory_valid(
        self, nana_agent, sample_context, mock_vector_store
    ):
        """Test storing valid episodic memory."""
        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="store_episodic",
            payload={
                "memory_entry": {
                    "investigation_id": "test_inv_001",
                    "query": "Contratos de TI",
                    "result": {"total_contracts": 100, "anomalies": 5},
                    "timestamp": datetime.utcnow().isoformat(),
                }
            },
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        assert response.result is not None
        assert "memory_id" in response.result
        # Verify vector store was called
        mock_vector_store.add_documents.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_episodic_memory_missing_data(self, nana_agent, sample_context):
        """Test storing episodic memory without required data."""
        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="store_episodic",
            payload={},  # Missing memory_entry
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.ERROR
        assert "No memory entry provided" in response.error

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_retrieve_episodic_memory_success(
        self, nana_agent, sample_context, mock_vector_store
    ):
        """Test retrieving episodic memories."""
        # Mock vector store to return sample memories
        mock_vector_store.similarity_search.return_value = [
            {
                "id": "mem_001",
                "text": "Investigation about IT contracts",
                "metadata": {
                    "investigation_id": "inv_001",
                    "query": "IT contracts",
                    "timestamp": datetime.utcnow().isoformat(),
                },
                "similarity": 0.95,
            }
        ]

        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="retrieve_episodic",
            payload={"query": "IT contracts", "limit": 5},
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        assert "memories" in response.result
        assert len(response.result["memories"]) > 0
        mock_vector_store.similarity_search.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_retrieve_episodic_memory_no_results(
        self, nana_agent, sample_context, mock_vector_store
    ):
        """Test retrieving episodic memories with no results."""
        mock_vector_store.similarity_search.return_value = []

        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="retrieve_episodic",
            payload={"query": "non-existent topic"},
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        assert response.result["memories"] == []


class TestSemanticMemory:
    """Test semantic memory operations."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_semantic_memory_valid(
        self, nana_agent, sample_context, mock_vector_store
    ):
        """Test storing valid semantic memory."""
        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="store_semantic",
            payload={
                "concept": "Supplier Concentration",
                "content": "Pattern indicating potential monopoly",
                "relationships": ["Monopoly", "Fraud", "Bidding"],
                "evidence": ["HHI > 0.7"],
                "confidence": 0.85,
            },
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        assert "memory_id" in response.result
        mock_vector_store.add_documents.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_semantic_memory_missing_data(self, nana_agent, sample_context):
        """Test storing semantic memory without required fields."""
        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="store_semantic",
            payload={
                "concept": "Test",
                # Missing content
            },
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.ERROR
        assert "Concept and content required" in response.error

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_retrieve_semantic_memory(
        self, nana_agent, sample_context, mock_vector_store
    ):
        """Test retrieving semantic memories."""
        mock_vector_store.similarity_search.return_value = [
            {
                "id": "sem_001",
                "text": "Supplier concentration pattern",
                "metadata": {
                    "concept": "Supplier Concentration",
                    "relationships": ["Monopoly"],
                    "confidence": 0.85,
                },
                "similarity": 0.90,
            }
        ]

        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="retrieve_semantic",
            payload={"concept": "Supplier Concentration"},
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        assert "concepts" in response.result


class TestConversationMemory:
    """Test conversation memory operations."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_store_conversation_valid(
        self, nana_agent, sample_context, mock_redis_client
    ):
        """Test storing conversation turn."""
        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="store_conversation",
            payload={
                "conversation_id": "conv_001",
                "turn_number": 1,
                "speaker": "user",
                "message": "I want to investigate IT contracts",
                "intent": "investigation_request",
            },
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        # Verify Redis operations were called
        assert mock_redis_client.hset.called or mock_redis_client.incr.called

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_conversation_context(
        self, nana_agent, sample_context, mock_redis_client
    ):
        """Test retrieving conversation context."""
        # Mock Redis to return conversation data
        mock_redis_client.hgetall.return_value = {
            "turn_1": '{"speaker": "user", "message": "test message"}',
            "turn_2": '{"speaker": "assistant", "message": "test response"}',
        }

        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="get_conversation_context",
            payload={"conversation_id": "conv_001", "limit": 10},
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        mock_redis_client.hgetall.assert_called()


class TestMemoryConsolidation:
    """Test memory consolidation operations."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_consolidate_memories_success(
        self, nana_agent, sample_context, mock_vector_store
    ):
        """Test memory consolidation."""
        # Mock similar memories
        mock_vector_store.similarity_search.return_value = [
            {
                "id": "mem_001",
                "text": "Investigation about IT contracts",
                "metadata": {"investigation_id": "inv_001"},
                "similarity": 0.90,
            },
            {
                "id": "mem_002",
                "text": "Investigation about technology contracts",
                "metadata": {"investigation_id": "inv_002"},
                "similarity": 0.88,
            },
        ]
        mock_vector_store.count.return_value = 2

        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="consolidate_memories",
            payload={"similarity_threshold": 0.85},
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        assert "consolidated_count" in response.result


class TestMemoryRetrieval:
    """Test memory retrieval and context operations."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_relevant_context_success(
        self, nana_agent, sample_context, mock_vector_store
    ):
        """Test getting relevant context for investigation."""
        mock_vector_store.similarity_search.return_value = [
            {
                "id": "mem_001",
                "text": "Previous investigation findings",
                "metadata": {"investigation_id": "inv_001"},
                "similarity": 0.85,
            }
        ]

        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="get_relevant_context",
            payload={"query": "IT contracts investigation", "limit": 5},
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        assert "context" in response.result


class TestMemoryForget:
    """Test memory deletion operations."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_forget_memories_by_investigation(
        self, nana_agent, sample_context, mock_vector_store
    ):
        """Test forgetting memories by investigation ID."""
        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="forget_memories",
            payload={"investigation_id": "inv_001"},
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        assert "deleted_count" in response.result


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_unknown_action(self, nana_agent, sample_context):
        """Test handling of unknown action."""
        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="unknown_action",
            payload={},
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.ERROR
        assert "Unknown action" in response.error

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_vector_store_failure(
        self, nana_agent, sample_context, mock_vector_store
    ):
        """Test handling of vector store failures."""
        mock_vector_store.add_documents.side_effect = Exception("Vector store error")

        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="store_episodic",
            payload={
                "memory_entry": {
                    "investigation_id": "test",
                    "query": "test",
                    "result": {},
                }
            },
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.ERROR
        assert "Vector store error" in response.error or "Failed" in response.error
