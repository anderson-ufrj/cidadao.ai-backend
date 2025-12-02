"""
Module: services.connection_pool_service
Description: Advanced connection pooling management
Author: Anderson H. Silva
Date: 2025-01-25
License: Proprietary - All rights reserved
"""

import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

import redis.asyncio as redis
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.core import get_logger
from src.core.config import settings

logger = get_logger(__name__)


class ConnectionStats:
    """Track connection pool statistics."""

    def __init__(self):
        self.connections_created = 0
        self.connections_closed = 0
        self.connections_recycled = 0
        self.connection_errors = 0
        self.wait_time_total = 0.0
        self.wait_count = 0
        self.active_connections = 0
        self.peak_connections = 0
        self.last_reset = datetime.now(UTC)

    def record_connection_created(self):
        """Record new connection creation."""
        self.connections_created += 1
        self.active_connections += 1
        self.peak_connections = max(self.peak_connections, self.active_connections)

    def record_connection_closed(self):
        """Record connection closure."""
        self.connections_closed += 1
        self.active_connections = max(0, self.active_connections - 1)

    def record_wait(self, wait_time: float):
        """Record connection wait time."""
        self.wait_time_total += wait_time
        self.wait_count += 1

    def get_stats(self) -> dict[str, Any]:
        """Get current statistics."""
        uptime = (datetime.now(UTC) - self.last_reset).total_seconds()

        return {
            "connections_created": self.connections_created,
            "connections_closed": self.connections_closed,
            "connections_recycled": self.connections_recycled,
            "connection_errors": self.connection_errors,
            "active_connections": self.active_connections,
            "peak_connections": self.peak_connections,
            "average_wait_time": self.wait_time_total / max(self.wait_count, 1),
            "total_waits": self.wait_count,
            "uptime_seconds": uptime,
            "connections_per_second": self.connections_created / max(uptime, 1),
        }


