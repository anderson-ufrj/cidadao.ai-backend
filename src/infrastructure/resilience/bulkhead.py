"""
Bulkhead pattern implementation for resource isolation.

This module provides bulkhead functionality to isolate different
types of operations and prevent resource exhaustion.
"""

import asyncio
from typing import Any, Callable, Optional, Dict, Set
from datetime import datetime, timedelta
from enum import Enum
import time
from dataclasses import dataclass
import uuid

from src.core import get_logger

logger = get_logger(__name__)


class BulkheadType(str, Enum):
    """Types of bulkhead isolation."""
    THREAD_POOL = "thread_pool"      # Thread pool isolation
    SEMAPHORE = "semaphore"          # Semaphore-based isolation
    QUEUE = "queue"                  # Queue-based isolation


@dataclass
class BulkheadConfig:
    """Bulkhead configuration."""
    max_concurrent: int = 10         # Maximum concurrent operations
    queue_size: Optional[int] = None # Queue size (None = unlimited)
    timeout: float = 30.0            # Operation timeout
    bulkhead_type: BulkheadType = BulkheadType.SEMAPHORE


@dataclass
class BulkheadStats:
    """Bulkhead statistics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rejected_requests: int = 0
    timeout_requests: int = 0
    current_active: int = 0
    current_queued: int = 0
    max_active_reached: int = 0
    max_queued_reached: int = 0
    total_wait_time_ms: float = 0.0
    total_execution_time_ms: float = 0.0


class BulkheadRejectedException(Exception):
    """Exception raised when bulkhead rejects request."""
    pass


class BulkheadTimeoutException(Exception):
    """Exception raised when operation times out."""
    pass


class Bulkhead:
    """
    Bulkhead implementation for resource isolation.
    
    Features:
    - Configurable concurrency limits
    - Queue management
    - Timeout handling
    - Performance monitoring
    - Different isolation strategies
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[BulkheadConfig] = None
    ):
        """
        Initialize bulkhead.
        
        Args:
            name: Bulkhead name for identification
            config: Configuration parameters
        """
        self.name = name
        self.config = config or BulkheadConfig()
        self.stats = BulkheadStats()
        
        # Initialize based on bulkhead type
        if self.config.bulkhead_type == BulkheadType.SEMAPHORE:
            self._semaphore = asyncio.Semaphore(self.config.max_concurrent)
        elif self.config.bulkhead_type == BulkheadType.QUEUE:
            self._queue: asyncio.Queue = asyncio.Queue(
                maxsize=self.config.queue_size or 0
            )
            self._workers: Set[asyncio.Task] = set()
            self._start_workers()
        
        self._active_operations: Set[str] = set()
        self._lock = asyncio.Lock()
        
        logger.info(f"Bulkhead '{name}' initialized with type {self.config.bulkhead_type}")
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with bulkhead protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            BulkheadRejectedException: When bulkhead rejects request
            BulkheadTimeoutException: When operation times out
        """
        operation_id = str(uuid.uuid4())
        start_time = time.time()
        
        async with self._lock:
            self.stats.total_requests += 1
        
        try:
            if self.config.bulkhead_type == BulkheadType.SEMAPHORE:
                return await self._execute_with_semaphore(
                    func, operation_id, start_time, *args, **kwargs
                )
            elif self.config.bulkhead_type == BulkheadType.QUEUE:
                return await self._execute_with_queue(
                    func, operation_id, start_time, *args, **kwargs
                )
            else:
                # Direct execution (no protection)
                return await self._execute_function(func, *args, **kwargs)
        
        except Exception as e:
            async with self._lock:
                if isinstance(e, (BulkheadRejectedException, BulkheadTimeoutException)):
                    if isinstance(e, BulkheadRejectedException):
                        self.stats.rejected_requests += 1
                    else:
                        self.stats.timeout_requests += 1
                else:
                    self.stats.failed_requests += 1
            raise
    
    async def _execute_with_semaphore(
        self,
        func: Callable,
        operation_id: str,
        start_time: float,
        *args,
        **kwargs
    ) -> Any:
        """Execute function using semaphore isolation."""
        wait_start = time.time()
        
        try:
            # Try to acquire semaphore with timeout
            await asyncio.wait_for(
                self._semaphore.acquire(),
                timeout=self.config.timeout
            )
        except asyncio.TimeoutError:
            raise BulkheadTimeoutException(
                f"Failed to acquire semaphore for bulkhead '{self.name}' "
                f"within {self.config.timeout}s"
            )
        
        wait_time = time.time() - wait_start
        
        try:
            async with self._lock:
                self.stats.current_active += 1
                self.stats.max_active_reached = max(
                    self.stats.max_active_reached,
                    self.stats.current_active
                )
                self.stats.total_wait_time_ms += wait_time * 1000
                self._active_operations.add(operation_id)
            
            # Execute function
            exec_start = time.time()
            result = await self._execute_function(func, *args, **kwargs)
            exec_time = time.time() - exec_start
            
            async with self._lock:
                self.stats.successful_requests += 1
                self.stats.total_execution_time_ms += exec_time * 1000
            
            return result
        
        finally:
            async with self._lock:
                self.stats.current_active -= 1
                self._active_operations.discard(operation_id)
            
            self._semaphore.release()
    
    async def _execute_with_queue(
        self,
        func: Callable,
        operation_id: str,
        start_time: float,
        *args,
        **kwargs
    ) -> Any:
        """Execute function using queue isolation."""
        # Create operation item
        operation = {
            "id": operation_id,
            "func": func,
            "args": args,
            "kwargs": kwargs,
            "future": asyncio.Future(),
            "submitted_at": time.time()
        }
        
        try:
            # Try to add to queue
            if self.config.queue_size and self._queue.qsize() >= self.config.queue_size:
                raise BulkheadRejectedException(
                    f"Queue full for bulkhead '{self.name}' "
                    f"(size: {self._queue.qsize()})"
                )
            
            await self._queue.put(operation)
            
            async with self._lock:
                self.stats.current_queued += 1
                self.stats.max_queued_reached = max(
                    self.stats.max_queued_reached,
                    self.stats.current_queued
                )
            
            # Wait for result with timeout
            try:
                result = await asyncio.wait_for(
                    operation["future"],
                    timeout=self.config.timeout
                )
                
                async with self._lock:
                    self.stats.successful_requests += 1
                
                return result
            
            except asyncio.TimeoutError:
                # Cancel the operation
                operation["future"].cancel()
                raise BulkheadTimeoutException(
                    f"Operation timed out in bulkhead '{self.name}' "
                    f"after {self.config.timeout}s"
                )
        
        finally:
            async with self._lock:
                if self.stats.current_queued > 0:
                    self.stats.current_queued -= 1
    
    def _start_workers(self):
        """Start worker tasks for queue processing."""
        for i in range(self.config.max_concurrent):
            worker = asyncio.create_task(
                self._worker_loop(f"worker-{i}")
            )
            self._workers.add(worker)
    
    async def _worker_loop(self, worker_name: str):
        """Worker loop for processing queued operations."""
        logger.debug(f"Worker {worker_name} started for bulkhead '{self.name}'")
        
        while True:
            try:
                # Get operation from queue
                operation = await self._queue.get()
                
                if operation is None:  # Shutdown signal
                    break
                
                operation_id = operation["id"]
                wait_time = time.time() - operation["submitted_at"]
                
                try:
                    async with self._lock:
                        self.stats.current_active += 1
                        self.stats.max_active_reached = max(
                            self.stats.max_active_reached,
                            self.stats.current_active
                        )
                        self.stats.total_wait_time_ms += wait_time * 1000
                        self._active_operations.add(operation_id)
                    
                    # Execute function
                    if not operation["future"].cancelled():
                        exec_start = time.time()
                        result = await self._execute_function(
                            operation["func"],
                            *operation["args"],
                            **operation["kwargs"]
                        )
                        exec_time = time.time() - exec_start
                        
                        operation["future"].set_result(result)
                        
                        async with self._lock:
                            self.stats.total_execution_time_ms += exec_time * 1000
                
                except Exception as e:
                    if not operation["future"].cancelled():
                        operation["future"].set_exception(e)
                    
                    async with self._lock:
                        self.stats.failed_requests += 1
                
                finally:
                    async with self._lock:
                        self.stats.current_active -= 1
                        self._active_operations.discard(operation_id)
                    
                    self._queue.task_done()
            
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
    
    async def _execute_function(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function, handling both sync and async functions."""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            # Run sync function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, func, *args, **kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bulkhead statistics."""
        success_rate = (
            self.stats.successful_requests / self.stats.total_requests
            if self.stats.total_requests > 0 else 0
        )
        
        avg_wait_time = (
            self.stats.total_wait_time_ms / self.stats.total_requests
            if self.stats.total_requests > 0 else 0
        )
        
        avg_exec_time = (
            self.stats.total_execution_time_ms / self.stats.successful_requests
            if self.stats.successful_requests > 0 else 0
        )
        
        return {
            "name": self.name,
            "type": self.config.bulkhead_type.value,
            "config": {
                "max_concurrent": self.config.max_concurrent,
                "queue_size": self.config.queue_size,
                "timeout": self.config.timeout
            },
            "stats": {
                "total_requests": self.stats.total_requests,
                "successful_requests": self.stats.successful_requests,
                "failed_requests": self.stats.failed_requests,
                "rejected_requests": self.stats.rejected_requests,
                "timeout_requests": self.stats.timeout_requests,
                "success_rate": success_rate,
                "current_active": self.stats.current_active,
                "current_queued": self.stats.current_queued,
                "max_active_reached": self.stats.max_active_reached,
                "max_queued_reached": self.stats.max_queued_reached,
                "avg_wait_time_ms": avg_wait_time,
                "avg_execution_time_ms": avg_exec_time
            }
        }
    
    async def shutdown(self):
        """Shutdown bulkhead and cleanup resources."""
        if self.config.bulkhead_type == BulkheadType.QUEUE:
            # Signal workers to stop
            for _ in self._workers:
                await self._queue.put(None)
            
            # Wait for workers to finish
            await asyncio.gather(*self._workers, return_exceptions=True)
            self._workers.clear()
        
        logger.info(f"Bulkhead '{self.name}' shut down")


