"""
Module: services.memory_service
Description: Memory service factory for Nanã agent with vector store and Redis
Author: Anderson H. Silva
Date: 2025-10-20
License: Proprietary - All rights reserved
"""

import structlog

from src.agents.nana import ContextMemoryAgent
from src.core.cache import get_redis_client
from src.services.vector_store_service import get_vector_store

logger = structlog.get_logger(__name__)


class MemoryServiceFactory:
    """Factory for creating properly configured memory service instances."""

    _instance: ContextMemoryAgent | None = None
    _initialized: bool = False

    @classmethod
    async def get_memory_agent(
        cls,
        max_episodic_memories: int = 1000,
        max_conversation_turns: int = 50,
        memory_decay_days: int = 30,
    ) -> ContextMemoryAgent:
        """
        Get or create memory agent instance.

        Args:
            max_episodic_memories: Maximum episodic memories to keep
            max_conversation_turns: Maximum conversation turns to remember
            memory_decay_days: Days after which memories start to decay

        Returns:
            Configured ContextMemoryAgent instance
        """
        if cls._instance is None:
            logger.info("creating_memory_agent_instance")

            # Get Redis client
            redis_client = await get_redis_client()

            # Get vector store
            vector_store = get_vector_store(
                collection_name="cidadao_memory",
                persist_directory="./data/chroma_db",
            )

            # Initialize vector store
            if not cls._initialized:
                await vector_store.initialize()
                cls._initialized = True

            # Create memory agent
            cls._instance = ContextMemoryAgent(
                redis_client=redis_client,
                vector_store=vector_store,
                max_episodic_memories=max_episodic_memories,
                max_conversation_turns=max_conversation_turns,
                memory_decay_days=memory_decay_days,
            )

            # Initialize agent
            await cls._instance.initialize()

            logger.info(
                "memory_agent_created",
                max_episodic=max_episodic_memories,
                max_conversation=max_conversation_turns,
                decay_days=memory_decay_days,
            )

        return cls._instance

    @classmethod
    async def shutdown(cls) -> None:
        """Shutdown memory agent and close connections."""
        if cls._instance is not None:
            logger.info("shutting_down_memory_agent")

            await cls._instance.shutdown()
            cls._instance = None
            cls._initialized = False

            logger.info("memory_agent_shutdown_complete")


# Convenience function
async def get_memory_agent() -> ContextMemoryAgent:
    """
    Get memory agent instance.

    Returns:
        Configured ContextMemoryAgent
    """
    return await MemoryServiceFactory.get_memory_agent()
