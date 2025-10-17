"""Unit tests for memory system components."""

from datetime import datetime, timedelta

import numpy as np
import pytest

from src.memory.base import ImportanceCalculator, MemoryEntry
from src.memory.conversational import (
    ConversationalMemory,
    DialogTurn,
    IntentMemory,
)
from src.memory.episodic import (
    Episode,
    EpisodeType,
    EpisodicMemory,
    MemoryConsolidation,
)
from src.memory.semantic import Concept, ConceptRelation, KnowledgeGraph, SemanticMemory


class TestMemoryEntry:
    """Test base memory entry."""

    def test_memory_entry_creation(self):
        """Test creating memory entry."""
        entry = MemoryEntry(
            id="mem_123",
            content={"data": "test memory"},
            timestamp=datetime.now(),
            importance=0.8,
            access_count=0,
        )

        assert entry.id == "mem_123"
        assert entry.content["data"] == "test memory"
        assert entry.importance == 0.8
        assert entry.access_count == 0

    def test_memory_entry_decay(self):
        """Test memory importance decay over time."""
        # Create old memory
        old_timestamp = datetime.now() - timedelta(days=7)
        entry = MemoryEntry(
            id="old_mem", content="old data", timestamp=old_timestamp, importance=1.0
        )

        # Calculate decayed importance
        decayed = entry.get_decayed_importance(decay_rate=0.1)

        # Should be less than original
        assert decayed < 1.0
        assert decayed > 0.0

    def test_memory_entry_access_tracking(self):
        """Test memory access tracking."""
        entry = MemoryEntry(id="tracked_mem", content="data", importance=0.5)

        # Track accesses
        entry.record_access()
        entry.record_access()
        entry.record_access()

        assert entry.access_count == 3
        assert entry.last_accessed is not None


class TestImportanceCalculator:
    """Test importance calculation strategies."""

    def test_recency_importance(self):
        """Test recency-based importance."""
        calculator = ImportanceCalculator(strategy="recency")

        # Recent memory should have high importance
        recent = datetime.now() - timedelta(minutes=10)
        importance = calculator.calculate(
            content="recent data", metadata={"timestamp": recent}
        )
        assert importance > 0.8

        # Old memory should have lower importance
        old = datetime.now() - timedelta(days=30)
        importance = calculator.calculate(
            content="old data", metadata={"timestamp": old}
        )
        assert importance < 0.3

    def test_frequency_importance(self):
        """Test frequency-based importance."""
        calculator = ImportanceCalculator(strategy="frequency")

        # High access count = high importance
        importance = calculator.calculate(
            content="popular data", metadata={"access_count": 100}
        )
        assert importance > 0.7

        # Low access count = low importance
        importance = calculator.calculate(
            content="unpopular data", metadata={"access_count": 1}
        )
        assert importance < 0.3

    def test_combined_importance(self):
        """Test combined importance calculation."""
        calculator = ImportanceCalculator(strategy="combined")

        # Recent and frequently accessed
        importance = calculator.calculate(
            content="important data",
            metadata={
                "timestamp": datetime.now() - timedelta(hours=1),
                "access_count": 50,
                "user_rating": 0.9,
            },
        )
        assert importance > 0.8


