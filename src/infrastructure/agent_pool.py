"""
Backward compatibility wrapper for agent_pool.

This module re-exports classes from distributed_agent_pool for backward compatibility
with code expecting AgentPool to be in src.infrastructure.agent_pool.
"""

from src.infrastructure.distributed_agent_pool import (
    AgentInstance,
    AgentPoolManager,
    PoolConfig,
)

# Backward compatibility aliases
AgentPool = AgentPoolManager
AgentPoolConfig = PoolConfig

__all__ = [
    "AgentPool",
    "AgentPoolConfig",
    "AgentInstance",
]
