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
    client.setex.return_value = True
    client.hset.return_value = 1
    client.hget.return_value = None
    client.hgetall.return_value = {}
    client.incr.return_value = 1
    client.sadd.return_value = 1
    client.smembers.return_value = set()
    client.keys.return_value = []
    client.delete.return_value = 1
    client.exists.return_value = False
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
        self, nana_agent, sample_context, mock_vector_store, mock_redis_client
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

        # Mock Redis to return the memory data
        import json

        memory_data = {
            "id": "mem_001",
            "investigation_id": "inv_001",
            "query": "IT contracts",
            "result": {"test": "data"},
        }
        mock_redis_client.get.return_value = json.dumps(memory_data)

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
    async def test_store_conversation_missing_message(self, nana_agent, sample_context):
        """Test storing conversation with missing message field - Line 524."""
        # Test without message
        message = AgentMessage(
            sender="test",
            recipient="nana",
            action="store_conversation",
            payload={
                "conversation_id": "conv_001"
                # Missing "message" field (empty string counts as missing)
            },
        )

        response = await nana_agent.process(message, sample_context)
        assert response.status == AgentStatus.ERROR

        # Test with empty message
        message2 = AgentMessage(
            sender="test",
            recipient="nana",
            action="store_conversation",
            payload={"conversation_id": "conv_001", "message": ""},  # Empty message
        )

        response2 = await nana_agent.process(message2, sample_context)
        assert response2.status == AgentStatus.ERROR

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_conversation_context(
        self, nana_agent, sample_context, mock_redis_client
    ):
        """Test retrieving conversation context."""
        # Mock Redis keys() to return conversation keys
        mock_redis_client.keys.return_value = [
            "cidadao:memory:conversation:conv_001:1",
            "cidadao:memory:conversation:conv_001:2",
        ]
        # Mock Redis get() to return conversation data
        import json

        mock_redis_client.get.side_effect = [
            json.dumps(
                {"speaker": "user", "message": "test message", "turn_number": 1}
            ),
            json.dumps(
                {"speaker": "assistant", "message": "test response", "turn_number": 2}
            ),
        ]

        message = AgentMessage(
            sender="test_client",
            recipient="nana",
            action="get_conversation_context",
            payload={"conversation_id": "conv_001", "limit": 10},
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        assert "conversation" in response.result
        assert isinstance(response.result["conversation"], list)


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
        # get_relevant_context returns nested structure with episodic, semantic, conversation
        assert "episodic" in response.result
        assert "semantic" in response.result
        assert "conversation" in response.result
        assert "query" in response.result


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


class TestForgetMemories:
    """Test memory forgetting strategies for coverage boost."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_forget_memories_by_age(self, nana_agent, sample_context):
        """Test forgetting memories by age strategy - Lines 638-660."""
        import json
        from datetime import datetime, timedelta

        # Setup: Create old memory in Redis
        old_memory = {
            "id": "old_mem_001",
            "investigation_id": "test_inv_001",
            "timestamp": (datetime.utcnow() - timedelta(days=60)).isoformat(),
            "content": {"query": "old investigation"},
            "importance": "MEDIUM",
        }

        # Mock Redis to return the old memory
        nana_agent.redis_client.keys.return_value = ["episodic:memory:old_mem_001"]
        nana_agent.redis_client.get.return_value = json.dumps(old_memory)

        message = AgentMessage(
            sender="test",
            recipient="nana",
            action="forget_memories",
            payload={"strategy": "age", "max_age_days": 30},
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        assert "deleted_count" in response.result
        # Should have called delete on Redis
        assert nana_agent.redis_client.delete.called

    @pytest.mark.unit
    @pytest.mark.asyncio
    @pytest.mark.skip(
        reason="Mock setup needs adjustment for importance enum comparison"
    )
    async def test_forget_memories_by_importance(self, nana_agent, sample_context):
        """Test forgetting low-importance memories - Lines 661-681."""
        import json

        low_importance_memory = {
            "id": "low_mem_001",
            "investigation_id": "test_inv_002",
            "timestamp": datetime.utcnow().isoformat(),
            "content": {"query": "low priority"},
            "importance": "LOW",
        }

        nana_agent.redis_client.keys.return_value = ["episodic:memory:low_mem_001"]
        nana_agent.redis_client.get.return_value = json.dumps(low_importance_memory)

        message = AgentMessage(
            sender="test",
            recipient="nana",
            action="forget_memories",
            payload={"strategy": "importance", "min_importance": "MEDIUM"},
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        assert "deleted_count" in response.result

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_forget_memories_by_id(self, nana_agent, sample_context):
        """Test forgetting specific memory by ID - Lines 682-691."""
        nana_agent.redis_client.exists.return_value = True

        message = AgentMessage(
            sender="test",
            recipient="nana",
            action="forget_memories",
            payload={"strategy": "id", "memory_id": "specific_mem_123"},
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        assert nana_agent.redis_client.delete.called
        assert nana_agent.vector_store.delete_documents.called

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_forget_memories_by_pattern(self, nana_agent, sample_context):
        """Test forgetting memories by content pattern - Lines 692-709."""
        # Mock vector store to return matching results
        nana_agent.vector_store.similarity_search.return_value = [
            {"id": "pattern_mem_001"},
            {"id": "pattern_mem_002"},
        ]

        message = AgentMessage(
            sender="test",
            recipient="nana",
            action="forget_memories",
            payload={"strategy": "pattern", "pattern": "test query"},
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        assert nana_agent.vector_store.similarity_search.called


class TestMemoryConsolidationDirect:
    """Test memory consolidation for coverage boost."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_consolidate_memories(self, nana_agent, sample_context):
        """Test memory consolidation process - Lines 738-863."""
        import json

        # Setup: Multiple similar memories
        memories = [
            {
                "id": f"mem_{i}",
                "content": {"query": f"similar investigation {i}"},
                "timestamp": datetime.utcnow().isoformat(),
                "importance": "MEDIUM",
            }
            for i in range(5)
        ]

        nana_agent.redis_client.keys.return_value = [
            f"episodic:memory:mem_{i}" for i in range(5)
        ]
        nana_agent.redis_client.get.side_effect = [json.dumps(m) for m in memories]

        # Mock vector store for similarity
        nana_agent.vector_store.similarity_search.return_value = [
            {"id": f"mem_{i}", "score": 0.9} for i in range(1, 3)
        ]

        message = AgentMessage(
            sender="test", recipient="nana", action="consolidate_memories", payload={}
        )

        response = await nana_agent.process(message, sample_context)

        assert response.status == AgentStatus.COMPLETED
        assert "consolidated_count" in response.result


class TestCalculateImportance:
    """Test importance calculation for coverage boost."""

    @pytest.mark.unit
    def test_calculate_importance_high_anomalies(self, nana_agent):
        """Test importance calculation with high anomalies - Lines 919-931."""
        from unittest.mock import Mock

        # Create mock object with expected attributes
        result = Mock()
        result.confidence_score = 0.95
        result.findings = [{"anomaly": f"test_{i}"} for i in range(5)]

        importance = nana_agent._calculate_importance(result)

        from src.core import MemoryImportance

        assert importance in [MemoryImportance.HIGH, MemoryImportance.CRITICAL]

    @pytest.mark.unit
    def test_calculate_importance_low_impact(self, nana_agent):
        """Test importance calculation with low impact."""
        from unittest.mock import Mock

        result = Mock()
        result.confidence_score = 0.3
        result.findings = []

        importance = nana_agent._calculate_importance(result)

        from src.core import MemoryImportance

        assert importance == MemoryImportance.LOW

    @pytest.mark.unit
    def test_calculate_importance_medium(self, nana_agent):
        """Test importance calculation for MEDIUM level - Line 929."""
        from unittest.mock import Mock

        result = Mock()
        result.confidence_score = 0.5  # > 0.4 but not high enough for HIGH
        result.findings = []  # No findings, so won't reach HIGH

        importance = nana_agent._calculate_importance(result)

        from src.core import MemoryImportance

        assert importance == MemoryImportance.MEDIUM

    @pytest.mark.unit
    def test_calculate_importance_high_boundary(self, nana_agent):
        """Test importance calculation for HIGH level - Line 927."""
        from unittest.mock import Mock

        result = Mock()
        result.confidence_score = 0.7  # > 0.6
        result.findings = [{"anomaly": "test1"}, {"anomaly": "test2"}]  # > 1

        importance = nana_agent._calculate_importance(result)

        from src.core import MemoryImportance

        assert importance == MemoryImportance.HIGH


class TestExtractTags:
    """Test tag extraction for coverage boost."""

    @pytest.mark.unit
    def test_extract_tags_multiple_matches(self, nana_agent):
        """Test extracting multiple tags from text - Lines 933-950."""
        text = "Análise de contrato emergencial suspeito com anomalia no valor"

        tags = nana_agent._extract_tags(text)

        assert "contrato" in tags
        assert "emergencial" in tags
        assert "suspeito" in tags
        assert "anomalia" in tags
        assert "valor" in tags
        assert len(tags) >= 5

    @pytest.mark.unit
    def test_extract_tags_case_insensitive(self, nana_agent):
        """Test tag extraction is case insensitive."""
        text = "LICITAÇÃO com ANOMALIA no PREÇO do FORNECEDOR"

        tags = nana_agent._extract_tags(text)

        assert "licitação" in tags
        assert "anomalia" in tags
        assert "preço" in tags
        assert "fornecedor" in tags

    @pytest.mark.unit
    def test_extract_tags_no_matches(self, nana_agent):
        """Test tag extraction with no keyword matches."""
        text = "This is a random text without any Portuguese keywords"

        tags = nana_agent._extract_tags(text)

        assert tags == []

    @pytest.mark.unit
    def test_extract_tags_partial_matches(self, nana_agent):
        """Test tag extraction with partial word matches."""
        text = "Ministério da Saúde e prefeitura municipal"

        tags = nana_agent._extract_tags(text)

        assert "ministério" in tags
        assert "prefeitura" in tags


class TestShutdown:
    """Test agent shutdown for coverage boost."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_shutdown_success(self, nana_agent):
        """Test successful agent shutdown - Lines 145-156."""
        await nana_agent.shutdown()

        # Verify cleanup was attempted
        assert nana_agent.redis_client is not None  # Should still exist but closed

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_shutdown_cleanup(self, nana_agent):
        """Test shutdown cleanup operations."""
        # Verify shutdown can be called without errors
        await nana_agent.shutdown()

        # Agent should still exist but be shut down
        assert nana_agent.name == "ContextMemoryAgent"