class ConnectionPoolService:
    """Advanced connection pool management service."""

    def __init__(self):
        """Initialize connection pool service."""
        self._engines: dict[str, AsyncEngine] = {}
        self._redis_pools: dict[str, redis.ConnectionPool] = {}
        self._stats: dict[str, ConnectionStats] = {}
        self._pool_configs: dict[str, dict[str, Any]] = {}

        # Default pool configurations
        self.DEFAULT_DB_POOL_CONFIG = {
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_pool_overflow,
            "pool_timeout": settings.database_pool_timeout,
            "pool_recycle": 3600,  # Recycle connections after 1 hour
            "pool_pre_ping": True,  # Test connections before use
            "echo_pool": settings.debug,
            "pool_use_lifo": True,  # Last In First Out for better cache locality
        }

        self.DEFAULT_REDIS_POOL_CONFIG = {
            "max_connections": settings.redis_pool_size,
            "decode_responses": True,
            "socket_keepalive": True,
            "socket_keepalive_options": {
                1: 1,  # TCP_KEEPIDLE
                2: 1,  # TCP_KEEPINTVL
                3: 5,  # TCP_KEEPCNT
            },
            "retry_on_timeout": True,
            "health_check_interval": 30,
        }

    async def initialize(self):
        """Initialize connection pools."""
        try:
            # Initialize main database pool
            await self.create_db_pool(
                "main",
                settings.get_database_url(async_mode=True),
                self.DEFAULT_DB_POOL_CONFIG,
            )

            # Initialize read replica pool if configured
            if hasattr(settings, "database_read_url"):
                read_config = self.DEFAULT_DB_POOL_CONFIG.copy()
                read_config["pool_size"] = (
                    settings.database_pool_size * 2
                )  # More connections for reads

                await self.create_db_pool(
                    "read", settings.database_read_url, read_config
                )

            # Initialize Redis pools
            await self.create_redis_pool(
                "main", settings.redis_url, self.DEFAULT_REDIS_POOL_CONFIG
            )

            # Initialize cache Redis pool with different settings
            cache_config = self.DEFAULT_REDIS_POOL_CONFIG.copy()
            cache_config["max_connections"] = settings.redis_pool_size * 2

            await self.create_redis_pool("cache", settings.redis_url, cache_config)

            logger.info("connection_pools_initialized")

        except Exception as e:
            logger.error(
                "connection_pool_initialization_failed", error=str(e), exc_info=True
            )
            raise

    async def create_db_pool(
        self, name: str, url: str, config: dict[str, Any]
    ) -> AsyncEngine:
        """Create database connection pool."""
        try:
            # Filter out pool-specific config when using NullPool
            nullpool_config = {
                k: v
                for k, v in config.items()
                if k
                not in ["pool_size", "max_overflow", "pool_timeout", "pool_use_lifo"]
            }

            # Create engine with async-compatible pool
            engine = create_async_engine(url, poolclass=NullPool, **nullpool_config)

            # Initialize stats
            self._stats[f"db_{name}"] = ConnectionStats()
            stats = self._stats[f"db_{name}"]

            # Add event listeners for monitoring
            @event.listens_for(engine.sync_engine, "connect")
            def on_connect(dbapi_conn, connection_record):
                stats.record_connection_created()
                connection_record.info["connected_at"] = time.time()
                logger.debug(f"Database connection created for pool '{name}'")

            @event.listens_for(engine.sync_engine, "close")
            def on_close(dbapi_conn, connection_record):
                stats.record_connection_closed()
                if "connected_at" in connection_record.info:
                    lifetime = time.time() - connection_record.info["connected_at"]
                    logger.debug(
                        f"Database connection closed for pool '{name}', lifetime: {lifetime:.1f}s"
                    )

            @event.listens_for(engine.sync_engine, "checkout")
            def on_checkout(dbapi_conn, connection_record, connection_proxy):
                connection_record.info["checkout_at"] = time.time()

            @event.listens_for(engine.sync_engine, "checkin")
            def on_checkin(dbapi_conn, connection_record):
                if "checkout_at" in connection_record.info:
                    usage_time = time.time() - connection_record.info["checkout_at"]
                    if usage_time > 1.0:  # Log slow connection usage
                        logger.warning(
                            f"Slow connection usage in pool '{name}': {usage_time:.2f}s"
                        )

            # Store engine and config
            self._engines[name] = engine
            self._pool_configs[f"db_{name}"] = config

            # Test connection
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

            logger.info(
                "database_pool_created",
                pool=name,
                size=config["pool_size"],
                max_overflow=config["max_overflow"],
            )

            return engine

        except Exception as e:
            logger.error("database_pool_creation_failed", pool=name, error=str(e))
            raise

    async def create_redis_pool(
        self, name: str, url: str, config: dict[str, Any]
    ) -> redis.ConnectionPool:
        """Create Redis connection pool."""
        try:
            # Parse password from URL if present
            if settings.redis_password:
                config["password"] = settings.redis_password.get_secret_value()

            # Create connection pool
            pool = redis.ConnectionPool.from_url(url, **config)

            # Initialize stats
            self._stats[f"redis_{name}"] = ConnectionStats()

            # Store pool and config
            self._redis_pools[name] = pool
            self._pool_configs[f"redis_{name}"] = config

            # Test connection
            client = redis.Redis(connection_pool=pool)
            await client.ping()
            await client.aclose()

            logger.info(
                "redis_pool_created",
                pool=name,
                max_connections=config["max_connections"],
            )

            return pool

        except Exception as e:
            logger.error("redis_pool_creation_failed", pool=name, error=str(e))
            raise

    @asynccontextmanager
    async def get_db_session(self, pool_name: str = "main", read_only: bool = False):
        """Get database session from pool."""
        # Use read pool if available and requested
        if read_only and "read" in self._engines:
            pool_name = "read"

        engine = self._engines.get(pool_name)
        if not engine:
            # No database available - return None
            logger.warning(
                f"Database pool '{pool_name}' not found - running without database"
            )
            yield None
            return

        # Track wait time
        start_time = time.time()

        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session() as session:
            wait_time = time.time() - start_time
            if wait_time > 0.1:
                self._stats[f"db_{pool_name}"].record_wait(wait_time)

            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def get_redis_client(self, pool_name: str = "main") -> redis.Redis:
        """Get Redis client from pool."""
        pool = self._redis_pools.get(pool_name)
        if not pool:
            raise ValueError(f"Redis pool '{pool_name}' not found")

        return redis.Redis(connection_pool=pool)

    async def get_pool_stats(self) -> dict[str, Any]:
        """Get statistics for all connection pools."""
        stats = {"database_pools": {}, "redis_pools": {}, "recommendations": []}

        # Database pool stats
        for name, engine in self._engines.items():
            pool = engine.pool
            pool_stats = self._stats.get(f"db_{name}")

            if pool_stats:
                db_stats = pool_stats.get_stats()

                # Add pool-specific stats
                if hasattr(pool, "size"):
                    db_stats["pool_size"] = pool.size()
                if hasattr(pool, "checked_out"):
                    db_stats["checked_out"] = pool.checked_out()
                if hasattr(pool, "overflow"):
                    db_stats["overflow"] = pool.overflow()

                stats["database_pools"][name] = db_stats

                # Generate recommendations
                if db_stats.get("average_wait_time", 0) > 0.5:
                    stats["recommendations"].append(
                        {
                            "pool": f"db_{name}",
                            "issue": "High wait times",
                            "suggestion": "Increase pool_size or max_overflow",
                        }
                    )

                if db_stats.get("connection_errors", 0) > 10:
                    stats["recommendations"].append(
                        {
                            "pool": f"db_{name}",
                            "issue": "High error rate",
                            "suggestion": "Check database health and network stability",
                        }
                    )

        # Redis pool stats
        for name, pool in self._redis_pools.items():
            pool_stats = self._stats.get(f"redis_{name}")

            if pool_stats:
                redis_stats = pool_stats.get_stats()

                # Add Redis-specific stats
                redis_stats["created_connections"] = pool.created_connections
                redis_stats["available_connections"] = len(pool._available_connections)
                redis_stats["in_use_connections"] = len(pool._in_use_connections)

                stats["redis_pools"][name] = redis_stats

                # Recommendations
                if redis_stats["in_use_connections"] > pool.max_connections * 0.8:
                    stats["recommendations"].append(
                        {
                            "pool": f"redis_{name}",
                            "issue": "Near connection limit",
                            "suggestion": "Increase max_connections",
                        }
                    )

        return stats

    async def optimize_pools(self) -> dict[str, Any]:
        """Analyze and optimize connection pools."""
        optimizations = {"performed": [], "suggested": []}

        # Check database pools
        for name, engine in self._engines.items():
            pool = engine.pool
            stats = self._stats.get(f"db_{name}")

            if stats:
                # Auto-adjust pool size based on usage
                current_config = self._pool_configs.get(f"db_{name}", {})
                current_size = current_config.get("pool_size", 10)

                if stats.peak_connections > current_size * 0.9:
                    suggested_size = min(current_size * 2, 50)
                    optimizations["suggested"].append(
                        {
                            "pool": f"db_{name}",
                            "action": "increase_pool_size",
                            "current": current_size,
                            "suggested": suggested_size,
                            "reason": f"Peak usage ({stats.peak_connections}) near limit",
                        }
                    )

                # Check for idle connections
                if hasattr(pool, "size") and hasattr(pool, "checked_out"):
                    idle_ratio = 1 - (pool.checked_out() / max(pool.size(), 1))
                    if idle_ratio > 0.7 and current_size > 5:
                        suggested_size = max(5, current_size // 2)
                        optimizations["suggested"].append(
                            {
                                "pool": f"db_{name}",
                                "action": "decrease_pool_size",
                                "current": current_size,
                                "suggested": suggested_size,
                                "reason": f"High idle ratio ({idle_ratio:.1%})",
                            }
                        )

        # Check Redis pools
        for name, pool in self._redis_pools.items():
            stats = self._stats.get(f"redis_{name}")

            if stats:
                current_max = pool.max_connections

                if stats.peak_connections > current_max * 0.8:
                    suggested_max = min(current_max * 2, 100)
                    optimizations["suggested"].append(
                        {
                            "pool": f"redis_{name}",
                            "action": "increase_max_connections",
                            "current": current_max,
                            "suggested": suggested_max,
                            "reason": f"Peak usage ({stats.peak_connections}) near limit",
                        }
                    )

        return optimizations

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on all pools."""
        health = {"status": "healthy", "pools": {}, "errors": []}

        # Check database pools
        for name, engine in self._engines.items():
            try:
                async with engine.connect() as conn:
                    result = await conn.execute(text("SELECT 1"))
                    health["pools"][f"db_{name}"] = {
                        "status": "healthy",
                        "response_time_ms": 0,  # Would need to measure
                    }
            except Exception as e:
                health["status"] = "unhealthy"
                health["pools"][f"db_{name}"] = {"status": "unhealthy", "error": str(e)}
                health["errors"].append(f"Database pool '{name}': {str(e)}")

        # Check Redis pools
        for name, pool in self._redis_pools.items():
            try:
                client = redis.Redis(connection_pool=pool)
                start = time.time()
                await client.ping()
                response_time = (time.time() - start) * 1000

                health["pools"][f"redis_{name}"] = {
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                }

                await client.aclose()
            except Exception as e:
                health["status"] = "unhealthy"
                health["pools"][f"redis_{name}"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                health["errors"].append(f"Redis pool '{name}': {str(e)}")

        return health

    async def cleanup(self):
        """Clean up all connection pools."""
        # Close database engines
        for name, engine in self._engines.items():
            try:
                await engine.dispose()
                logger.info(f"Database pool '{name}' closed")
            except Exception as e:
                logger.error(f"Error closing database pool '{name}': {e}")

        # Close Redis pools
        for name, pool in self._redis_pools.items():
            try:
                await pool.disconnect()
                logger.info(f"Redis pool '{name}' closed")
            except Exception as e:
                logger.error(f"Error closing Redis pool '{name}': {e}")

        self._engines.clear()
        self._redis_pools.clear()
        self._stats.clear()


# Global instance
connection_pool_service = ConnectionPoolService()
