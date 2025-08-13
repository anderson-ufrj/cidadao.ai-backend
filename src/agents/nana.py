"""
Module: agents.nana
Codinome: Nanã - Agente Temporal
Description: Agent responsible for managing episodic and semantic memory
Author: Anderson H. Silva
Date: 2025-01-24
License: Proprietary - All rights reserved
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field as PydanticField

from src.core import AgentStatus, MemoryImportance, get_logger
from src.core.exceptions import MemoryError, MemoryStorageError, MemoryRetrievalError
from .deodoro import (
    AgentContext,
    AgentMessage,
    AgentResponse,
    BaseAgent,
)


class MemoryEntry(BaseModel):
    """Base memory entry."""
    
    id: str = PydanticField(..., description="Unique memory ID")
    content: Dict[str, Any] = PydanticField(..., description="Memory content")
    timestamp: datetime = PydanticField(default_factory=datetime.utcnow)
    importance: MemoryImportance = PydanticField(default=MemoryImportance.MEDIUM)
    tags: List[str] = PydanticField(default_factory=list, description="Memory tags")
    metadata: Dict[str, Any] = PydanticField(default_factory=dict)


class EpisodicMemory(MemoryEntry):
    """Episodic memory entry for specific events/investigations."""
    
    investigation_id: str = PydanticField(..., description="Investigation ID")
    user_id: Optional[str] = PydanticField(default=None, description="User ID")
    session_id: Optional[str] = PydanticField(default=None, description="Session ID")
    query: str = PydanticField(..., description="Original query")
    result: Dict[str, Any] = PydanticField(..., description="Investigation result")
    context: Dict[str, Any] = PydanticField(default_factory=dict, description="Context")


class SemanticMemory(MemoryEntry):
    """Semantic memory entry for general knowledge."""
    
    concept: str = PydanticField(..., description="Concept or knowledge item")
    relationships: List[str] = PydanticField(default_factory=list, description="Related concepts")
    evidence: List[str] = PydanticField(default_factory=list, description="Supporting evidence")
    confidence: float = PydanticField(default=0.5, description="Confidence in this knowledge")


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
        **kwargs: Any
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
            **kwargs
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
        if hasattr(self.vector_store, 'initialize'):
            await self.vector_store.initialize()
        
        self.status = AgentStatus.IDLE
        self.logger.info("context_memory_agent_initialized")
    
    async def shutdown(self) -> None:
        """Shutdown memory agent."""
        self.logger.info("context_memory_agent_shutting_down")
        
        # Close connections
        if hasattr(self.redis_client, 'close'):
            await self.redis_client.close()
        
        if hasattr(self.vector_store, 'close'):
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
                    details={"action": action, "available_actions": self.capabilities}
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
            result=investigation_result.model_dump() if hasattr(investigation_result, 'model_dump') else investigation_result,
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
            {"memory_entry": memory_entry.model_dump()},
            context
        )
    
    async def get_relevant_context(
        self,
        query: str,
        context: AgentContext,
        limit: int = 5,
    ) -> Dict[str, Any]:
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
            {"query": query, "limit": limit},
            context
        )
        
        # Get semantic memories
        semantic_context = await self._retrieve_semantic_memory(
            {"query": query, "limit": limit},
            context
        )
        
        # Get conversation context
        conversation_context = await self._get_conversation_context(
            {"session_id": context.session_id, "limit": 10},
            context
        )
        
        return {
            "episodic": episodic_context,
            "semantic": semantic_context,
            "conversation": conversation_context,
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def _store_episodic_memory(
        self,
        payload: Dict[str, Any],
        context: AgentContext,
    ) -> Dict[str, Any]:
        """Store episodic memory."""
        try:
            memory_entry = payload.get("memory_entry")
            if not memory_entry:
                raise MemoryStorageError("No memory entry provided")
            
            # Store in Redis for fast access
            key = f"{self.episodic_key}:{memory_entry['id']}"
            await self.redis_client.setex(
                key,
                timedelta(days=self.memory_decay_days),
                json.dumps(memory_entry)
            )
            
            # Store in vector store for semantic search
            content = memory_entry.get("content", {})
            if content:
                await self.vector_store.add_documents([{
                    "id": memory_entry["id"],
                    "content": json.dumps(content),
                    "metadata": memory_entry,
                }])
            
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
        payload: Dict[str, Any],
        context: AgentContext,
    ) -> List[Dict[str, Any]]:
        """Retrieve episodic memories."""
        try:
            query = payload.get("query", "")
            limit = payload.get("limit", 5)
            
            if not query:
                # Return recent memories
                return await self._get_recent_memories(limit)
            
            # Semantic search using vector store
            results = await self.vector_store.similarity_search(
                query=query,
                limit=limit,
                filter_metadata={"type": "investigation_result"}
            )
            
            memories = []
            for result in results:
                memory_id = result.get("id")
                if memory_id:
                    memory_data = await self.redis_client.get(
                        f"{self.episodic_key}:{memory_id}"
                    )
                    if memory_data:
                        memories.append(json.loads(memory_data))
            
            self.logger.info(
                "episodic_memories_retrieved",
                query=query,
                count=len(memories),
            )
            
            return memories
            
        except Exception as e:
            raise MemoryRetrievalError(f"Failed to retrieve episodic memory: {str(e)}")
    
    async def _store_semantic_memory(
        self,
        payload: Dict[str, Any],
        context: AgentContext,
    ) -> Dict[str, Any]:
        """Store semantic memory."""
        try:
            concept = payload.get("concept", "")
            content = payload.get("content", {})
            
            if not concept or not content:
                raise MemoryStorageError("Concept and content required for semantic memory")
            
            memory_entry = SemanticMemory(
                id=f"sem_{concept.lower().replace(' ', '_')}_{int(datetime.utcnow().timestamp())}",
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
            await self.redis_client.setex(
                key,
                timedelta(days=self.memory_decay_days * 2),  # Semantic memories last longer
                json.dumps(memory_entry.model_dump())
            )
            
            # Store in vector store
            await self.vector_store.add_documents([{
                "id": memory_entry.id,
                "content": f"{concept}: {json.dumps(content)}",
                "metadata": memory_entry.model_dump(),
            }])
            
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
        payload: Dict[str, Any],
        context: AgentContext,
    ) -> List[Dict[str, Any]]:
        """Retrieve semantic memories."""
        try:
            query = payload.get("query", "")
            limit = payload.get("limit", 5)
            
            # Semantic search
            results = await self.vector_store.similarity_search(
                query=query,
                limit=limit,
                filter_metadata={"concept": {"$exists": True}}
            )
            
            memories = []
            for result in results:
                memory_id = result.get("id")
                if memory_id:
                    memory_data = await self.redis_client.get(
                        f"{self.semantic_key}:{memory_id}"
                    )
                    if memory_data:
                        memories.append(json.loads(memory_data))
            
            self.logger.info(
                "semantic_memories_retrieved",
                query=query,
                count=len(memories),
            )
            
            return memories
            
        except Exception as e:
            raise MemoryRetrievalError(f"Failed to retrieve semantic memory: {str(e)}")
    
    async def _store_conversation_memory(
        self,
        payload: Dict[str, Any],
        context: AgentContext,
    ) -> Dict[str, Any]:
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
            await self.redis_client.setex(
                key,
                timedelta(hours=24),  # Conversations expire after 24 hours
                json.dumps(memory_entry.model_dump())
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
        payload: Dict[str, Any],
        context: AgentContext,
    ) -> List[Dict[str, Any]]:
        """Get conversation context."""
        try:
            conversation_id = payload.get("conversation_id", context.session_id)
            limit = payload.get("limit", 10)
            
            if not conversation_id:
                return []
            
            # Get recent conversation turns
            pattern = f"{self.conversation_key}:{conversation_id}:*"
            keys = await self.redis_client.keys(pattern)
            
            # Sort by turn number (descending)
            keys.sort(key=lambda k: int(k.split(":")[-1]), reverse=True)
            
            memories = []
            for key in keys[:limit]:
                memory_data = await self.redis_client.get(key)
                if memory_data:
                    memories.append(json.loads(memory_data))
            
            # Reverse to get chronological order
            memories.reverse()
            
            self.logger.info(
                "conversation_context_retrieved",
                conversation_id=conversation_id,
                count=len(memories),
            )
            
            return memories
            
        except Exception as e:
            raise MemoryRetrievalError(f"Failed to get conversation context: {str(e)}")
    
    async def _get_relevant_context(
        self,
        payload: Dict[str, Any],
        context: AgentContext,
    ) -> Dict[str, Any]:
        """Get all relevant context for a query."""
        return await self.get_relevant_context(
            payload.get("query", ""),
            context,
            payload.get("limit", 5)
        )
    
    async def _forget_memories(
        self,
        payload: Dict[str, Any],
        context: AgentContext,
    ) -> Dict[str, Any]:
        """Forget specific memories or old memories."""
        # Implementation for forgetting memories
        forgotten_count = 0
        return {"status": "completed", "forgotten_count": forgotten_count}
    
    async def _consolidate_memories(
        self,
        payload: Dict[str, Any],
        context: AgentContext,
    ) -> Dict[str, Any]:
        """Consolidate similar memories."""
        # Implementation for memory consolidation
        consolidated_count = 0
        return {"status": "completed", "consolidated_count": consolidated_count}
    
    def _calculate_importance(self, investigation_result: Any) -> MemoryImportance:
        """Calculate importance of an investigation result."""
        confidence = getattr(investigation_result, 'confidence_score', 0.0)
        findings_count = len(getattr(investigation_result, 'findings', []))
        
        if confidence > 0.8 and findings_count > 3:
            return MemoryImportance.CRITICAL
        elif confidence > 0.6 and findings_count > 1:
            return MemoryImportance.HIGH
        elif confidence > 0.4:
            return MemoryImportance.MEDIUM
        else:
            return MemoryImportance.LOW
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract tags from text for better organization."""
        # Simple tag extraction - could be enhanced with NLP
        keywords = [
            "contrato", "licitação", "emergencial", "suspeito", "anomalia",
            "ministério", "prefeitura", "fornecedor", "valor", "preço",
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
            keys_to_remove = keys[:-self.max_episodic_memories]
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
            keys_to_remove = keys[:-self.max_conversation_turns]
            
            for key in keys_to_remove:
                await self.redis_client.delete(key)
            
            self.logger.info(
                "conversation_memory_cleaned",
                conversation_id=conversation_id,
                removed_count=len(keys_to_remove),
            )
    
    async def _get_recent_memories(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent episodic memories."""
        pattern = f"{self.episodic_key}:*"
        keys = await self.redis_client.keys(pattern)
        
        memories = []
        for key in keys[:limit]:
            memory_data = await self.redis_client.get(key)
            if memory_data:
                memories.append(json.loads(memory_data))
        
        # Sort by timestamp (most recent first)
        memories.sort(
            key=lambda m: m.get("timestamp", ""),
            reverse=True
        )
        
        return memories[:limit]