class TestEpisodicMemory:
    """Test episodic memory system."""

    @pytest.fixture
    def episodic_memory(self):
        """Create episodic memory instance."""
        return EpisodicMemory(max_episodes=100)

    @pytest.mark.asyncio
    async def test_store_episode(self, episodic_memory):
        """Test storing investigation episode."""
        episode = Episode(
            id="ep_123",
            type=EpisodeType.INVESTIGATION,
            content={
                "investigation_id": "inv_456",
                "anomalies_found": 5,
                "confidence": 0.85,
            },
            participants=["zumbi", "anita"],
            outcome="success",
        )

        await episodic_memory.store_episode(episode)

        # Retrieve episode
        retrieved = await episodic_memory.get_episode("ep_123")
        assert retrieved is not None
        assert retrieved.content["anomalies_found"] == 5
        assert "zumbi" in retrieved.participants

    @pytest.mark.asyncio
    async def test_retrieve_similar_episodes(self, episodic_memory):
        """Test retrieving similar episodes."""
        # Store multiple episodes
        episodes = [
            Episode(
                id=f"ep_{i}",
                type=EpisodeType.INVESTIGATION,
                content={
                    "target_entity": "Ministry of Health",
                    "anomaly_type": "price" if i % 2 == 0 else "vendor",
                    "severity": 0.7 + (i * 0.05),
                },
            )
            for i in range(5)
        ]

        for episode in episodes:
            await episodic_memory.store_episode(episode)

        # Query similar episodes
        query = {"target_entity": "Ministry of Health", "anomaly_type": "price"}

        similar = await episodic_memory.retrieve_similar(query, top_k=3)

        assert len(similar) <= 3
        # Should prioritize episodes with price anomalies
        assert all(
            ep.content.get("anomaly_type") == "price"
            for ep in similar[:2]
            if "anomaly_type" in ep.content
        )

    @pytest.mark.asyncio
    async def test_episode_consolidation(self, episodic_memory):
        """Test episode consolidation process."""
        # Create related episodes
        episodes = []
        base_time = datetime.now() - timedelta(days=7)

        for i in range(10):
            episode = Episode(
                id=f"consolidate_{i}",
                type=EpisodeType.INVESTIGATION,
                content={
                    "entity": "Entity_A",
                    "pattern": "suspicious_spending",
                    "value": 100000 + (i * 10000),
                },
                timestamp=base_time + timedelta(hours=i),
            )
            episodes.append(episode)
            await episodic_memory.store_episode(episode)

        # Consolidate episodes
        consolidator = MemoryConsolidation()
        consolidated = await consolidator.consolidate_episodes(episodes)

        assert consolidated is not None
        assert consolidated.type == EpisodeType.PATTERN
        assert "Entity_A" in consolidated.content.get("entities", [])
        assert consolidated.content.get("pattern_type") == "suspicious_spending"

    @pytest.mark.asyncio
    async def test_episode_temporal_retrieval(self, episodic_memory):
        """Test temporal-based episode retrieval."""
        # Store episodes at different times
        now = datetime.now()
        time_points = [
            now - timedelta(days=30),  # Old
            now - timedelta(days=7),  # Week ago
            now - timedelta(days=1),  # Yesterday
            now - timedelta(hours=1),  # Recent
        ]

        for i, timestamp in enumerate(time_points):
            episode = Episode(
                id=f"temporal_{i}",
                type=EpisodeType.ANALYSIS,
                content={"data": f"event_{i}"},
                timestamp=timestamp,
            )
            await episodic_memory.store_episode(episode)

        # Retrieve recent episodes
        recent = await episodic_memory.get_recent_episodes(days=3)

        assert len(recent) == 2  # Yesterday and 1 hour ago
        assert all(ep.id in ["temporal_2", "temporal_3"] for ep in recent)