class BulkheadManager:
    """
    Manager for multiple bulkheads.
    
    Provides centralized management and monitoring of bulkheads.
    """
    
    def __init__(self):
        """Initialize bulkhead manager."""
        self._bulkheads: Dict[str, Bulkhead] = {}
        self._default_configs: Dict[str, BulkheadConfig] = {}
    
    def register_default_config(
        self,
        resource_type: str,
        config: BulkheadConfig
    ):
        """
        Register default configuration for a resource type.
        
        Args:
            resource_type: Resource type name
            config: Default configuration
        """
        self._default_configs[resource_type] = config
        logger.info(f"Registered default bulkhead config for '{resource_type}'")
    
    def get_bulkhead(
        self,
        resource_type: str,
        config: Optional[BulkheadConfig] = None
    ) -> Bulkhead:
        """
        Get or create bulkhead for resource type.
        
        Args:
            resource_type: Resource type name
            config: Configuration (uses default if not provided)
            
        Returns:
            Bulkhead instance
        """
        if resource_type not in self._bulkheads:
            # Use provided config or default
            bulkhead_config = (
                config or 
                self._default_configs.get(resource_type) or 
                BulkheadConfig()
            )
            
            self._bulkheads[resource_type] = Bulkhead(
                resource_type,
                bulkhead_config
            )
        
        return self._bulkheads[resource_type]
    
    async def execute_with_bulkhead(
        self,
        resource_type: str,
        func: Callable,
        *args,
        config: Optional[BulkheadConfig] = None,
        **kwargs
    ) -> Any:
        """
        Execute function with bulkhead protection.
        
        Args:
            resource_type: Resource type name
            func: Function to execute
            *args: Function arguments
            config: Optional configuration
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        bulkhead = self.get_bulkhead(resource_type, config)
        return await bulkhead.execute(func, *args, **kwargs)
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all bulkheads."""
        return {
            name: bulkhead.get_stats()
            for name, bulkhead in self._bulkheads.items()
        }
    
    async def shutdown_all(self):
        """Shutdown all bulkheads."""
        for bulkhead in self._bulkheads.values():
            await bulkhead.shutdown()
        
        logger.info("All bulkheads shut down")
    
    def get_resource_utilization(self) -> Dict[str, Any]:
        """Get resource utilization across all bulkheads."""
        total_capacity = 0
        total_active = 0
        total_queued = 0
        
        resource_stats = {}
        
        for name, bulkhead in self._bulkheads.items():
            stats = bulkhead.get_stats()
            capacity = stats["config"]["max_concurrent"]
            active = stats["stats"]["current_active"]
            queued = stats["stats"]["current_queued"]
            
            total_capacity += capacity
            total_active += active
            total_queued += queued
            
            resource_stats[name] = {
                "utilization": active / capacity if capacity > 0 else 0,
                "active": active,
                "capacity": capacity,
                "queued": queued
            }
        
        overall_utilization = (
            total_active / total_capacity if total_capacity > 0 else 0
        )
        
        return {
            "overall_utilization": overall_utilization,
            "total_capacity": total_capacity,
            "total_active": total_active,
            "total_queued": total_queued,
            "resources": resource_stats
        }


