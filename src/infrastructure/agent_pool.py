"""
Backward compatibility wrapper for agent_pool.

This module re-exports classes from distributed_agent_pool for backward compatibility
with code expecting AgentPool to be in src.infrastructure.agent_pool.
"""

from src.infrastructure.distributed_agent_pool import (
    AgentHealth,
    AgentInstance,
    AgentPool,
    AgentPoolConfig,
    AgentType,
    LoadBalancer,
)

__all__ = [
    "AgentPool",
    "AgentPoolConfig",
    "AgentType",
    "AgentInstance",
    "AgentHealth",
    "LoadBalancer",
]
