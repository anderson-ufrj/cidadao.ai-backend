"""
Memory System Startup Service

Initializes the memory system and integrates it with all agents
during application startup.
"""

import asyncio
from typing import Optional

from src.agents.nana import ContextMemoryAgent
from src.services.agent_memory_integration import initialize_memory_integration
from src.infrastructure.cache.redis_client import get_redis_client
from src.core import get_logger
from src.core.config import settings


logger = get_logger(__name__)


async def initialize_memory_system() -> Optional[ContextMemoryAgent]:
    """
    Initialize the complete memory system.
    
    This function:
    1. Creates the Nanã memory agent
    2. Sets up the memory integration service
    3. Returns the configured memory agent
    """
    try:
        logger.info("Initializing memory system...")
        
        # Get Redis client for memory storage
        redis_client = await get_redis_client()
        
        # Initialize vector store (using ChromaDB or similar)
        # For now, we'll use a simple in-memory store
        vector_store = None  # This would be ChromaDB, Pinecone, etc.
        
        # Create Nanã memory agent
        memory_agent = ContextMemoryAgent(
            redis_client=redis_client,
            vector_store=vector_store,
            max_episodic_memories=settings.get("MAX_EPISODIC_MEMORIES", 10000),
            max_conversation_turns=settings.get("MAX_CONVERSATION_TURNS", 100),
            memory_decay_days=settings.get("MEMORY_DECAY_DAYS", 90)
        )
        
        # Initialize the memory agent
        await memory_agent.initialize()
        
        # Initialize memory integration service
        memory_integration = await initialize_memory_integration(memory_agent)
        
        # Configure memory integration settings
        memory_integration.auto_store = settings.get("AUTO_STORE_MEMORIES", True)
        memory_integration.auto_retrieve = settings.get("AUTO_RETRIEVE_MEMORIES", True)
        memory_integration.cache_ttl = settings.get("MEMORY_CACHE_TTL", 300)
        
        logger.info("Memory system initialized successfully")
        logger.info(f"Auto-store: {memory_integration.auto_store}")
        logger.info(f"Auto-retrieve: {memory_integration.auto_retrieve}")
        logger.info(f"Cache TTL: {memory_integration.cache_ttl}s")
        
        return memory_agent
        
    except Exception as e:
        logger.error(f"Failed to initialize memory system: {str(e)}")
        logger.warning("Continuing without memory system - agents will operate independently")
        return None


async def integrate_existing_agents():
    """
    Integrate all existing agents with the memory system.
    
    This is useful when agents are already created and we need
    to retrofit them with memory capabilities.
    """
    try:
        from src.agents.agent_pool import get_agent_pool
        from src.services.agent_memory_integration import get_memory_integration
        
        memory_integration = get_memory_integration()
        if not memory_integration:
            logger.warning("Memory integration not available")
            return
        
        agent_pool = get_agent_pool()
        if not agent_pool:
            logger.warning("Agent pool not available")
            return
        
        # Get all agents from the pool
        integrated_count = 0
        for agent_type, pool_entries in agent_pool._pools.items():
            for entry in pool_entries:
                try:
                    await memory_integration.integrate_agent(entry.agent)
                    integrated_count += 1
                except Exception as e:
                    logger.error(f"Failed to integrate agent {entry.agent.agent_id}: {str(e)}")
        
        logger.info(f"Integrated {integrated_count} existing agents with memory system")
        
    except Exception as e:
        logger.error(f"Failed to integrate existing agents: {str(e)}")


async def demonstrate_memory_sharing():
    """
    Demonstrate how agents can share knowledge through memory.
    
    This is an example of cross-agent learning.
    """
    try:
        from src.services.agent_memory_integration import get_memory_integration
        
        memory_integration = get_memory_integration()
        if not memory_integration:
            logger.warning("Memory integration not available for demonstration")
            return
        
        # Example: Share anomaly patterns from Zumbi to Oxóssi
        logger.info("Demonstrating knowledge sharing between agents...")
        
        # Share anomaly patterns
        success = await memory_integration.share_knowledge_between_agents(
            source_agent="zumbi",
            target_agent="oxossi",
            knowledge_type="anomaly",
            filters={"importance": "HIGH"}
        )
        
        if success:
            logger.info("Successfully shared anomaly patterns from Zumbi to Oxóssi")
        
        # Share fraud patterns back to Zumbi
        success = await memory_integration.share_knowledge_between_agents(
            source_agent="oxossi",
            target_agent="zumbi",
            knowledge_type="fraud"
        )
        
        if success:
            logger.info("Successfully shared fraud patterns from Oxóssi to Zumbi")
        
        # Get memory statistics
        stats = await memory_integration.get_memory_statistics()
        logger.info(f"Memory statistics: {stats}")
        
    except Exception as e:
        logger.error(f"Memory sharing demonstration failed: {str(e)}")


async def optimize_agent_memories():
    """
    Optimize memories for all agents by consolidating and cleaning up.
    
    This should be run periodically (e.g., daily) to maintain
    memory system performance.
    """
    try:
        from src.services.agent_memory_integration import get_memory_integration
        
        memory_integration = get_memory_integration()
        if not memory_integration:
            logger.warning("Memory integration not available for optimization")
            return
        
        logger.info("Starting memory optimization for all agents...")
        
        # List of agents to optimize
        agents_to_optimize = [
            "zumbi", "anita", "oxossi", "bonifacio", "dandara",
            "machado", "lampiao", "maria_quiteria", "obaluaie"
        ]
        
        for agent_id in agents_to_optimize:
            try:
                await memory_integration.optimize_memory_for_agent(agent_id)
                logger.info(f"Optimized memory for {agent_id}")
            except Exception as e:
                logger.error(f"Failed to optimize memory for {agent_id}: {str(e)}")
        
        logger.info("Memory optimization completed")
        
    except Exception as e:
        logger.error(f"Memory optimization failed: {str(e)}")


# Convenience functions for FastAPI startup

async def setup_memory_on_startup():
    """Setup memory system during FastAPI startup."""
    memory_agent = await initialize_memory_system()
    if memory_agent:
        await integrate_existing_agents()
        # Optionally demonstrate memory sharing
        if settings.get("DEMO_MEMORY_SHARING", False):
            await demonstrate_memory_sharing()
    return memory_agent


async def cleanup_memory_on_shutdown():
    """Cleanup memory system during FastAPI shutdown."""
    try:
        from src.services.agent_memory_integration import get_memory_integration
        
        memory_integration = get_memory_integration()
        if memory_integration:
            # Save any pending memories
            logger.info("Saving pending memories before shutdown...")
            
            # Get final statistics
            stats = await memory_integration.get_memory_statistics()
            logger.info(f"Final memory statistics: {stats}")
            
    except Exception as e:
        logger.error(f"Memory cleanup failed: {str(e)}")


# Background task for periodic optimization
async def periodic_memory_optimization():
    """Run memory optimization periodically."""
    while True:
        try:
            # Wait for configured interval (default: 24 hours)
            interval = settings.get("MEMORY_OPTIMIZATION_INTERVAL", 86400)
            await asyncio.sleep(interval)
            
            # Run optimization
            await optimize_agent_memories()
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Periodic optimization error: {str(e)}")
            # Continue after error with shorter interval
            await asyncio.sleep(3600)  # Retry in 1 hour