class TestSemanticMemory:
    """Test semantic memory and knowledge graph."""

    @pytest.fixture
    def semantic_memory(self):
        """Create semantic memory instance."""
        return SemanticMemory()

    @pytest.mark.asyncio
    async def test_store_concept(self, semantic_memory):
        """Test storing concepts in semantic memory."""
        concept = Concept(
            id="concept_price_anomaly",
            name="Price Anomaly",
            category="anomaly_type",
            properties={
                "detection_method": "statistical",
                "severity_range": [0.5, 1.0],
                "common_causes": ["overpricing", "emergency_purchase"],
            },
            embeddings=np.random.rand(384).tolist(),  # Mock embedding
        )

        await semantic_memory.store_concept(concept)

        # Retrieve concept
        retrieved = await semantic_memory.get_concept("concept_price_anomaly")
        assert retrieved is not None
        assert retrieved.name == "Price Anomaly"
        assert "statistical" in retrieved.properties["detection_method"]

    @pytest.mark.asyncio
    async def test_concept_relations(self, semantic_memory):
        """Test concept relationships in knowledge graph."""
        # Create related concepts
        anomaly = Concept(id="anomaly", name="Anomaly", category="root")
        price_anomaly = Concept(
            id="price_anomaly", name="Price Anomaly", category="anomaly_type"
        )
        overpricing = Concept(
            id="overpricing", name="Overpricing", category="anomaly_subtype"
        )

        # Store concepts
        for concept in [anomaly, price_anomaly, overpricing]:
            await semantic_memory.store_concept(concept)

        # Create relations
        relations = [
            ConceptRelation(
                source_id="anomaly",
                target_id="price_anomaly",
                relation_type="has_subtype",
                strength=1.0,
            ),
            ConceptRelation(
                source_id="price_anomaly",
                target_id="overpricing",
                relation_type="includes",
                strength=0.9,
            ),
        ]

        for relation in relations:
            await semantic_memory.add_relation(relation)

        # Query related concepts
        related = await semantic_memory.get_related_concepts(
            "anomaly", relation_type="has_subtype"
        )

        assert len(related) >= 1
        assert any(c.id == "price_anomaly" for c in related)

    @pytest.mark.asyncio
    async def test_semantic_search(self, semantic_memory):
        """Test semantic similarity search."""
        # Create concepts with embeddings
        concepts = [
            Concept(
                id=f"concept_{i}",
                name=f"Concept {i}",
                category="test",
                embeddings=np.random.rand(384).tolist(),
            )
            for i in range(5)
        ]

        for concept in concepts:
            await semantic_memory.store_concept(concept)

        # Search with query embedding
        query_embedding = np.random.rand(384).tolist()
        similar = await semantic_memory.search_similar(query_embedding, top_k=3)

        assert len(similar) <= 3
        assert all(isinstance(c, Concept) for c in similar)

    @pytest.mark.asyncio
    async def test_knowledge_graph_traversal(self, semantic_memory):
        """Test knowledge graph traversal."""
        # Build a simple knowledge graph
        kg = KnowledgeGraph()

        # Add nodes
        nodes = ["government", "ministry", "health_ministry", "contracts"]
        for node in nodes:
            kg.add_node(node, {"type": "entity"})

        # Add edges
        kg.add_edge("government", "ministry", "contains")
        kg.add_edge("ministry", "health_ministry", "instance_of")
        kg.add_edge("health_ministry", "contracts", "manages")

        # Find path
        path = kg.find_path("government", "contracts")

        assert path is not None
        assert len(path) == 4  # government -> ministry -> health_ministry -> contracts


