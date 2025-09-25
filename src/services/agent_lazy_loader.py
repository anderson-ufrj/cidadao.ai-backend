"""
Lazy Loading Service for AI Agents
Optimizes memory usage and startup time by loading agents on-demand
"""

import asyncio
import importlib
import inspect
from typing import Dict, Type, Optional, Any, List, Callable
from datetime import datetime, timedelta
import weakref

from src.core import get_logger
from src.agents.deodoro import BaseAgent
from src.core.exceptions import AgentExecutionError

logger = get_logger(__name__)


class AgentMetadata:
    """Metadata for lazy-loaded agents."""
    
    def __init__(
        self,
        name: str,
        module_path: str,
        class_name: str,
        description: str,
        capabilities: List[str],
        priority: int = 0,
        preload: bool = False
    ):
        self.name = name
        self.module_path = module_path
        self.class_name = class_name
        self.description = description
        self.capabilities = capabilities
        self.priority = priority
        self.preload = preload
        self.loaded_class: Optional[Type[BaseAgent]] = None
        self.last_used: Optional[datetime] = None
        self.usage_count: int = 0
        self.load_time_ms: Optional[float] = None


class AgentLazyLoader:
    """
    Lazy loading manager for AI agents.
    
    Features:
    - On-demand agent loading
    - Memory-efficient agent management
    - Automatic unloading of unused agents
    - Preloading for critical agents
    - Usage tracking and statistics
    """
    
    def __init__(
        self,
        unload_after_minutes: int = 15,
        max_loaded_agents: int = 10
    ):
        """
        Initialize lazy loader.
        
        Args:
            unload_after_minutes: Minutes of inactivity before unloading
            max_loaded_agents: Maximum number of loaded agents in memory
        """
        self.unload_after_minutes = unload_after_minutes
        self.max_loaded_agents = max_loaded_agents
        
        # Agent registry
        self._registry: Dict[str, AgentMetadata] = {}
        
        # Weak references to track agent instances
        self._instances: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
        
        # Loading statistics
        self._stats = {
            "total_loads": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_unloads": 0,
            "avg_load_time_ms": 0.0
        }
        
        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Initialize with default agents
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register all available agents."""
        # Core agents - high priority, preload
        self.register_agent(
            name="Zumbi",
            module_path="src.agents.zumbi",
            class_name="ZumbiAgent",
            description="Anomaly detection investigator",
            capabilities=["anomaly_detection", "fraud_analysis", "pattern_recognition"],
            priority=10,
            preload=True
        )
        
        self.register_agent(
            name="Anita",
            module_path="src.agents.anita",
            class_name="AnitaAgent",
            description="Pattern analysis specialist",
            capabilities=["pattern_analysis", "trend_detection", "correlation_analysis"],
            priority=10,
            preload=True
        )
        
        self.register_agent(
            name="Tiradentes",
            module_path="src.agents.tiradentes",
            class_name="TiradentesAgent",
            description="Natural language report generation",
            capabilities=["report_generation", "summarization", "natural_language"],
            priority=10,
            preload=True
        )
        
        # Extended agents - lower priority, lazy load
        self.register_agent(
            name="MariaCurie",
            module_path="src.agents.legacy.mariacurie",
            class_name="MariaCurieAgent",
            description="Scientific research specialist",
            capabilities=["research", "data_analysis", "methodology"],
            priority=5,
            preload=False
        )
        
        self.register_agent(
            name="Drummond",
            module_path="src.agents.legacy.drummond",
            class_name="DrummondAgent",
            description="Communication and writing specialist",
            capabilities=["writing", "communication", "poetry"],
            priority=5,
            preload=False
        )
        
        self.register_agent(
            name="JoseBonifacio",
            module_path="src.agents.legacy.jose_bonifacio",
            class_name="JoseBonifacioAgent",
            description="Policy and governance analyst",
            capabilities=["policy_analysis", "governance", "regulation"],
            priority=5,
            preload=False
        )
    
    def register_agent(
        self,
        name: str,
        module_path: str,
        class_name: str,
        description: str,
        capabilities: List[str],
        priority: int = 0,
        preload: bool = False
    ):
        """Register an agent for lazy loading."""
        metadata = AgentMetadata(
            name=name,
            module_path=module_path,
            class_name=class_name,
            description=description,
            capabilities=capabilities,
            priority=priority,
            preload=preload
        )
        
        self._registry[name] = metadata
        logger.info(
            f"Registered agent {name}",
            module=module_path,
            class_name=class_name,
            preload=preload
        )
    
    async def start(self):
        """Start the lazy loader and preload critical agents."""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Preload high-priority agents
        await self._preload_agents()
        
        logger.info("Agent lazy loader started")
    
    async def stop(self):
        """Stop the lazy loader and cleanup resources."""
        self._running = False
        
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Cleanup all loaded agents
        for metadata in self._registry.values():
            if metadata.loaded_class:
                await self._unload_agent(metadata)
        
        logger.info("Agent lazy loader stopped")
    
    async def _preload_agents(self):
        """Preload high-priority agents."""
        preload_agents = [
            (metadata.priority, name, metadata)
            for name, metadata in self._registry.items()
            if metadata.preload
        ]
        
        # Sort by priority (descending)
        preload_agents.sort(key=lambda x: x[0], reverse=True)
        
        for _, name, metadata in preload_agents:
            try:
                await self._load_agent(metadata)
                logger.info(f"Preloaded agent {name}")
            except Exception as e:
                logger.error(f"Failed to preload agent {name}: {e}")
    
    async def get_agent_class(self, name: str) -> Type[BaseAgent]:
        """
        Get agent class, loading if necessary.
        
        Args:
            name: Agent name
            
        Returns:
            Agent class
            
        Raises:
            AgentExecutionError: If agent not found or load fails
        """
        if name not in self._registry:
            raise AgentExecutionError(
                f"Agent '{name}' not registered",
                details={"available_agents": list(self._registry.keys())}
            )
        
        metadata = self._registry[name]
        
        # Return cached class if available
        if metadata.loaded_class:
            metadata.last_used = datetime.now()
            metadata.usage_count += 1
            self._stats["cache_hits"] += 1
            return metadata.loaded_class
        
        # Load agent class
        self._stats["cache_misses"] += 1
        await self._load_agent(metadata)
        
        # Check if we need to unload other agents
        await self._check_memory_pressure()
        
        return metadata.loaded_class
    
    async def create_agent(self, name: str, **kwargs) -> BaseAgent:
        """
        Create an agent instance.
        
        Args:
            name: Agent name
            **kwargs: Agent initialization arguments
            
        Returns:
            Agent instance
        """
        agent_class = await self.get_agent_class(name)
        
        # Create instance
        instance = agent_class(**kwargs)
        
        # Track instance
        self._instances[f"{name}_{id(instance)}"] = instance
        
        # Initialize if needed
        if hasattr(instance, 'initialize'):
            await instance.initialize()
        
        return instance
    
    async def _load_agent(self, metadata: AgentMetadata):
        """Load an agent class."""
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Import module
            module = importlib.import_module(metadata.module_path)
            
            # Get class
            agent_class = getattr(module, metadata.class_name)
            
            # Verify it's a valid agent
            if not issubclass(agent_class, BaseAgent):
                raise ValueError(f"{metadata.class_name} is not a BaseAgent subclass")
            
            metadata.loaded_class = agent_class
            metadata.last_used = datetime.now()
            metadata.usage_count += 1
            
            # Calculate load time
            load_time = (asyncio.get_event_loop().time() - start_time) * 1000
            metadata.load_time_ms = load_time
            
            # Update statistics
            self._stats["total_loads"] += 1
            total_loads = self._stats["total_loads"]
            avg_load_time = self._stats["avg_load_time_ms"]
            self._stats["avg_load_time_ms"] = (
                (avg_load_time * (total_loads - 1) + load_time) / total_loads
            )
            
            logger.info(
                f"Loaded agent {metadata.name}",
                load_time_ms=round(load_time, 2),
                module=metadata.module_path
            )
            
        except Exception as e:
            logger.error(
                f"Failed to load agent {metadata.name}",
                error=str(e),
                module=metadata.module_path
            )
            raise AgentExecutionError(
                f"Failed to load agent '{metadata.name}'",
                details={"error": str(e), "module": metadata.module_path}
            )
    
    async def _unload_agent(self, metadata: AgentMetadata):
        """Unload an agent from memory."""
        if not metadata.loaded_class:
            return
        
        # Check if any instances are still active
        active_instances = [
            key for key in self._instances
            if key.startswith(f"{metadata.name}_")
        ]
        
        if active_instances:
            logger.debug(
                f"Cannot unload agent {metadata.name}, {len(active_instances)} instances active"
            )
            return
        
        # Unload the module
        try:
            # Remove class reference
            metadata.loaded_class = None
            
            # Try to remove from sys.modules
            import sys
            if metadata.module_path in sys.modules:
                del sys.modules[metadata.module_path]
            
            self._stats["total_unloads"] += 1
            
            logger.info(f"Unloaded agent {metadata.name}")
            
        except Exception as e:
            logger.error(f"Error unloading agent {metadata.name}: {e}")
    
    async def _check_memory_pressure(self):
        """Check if we need to unload agents to free memory."""
        loaded_agents = [
            (metadata.last_used, metadata)
            for metadata in self._registry.values()
            if metadata.loaded_class
        ]
        
        # If under limit, no action needed
        if len(loaded_agents) <= self.max_loaded_agents:
            return
        
        # Sort by last used (oldest first)
        loaded_agents.sort(key=lambda x: x[0] or datetime.min)
        
        # Unload oldest agents
        to_unload = len(loaded_agents) - self.max_loaded_agents
        for _, metadata in loaded_agents[:to_unload]:
            # Skip preloaded agents
            if metadata.preload:
                continue
            
            await self._unload_agent(metadata)
    
    async def _cleanup_loop(self):
        """Background task to unload unused agents."""
        while self._running:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self._cleanup_unused_agents()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_unused_agents(self):
        """Unload agents that haven't been used recently."""
        cutoff_time = datetime.now() - timedelta(minutes=self.unload_after_minutes)
        
        for metadata in self._registry.values():
            # Skip if not loaded or preloaded
            if not metadata.loaded_class or metadata.preload:
                continue
            
            # Check last used time
            if metadata.last_used and metadata.last_used < cutoff_time:
                await self._unload_agent(metadata)
    
    def get_available_agents(self) -> List[Dict[str, Any]]:
        """Get list of available agents."""
        agents = []
        
        for name, metadata in self._registry.items():
            agents.append({
                "name": name,
                "description": metadata.description,
                "capabilities": metadata.capabilities,
                "loaded": metadata.loaded_class is not None,
                "usage_count": metadata.usage_count,
                "last_used": metadata.last_used.isoformat() if metadata.last_used else None,
                "load_time_ms": metadata.load_time_ms,
                "priority": metadata.priority,
                "preload": metadata.preload
            })
        
        # Sort by priority and usage
        agents.sort(key=lambda x: (-x["priority"], -x["usage_count"]))
        
        return agents
    
    def get_stats(self) -> Dict[str, Any]:
        """Get lazy loader statistics."""
        loaded_count = sum(
            1 for m in self._registry.values()
            if m.loaded_class
        )
        
        return {
            "total_agents": len(self._registry),
            "loaded_agents": loaded_count,
            "active_instances": len(self._instances),
            "statistics": self._stats,
            "memory_usage": {
                "max_loaded_agents": self.max_loaded_agents,
                "unload_after_minutes": self.unload_after_minutes
            }
        }


# Global lazy loader instance
agent_lazy_loader = AgentLazyLoader()


async def get_agent_lazy_loader() -> AgentLazyLoader:
    """Get the global agent lazy loader instance."""
    if not agent_lazy_loader._running:
        await agent_lazy_loader.start()
    return agent_lazy_loader