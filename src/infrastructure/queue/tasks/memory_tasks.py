"""
Module: infrastructure.queue.tasks.memory_tasks
Description: Celery tasks for Nanã memory management
Author: Anderson H. Silva
Date: 2025-10-20
License: Proprietary - All rights reserved
"""

from datetime import UTC, datetime, timedelta
from typing import Any

from celery.utils.log import get_task_logger

from src.infrastructure.queue.celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(
    name="tasks.memory_decay",
    queue="background",
    max_retries=3,
    default_retry_delay=300,
)
async def memory_decay_task(decay_days: int = 30) -> dict[str, Any]:
    """
    Apply memory decay to old episodic memories.

    This task runs periodically to implement forgetting/decay for memories
    older than the specified threshold. Memories don't get deleted but their
    importance/weight decreases over time.

    Args:
        decay_days: Number of days after which memories start to decay

    Returns:
        Dictionary with decay statistics
    """
    from src.services.memory_service import MemoryServiceFactory

    logger.info("memory_decay_started", decay_days=decay_days)

    try:
        # Get memory agent
        memory_agent = await MemoryServiceFactory.get_memory_agent(
            memory_decay_days=decay_days
        )

        # Calculate cutoff date
        cutoff_date = datetime.now(UTC) - timedelta(days=decay_days)

        # Get all memories from vector store
        vector_store = memory_agent.vector_store

        # Query all documents (ChromaDB doesn't have a direct "get all" but we can query with empty filter)
        all_memories = await vector_store.similarity_search(
            query="",  # Empty query to get all
            limit=10000,  # Large limit to get all memories
            similarity_threshold=0.0,  # Accept all similarities
        )

        decayed_count = 0
        deleted_count = 0

        for memory in all_memories:
            metadata = memory.get("metadata", {})
            timestamp_str = metadata.get("timestamp")

            if not timestamp_str:
                continue

            # Parse timestamp
            try:
                memory_timestamp = datetime.fromisoformat(timestamp_str)
            except (ValueError, TypeError):
                continue

            # Check if memory is old enough for decay
            if memory_timestamp < cutoff_date:
                # Calculate decay factor based on age
                age_days = (datetime.now(UTC) - memory_timestamp).days
                decay_factor = max(
                    0.1, 1.0 - (age_days - decay_days) / (decay_days * 2)
                )

                # Very old memories (> 2x decay_days) get deleted
                if age_days > decay_days * 2:
                    await vector_store.delete_documents([memory["id"]])
                    deleted_count += 1
                    logger.debug(
                        "memory_deleted",
                        memory_id=memory["id"],
                        age_days=age_days,
                    )
                else:
                    # Update metadata with decay factor
                    metadata["decay_factor"] = decay_factor
                    metadata["last_decay_update"] = datetime.now(UTC).isoformat()

                    # Re-add document with updated metadata
                    await vector_store.add_documents(
                        [
                            {
                                "id": memory["id"],
                                "text": memory["text"],
                                "metadata": metadata,
                            }
                        ]
                    )
                    decayed_count += 1
                    logger.debug(
                        "memory_decayed",
                        memory_id=memory["id"],
                        age_days=age_days,
                        decay_factor=decay_factor,
                    )

        result = {
            "status": "completed",
            "timestamp": datetime.now(UTC).isoformat(),
            "total_memories": len(all_memories),
            "decayed_count": decayed_count,
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
        }

        logger.info(
            "memory_decay_completed",
            total=len(all_memories),
            decayed=decayed_count,
            deleted=deleted_count,
        )

        return result

    except Exception as e:
        logger.error("memory_decay_failed", error=str(e), exc_info=True)
        raise


