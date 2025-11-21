"""
Module: agents.nana
Codinome: Nanã - Agente Temporal
Description: Agent responsible for managing episodic and semantic memory
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

from datetime import UTC, datetime, timedelta
from typing import Any, Optional

from pydantic import BaseModel
from pydantic import Field as PydanticField

from src.core import AgentStatus, MemoryImportance, json_utils
from src.core.exceptions import MemoryError, MemoryRetrievalError, MemoryStorageError

from .deodoro import AgentContext, AgentMessage, AgentResponse, BaseAgent


class MemoryEntry(BaseModel):
    """Base memory entry."""

    id: str = PydanticField(..., description="Unique memory ID")
    content: dict[str, Any] = PydanticField(..., description="Memory content")
    timestamp: datetime = PydanticField(default_factory=datetime.utcnow)
    importance: MemoryImportance = PydanticField(default=MemoryImportance.MEDIUM)
    tags: list[str] = PydanticField(default_factory=list, description="Memory tags")
    metadata: dict[str, Any] = PydanticField(default_factory=dict)


class EpisodicMemory(MemoryEntry):
    """Episodic memory entry for specific events/investigations."""

    investigation_id: str = PydanticField(..., description="Investigation ID")
    user_id: Optional[str] = PydanticField(default=None, description="User ID")
    session_id: Optional[str] = PydanticField(default=None, description="Session ID")
    query: str = PydanticField(..., description="Original query")
    result: dict[str, Any] = PydanticField(..., description="Investigation result")
    context: dict[str, Any] = PydanticField(default_factory=dict, description="Context")


class SemanticMemory(MemoryEntry):
    """Semantic memory entry for general knowledge."""

    concept: str = PydanticField(..., description="Concept or knowledge item")
    relationships: list[str] = PydanticField(
        default_factory=list, description="Related concepts"
    )
    evidence: list[str] = PydanticField(
        default_factory=list, description="Supporting evidence"
    )
    confidence: float = PydanticField(
        default=0.5, description="Confidence in this knowledge"
    )


class ConversationMemory(MemoryEntry):
    """Memory for conversation context."""

    conversation_id: str = PydanticField(..., description="Conversation ID")
    turn_number: int = PydanticField(..., description="Turn in conversation")
    speaker: str = PydanticField(..., description="Speaker (user/agent)")
    message: str = PydanticField(..., description="Message content")
    intent: Optional[str] = PydanticField(default=None, description="Detected intent")


class ContextMemoryAgent(BaseAgent):
    """
    Agent responsible for managing different types of memory:
    - Episodic: Specific investigations and their results
    - Semantic: General knowledge about patterns and anomalies
    - Conversational: Context from ongoing conversations
    """

    def __init__(
        self,
        redis_client: Any,
        vector_store: Any,
        max_episodic_memories: int = 1000,
        max_conversation_turns: int = 50,
        memory_decay_days: int = 30,
        **kwargs: Any,
    ) -> None:
        """
        Initialize context memory agent.

        Args:
            redis_client: Redis client for fast access
            vector_store: Vector store for semantic search
            max_episodic_memories: Maximum episodic memories to keep
            max_conversation_turns: Maximum conversation turns to remember
            memory_decay_days: Days after which memories start to decay
            **kwargs: Additional arguments
        """
        super().__init__(
            name="ContextMemoryAgent",
            description="Manages episodic, semantic, and conversational memory",
            capabilities=[
                "store_episodic",
                "retrieve_episodic",
                "store_semantic",
                "retrieve_semantic",
                "store_conversation",
                "get_conversation_context",
                "get_relevant_context",
                "forget_memories",
                "consolidate_memories",
            ],
            **kwargs,
        )

        self.redis_client = redis_client
        self.vector_store = vector_store
        self.max_episodic_memories = max_episodic_memories
        self.max_conversation_turns = max_conversation_turns
        self.memory_decay_days = memory_decay_days

        # Memory keys
        self.episodic_key = "cidadao:memory:episodic"
        self.semantic_key = "cidadao:memory:semantic"
        self.conversation_key = "cidadao:memory:conversation"

        self.logger.info(
            "context_memory_agent_initialized",
            max_episodic=max_episodic_memories,
            max_conversation=max_conversation_turns,
        )

    async def initialize(self) -> None:
        """Initialize memory agent."""
        self.logger.info("context_memory_agent_initializing")

        # Test Redis connection
        await self.redis_client.ping()

        # Initialize vector store if needed
        if hasattr(self.vector_store, "initialize"):
            await self.vector_store.initialize()

        self.status = AgentStatus.IDLE
        self.logger.info("context_memory_agent_initialized")

    async def shutdown(self) -> None:
        """Shutdown memory agent."""
        self.logger.info("context_memory_agent_shutting_down")

        # Close connections
        if hasattr(self.redis_client, "close"):
            await self.redis_client.close()

        if hasattr(self.vector_store, "close"):
            await self.vector_store.close()

        self.logger.info("context_memory_agent_shutdown_complete")

    async def process(
        self,
        message: AgentMessage,
        context: AgentContext,
    ) -> AgentResponse:
        """
        Process memory-related messages.

        Args:
            message: Message to process
            context: Agent context

        Returns:
            Agent response
        """
        action = message.action
        payload = message.payload

        self.logger.info(
            "memory_agent_processing",
            action=action,
            context_id=context.investigation_id,
        )

        try:
            if action == "store_episodic":
                result = await self._store_episodic_memory(payload, context)
            elif action == "retrieve_episodic":
                result = await self._retrieve_episodic_memory(payload, context)
            elif action == "store_semantic":
                result = await self._store_semantic_memory(payload, context)
            elif action == "retrieve_semantic":
                result = await self._retrieve_semantic_memory(payload, context)
            elif action == "store_conversation":
                result = await self._store_conversation_memory(payload, context)
            elif action == "get_conversation_context":
                result = await self._get_conversation_context(payload, context)
            elif action == "get_relevant_context":
                result = await self._get_relevant_context(payload, context)
            elif action == "forget_memories":
                result = await self._forget_memories(payload, context)
            elif action == "consolidate_memories":
                result = await self._consolidate_memories(payload, context)
            else:
                raise MemoryError(
                    f"Unknown action: {action}",
                    details={"action": action, "available_actions": self.capabilities},
                )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.COMPLETED,
                result=result,
                metadata={"action": action, "context_id": context.investigation_id},
            )

        except Exception as e:
            self.logger.error(
                "memory_agent_processing_failed",
                action=action,
                error=str(e),
                context_id=context.investigation_id,
            )

            return AgentResponse(
                agent_name=self.name,
                status=AgentStatus.ERROR,
                error=str(e),
                metadata={"action": action, "context_id": context.investigation_id},
            )

    async def store_investigation(
        self,
        investigation_result: Any,
        context: AgentContext,
    ) -> None:
        """
        Store investigation result in memory.

        Args:
            investigation_result: Investigation result to store
            context: Agent context
        """
        memory_entry = EpisodicMemory(
            id=f"inv_{investigation_result.investigation_id}",
            investigation_id=investigation_result.investigation_id,
            user_id=context.user_id,
            session_id=context.session_id,
            query=investigation_result.query,
            result=(
                investigation_result.model_dump()
                if hasattr(investigation_result, "model_dump")
                else investigation_result
            ),
            content={
                "type": "investigation_result",
                "query": investigation_result.query,
                "findings_count": len(investigation_result.findings),
                "confidence": investigation_result.confidence_score,
            },
            importance=self._calculate_importance(investigation_result),
            tags=self._extract_tags(investigation_result.query),
            context=context.to_dict(),
        )

        await self._store_episodic_memory(
            {"memory_entry": memory_entry.model_dump()}, context
        )

    async def get_relevant_context(
        self,
        query: str,
        context: AgentContext,
        limit: int = 5,
    ) -> dict[str, Any]:
        """
        Get relevant context for a query.

        Args:
            query: Query to find context for
            context: Agent context
            limit: Maximum number of relevant memories

        Returns:
            Relevant context
        """
        # Get episodic memories
        episodic_context = await self._retrieve_episodic_memory(
            {"query": query, "limit": limit}, context
        )

        # Get semantic memories
        semantic_context = await self._retrieve_semantic_memory(
            {"query": query, "limit": limit}, context
        )

        # Get conversation context
        conversation_context = await self._get_conversation_context(
            {"session_id": context.session_id, "limit": 10}, context
        )

        return {
            "episodic": episodic_context,
            "semantic": semantic_context,
            "conversation": conversation_context,
            "query": query,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def _store_episodic_memory(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """Store episodic memory."""
        try:
            memory_entry = payload.get("memory_entry")
            if not memory_entry:
                raise MemoryStorageError("No memory entry provided")

            # Generate ID if not present
            if "id" not in memory_entry:
                investigation_id = memory_entry.get("investigation_id", "unknown")
                memory_entry["id"] = (
                    f"mem_{investigation_id}_{int(datetime.now(UTC).timestamp())}"
                )

            # Store in Redis for fast access
            key = f"{self.episodic_key}:{memory_entry['id']}"
            ttl_seconds = int(timedelta(days=self.memory_decay_days).total_seconds())
            await self.redis_client.setex(
                key,
                ttl_seconds,
                json_utils.dumps(memory_entry),
            )

            # Store in vector store for semantic search
            # Create searchable content from memory entry
            content = memory_entry.get("content", {})
            if not content:
                # Build content from available fields for older test compatibility
                content = {
                    "query": memory_entry.get("query", ""),
                    "result": memory_entry.get("result", {}),
                    "investigation_id": memory_entry.get("investigation_id", ""),
                }

            # Always store in vector store for semantic search
            await self.vector_store.add_documents(
                [
                    {
                        "id": memory_entry["id"],
                        "content": json_utils.dumps(content),
                        "metadata": memory_entry,
                    }
                ]
            )

            # Manage memory size
            await self._manage_memory_size()

            self.logger.info(
                "episodic_memory_stored",
                memory_id=memory_entry["id"],
                importance=memory_entry.get("importance"),
            )

            return {"status": "stored", "memory_id": memory_entry["id"]}

        except Exception as e:
            raise MemoryStorageError(f"Failed to store episodic memory: {str(e)}")

    async def _retrieve_episodic_memory(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """Retrieve episodic memories."""
        try:
            query = payload.get("query", "")
            limit = payload.get("limit", 5)

            if not query:
                # Return recent memories
                memories = await self._get_recent_memories(limit)
                return {"memories": memories}

            # Semantic search using vector store
            results = await self.vector_store.similarity_search(
                query=query,
                limit=limit,
                filter_metadata={"type": "investigation_result"},
            )

            memories = []
            for result in results:
                memory_id = result.get("id")
                if memory_id:
                    memory_data = await self.redis_client.get(
                        f"{self.episodic_key}:{memory_id}"
                    )
                    if memory_data:
                        memories.append(json_utils.loads(memory_data))

            self.logger.info(
                "episodic_memories_retrieved",
                query=query,
                count=len(memories),
            )

            return {"memories": memories}

        except Exception as e:
            raise MemoryRetrievalError(f"Failed to retrieve episodic memory: {str(e)}")

    async def _store_semantic_memory(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """Store semantic memory."""
        try:
            concept = payload.get("concept", "")
            content = payload.get("content", {})

            if not concept or not content:
                raise MemoryStorageError(
                    "Concept and content required for semantic memory"
                )

            # Normalize content to dict if it's a string
            if isinstance(content, str):
                content = {"description": content}

            memory_entry = SemanticMemory(
                id=f"sem_{concept.lower().replace(' ', '_')}_{int(datetime.now(UTC).timestamp())}",
                concept=concept,
                content=content,
                relationships=payload.get("relationships", []),
                evidence=payload.get("evidence", []),
                confidence=payload.get("confidence", 0.5),
                importance=MemoryImportance.MEDIUM,
                tags=self._extract_tags(concept),
            )

            # Store in Redis
            key = f"{self.semantic_key}:{memory_entry.id}"
            ttl_seconds = int(
                timedelta(days=self.memory_decay_days * 2).total_seconds()
            )
            await self.redis_client.setex(
                key,
                ttl_seconds,
                json_utils.dumps(memory_entry.model_dump()),
            )

            # Store in vector store
            await self.vector_store.add_documents(
                [
                    {
                        "id": memory_entry.id,
                        "content": f"{concept}: {json_utils.dumps(content)}",
                        "metadata": memory_entry.model_dump(),
                    }
                ]
            )

            self.logger.info(
                "semantic_memory_stored",
                concept=concept,
                memory_id=memory_entry.id,
            )

            return {"status": "stored", "memory_id": memory_entry.id}

        except Exception as e:
            raise MemoryStorageError(f"Failed to store semantic memory: {str(e)}")

    async def _retrieve_semantic_memory(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """Retrieve semantic memories."""
        try:
            query = payload.get("query", "")
            limit = payload.get("limit", 5)

            # Semantic search
            results = await self.vector_store.similarity_search(
                query=query, limit=limit, filter_metadata={"concept": {"$exists": True}}
            )

            memories = []
            for result in results:
                memory_id = result.get("id")
                if memory_id:
                    memory_data = await self.redis_client.get(
                        f"{self.semantic_key}:{memory_id}"
                    )
                    if memory_data:
                        memories.append(json_utils.loads(memory_data))

            self.logger.info(
                "semantic_memories_retrieved",
                query=query,
                count=len(memories),
            )

            return {"concepts": memories}

        except Exception as e:
            raise MemoryRetrievalError(f"Failed to retrieve semantic memory: {str(e)}")

    async def _store_conversation_memory(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """Store conversation memory."""
        try:
            conversation_id = payload.get("conversation_id", context.session_id)
            message = payload.get("message", "")
            speaker = payload.get("speaker", "user")

            if not conversation_id or not message:
                raise MemoryStorageError("Conversation ID and message required")

            # Get current turn number
            turn_key = f"{self.conversation_key}:turns:{conversation_id}"
            turn_number = await self.redis_client.incr(turn_key)

            memory_entry = ConversationMemory(
                id=f"conv_{conversation_id}_{turn_number}",
                conversation_id=conversation_id,
                turn_number=turn_number,
                speaker=speaker,
                message=message,
                intent=payload.get("intent"),
                content={
                    "type": "conversation",
                    "speaker": speaker,
                    "message": message,
                },
                importance=MemoryImportance.LOW,
                tags=self._extract_tags(message),
            )

            # Store in Redis with conversation-specific key
            key = f"{self.conversation_key}:{conversation_id}:{turn_number}"
            ttl_seconds = int(timedelta(hours=24).total_seconds())
            await self.redis_client.setex(
                key,
                ttl_seconds,
                json_utils.dumps(memory_entry.model_dump()),
            )

            # Manage conversation size
            await self._manage_conversation_size(conversation_id)

            self.logger.info(
                "conversation_memory_stored",
                conversation_id=conversation_id,
                turn_number=turn_number,
                speaker=speaker,
            )

            return {"status": "stored", "turn_number": turn_number}

        except Exception as e:
            raise MemoryStorageError(f"Failed to store conversation memory: {str(e)}")

    async def _get_conversation_context(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """Get conversation context."""
        try:
            conversation_id = payload.get("conversation_id", context.session_id)
            limit = payload.get("limit", 10)

            if not conversation_id:
                return {"conversation": []}

            # Get recent conversation turns
            pattern = f"{self.conversation_key}:{conversation_id}:*"
            keys = await self.redis_client.keys(pattern)

            # Sort by turn number (descending)
            keys.sort(key=lambda k: int(k.split(":")[-1]), reverse=True)

            memories = []
            for key in keys[:limit]:
                memory_data = await self.redis_client.get(key)
                if memory_data:
                    memories.append(json_utils.loads(memory_data))

            # Reverse to get chronological order
            memories.reverse()

            self.logger.info(
                "conversation_context_retrieved",
                conversation_id=conversation_id,
                count=len(memories),
            )

            return {"conversation": memories}

        except Exception as e:
            raise MemoryRetrievalError(f"Failed to get conversation context: {str(e)}")

    async def _get_relevant_context(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """Get all relevant context for a query."""
        return await self.get_relevant_context(
            payload.get("query", ""), context, payload.get("limit", 5)
        )

    async def _forget_memories(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """
        Forget specific memories or old memories.

        Strategies:
        - By age: Remove memories older than specified days
        - By importance: Remove low-importance memories
        - By ID: Remove specific memory by ID
        - By pattern: Remove memories matching pattern
        """
        try:
            strategy = payload.get("strategy", "age")  # age, importance, id, pattern
            forgotten_count = 0

            if strategy == "age":
                # Remove memories older than specified days
                max_age_days = payload.get("max_age_days", self.memory_decay_days)
                cutoff_date = datetime.now(UTC) - timedelta(days=max_age_days)

                # Get all episodic memory keys
                pattern = f"{self.episodic_key}:*"
                keys = await self.redis_client.keys(pattern)

                for key in keys:
                    memory_data = await self.redis_client.get(key)
                    if memory_data:
                        memory = json_utils.loads(memory_data)
                        timestamp_str = memory.get("timestamp", datetime.now(UTC).isoformat())
                        timestamp = datetime.fromisoformat(timestamp_str)
                        # Ensure timezone-aware for comparison
                        if timestamp.tzinfo is None:
                            timestamp = timestamp.replace(tzinfo=UTC)

                        if timestamp < cutoff_date:
                            await self.redis_client.delete(key)
                            # Also remove from vector store
                            await self.vector_store.delete_documents([memory.get("id")])
                            forgotten_count += 1

            elif strategy == "importance":
                # Remove memories below importance threshold
                min_importance = payload.get("min_importance", MemoryImportance.LOW)

                pattern = f"{self.episodic_key}:*"
                keys = await self.redis_client.keys(pattern)

                for key in keys:
                    memory_data = await self.redis_client.get(key)
                    if memory_data:
                        memory = json_utils.loads(memory_data)
                        importance = MemoryImportance(
                            memory.get("importance", MemoryImportance.LOW.value)
                        )

                        # Remove if importance is below threshold
                        if importance.value < min_importance.value:
                            await self.redis_client.delete(key)
                            await self.vector_store.delete_documents([memory.get("id")])
                            forgotten_count += 1

            elif strategy == "id":
                # Remove specific memory by ID
                memory_id = payload.get("memory_id")
                if memory_id:
                    key = f"{self.episodic_key}:{memory_id}"
                    if await self.redis_client.exists(key):
                        await self.redis_client.delete(key)
                        await self.vector_store.delete_documents([memory_id])
                        forgotten_count = 1

            elif strategy == "pattern":
                # Remove memories matching content pattern
                search_pattern = payload.get("pattern", "")
                if search_pattern:
                    # Search in vector store
                    results = await self.vector_store.similarity_search(
                        query=search_pattern, limit=100
                    )

                    for result in results:
                        memory_id = result.get("id")
                        if memory_id:
                            await self.redis_client.delete(
                                f"{self.episodic_key}:{memory_id}"
                            )
                            await self.vector_store.delete_documents([memory_id])
                            forgotten_count += 1

            # Handle forget by investigation_id (special case for tests)
            investigation_id = payload.get("investigation_id")
            if investigation_id:
                pattern = f"{self.episodic_key}:*"
                keys = await self.redis_client.keys(pattern)
                for key in keys:
                    memory_data = await self.redis_client.get(key)
                    if memory_data:
                        memory = json_utils.loads(memory_data)
                        if memory.get("investigation_id") == investigation_id:
                            await self.redis_client.delete(key)
                            await self.vector_store.delete_documents([memory.get("id")])
                            forgotten_count += 1

            self.logger.info(
                "memories_forgotten", strategy=strategy, count=forgotten_count
            )

            return {
                "status": "completed",
                "deleted_count": forgotten_count,
                "strategy": strategy,
            }

        except Exception as e:
            self.logger.error(f"Failed to forget memories: {str(e)}")
            return {"status": "error", "forgotten_count": 0, "error": str(e)}

    async def _consolidate_memories(
        self,
        payload: dict[str, Any],
        context: AgentContext,
    ) -> dict[str, Any]:
        """
        Consolidate similar memories to reduce redundancy.

        Process:
        1. Find similar memories using vector similarity
        2. Merge similar memories keeping most important
        3. Update combined memory with aggregated information
        4. Remove duplicate/merged memories
        """
        try:
            similarity_threshold = payload.get("similarity_threshold", 0.85)
            consolidated_count = 0
            merged_groups = []

            # Get all episodic memories
            pattern = f"{self.episodic_key}:*"
            keys = await self.redis_client.keys(pattern)

            if len(keys) < 2:
                return {
                    "status": "completed",
                    "consolidated_count": 0,
                    "message": "Not enough memories to consolidate",
                }

            # Load all memories
            memories = []
            for key in keys:
                memory_data = await self.redis_client.get(key)
                if memory_data:
                    memories.append(json_utils.loads(memory_data))

            # Find similar memories using vector store
            processed_ids = set()

            for memory in memories:
                memory_id = memory.get("id")

                if memory_id in processed_ids:
                    continue

                # Search for similar memories
                content_str = json_utils.dumps(memory.get("content", {}))
                similar = await self.vector_store.similarity_search(
                    query=content_str,
                    limit=10,
                    similarity_threshold=similarity_threshold,
                )

                # Group similar memories (excluding self)
                similar_ids = [s.get("id") for s in similar if s.get("id") != memory_id]

                if similar_ids:
                    # Mark all as processed
                    processed_ids.add(memory_id)
                    processed_ids.update(similar_ids)

                    # Collect similar memories
                    similar_memories = [memory] + [
                        m for m in memories if m.get("id") in similar_ids
                    ]

                    # Consolidate: keep highest importance, merge content
                    consolidated = await self._merge_similar_memories(similar_memories)

                    # Store consolidated memory
                    key = f"{self.episodic_key}:{consolidated['id']}"
                    ttl_seconds = int(
                        timedelta(days=self.memory_decay_days).total_seconds()
                    )
                    await self.redis_client.setex(
                        key,
                        ttl_seconds,
                        json_utils.dumps(consolidated),
                    )

                    # Update vector store
                    await self.vector_store.add_documents(
                        [
                            {
                                "id": consolidated["id"],
                                "content": json_utils.dumps(
                                    consolidated.get("content", {})
                                ),
                                "metadata": consolidated,
                            }
                        ]
                    )

                    # Remove original memories
                    for similar_id in similar_ids:
                        await self.redis_client.delete(
                            f"{self.episodic_key}:{similar_id}"
                        )
                        await self.vector_store.delete_documents([similar_id])

                    consolidated_count += len(similar_ids)
                    merged_groups.append(
                        {
                            "consolidated_id": consolidated["id"],
                            "merged_count": len(similar_ids),
                            "merged_ids": similar_ids,
                        }
                    )

            self.logger.info(
                "memories_consolidated",
                count=consolidated_count,
                groups=len(merged_groups),
            )

            return {
                "status": "completed",
                "consolidated_count": consolidated_count,
                "merged_groups": len(merged_groups),
                "groups": merged_groups,
            }

        except Exception as e:
            self.logger.error(f"Failed to consolidate memories: {str(e)}")
            return {"status": "error", "consolidated_count": 0, "error": str(e)}

    async def _merge_similar_memories(
        self, memories: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Merge similar memories into one consolidated memory.

        Strategy:
        - Keep ID of most important memory
        - Keep highest importance level
        - Merge tags (unique union)
        - Aggregate metadata
        - Use most recent timestamp
        """
        # Sort by importance (descending)
        importance_order = {
            MemoryImportance.CRITICAL.value: 4,
            MemoryImportance.HIGH.value: 3,
            MemoryImportance.MEDIUM.value: 2,
            MemoryImportance.LOW.value: 1,
        }

        sorted_memories = sorted(
            memories,
            key=lambda m: (
                importance_order.get(
                    m.get("importance", MemoryImportance.LOW.value), 0
                ),
                m.get("timestamp", ""),
            ),
            reverse=True,
        )

        # Base: most important/recent memory
        consolidated = sorted_memories[0].copy()

        # Merge tags from all memories
        all_tags = set(consolidated.get("tags", []))
        for memory in sorted_memories[1:]:
            all_tags.update(memory.get("tags", []))

        consolidated["tags"] = list(all_tags)

        # Aggregate metadata
        consolidated["metadata"] = consolidated.get("metadata", {})
        consolidated["metadata"]["consolidated_from"] = [
            m.get("id") for m in sorted_memories
        ]
        consolidated["metadata"]["consolidated_count"] = len(sorted_memories)
        consolidated["metadata"][
            "consolidation_timestamp"
        ] = datetime.now(UTC).isoformat()

        return consolidated

    def _calculate_importance(self, investigation_result: Any) -> MemoryImportance:
        """Calculate importance of an investigation result."""
        confidence = getattr(investigation_result, "confidence_score", 0.0)
        findings_count = len(getattr(investigation_result, "findings", []))

        if confidence > 0.8 and findings_count > 3:
            return MemoryImportance.CRITICAL
        elif confidence > 0.6 and findings_count > 1:
            return MemoryImportance.HIGH
        elif confidence > 0.4:
            return MemoryImportance.MEDIUM
        else:
            return MemoryImportance.LOW

    def _extract_tags(self, text: str) -> list[str]:
        """Extract tags from text for better organization."""
        # Simple tag extraction - could be enhanced with NLP
        keywords = [
            "contrato",
            "licitação",
            "emergencial",
            "suspeito",
            "anomalia",
            "ministério",
            "prefeitura",
            "fornecedor",
            "valor",
            "preço",
        ]

        text_lower = text.lower()
        return [keyword for keyword in keywords if keyword in text_lower]

    async def _manage_memory_size(self) -> None:
        """Manage memory size by removing old/unimportant memories."""
        # Get count of episodic memories
        pattern = f"{self.episodic_key}:*"
        keys = await self.redis_client.keys(pattern)

        if len(keys) > self.max_episodic_memories:
            # Remove oldest memories first
            # In production, would consider importance scores
            keys_to_remove = keys[: -self.max_episodic_memories]
            for key in keys_to_remove:
                await self.redis_client.delete(key)

            self.logger.info(
                "episodic_memories_cleaned",
                removed_count=len(keys_to_remove),
                remaining_count=self.max_episodic_memories,
            )

    async def _manage_conversation_size(self, conversation_id: str) -> None:
        """Manage conversation memory size."""
        pattern = f"{self.conversation_key}:{conversation_id}:*"
        keys = await self.redis_client.keys(pattern)

        if len(keys) > self.max_conversation_turns:
            # Sort by turn number and keep only recent ones
            keys.sort(key=lambda k: int(k.split(":")[-1]))
            keys_to_remove = keys[: -self.max_conversation_turns]

            for key in keys_to_remove:
                await self.redis_client.delete(key)

            self.logger.info(
                "conversation_memory_cleaned",
                conversation_id=conversation_id,
                removed_count=len(keys_to_remove),
            )

    async def _get_recent_memories(self, limit: int) -> list[dict[str, Any]]:
        """Get recent episodic memories."""
        pattern = f"{self.episodic_key}:*"
        keys = await self.redis_client.keys(pattern)

        memories = []
        for key in keys[:limit]:
            memory_data = await self.redis_client.get(key)
            if memory_data:
                memories.append(json_utils.loads(memory_data))

        # Sort by timestamp (most recent first)
        memories.sort(key=lambda m: m.get("timestamp", ""), reverse=True)

        return memories[:limit]
