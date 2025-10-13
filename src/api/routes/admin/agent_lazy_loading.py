"""
Admin routes for agent lazy loading management
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.api.dependencies import require_admin
from src.core import get_logger
from src.services.agent_lazy_loader import agent_lazy_loader

logger = get_logger(__name__)
router = APIRouter()


class LoadAgentRequest(BaseModel):
    """Request to load an agent."""

    agent_name: str = Field(..., description="Name of the agent to load")


class UnloadAgentRequest(BaseModel):
    """Request to unload an agent."""

    agent_name: str = Field(..., description="Name of the agent to unload")
    force: bool = Field(False, description="Force unload even with active instances")


class LazyLoaderConfig(BaseModel):
    """Configuration for lazy loader."""

    unload_after_minutes: int = Field(
        15, ge=1, description="Minutes of inactivity before unloading"
    )
    max_loaded_agents: int = Field(
        10, ge=1, description="Maximum number of loaded agents"
    )
    preload_agents: list[str] = Field([], description="Agents to preload on startup")


@router.get("/agent-lazy-loading/status")
async def get_lazy_loading_status(_: None = Depends(require_admin)) -> dict[str, Any]:
    """
    Get lazy loading status and statistics.

    Returns:
        Lazy loading status including loaded agents and statistics
    """
    try:
        stats = agent_lazy_loader.get_stats()
        available_agents = agent_lazy_loader.get_available_agents()

        return {
            "status": "operational",
            "statistics": stats,
            "available_agents": available_agents,
            "config": {
                "unload_after_minutes": agent_lazy_loader.unload_after_minutes,
                "max_loaded_agents": agent_lazy_loader.max_loaded_agents,
            },
        }
    except Exception as e:
        logger.error(f"Failed to get lazy loading status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent-lazy-loading/load")
async def load_agent(
    request: LoadAgentRequest, _: None = Depends(require_admin)
) -> dict[str, Any]:
    """
    Load an agent manually.

    Args:
        request: Load agent request

    Returns:
        Load operation result
    """
    try:
        # Load the agent
        agent_class = await agent_lazy_loader.get_agent_class(request.agent_name)

        return {
            "success": True,
            "agent": request.agent_name,
            "class": agent_class.__name__,
            "module": agent_class.__module__,
        }
    except Exception as e:
        logger.error(f"Failed to load agent {request.agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent-lazy-loading/unload")
async def unload_agent(
    request: UnloadAgentRequest, _: None = Depends(require_admin)
) -> dict[str, Any]:
    """
    Unload an agent from memory.

    Args:
        request: Unload agent request

    Returns:
        Unload operation result
    """
    try:
        # Get agent metadata
        if request.agent_name not in agent_lazy_loader._registry:
            raise HTTPException(
                status_code=404, detail=f"Agent '{request.agent_name}' not found"
            )

        metadata = agent_lazy_loader._registry[request.agent_name]

        # Check if agent is loaded
        if not metadata.loaded_class:
            return {
                "success": True,
                "agent": request.agent_name,
                "message": "Agent was not loaded",
            }

        # Unload the agent
        await agent_lazy_loader._unload_agent(metadata)

        return {
            "success": True,
            "agent": request.agent_name,
            "message": "Agent unloaded successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unload agent {request.agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent-lazy-loading/preload-all")
async def preload_all_agents(_: None = Depends(require_admin)) -> dict[str, Any]:
    """
    Preload all high-priority agents.

    Returns:
        Preload operation result
    """
    try:
        await agent_lazy_loader._preload_agents()

        # Get loaded agents
        loaded_agents = [
            name
            for name, metadata in agent_lazy_loader._registry.items()
            if metadata.loaded_class
        ]

        return {
            "success": True,
            "loaded_agents": loaded_agents,
            "count": len(loaded_agents),
        }
    except Exception as e:
        logger.error(f"Failed to preload agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/agent-lazy-loading/config")
async def update_lazy_loader_config(
    config: LazyLoaderConfig, _: None = Depends(require_admin)
) -> dict[str, Any]:
    """
    Update lazy loader configuration.

    Args:
        config: New configuration

    Returns:
        Update result
    """
    try:
        # Update configuration
        agent_lazy_loader.unload_after_minutes = config.unload_after_minutes
        agent_lazy_loader.max_loaded_agents = config.max_loaded_agents

        # Update preload flags
        for name in agent_lazy_loader._registry:
            agent_lazy_loader._registry[name].preload = name in config.preload_agents

        logger.info(
            "Updated lazy loader config",
            unload_after_minutes=config.unload_after_minutes,
            max_loaded_agents=config.max_loaded_agents,
            preload_agents=config.preload_agents,
        )

        return {
            "success": True,
            "config": {
                "unload_after_minutes": agent_lazy_loader.unload_after_minutes,
                "max_loaded_agents": agent_lazy_loader.max_loaded_agents,
                "preload_agents": config.preload_agents,
            },
        }
    except Exception as e:
        logger.error(f"Failed to update lazy loader config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent-lazy-loading/cleanup")
async def trigger_cleanup(_: None = Depends(require_admin)) -> dict[str, Any]:
    """
    Trigger manual cleanup of unused agents.

    Returns:
        Cleanup operation result
    """
    try:
        # Get stats before cleanup
        before_stats = agent_lazy_loader.get_stats()

        # Run cleanup
        await agent_lazy_loader._cleanup_unused_agents()

        # Get stats after cleanup
        after_stats = agent_lazy_loader.get_stats()

        return {
            "success": True,
            "agents_unloaded": before_stats["loaded_agents"]
            - after_stats["loaded_agents"],
            "before": {
                "loaded_agents": before_stats["loaded_agents"],
                "active_instances": before_stats["active_instances"],
            },
            "after": {
                "loaded_agents": after_stats["loaded_agents"],
                "active_instances": after_stats["active_instances"],
            },
        }
    except Exception as e:
        logger.error(f"Failed to trigger cleanup: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agent-lazy-loading/memory-usage")
async def get_memory_usage(_: None = Depends(require_admin)) -> dict[str, Any]:
    """
    Get estimated memory usage by agents.

    Returns:
        Memory usage information
    """
    try:
        import gc
        import sys

        # Get loaded agents
        loaded_agents = []
        total_size = 0

        for name, metadata in agent_lazy_loader._registry.items():
            if metadata.loaded_class:
                # Estimate size (basic approximation)
                size_estimate = sys.getsizeof(metadata.loaded_class)

                # Count instances
                instance_count = sum(
                    1
                    for key in agent_lazy_loader._instances
                    if key.startswith(f"{name}_")
                )

                loaded_agents.append(
                    {
                        "agent": name,
                        "class_size_bytes": size_estimate,
                        "instance_count": instance_count,
                        "load_time_ms": metadata.load_time_ms,
                        "usage_count": metadata.usage_count,
                    }
                )

                total_size += size_estimate

        # Force garbage collection and get stats
        gc.collect()
        gc_stats = gc.get_stats()

        return {
            "loaded_agents": loaded_agents,
            "summary": {
                "total_agents_loaded": len(loaded_agents),
                "estimated_memory_bytes": total_size,
                "estimated_memory_mb": round(total_size / 1024 / 1024, 2),
            },
            "gc_stats": gc_stats[0] if gc_stats else {},
        }
    except Exception as e:
        logger.error(f"Failed to get memory usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))
