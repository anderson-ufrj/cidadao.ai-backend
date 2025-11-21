"""
Sistema de Cache Distribuído Avançado
Multi-layer caching com Redis Cluster, invalidação inteligente e otimizações de performance
"""

import asyncio
import gzip
import hashlib
import pickle
import threading
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any, Optional, Union

import msgpack
import redis.asyncio as redis
import structlog
from aiocache import Cache
from aiocache.serializers import JsonSerializer, PickleSerializer
from pydantic import BaseModel
from redis.asyncio.cluster import RedisCluster

logger = structlog.get_logger(__name__)


class CacheLevel(Enum):
    """Níveis de cache"""

    L1_MEMORY = "l1_memory"  # In-process memory cache
    L2_REDIS = "l2_redis"  # Redis cache
    L3_PERSISTENT = "l3_persistent"  # Persistent storage


class CacheStrategy(Enum):
    """Estratégias de cache"""

    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    READ_THROUGH = "read_through"


class SerializationType(Enum):
    """Tipos de serialização"""

    JSON = "json"
    PICKLE = "pickle"
    MSGPACK = "msgpack"
    COMPRESSED = "compressed"


@dataclass
class CacheEntry:
    """Entrada do cache"""

    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    tags: list[str] = field(default_factory=list)
    size_bytes: int = 0
    hit_count: int = 0
    miss_count: int = 0


class CacheConfig(BaseModel):
    """Configuração do sistema de cache"""

    # Redis Cluster configuration
    redis_nodes: list[dict[str, Union[str, int]]] = [
        {"host": "localhost", "port": 7000},
        {"host": "localhost", "port": 7001},
        {"host": "localhost", "port": 7002},
    ]
    redis_password: Optional[str] = None
    redis_db: int = 0
    redis_decode_responses: bool = False  # Keep False for binary data

    # Cache sizes (in MB)
    l1_cache_size_mb: int = 256
    l2_cache_size_mb: int = 1024

    # TTL defaults (seconds)
    default_ttl: int = 3600
    short_ttl: int = 300
    medium_ttl: int = 1800
    long_ttl: int = 86400

    # Performance settings
    compression_threshold: int = 1024  # Compress values > 1KB
    max_value_size_mb: int = 10
    batch_size: int = 100
    pipeline_size: int = 50

    # Eviction policies
    l1_eviction_policy: CacheStrategy = CacheStrategy.LRU
    l2_eviction_policy: CacheStrategy = CacheStrategy.LFU

    # Monitoring
    enable_metrics: bool = True
    metrics_interval: int = 60
    log_slow_operations: bool = True
    slow_operation_threshold_ms: float = 100.0

    # Serialization
    default_serialization: SerializationType = SerializationType.MSGPACK
    enable_compression: bool = True


class CacheMetrics:
    """Métricas do cache"""

    def __init__(self):
        self.hits: dict[str, int] = {"l1": 0, "l2": 0, "l3": 0}
        self.misses: dict[str, int] = {"l1": 0, "l2": 0, "l3": 0}
        self.sets: dict[str, int] = {"l1": 0, "l2": 0, "l3": 0}
        self.deletes: dict[str, int] = {"l1": 0, "l2": 0, "l3": 0}
        self.errors: dict[str, int] = {"l1": 0, "l2": 0, "l3": 0}

        self.response_times: dict[str, list[float]] = {"l1": [], "l2": [], "l3": []}

        self.memory_usage: dict[str, int] = {"l1": 0, "l2": 0}
        self.evictions: dict[str, int] = {"l1": 0, "l2": 0}

        self.start_time = time.time()
        self._lock = threading.Lock()

    def record_hit(self, level: str, response_time: float = 0.0):
        with self._lock:
            self.hits[level] += 1
            if response_time > 0:
                self.response_times[level].append(response_time)
                # Keep only last 1000 measurements
                if len(self.response_times[level]) > 1000:
                    self.response_times[level] = self.response_times[level][-1000:]

    def record_miss(self, level: str):
        with self._lock:
            self.misses[level] += 1

    def record_set(self, level: str):
        with self._lock:
            self.sets[level] += 1

    def record_error(self, level: str):
        with self._lock:
            self.errors[level] += 1

    def get_hit_rate(self, level: str) -> float:
        total = self.hits[level] + self.misses[level]
        return self.hits[level] / total if total > 0 else 0.0

    def get_avg_response_time(self, level: str) -> float:
        times = self.response_times[level]
        return sum(times) / len(times) if times else 0.0

    def get_summary(self) -> dict[str, Any]:
        uptime = time.time() - self.start_time

        summary = {"uptime_seconds": uptime, "levels": {}}

        for level in ["l1", "l2", "l3"]:
            summary["levels"][level] = {
                "hits": self.hits[level],
                "misses": self.misses[level],
                "hit_rate": self.get_hit_rate(level),
                "avg_response_time_ms": self.get_avg_response_time(level) * 1000,
                "sets": self.sets[level],
                "errors": self.errors[level],
            }

        return summary