class TestConversationalMemory:
    """Test conversational memory system."""

    @pytest.fixture
    def conv_memory(self):
        """Create conversational memory instance."""
        return ConversationalMemory(max_turns=50)

    @pytest.mark.asyncio
    async def test_store_dialog_turn(self, conv_memory):
        """Test storing dialog turns."""
        turn = DialogTurn(
            id="turn_1",
            conversation_id="conv_123",
            speaker="user",
            utterance="Find anomalies in health ministry contracts",
            intent="investigate_anomalies",
            entities=["health_ministry", "contracts"],
        )

        await conv_memory.add_turn(turn)

        # Retrieve conversation
        conversation = await conv_memory.get_conversation("conv_123")
        assert len(conversation) == 1
        assert conversation[0].speaker == "user"
        assert "health_ministry" in conversation[0].entities

    @pytest.mark.asyncio
    async def test_conversation_context(self, conv_memory):
        """Test maintaining conversation context."""
        conv_id = "context_test"

        # Multi-turn conversation
        turns = [
            DialogTurn(
                id="t1",
                conversation_id=conv_id,
                speaker="user",
                utterance="Analyze ministry of health",
                entities=["ministry_of_health"],
            ),
            DialogTurn(
                id="t2",
                conversation_id=conv_id,
                speaker="agent",
                utterance="Found 5 anomalies in contracts",
                entities=["anomalies", "contracts"],
            ),
            DialogTurn(
                id="t3",
                conversation_id=conv_id,
                speaker="user",
                utterance="Show me the price anomalies",
                intent="filter_results",
                entities=["price_anomalies"],
            ),
        ]

        for turn in turns:
            await conv_memory.add_turn(turn)

        # Get context
        context = await conv_memory.get_context(conv_id)

        assert context is not None
        assert len(context.entities) >= 3
        assert "ministry_of_health" in context.entities
        assert context.current_topic is not None

    @pytest.mark.asyncio
    async def test_intent_memory(self, conv_memory):
        """Test intent pattern memory."""
        # Store intent patterns
        intents = [
            ("Find anomalies in {entity}", "investigate_anomalies"),
            ("Show me {anomaly_type} anomalies", "filter_anomalies"),
            ("Generate report for {investigation}", "generate_report"),
        ]

        intent_memory = IntentMemory()
        for pattern, intent in intents:
            await intent_memory.store_pattern(pattern, intent)

        # Match new utterance
        utterance = "Find anomalies in education ministry"
        matched_intent = await intent_memory.match_intent(utterance)

        assert matched_intent is not None
        assert matched_intent["intent"] == "investigate_anomalies"
        assert matched_intent["entities"]["entity"] == "education ministry"

    @pytest.mark.asyncio
    async def test_conversation_summarization(self, conv_memory):
        """Test conversation summarization."""
        conv_id = "long_conv"

        # Create long conversation
        for i in range(20):
            turn = DialogTurn(
                id=f"turn_{i}",
                conversation_id=conv_id,
                speaker="user" if i % 2 == 0 else "agent",
                utterance=f"Message {i} about topic {i // 5}",
            )
            await conv_memory.add_turn(turn)

        # Summarize conversation
        summary = await conv_memory.summarize_conversation(conv_id)

        assert summary is not None
        assert "topics" in summary
        assert "key_points" in summary
        assert len(summary["key_points"]) < 20  # Condensed


class TestMemoryIntegration:
    """Test integration between memory systems."""

    @pytest.mark.asyncio
    async def test_episodic_to_semantic_transfer(self):
        """Test transferring episodic memories to semantic knowledge."""
        episodic = EpisodicMemory()
        semantic = SemanticMemory()

        # Create multiple similar episodes
        for i in range(10):
            episode = Episode(
                id=f"pattern_{i}",
                type=EpisodeType.INVESTIGATION,
                content={
                    "entity": "Ministry X",
                    "pattern": "end_of_year_spending_spike",
                    "severity": 0.8 + (i * 0.01),
                },
            )
            await episodic.store_episode(episode)

        # Consolidate into semantic knowledge
        pattern_concept = Concept(
            id="end_year_spike",
            name="End of Year Spending Spike",
            category="spending_pattern",
            properties={
                "frequency": "annual",
                "typical_months": [11, 12],
                "average_severity": 0.85,
            },
        )

        await semantic.store_concept(pattern_concept)

        # Verify knowledge transfer
        retrieved = await semantic.get_concept("end_year_spike")
        assert retrieved is not None
        assert retrieved.properties["frequency"] == "annual"

    @pytest.mark.asyncio
    async def test_memory_cross_referencing(self):
        """Test cross-referencing between memory types."""
        episodic = EpisodicMemory()
        semantic = SemanticMemory()
        conversational = ConversationalMemory()

        # Create related memories
        episode = Episode(
            id="cross_ref_ep",
            type=EpisodeType.DISCOVERY,
            content={
                "discovery": "New fraud pattern",
                "concept_id": "fraud_pattern_123",
            },
        )

        concept = Concept(
            id="fraud_pattern_123",
            name="Invoice Splitting Fraud",
            category="fraud_type",
        )

        turn = DialogTurn(
            id="turn_cross",
            conversation_id="conv_cross",
            speaker="agent",
            utterance="Discovered new invoice splitting fraud pattern",
            entities=["fraud_pattern_123"],
        )

        # Store all
        await episodic.store_episode(episode)
        await semantic.store_concept(concept)
        await conversational.add_turn(turn)

        # Cross-reference
        episode_ref = await episodic.get_episode("cross_ref_ep")
        concept_ref = await semantic.get_concept(episode_ref.content["concept_id"])

        assert concept_ref is not None
        assert concept_ref.name == "Invoice Splitting Fraud"
