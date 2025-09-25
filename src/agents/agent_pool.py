"""
Agent pooling system for improved performance.

This module provides a pool of pre-initialized agents that can be
reused across requests, avoiding the overhead of creating new instances.
"""

import asyncio
from typing import Dict, Type, Optional, Any, List
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import weakref

from src.core import get_logger
from src.agents.deodoro import BaseAgent, AgentContext

logger = get_logger(__name__)


class AgentPoolEntry:
    """Entry in the agent pool."""
    
    def __init__(self, agent: BaseAgent):
        self.agent = agent
        self.in_use = False
        self.last_used = datetime.now()
        self.usage_count = 0
        self.created_at = datetime.now()
        self._lock = asyncio.Lock()
    
    @property
    def idle_time(self) -> float:
        """Get idle time in seconds."""
        return (datetime.now() - self.last_used).total_seconds()
    
    async def acquire(self) -> BaseAgent:
        """Acquire the agent for use."""
        async with self._lock:
            if self.in_use:
                raise RuntimeError("Agent already in use")
            self.in_use = True
            self.usage_count += 1
            return self.agent
    
    async def release(self):
        """Release the agent back to pool."""
        async with self._lock:
            self.in_use = False
            self.last_used = datetime.now()


class AgentPool:
    """
    Pool manager for AI agents.
    
    Features:
    - Pre-warmed agent instances
    - Automatic cleanup of idle agents
    - Usage statistics and monitoring
    - Thread-safe operations
    """
    
    def __init__(
        self,
        min_size: int = 2,
        max_size: int = 10,
        idle_timeout: int = 300,  # 5 minutes
        max_agent_lifetime: int = 3600,  # 1 hour
        use_lazy_loading: bool = True
    ):
        """
        Initialize agent pool.
        
        Args:
            min_size: Minimum pool size per agent type
            max_size: Maximum pool size per agent type
            idle_timeout: Seconds before removing idle agents
            max_agent_lifetime: Maximum agent lifetime in seconds
            use_lazy_loading: Enable lazy loading for agents
        """
        self.min_size = min_size
        self.max_size = max_size
        self.idle_timeout = idle_timeout
        self.max_agent_lifetime = max_agent_lifetime
        self._use_lazy_loading = use_lazy_loading
        
        # Pool storage: agent_type -> list of entries
        self._pools: Dict[Type[BaseAgent], List[AgentPoolEntry]] = {}
        
        # Weak references to track all created agents
        self._all_agents: weakref.WeakSet = weakref.WeakSet()
        
        # Statistics
        self._stats = {
            "created": 0,
            "reused": 0,
            "evicted": 0,
            "errors": 0,
            "lazy_loaded": 0
        }
        
        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def start(self):
        """Start the agent pool and cleanup task."""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Initialize lazy loader if enabled
        if self._use_lazy_loading:
            from src.services.agent_lazy_loader import agent_lazy_loader
            await agent_lazy_loader.start()
        
        logger.info("Agent pool started", lazy_loading=self._use_lazy_loading)
    
    async def stop(self):
        """Stop the agent pool and cleanup resources."""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Cleanup all agents
        for agent_type, entries in self._pools.items():
            for entry in entries:
                try:
                    if hasattr(entry.agent, 'cleanup'):
                        await entry.agent.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up agent: {e}")
        
        self._pools.clear()
        
        # Stop lazy loader if enabled
        if self._use_lazy_loading:
            from src.services.agent_lazy_loader import agent_lazy_loader
            await agent_lazy_loader.stop()
        
        logger.info("Agent pool stopped")
    
    @asynccontextmanager
    async def acquire(self, agent_type: Type[BaseAgent], context: AgentContext):
        """
        Acquire an agent from the pool.
        
        Args:
            agent_type: Type of agent to acquire
            context: Agent execution context
            
        Yields:
            Agent instance
        """
        entry = await self._get_or_create_agent(agent_type)
        agent = await entry.acquire()
        
        try:
            # Update agent context
            agent.context = context
            yield agent
        finally:
            # Clear sensitive data
            agent.context = None
            await entry.release()
    
    async def _get_or_create_agent(self, agent_type: Type[BaseAgent]) -> AgentPoolEntry:
        """Get an available agent or create a new one."""
        # Initialize pool for agent type if needed
        if agent_type not in self._pools:
            self._pools[agent_type] = []
        
        pool = self._pools[agent_type]
        
        # Find available agent
        for entry in pool:
            if not entry.in_use:
                self._stats["reused"] += 1
                logger.debug(f"Reusing agent {agent_type.__name__} from pool")
                return entry
        
        # Create new agent if under limit
        if len(pool) < self.max_size:
            agent = await self._create_agent(agent_type)
            entry = AgentPoolEntry(agent)
            pool.append(entry)
            self._stats["created"] += 1
            logger.info(f"Created new agent {agent_type.__name__} (pool size: {len(pool)})")
            return entry
        
        # Wait for available agent
        logger.warning(f"Agent pool full for {agent_type.__name__}, waiting...")
        while True:
            await asyncio.sleep(0.1)
            for entry in pool:
                if not entry.in_use:
                    return entry
    
    async def _create_agent(self, agent_type: Type[BaseAgent]) -> BaseAgent:
        """Create and initialize a new agent."""
        try:
            # Check if we should use lazy loader
            if hasattr(agent_type, '__name__') and self._use_lazy_loading:
                # Try to get from lazy loader
                from src.services.agent_lazy_loader import agent_lazy_loader
                agent_name = agent_type.__name__.replace('Agent', '')
                
                try:
                    # Use lazy loader to create agent
                    agent = await agent_lazy_loader.create_agent(agent_name)
                    self._all_agents.add(agent)
                    self._stats["lazy_loaded"] += 1
                    logger.debug(f"Created agent {agent_name} using lazy loader")
                    return agent
                except Exception:
                    # Fallback to direct instantiation
                    logger.debug(f"Lazy loader failed for {agent_name}, using direct instantiation")
            
            # Direct instantiation
            agent = agent_type()
            self._all_agents.add(agent)
            
            # Initialize if needed
            if hasattr(agent, 'initialize'):
                await agent.initialize()
            
            return agent
            
        except Exception as e:
            self._stats["errors"] += 1
            logger.error(f"Failed to create agent {agent_type.__name__}: {e}")
            raise
    
    async def _cleanup_loop(self):
        """Background task to cleanup idle agents."""
        while self._running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._cleanup_idle_agents()
                await self._maintain_minimum_pool()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_idle_agents(self):
        """Remove agents that have been idle too long."""
        for agent_type, pool in self._pools.items():
            to_remove = []
            
            for entry in pool:
                # Check idle timeout
                if not entry.in_use and entry.idle_time > self.idle_timeout:
                    # Keep minimum pool size
                    active_count = sum(1 for e in pool if not e.in_use)
                    if active_count > self.min_size:
                        to_remove.append(entry)
                
                # Check lifetime
                lifetime = (datetime.now() - entry.created_at).total_seconds()
                if lifetime > self.max_agent_lifetime:
                    to_remove.append(entry)
            
            # Remove identified agents
            for entry in to_remove:
                if entry.in_use:
                    continue  # Skip if now in use
                
                pool.remove(entry)
                self._stats["evicted"] += 1
                
                try:
                    if hasattr(entry.agent, 'cleanup'):
                        await entry.agent.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up agent: {e}")
                
                logger.debug(f"Evicted idle agent {agent_type.__name__}")
    
    async def _maintain_minimum_pool(self):
        """Ensure minimum pool size for each agent type."""
        for agent_type, pool in self._pools.items():
            available = sum(1 for e in pool if not e.in_use)
            
            # Create agents to maintain minimum
            while available < self.min_size and len(pool) < self.max_size:
                try:
                    agent = await self._create_agent(agent_type)
                    entry = AgentPoolEntry(agent)
                    pool.append(entry)
                    available += 1
                    logger.debug(f"Pre-warmed agent {agent_type.__name__}")
                except Exception as e:
                    logger.error(f"Failed to maintain pool: {e}")
                    break
    
    async def prewarm(self, agent_types: List[Type[BaseAgent]]):
        """Pre-warm the pool with specified agent types."""
        for agent_type in agent_types:
            if agent_type not in self._pools:
                self._pools[agent_type] = []
            
            # Create minimum agents
            pool = self._pools[agent_type]
            while len(pool) < self.min_size:
                try:
                    agent = await self._create_agent(agent_type)
                    entry = AgentPoolEntry(agent)
                    pool.append(entry)
                    logger.info(f"Pre-warmed {agent_type.__name__} agent")
                except Exception as e:
                    logger.error(f"Failed to prewarm {agent_type.__name__}: {e}")
                    break
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        pool_stats = {}
        
        for agent_type, pool in self._pools.items():
            pool_stats[agent_type.__name__] = {
                "total": len(pool),
                "in_use": sum(1 for e in pool if e.in_use),
                "available": sum(1 for e in pool if not e.in_use),
                "avg_usage": sum(e.usage_count for e in pool) / len(pool) if pool else 0
            }
        
        return {
            "pools": pool_stats,
            "global_stats": self._stats,
            "total_agents": sum(len(p) for p in self._pools.values())
        }


# Global agent pool instance
agent_pool = AgentPool()


async def get_agent_pool() -> AgentPool:
    """Get the global agent pool instance."""
    if not agent_pool._running:
        await agent_pool.start()
    return agent_pool