class AdvancedCacheManager:
    """Gerenciador avançado de cache distribuído"""

    def __init__(self, config: CacheConfig):
        self.config = config
        self.metrics = CacheMetrics()

        # Cache layers
        self.l1_cache: Optional[Cache] = None
        self.l2_cache: Optional[Union[redis.Redis, RedisCluster]] = None

        # Serializers
        self.serializers = {
            SerializationType.JSON: JsonSerializer(),
            SerializationType.PICKLE: PickleSerializer(),
            SerializationType.MSGPACK: self._msgpack_serializer(),
            SerializationType.COMPRESSED: self._compressed_serializer(),
        }

        # Cache entries tracking
        self.l1_entries: dict[str, CacheEntry] = {}

        # Background tasks
        self._metrics_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None

        self._initialized = False

    def _msgpack_serializer(self):
        """Serializer MsgPack customizado"""

        class MsgPackSerializer:
            def dumps(self, value):
                return msgpack.packb(value, use_bin_type=True)

            def loads(self, value):
                return msgpack.unpackb(value, raw=False)

        return MsgPackSerializer()

    def _compressed_serializer(self):
        """Serializer com compressão"""

        class CompressedSerializer:
            def dumps(self, value):
                # Use pickle then gzip
                pickled = pickle.dumps(value)
                return gzip.compress(pickled)

            def loads(self, value):
                # Decompress then unpickle
                decompressed = gzip.decompress(value)
                return pickle.loads(decompressed)

        return CompressedSerializer()

    async def initialize(self) -> bool:
        """Inicializar sistema de cache"""

        try:
            logger.info("Inicializando sistema de cache avançado...")

            # Initialize L1 cache (memory)
            await self._init_l1_cache()

            # Initialize L2 cache (Redis)
            await self._init_l2_cache()

            # Start background tasks
            await self._start_background_tasks()

            self._initialized = True
            logger.info("✅ Sistema de cache inicializado com sucesso")

            return True

        except Exception as e:
            logger.error(f"❌ Falha na inicialização do cache: {e}")
            return False

    async def _init_l1_cache(self):
        """Inicializar cache L1 (memória)"""

        self.l1_cache = Cache(
            Cache.MEMORY,
            ttl=self.config.default_ttl,
            serializer=self.serializers[self.config.default_serialization],
        )

        logger.info(f"✅ Cache L1 inicializado ({self.config.l1_cache_size_mb}MB)")

    async def _init_l2_cache(self):
        """Inicializar cache L2 (Redis)"""

        try:
            # Try Redis Cluster first
            self.l2_cache = RedisCluster(
                startup_nodes=self.config.redis_nodes,
                password=self.config.redis_password,
                decode_responses=self.config.redis_decode_responses,
                skip_full_coverage_check=True,
                health_check_interval=30,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                retry_on_timeout=True,
            )

            # Test connection
            await self.l2_cache.ping()
            logger.info("✅ Redis Cluster conectado para cache L2")

        except Exception as e:
            logger.warning(f"⚠️ Redis Cluster falhou, usando Redis simples: {e}")

            # Fallback to simple Redis
            node = self.config.redis_nodes[0]
            self.l2_cache = redis.Redis(
                host=node["host"],
                port=node["port"],
                db=self.config.redis_db,
                password=self.config.redis_password,
                decode_responses=self.config.redis_decode_responses,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                retry_on_timeout=True,
            )

            await self.l2_cache.ping()
            logger.info("✅ Redis simples conectado para cache L2")

    async def _start_background_tasks(self):
        """Iniciar tarefas de background"""

        if self.config.enable_metrics:
            self._metrics_task = asyncio.create_task(self._metrics_collection_loop())

        self._cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("✅ Tarefas de background iniciadas")

    async def get(
        self,
        key: str,
        default: Any = None,
        ttl: Optional[int] = None,
        serialization: Optional[SerializationType] = None,
    ) -> Any:
        """Buscar valor do cache com fallback multi-layer"""

        start_time = time.time()

        try:
            # Try L1 cache first
            value = await self._get_from_l1(key)
            if value is not None:
                self.metrics.record_hit("l1", time.time() - start_time)
                await self._update_access_stats(key)
                return value

            self.metrics.record_miss("l1")

            # Try L2 cache
            value = await self._get_from_l2(key, serialization)
            if value is not None:
                self.metrics.record_hit("l2", time.time() - start_time)

                # Promote to L1
                await self._set_to_l1(key, value, ttl)
                await self._update_access_stats(key)
                return value

            self.metrics.record_miss("l2")

            return default

        except Exception as e:
            logger.error(f"❌ Erro ao buscar {key}: {e}")
            self.metrics.record_error("l2")
            return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: list[str] = None,
        serialization: Optional[SerializationType] = None,
    ) -> bool:
        """Definir valor no cache"""

        try:
            ttl = ttl or self.config.default_ttl
            tags = tags or []
            serialization = serialization or self.config.default_serialization

            # Calculate size
            serialized_value = self._serialize_value(value, serialization)
            size_bytes = (
                len(serialized_value)
                if isinstance(serialized_value, bytes)
                else len(str(serialized_value))
            )

            # Check size limit
            if size_bytes > self.config.max_value_size_mb * 1024 * 1024:
                logger.warning(f"⚠️ Valor muito grande para cache: {size_bytes} bytes")
                return False

            # Set in both layers
            success_l1 = await self._set_to_l1(key, value, ttl)
            success_l2 = await self._set_to_l2(key, value, ttl, serialization)

            # Track entry
            self.l1_entries[key] = CacheEntry(
                key=key, value=value, ttl_seconds=ttl, tags=tags, size_bytes=size_bytes
            )

            if success_l1:
                self.metrics.record_set("l1")
            if success_l2:
                self.metrics.record_set("l2")

            return success_l1 or success_l2

        except Exception as e:
            logger.error(f"❌ Erro ao definir {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Deletar do cache"""

        try:
            success_l1 = await self._delete_from_l1(key)
            success_l2 = await self._delete_from_l2(key)

            # Remove from tracking
            self.l1_entries.pop(key, None)

            return success_l1 or success_l2

        except Exception as e:
            logger.error(f"❌ Erro ao deletar {key}: {e}")
            return False

    async def delete_by_tags(self, tags: list[str]) -> int:
        """Deletar entradas por tags"""

        deleted_count = 0

        # Find keys with matching tags
        keys_to_delete = []
        for key, entry in self.l1_entries.items():
            if any(tag in entry.tags for tag in tags):
                keys_to_delete.append(key)

        # Delete found keys
        for key in keys_to_delete:
            if await self.delete(key):
                deleted_count += 1

        logger.info(f"✅ Deletadas {deleted_count} entradas por tags: {tags}")
        return deleted_count

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidar chaves por padrão"""

        try:
            # Get keys matching pattern from L2
            if isinstance(self.l2_cache, RedisCluster):
                # For cluster, we need to scan all nodes
                keys = []
                for node in self.l2_cache.get_nodes():
                    node_keys = await node.keys(pattern)
                    keys.extend(node_keys)
            else:
                keys = await self.l2_cache.keys(pattern)

            # Delete all matching keys
            deleted_count = 0
            if keys:
                # Use pipeline for efficiency
                pipe = self.l2_cache.pipeline()
                for key in keys:
                    pipe.delete(key)
                    # Also delete from L1
                    await self._delete_from_l1(
                        key.decode() if isinstance(key, bytes) else key
                    )

                await pipe.execute()
                deleted_count = len(keys)

            logger.info(f"✅ Invalidadas {deleted_count} chaves com padrão: {pattern}")
            return deleted_count

        except Exception as e:
            logger.error(f"❌ Erro ao invalidar padrão {pattern}: {e}")
            return 0

    async def batch_get(self, keys: list[str]) -> dict[str, Any]:
        """Buscar múltiplas chaves em lote"""

        results = {}

        # Split into chunks
        chunk_size = self.config.batch_size
        for i in range(0, len(keys), chunk_size):
            chunk = keys[i : i + chunk_size]

            # Try L1 first
            l1_results = await self._batch_get_l1(chunk)
            results.update(l1_results)

            # Get missing keys from L2
            missing_keys = [k for k in chunk if k not in l1_results]
            if missing_keys:
                l2_results = await self._batch_get_l2(missing_keys)
                results.update(l2_results)

                # Promote L2 hits to L1
                for key, value in l2_results.items():
                    await self._set_to_l1(key, value)

        return results

    async def batch_set(self, items: dict[str, Any], ttl: Optional[int] = None) -> int:
        """Definir múltiplas chaves em lote"""

        success_count = 0

        # Split into chunks
        items_list = list(items.items())
        chunk_size = self.config.batch_size

        for i in range(0, len(items_list), chunk_size):
            chunk = dict(items_list[i : i + chunk_size])

            # Set in L1
            l1_success = await self._batch_set_l1(chunk, ttl)

            # Set in L2
            l2_success = await self._batch_set_l2(chunk, ttl)

            success_count += max(l1_success, l2_success)

        return success_count

    async def _get_from_l1(self, key: str) -> Any:
        """Buscar do cache L1"""
        if self.l1_cache:
            return await self.l1_cache.get(key)
        return None

    async def _get_from_l2(
        self, key: str, serialization: Optional[SerializationType] = None
    ) -> Any:
        """Buscar do cache L2"""
        if not self.l2_cache:
            return None

        try:
            value = await self.l2_cache.get(key)
            if value is None:
                return None

            # Deserialize
            serialization = serialization or self.config.default_serialization
            serializer = self.serializers[serialization]

            return serializer.loads(value)

        except Exception as e:
            logger.error(f"❌ Erro ao deserializar {key}: {e}")
            return None

    async def _set_to_l1(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Definir no cache L1"""
        if self.l1_cache:
            try:
                await self.l1_cache.set(key, value, ttl=ttl)
                return True
            except Exception as e:
                logger.error(f"❌ Erro L1 set {key}: {e}")
        return False

    async def _set_to_l2(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        serialization: Optional[SerializationType] = None,
    ) -> bool:
        """Definir no cache L2"""
        if not self.l2_cache:
            return False

        try:
            # Serialize
            serialization = serialization or self.config.default_serialization
            serializer = self.serializers[serialization]

            serialized_value = serializer.dumps(value)

            # Compress if needed
            if (
                self.config.enable_compression
                and len(serialized_value) > self.config.compression_threshold
            ):
                serialized_value = gzip.compress(serialized_value)
                key = f"compressed:{key}"

            # Set with TTL
            ttl = ttl or self.config.default_ttl
            await self.l2_cache.setex(key, ttl, serialized_value)

            return True

        except Exception as e:
            logger.error(f"❌ Erro L2 set {key}: {e}")
            return False

    async def _delete_from_l1(self, key: str) -> bool:
        """Deletar do cache L1"""
        if self.l1_cache:
            try:
                return await self.l1_cache.delete(key)
            except Exception:
                pass
        return False

    async def _delete_from_l2(self, key: str) -> bool:
        """Deletar do cache L2"""
        if self.l2_cache:
            try:
                result = await self.l2_cache.delete(key)
                # Also try compressed version
                await self.l2_cache.delete(f"compressed:{key}")
                return result > 0
            except Exception:
                pass
        return False

    async def _batch_get_l1(self, keys: list[str]) -> dict[str, Any]:
        """Buscar lote do L1"""
        results = {}
        if self.l1_cache:
            for key in keys:
                value = await self._get_from_l1(key)
                if value is not None:
                    results[key] = value
        return results

    async def _batch_get_l2(self, keys: list[str]) -> dict[str, Any]:
        """Buscar lote do L2"""
        results = {}
        if not self.l2_cache or not keys:
            return results

        try:
            # Use pipeline for efficiency
            pipe = self.l2_cache.pipeline()
            for key in keys:
                pipe.get(key)
                pipe.get(f"compressed:{key}")  # Also check compressed version

            values = await pipe.execute()

            # Process results
            for i, key in enumerate(keys):
                value = values[i * 2]  # Regular value
                compressed_value = values[i * 2 + 1]  # Compressed value

                if compressed_value:
                    # Decompress and deserialize
                    try:
                        decompressed = gzip.decompress(compressed_value)
                        serializer = self.serializers[self.config.default_serialization]
                        results[key] = serializer.loads(decompressed)
                    except Exception:
                        pass
                elif value:
                    # Regular deserialize
                    try:
                        serializer = self.serializers[self.config.default_serialization]
                        results[key] = serializer.loads(value)
                    except Exception:
                        pass

        except Exception as e:
            logger.error(f"❌ Erro batch get L2: {e}")

        return results

    async def _batch_set_l1(
        self, items: dict[str, Any], ttl: Optional[int] = None
    ) -> int:
        """Definir lote no L1"""
        success_count = 0
        for key, value in items.items():
            if await self._set_to_l1(key, value, ttl):
                success_count += 1
        return success_count

    async def _batch_set_l2(
        self, items: dict[str, Any], ttl: Optional[int] = None
    ) -> int:
        """Definir lote no L2"""
        if not self.l2_cache or not items:
            return 0

        try:
            # Use pipeline for efficiency
            pipe = self.l2_cache.pipeline()
            ttl = ttl or self.config.default_ttl
            serializer = self.serializers[self.config.default_serialization]

            for key, value in items.items():
                try:
                    serialized_value = serializer.dumps(value)

                    # Compress if needed
                    if (
                        self.config.enable_compression
                        and len(serialized_value) > self.config.compression_threshold
                    ):
                        serialized_value = gzip.compress(serialized_value)
                        key = f"compressed:{key}"

                    pipe.setex(key, ttl, serialized_value)

                except Exception as e:
                    logger.error(f"❌ Erro ao serializar {key}: {e}")

            results = await pipe.execute()
            return sum(1 for result in results if result)

        except Exception as e:
            logger.error(f"❌ Erro batch set L2: {e}")
            return 0

    def _serialize_value(self, value: Any, serialization: SerializationType) -> bytes:
        """Serializar valor"""
        serializer = self.serializers[serialization]
        return serializer.dumps(value)

    async def _update_access_stats(self, key: str):
        """Atualizar estatísticas de acesso"""
        if key in self.l1_entries:
            entry = self.l1_entries[key]
            entry.last_accessed = datetime.now(UTC)
            entry.access_count += 1
            entry.hit_count += 1

    async def _metrics_collection_loop(self):
        """Loop de coleta de métricas"""
        while True:
            try:
                await asyncio.sleep(self.config.metrics_interval)

                # Log metrics summary
                summary = self.metrics.get_summary()
                logger.info(f"📊 Cache metrics: {summary}")

                # Could send to monitoring system here

            except Exception as e:
                logger.error(f"❌ Erro na coleta de métricas: {e}")
                await asyncio.sleep(5)

    async def _cleanup_loop(self):
        """Loop de limpeza"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes

                # Clean up expired entries from tracking
                now = datetime.now(UTC)
                expired_keys = []

                for key, entry in self.l1_entries.items():
                    if entry.ttl_seconds:
                        expiry = entry.created_at + timedelta(seconds=entry.ttl_seconds)
                        if now > expiry:
                            expired_keys.append(key)

                for key in expired_keys:
                    del self.l1_entries[key]

                if expired_keys:
                    logger.info(
                        f"🧹 Limpeza: removidas {len(expired_keys)} entradas expiradas"
                    )

            except Exception as e:
                logger.error(f"❌ Erro na limpeza: {e}")
                await asyncio.sleep(30)

    async def get_stats(self) -> dict[str, Any]:
        """Obter estatísticas completas do cache"""

        # Basic metrics
        stats = self.metrics.get_summary()

        # L1 cache stats
        l1_size = len(self.l1_entries)
        l1_memory_usage = sum(entry.size_bytes for entry in self.l1_entries.values())

        stats["l1_cache"] = {
            "entries": l1_size,
            "memory_usage_bytes": l1_memory_usage,
            "memory_usage_mb": l1_memory_usage / (1024 * 1024),
        }

        # L2 cache stats
        if self.l2_cache:
            try:
                if isinstance(self.l2_cache, RedisCluster):
                    # Get stats from all nodes
                    l2_info = {}
                    for node in self.l2_cache.get_nodes():
                        node_info = await node.info()
                        for key, value in node_info.items():
                            if key not in l2_info:
                                l2_info[key] = 0
                            if isinstance(value, (int, float)):
                                l2_info[key] += value
                else:
                    l2_info = await self.l2_cache.info()

                stats["l2_cache"] = {
                    "connected_clients": l2_info.get("connected_clients", 0),
                    "used_memory": l2_info.get("used_memory", 0),
                    "used_memory_human": l2_info.get("used_memory_human", "0B"),
                    "keyspace_hits": l2_info.get("keyspace_hits", 0),
                    "keyspace_misses": l2_info.get("keyspace_misses", 0),
                }

            except Exception as e:
                logger.error(f"❌ Erro ao obter stats L2: {e}")
                stats["l2_cache"] = {"error": str(e)}

        return stats

    async def warm_up(self, data: dict[str, Any], ttl: Optional[int] = None):
        """Pré-carregar cache com dados"""

        logger.info(f"🔥 Aquecendo cache com {len(data)} entradas...")

        success_count = await self.batch_set(data, ttl)

        logger.info(f"✅ Cache aquecido: {success_count}/{len(data)} entradas")

    async def health_check(self) -> dict[str, Any]:
        """Health check do sistema de cache"""

        health = {
            "l1_cache": {"status": "unknown"},
            "l2_cache": {"status": "unknown"},
            "overall": {"status": "unknown"},
        }

        # Test L1
        try:
            test_key = f"health_check_{int(time.time())}"
            await self._set_to_l1(test_key, "test", 5)
            value = await self._get_from_l1(test_key)
            await self._delete_from_l1(test_key)

            health["l1_cache"] = {
                "status": "healthy" if value == "test" else "degraded"
            }
        except Exception as e:
            health["l1_cache"] = {"status": "unhealthy", "error": str(e)}

        # Test L2
        try:
            test_key = f"health_check_{int(time.time())}"
            await self._set_to_l2(test_key, "test", 5)
            value = await self._get_from_l2(test_key)
            await self._delete_from_l2(test_key)

            health["l2_cache"] = {
                "status": "healthy" if value == "test" else "degraded"
            }
        except Exception as e:
            health["l2_cache"] = {"status": "unhealthy", "error": str(e)}

        # Overall status
        l1_healthy = health["l1_cache"]["status"] == "healthy"
        l2_healthy = health["l2_cache"]["status"] == "healthy"

        if l1_healthy and l2_healthy:
            health["overall"]["status"] = "healthy"
        elif l1_healthy or l2_healthy:
            health["overall"]["status"] = "degraded"
        else:
            health["overall"]["status"] = "unhealthy"

        return health

    async def cleanup(self):
        """Cleanup de recursos"""

        try:
            # Cancel background tasks
            if self._metrics_task:
                self._metrics_task.cancel()
            if self._cleanup_task:
                self._cleanup_task.cancel()

            # Close connections
            if self.l2_cache:
                await self.l2_cache.close()

            logger.info("✅ Cleanup do sistema de cache concluído")

        except Exception as e:
            logger.error(f"❌ Erro no cleanup: {e}")


# Decorators for caching
def cached_result(ttl: int = 3600, key_prefix: str = "", tags: list[str] = None):
    """Decorator para cache automático de resultados de função"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            if args:
                key_parts.append(hashlib.md5(str(args).encode()).hexdigest()[:8])
            if kwargs:
                key_parts.append(
                    hashlib.md5(str(sorted(kwargs.items())).encode()).hexdigest()[:8]
                )

            cache_key = ":".join(filter(None, key_parts))

            # Try to get from cache
            cache_manager = await get_cache_manager()
            result = await cache_manager.get(cache_key)

            if result is not None:
                return result

            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Store in cache
            await cache_manager.set(cache_key, result, ttl, tags or [])

            return result

        return wrapper

    return decorator


# Singleton instance
_cache_manager: Optional[AdvancedCacheManager] = None


async def get_cache_manager() -> AdvancedCacheManager:
    """Obter instância singleton do cache manager"""

    global _cache_manager

    if _cache_manager is None or not _cache_manager._initialized:
        config = CacheConfig()
        _cache_manager = AdvancedCacheManager(config)
        await _cache_manager.initialize()

    return _cache_manager


async def cleanup_cache():
    """Cleanup global do sistema de cache"""

    global _cache_manager

    if _cache_manager:
        await _cache_manager.cleanup()
        _cache_manager = None


if __name__ == "__main__":
    # Teste do sistema
    import asyncio

    async def test_cache_system():
        """Teste completo do sistema de cache"""

        print("🧪 Testando sistema de cache avançado...")

        # Get cache manager
        cache = await get_cache_manager()

        # Test basic operations
        await cache.set("test_key", {"data": "test_value", "number": 42}, ttl=60)
        result = await cache.get("test_key")
        print(f"✅ Set/Get: {result}")

        # Test batch operations
        batch_data = {f"key_{i}": f"value_{i}" for i in range(10)}
        await cache.batch_set(batch_data, ttl=30)

        batch_results = await cache.batch_get(list(batch_data.keys()))
        print(f"✅ Batch operations: {len(batch_results)} items")

        # Test with compression
        large_data = {"large_payload": "x" * 2000}  # Triggers compression
        await cache.set("large_key", large_data, ttl=60)
        large_result = await cache.get("large_key")
        print(f"✅ Compression: {len(large_result['large_payload'])} chars")

        # Test cache stats
        stats = await cache.get_stats()
        print(f"✅ Stats: L1 hit rate = {stats['levels']['l1']['hit_rate']:.2%}")

        # Test health check
        health = await cache.health_check()
        print(f"✅ Health: {health['overall']['status']}")

        # Test decorator
        @cached_result(ttl=30, key_prefix="test_func")
        async def expensive_operation(x: int, y: int) -> int:
            await asyncio.sleep(0.1)  # Simulate expensive operation
            return x * y

        # First call (cache miss)
        start_time = time.time()
        result1 = await expensive_operation(5, 10)
        time1 = time.time() - start_time

        # Second call (cache hit)
        start_time = time.time()
        result2 = await expensive_operation(5, 10)
        time2 = time.time() - start_time

        print(
            f"✅ Decorator: {result1} == {result2}, time1: {time1:.3f}s, time2: {time2:.3f}s"
        )

        # Cleanup
        await cleanup_cache()
        print("✅ Teste concluído!")

    asyncio.run(test_cache_system())