# Global bulkhead manager
bulkhead_manager = BulkheadManager()


# Pre-configured bulkheads for common resource types
def setup_default_bulkheads():
    """Setup default bulkhead configurations."""
    
    # Database operations
    bulkhead_manager.register_default_config(
        "database",
        BulkheadConfig(
            max_concurrent=20,
            queue_size=100,
            timeout=30.0,
            bulkhead_type=BulkheadType.SEMAPHORE
        )
    )
    
    # External API calls
    bulkhead_manager.register_default_config(
        "external_api",
        BulkheadConfig(
            max_concurrent=10,
            queue_size=50,
            timeout=15.0,
            bulkhead_type=BulkheadType.QUEUE
        )
    )
    
    # LLM operations
    bulkhead_manager.register_default_config(
        "llm_operations",
        BulkheadConfig(
            max_concurrent=5,
            queue_size=20,
            timeout=60.0,
            bulkhead_type=BulkheadType.QUEUE
        )
    )
    
    # File operations
    bulkhead_manager.register_default_config(
        "file_operations",
        BulkheadConfig(
            max_concurrent=15,
            timeout=30.0,
            bulkhead_type=BulkheadType.SEMAPHORE
        )
    )
    
    # Analytics operations
    bulkhead_manager.register_default_config(
        "analytics",
        BulkheadConfig(
            max_concurrent=8,
            queue_size=30,
            timeout=120.0,
            bulkhead_type=BulkheadType.QUEUE
        )
    )


# Initialize default configurations
setup_default_bulkheads()


# Convenience decorator
def bulkhead(
    resource_type: str,
    config: Optional[BulkheadConfig] = None
):
    """
    Decorator to protect functions with bulkhead.
    
    Args:
        resource_type: Resource type for bulkhead
        config: Optional configuration
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await bulkhead_manager.execute_with_bulkhead(
                resource_type, func, *args, config=config, **kwargs
            )
        return wrapper
    return decorator