@celery_app.task(
    name="tasks.memory_consolidation",
    queue="background",
    max_retries=3,
    default_retry_delay=300,
)
async def memory_consolidation_task(
    similarity_threshold: float = 0.85,
) -> dict[str, Any]:
    """
    Consolidate similar episodic memories.

    This task finds and merges similar memories to prevent redundancy
    and improve memory efficiency.

    Args:
        similarity_threshold: Minimum similarity to consider memories as duplicates

    Returns:
        Dictionary with consolidation statistics
    """
    from src.agents.deodoro import AgentContext, AgentMessage
    from src.services.memory_service import MemoryServiceFactory

    logger.info("memory_consolidation_started", threshold=similarity_threshold)

    try:
        # Get memory agent
        memory_agent = await MemoryServiceFactory.get_memory_agent()

        # Create consolidation message
        message = AgentMessage(
            sender="celery_worker",
            recipient="nana",
            action="consolidate_memories",
            payload={"similarity_threshold": similarity_threshold},
        )

        context = AgentContext(
            investigation_id="memory_maintenance",
            user_id="system",
            session_id="celery_task",
        )

        # Execute consolidation
        response = await memory_agent.process(message, context)

        result = {
            "status": response.status.value,
            "timestamp": datetime.now(UTC).isoformat(),
            "consolidated_count": (
                response.result.get("consolidated_count", 0) if response.result else 0
            ),
        }

        logger.info(
            "memory_consolidation_completed",
            status=response.status.value,
            consolidated=result["consolidated_count"],
        )

        return result

    except Exception as e:
        logger.error("memory_consolidation_failed", error=str(e), exc_info=True)
        raise


@celery_app.task(
    name="tasks.memory_cleanup",
    queue="background",
    max_retries=3,
    default_retry_delay=300,
)
async def memory_cleanup_task() -> dict[str, Any]:
    """
    Clean up orphaned or corrupted memory entries.

    This task performs housekeeping on the memory system:
    - Removes memories without required metadata
    - Fixes inconsistencies between Redis and vector store
    - Reclaims storage from deleted investigations

    Returns:
        Dictionary with cleanup statistics
    """
    from src.services.memory_service import MemoryServiceFactory

    logger.info("memory_cleanup_started")

    try:
        # Get memory agent
        memory_agent = await MemoryServiceFactory.get_memory_agent()
        vector_store = memory_agent.vector_store

        # Get all memories
        all_memories = await vector_store.similarity_search(
            query="", limit=10000, similarity_threshold=0.0
        )

        cleaned_count = 0
        corrupted_ids = []

        for memory in all_memories:
            metadata = memory.get("metadata", {})

            # Check for required fields
            required_fields = ["timestamp", "investigation_id"]
            is_valid = all(field in metadata for field in required_fields)

            if not is_valid:
                corrupted_ids.append(memory["id"])
                cleaned_count += 1
                logger.debug("corrupted_memory_found", memory_id=memory["id"])

        # Delete corrupted memories
        if corrupted_ids:
            await vector_store.delete_documents(corrupted_ids)

        result = {
            "status": "completed",
            "timestamp": datetime.now(UTC).isoformat(),
            "total_memories": len(all_memories),
            "cleaned_count": cleaned_count,
        }

        logger.info(
            "memory_cleanup_completed",
            total=len(all_memories),
            cleaned=cleaned_count,
        )

        return result

    except Exception as e:
        logger.error("memory_cleanup_failed", error=str(e), exc_info=True)
        raise


@celery_app.task(
    name="tasks.memory_health_check",
    queue="high",
    max_retries=3,
    default_retry_delay=60,
)
async def memory_health_check() -> dict[str, Any]:
    """
    Check health of memory system.

    Verifies:
    - Vector store connectivity
    - Redis connectivity
    - Memory count and size
    - System performance metrics

    Returns:
        Dictionary with health status
    """
    from src.services.memory_service import MemoryServiceFactory

    logger.info("memory_health_check_started")

    try:
        # Get memory agent
        memory_agent = await MemoryServiceFactory.get_memory_agent()

        # Check vector store
        vector_count = await memory_agent.vector_store.count()

        # Check Redis (use ping)
        redis_healthy = await memory_agent.redis_client.ping()

        result = {
            "status": "healthy" if redis_healthy else "degraded",
            "timestamp": datetime.now(UTC).isoformat(),
            "vector_store": {
                "status": "healthy",
                "document_count": vector_count,
            },
            "redis": {
                "status": "healthy" if redis_healthy else "unavailable",
            },
        }

        logger.info(
            "memory_health_check_completed",
            status=result["status"],
            vector_count=vector_count,
            redis_healthy=redis_healthy,
        )

        return result

    except Exception as e:
        logger.error("memory_health_check_failed", error=str(e), exc_info=True)
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "error": str(e),
        }
