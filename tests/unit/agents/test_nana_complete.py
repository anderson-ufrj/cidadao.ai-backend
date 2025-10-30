"""
Additional comprehensive tests for Nanã to achieve 80%+ coverage.
Tests store_investigation, edge cases, and error paths.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio

from src.agents.deodoro import AgentContext
from src.agents.nana import ContextMemoryAgent


@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    client = AsyncMock()
    client.ping = AsyncMock(return_value=True)
    client.get = AsyncMock(return_value=None)
    client.setex = AsyncMock(return_value=True)
    client.keys = AsyncMock(return_value=[])
    client.delete = AsyncMock(return_value=1)
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_vector_store():
    """Mock vector store."""
    store = AsyncMock()
    store.initialize = AsyncMock()
    store.add_documents = AsyncMock()
    store.similarity_search = AsyncMock(return_value=[])
    store.delete_documents = AsyncMock()
    store.close = AsyncMock()
    return store


@pytest_asyncio.fixture
async def nana_agent(mock_redis_client, mock_vector_store):
    """Create Nanã agent."""
    agent = ContextMemoryAgent(
        redis_client=mock_redis_client,
        vector_store=mock_vector_store,
    )
    await agent.initialize()
    return agent


@pytest.fixture
def sample_context():
    """Sample context."""
    return AgentContext(
        investigation_id="test_001",
        user_id="user_123",
        session_id="session_456",
    )


@pytest.fixture
def sample_investigation_result():
    """Sample investigation result."""
    result = MagicMock()
    result.investigation_id = "inv_001"
    result.query = "Test query"
    result.findings = [{"type": "anomaly", "score": 0.9}]
    result.confidence_score = 0.85
    result.model_dump = MagicMock(
        return_value={
            "investigation_id": "inv_001",
            "query": "Test query",
            "findings": [{"type": "anomaly"}],
            "confidence_score": 0.85,
        }
    )
    return result


@pytest.mark.unit
class TestNanaCompleteCoverage:
    """Test suite for complete Nanã coverage."""

    @pytest.mark.asyncio
    async def test_store_investigation(
        self, nana_agent, sample_context, sample_investigation_result
    ):
        """Test storing investigation result in memory."""
        await nana_agent.store_investigation(
            sample_investigation_result, sample_context
        )

        # Verify Redis was called
        nana_agent.redis_client.setex.assert_called_once()

        # Verify vector store was called
        nana_agent.vector_store.add_documents.assert_called_once()

    @pytest.mark.asyncio
    async def test_initialize_with_vector_store_initialize(
        self, mock_redis_client, mock_vector_store
    ):
        """Test initialization when vector store has initialize method."""
        agent = ContextMemoryAgent(
            redis_client=mock_redis_client,
            vector_store=mock_vector_store,
        )

        await agent.initialize()

        mock_vector_store.initialize.assert_called_once()
        assert agent.status.value == "idle"

    @pytest.mark.asyncio
    async def test_shutdown_with_close_methods(
        self, mock_redis_client, mock_vector_store
    ):
        """Test shutdown calls close methods."""
        agent = ContextMemoryAgent(
            redis_client=mock_redis_client,
            vector_store=mock_vector_store,
        )
        await agent.initialize()

        await agent.shutdown()

        mock_redis_client.close.assert_called_once()
        mock_vector_store.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_episodic_memory_without_content(
        self, nana_agent, sample_context
    ):
        """Test storing episodic memory without content field (backward compatibility)."""
        # Memory entry without content field
        memory_entry = {
            "id": "test_memory_001",
            "investigation_id": "inv_001",
            "query": "Test query",
            "result": {"findings": []},
        }

        result = await nana_agent._store_episodic_memory(
            {"memory_entry": memory_entry}, sample_context
        )

        assert result["status"] == "stored"
        # Should build content from available fields
        nana_agent.vector_store.add_documents.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_episodic_memory_without_query(
        self, nana_agent, sample_context
    ):
        """Test retrieving episodic memories without query (recent memories)."""
        # Mock get_recent_memories to return some data
        nana_agent._get_recent_memories = AsyncMock(
            return_value=[{"id": "mem_1", "query": "old query"}]
        )

        result = await nana_agent._retrieve_episodic_memory({}, sample_context)

        assert "memories" in result
        nana_agent._get_recent_memories.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_episodic_memory_with_missing_redis_data(
        self, nana_agent, sample_context
    ):
        """Test retrieving memories when Redis data is missing."""
        # Mock vector store to return results
        nana_agent.vector_store.similarity_search = AsyncMock(
            return_value=[
                {"id": "mem_001", "content": "test"},
                {"id": "mem_002", "content": "test2"},
            ]
        )

        # Mock Redis to return None (missing data)
        nana_agent.redis_client.get = AsyncMock(return_value=None)

        result = await nana_agent._retrieve_episodic_memory(
            {"query": "test query", "limit": 5}, sample_context
        )

        # Should return empty or partial results
        assert "memories" in result

    @pytest.mark.asyncio
    async def test_calculate_importance(self, nana_agent, sample_investigation_result):
        """Test importance calculation."""
        importance = nana_agent._calculate_importance(sample_investigation_result)

        # Should return a MemoryImportance enum value
        assert importance is not None

    @pytest.mark.asyncio
    async def test_extract_tags(self, nana_agent):
        """Test tag extraction from query."""
        # Use keywords that actually match the extraction logic
        query = "Analisar contratos suspeitos com anomalias de licitação emergencial"

        tags = nana_agent._extract_tags(query)

        assert isinstance(tags, list)
        # Should extract keywords like "contrato", "suspeito", "anomalia", "licitação", "emergencial"
        assert len(tags) >= 3

    @pytest.mark.asyncio
    async def test_store_episodic_memory_without_id(self, nana_agent, sample_context):
        """Test storing memory generates ID if not present."""
        memory_entry = {
            "investigation_id": "inv_003",
            "query": "Test",
            "content": {"test": "data"},
        }

        result = await nana_agent._store_episodic_memory(
            {"memory_entry": memory_entry}, sample_context
        )

        assert result["status"] == "stored"
        assert "memory_id" in result
        # ID should be generated
        assert result["memory_id"].startswith("mem_")

    @pytest.mark.asyncio
    async def test_get_relevant_context_integration(self, nana_agent, sample_context):
        """Test get_relevant_context integrates all memory types."""
        # Mock the retrieval methods
        nana_agent._retrieve_episodic_memory = AsyncMock(
            return_value={"memories": [{"query": "old query"}]}
        )
        nana_agent._retrieve_semantic_memory = AsyncMock(
            return_value={"concepts": ["concept1"]}
        )
        nana_agent._get_conversation_context = AsyncMock(
            return_value={"turns": [{"message": "hello"}]}
        )

        result = await nana_agent.get_relevant_context(
            "test query", sample_context, limit=5
        )

        assert "episodic" in result
        assert "semantic" in result
        assert "conversation" in result
        assert "query" in result
        assert result["query"] == "test query"

    @pytest.mark.asyncio
    async def test_forget_memories_by_importance(self, nana_agent, sample_context):
        """Test forgetting memories by importance level."""
        import json

        from src.core import MemoryImportance

        # Mock Redis keys (return as bytes)
        nana_agent.redis_client.keys = AsyncMock(
            return_value=[
                b"cidadao:memory:episodic:mem_001",
                b"cidadao:memory:episodic:mem_002",
            ]
        )

        # Mock get to return memory data (as JSON string)
        nana_agent.redis_client.get = AsyncMock(
            side_effect=[
                json.dumps({"id": "mem_001", "importance": "LOW"}),
                json.dumps({"id": "mem_002", "importance": "HIGH"}),
            ]
        )

        result = await nana_agent._forget_memories(
            {"importance_threshold": MemoryImportance.MEDIUM.value}, sample_context
        )

        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_consolidate_memories_with_patterns(self, nana_agent, sample_context):
        """Test memory consolidation identifies patterns."""
        import json

        # Mock episodic memories with similar patterns
        nana_agent.redis_client.keys = AsyncMock(
            return_value=[
                b"cidadao:memory:episodic:mem_001",
                b"cidadao:memory:episodic:mem_002",
                b"cidadao:memory:episodic:mem_003",
            ]
        )

        # Mock get to return similar memories (as JSON string)
        nana_agent.redis_client.get = AsyncMock(
            side_effect=[
                json.dumps(
                    {
                        "id": "mem_001",
                        "query": "contract anomaly",
                        "content": {"findings_count": 5},
                    }
                ),
                json.dumps(
                    {
                        "id": "mem_002",
                        "query": "contract anomaly",
                        "content": {"findings_count": 3},
                    }
                ),
                json.dumps(
                    {
                        "id": "mem_003",
                        "query": "contract anomaly",
                        "content": {"findings_count": 7},
                    }
                ),
            ]
        )

        result = await nana_agent._consolidate_memories({}, sample_context)

        assert result["status"] == "completed"
        # Check the actual fields returned by the method
        assert "consolidated_count" in result
        assert "merged_groups" in result
        assert "groups" in result
