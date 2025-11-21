"""
Sistema de Persistência Distribuída - Nível Enterprise
Suporte para PostgreSQL, Redis Cluster, e cache inteligente
"""

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional, Union

import aiocache
import asyncpg
import redis.asyncio as redis
import structlog
from pydantic import BaseModel, Field
from redis.asyncio.cluster import RedisCluster
from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core import json_utils

logger = structlog.get_logger(__name__)


class DatabaseConfig(BaseModel):
    """Configuração do sistema de banco de dados"""

    # PostgreSQL - Optimized pool configuration
    # Pool sizing: Hikari formula (core_count * 2) + effective_spindle_count
    # For cloud: 4 cores → 9 base * 2× safety = 18-20 connections
    postgres_url: str = "postgresql+asyncpg://user:pass@localhost:5432/cidadao_ai"
    postgres_pool_size: int = 20  # Base pool (optimized for typical load)
    postgres_max_overflow: int = 30  # Extra connections during spikes
    postgres_pool_timeout: int = 30  # Wait time for connection (seconds)

    # Redis Cluster
    redis_nodes: list[dict[str, Union[str, int]]] = [
        {"host": "localhost", "port": 7000},
        {"host": "localhost", "port": 7001},
        {"host": "localhost", "port": 7002},
    ]
    redis_password: Optional[str] = None
    redis_decode_responses: bool = True

    # Cache TTL configurations
    cache_ttl_short: int = 300  # 5 minutes
    cache_ttl_medium: int = 3600  # 1 hour
    cache_ttl_long: int = 86400  # 24 hours

    # Performance tuning
    connection_retry_attempts: int = 3
    connection_retry_delay: float = 1.0
    query_timeout: int = 30


class CacheLayer(Enum):
    """Camadas de cache com diferentes TTLs"""

    MEMORY = "memory"  # In-process cache
    REDIS = "redis"  # Distributed cache
    PERSISTENT = "db"  # Database cache


class Investigation(BaseModel):
    """Modelo para investigações"""

    id: str = Field(..., description="ID único da investigação")
    user_id: Optional[str] = Field(None, description="ID do usuário")
    query: str = Field(..., description="Query da investigação")
    status: str = Field("pending", description="Status atual")
    progress: float = Field(0.0, description="Progresso da investigação (0.0 a 1.0)")
    current_phase: str = Field("pending", description="Fase atual da investigação")
    results: Optional[dict[str, Any]] = Field(None, description="Resultados")
    summary: Optional[str] = Field(None, description="Sumário da investigação")
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    confidence_score: Optional[float] = None
    anomalies_found: int = 0
    records_processed: int = 0
    processing_time_ms: Optional[int] = None


class DatabaseManager:
    """Gerenciador avançado de banco de dados com cache distribuído"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pg_engine = None
        self.redis_cluster = None
        self.session_factory = None
        self._initialized = False

        # Métricas de performance
        self.metrics = {
            "queries_executed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_query_time": 0.0,
        }

    async def initialize(self) -> bool:
        """Inicializar todas as conexões de banco"""

        try:
            logger.info("Inicializando sistema de persistência...")

            # PostgreSQL
            await self._init_postgresql()

            # Redis Cluster
            await self._init_redis_cluster()

            # Cache layers
            await self._init_cache_layers()

            # Health checks
            await self._verify_connections()

            self._initialized = True
            logger.info("✅ Sistema de persistência inicializado com sucesso")

            return True

        except Exception as e:
            logger.error(f"❌ Falha na inicialização do banco: {e}")
            return False

    async def _init_postgresql(self):
        """Inicializar PostgreSQL com pool de conexões otimizado

        Pool configuration based on Hikari formula and production best practices.
        Total capacity: pool_size (20) + max_overflow (30) = 50 connections
        Target: 200+ concurrent requests with avg 100ms query time
        """

        self.pg_engine = create_async_engine(
            self.config.postgres_url,
            pool_size=self.config.postgres_pool_size,
            max_overflow=self.config.postgres_max_overflow,
            pool_timeout=self.config.postgres_pool_timeout,
            pool_recycle=3600,  # Recycle connections every hour (prevent stale)
            pool_pre_ping=True,  # Validate connections before use (health check)
            echo=False,  # Set True for SQL debugging
            future=True,
            connect_args={
                "server_settings": {
                    "application_name": "cidadao-ai-backend",
                    "jit": "off",  # Disable JIT for small/frequent queries
                },
                "command_timeout": 30,  # Query execution timeout
                "timeout": 10,  # Connection establishment timeout
            },
        )

        self.session_factory = sessionmaker(
            self.pg_engine, class_=AsyncSession, expire_on_commit=False
        )

        # Criar tabelas se não existirem
        await self._create_tables()

        logger.info("✅ PostgreSQL inicializado com pool otimizado")

    async def _init_redis_cluster(self):
        """Inicializar Redis Cluster"""

        try:
            # Tentar cluster primeiro
            self.redis_cluster = RedisCluster(
                startup_nodes=self.config.redis_nodes,
                password=self.config.redis_password,
                decode_responses=self.config.redis_decode_responses,
                skip_full_coverage_check=True,
                health_check_interval=30,
            )

            # Testar conexão
            await self.redis_cluster.ping()
            logger.info("✅ Redis Cluster conectado")

        except Exception as e:
            logger.warning(f"⚠️ Redis Cluster falhou, usando Redis simples: {e}")

            # Fallback para Redis simples
            node = self.config.redis_nodes[0]
            self.redis_cluster = redis.Redis(
                host=node["host"],
                port=node["port"],
                password=self.config.redis_password,
                decode_responses=self.config.redis_decode_responses,
            )

            await self.redis_cluster.ping()
            logger.info("✅ Redis simples conectado")

    async def _init_cache_layers(self):
        """Configurar camadas de cache"""

        # Memory cache
        aiocache.caches.set_config(
            {
                "default": {
                    "cache": "aiocache.SimpleMemoryCache",
                    "serializer": {"class": "aiocache.serializers.PickleSerializer"},
                },
                "redis": {
                    "cache": "aiocache.RedisCache",
                    "endpoint": self.config.redis_nodes[0]["host"],
                    "port": self.config.redis_nodes[0]["port"],
                    "serializer": {"class": "aiocache.serializers.JsonSerializer"},
                },
            }
        )

        logger.info("✅ Cache layers configurados")

    async def _create_tables(self):
        """Criar estrutura de tabelas"""

        metadata = MetaData()

        # Tabela de investigações
        investigations_table = Table(
            "investigations",
            metadata,
            Column("id", String(50), primary_key=True),
            Column("user_id", String(50), nullable=True),
            Column("query", Text, nullable=False),
            Column("status", String(20), nullable=False, default="pending"),
            Column("results", JSON, nullable=True),
            Column("metadata", JSON, nullable=True),
            Column("created_at", DateTime, nullable=False),
            Column("updated_at", DateTime, nullable=False),
            Column("completed_at", DateTime, nullable=True),
            Column("error_message", Text, nullable=True),
            Column("confidence_score", Float, nullable=True),
            Column("anomalies_found", Integer, default=0),
            Column("processing_time_ms", Integer, nullable=True),
        )

        # Tabela de audit logs
        audit_logs_table = Table(
            "audit_logs",
            metadata,
            Column("id", String(50), primary_key=True),
            Column("investigation_id", String(50), nullable=True),
            Column("agent_name", String(100), nullable=False),
            Column("action", String(100), nullable=False),
            Column("timestamp", DateTime, nullable=False),
            Column("data", JSON, nullable=True),
            Column("hash_chain", String(64), nullable=True),
        )

        # Tabela de métricas
        metrics_table = Table(
            "metrics",
            metadata,
            Column("id", String(50), primary_key=True),
            Column("metric_name", String(100), nullable=False),
            Column("metric_value", Float, nullable=False),
            Column("tags", JSON, nullable=True),
            Column("timestamp", DateTime, nullable=False),
        )

        async with self.pg_engine.begin() as conn:
            await conn.run_sync(metadata.create_all)

        logger.info("✅ Tabelas criadas/verificadas")

    async def _verify_connections(self):
        """Verificar todas as conexões"""

        # Test PostgreSQL
        async with self.session_factory() as session:
            result = await session.execute("SELECT 1")
            assert result.scalar() == 1

        # Test Redis
        pong = await self.redis_cluster.ping()
        assert pong

        logger.info("✅ Todas as conexões verificadas")

    @asynccontextmanager
    async def get_session(self):
        """Context manager para sessões do PostgreSQL"""

        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def save_investigation(self, investigation: Investigation) -> bool:
        """Salvar investigação no banco"""

        try:
            async with self.get_session() as session:
                query = """
                INSERT INTO investigations
                (id, user_id, query, status, results, metadata, created_at, updated_at,
                 completed_at, error_message, confidence_score, anomalies_found, processing_time_ms)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                ON CONFLICT (id) DO UPDATE SET
                    status = EXCLUDED.status,
                    results = EXCLUDED.results,
                    updated_at = EXCLUDED.updated_at,
                    completed_at = EXCLUDED.completed_at,
                    error_message = EXCLUDED.error_message,
                    confidence_score = EXCLUDED.confidence_score,
                    anomalies_found = EXCLUDED.anomalies_found,
                    processing_time_ms = EXCLUDED.processing_time_ms
                """

                await session.execute(
                    query,
                    [
                        investigation.id,
                        investigation.user_id,
                        investigation.query,
                        investigation.status,
                        (
                            json_utils.dumps(investigation.results)
                            if investigation.results
                            else None
                        ),
                        json_utils.dumps(investigation.metadata),
                        investigation.created_at,
                        investigation.updated_at,
                        investigation.completed_at,
                        investigation.error_message,
                        investigation.confidence_score,
                        investigation.anomalies_found,
                        investigation.processing_time_ms,
                    ],
                )

            # Cache na Redis também
            cache_key = f"investigation:{investigation.id}"
            await self.redis_cluster.setex(
                cache_key, self.config.cache_ttl_medium, investigation.model_dump_json()
            )

            logger.info(f"✅ Investigação {investigation.id} salva")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao salvar investigação {investigation.id}: {e}")
            return False

    async def get_investigation(self, investigation_id: str) -> Optional[Investigation]:
        """Buscar investigação por ID (com cache)"""

        # Tentar cache primeiro
        cache_key = f"investigation:{investigation_id}"

        try:
            cached = await self.redis_cluster.get(cache_key)
            if cached:
                self.metrics["cache_hits"] += 1
                return Investigation.model_validate_json(cached)
        except Exception:
            pass

        # Se não está no cache, buscar no banco
        self.metrics["cache_misses"] += 1

        try:
            async with self.get_session() as session:
                query = "SELECT * FROM investigations WHERE id = $1"
                result = await session.execute(query, [investigation_id])
                row = result.fetchone()

                if row:
                    investigation = Investigation(
                        id=row["id"],
                        user_id=row["user_id"],
                        query=row["query"],
                        status=row["status"],
                        results=(
                            json_utils.loads(row["results"]) if row["results"] else None
                        ),
                        metadata=(
                            json_utils.loads(row["metadata"]) if row["metadata"] else {}
                        ),
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                        completed_at=row["completed_at"],
                        error_message=row["error_message"],
                        confidence_score=row["confidence_score"],
                        anomalies_found=row["anomalies_found"],
                        processing_time_ms=row["processing_time_ms"],
                    )

                    # Adicionar ao cache
                    await self.redis_cluster.setex(
                        cache_key,
                        self.config.cache_ttl_medium,
                        investigation.model_dump_json(),
                    )

                    return investigation

        except Exception as e:
            logger.error(f"❌ Erro ao buscar investigação {investigation_id}: {e}")

        return None

    async def cache_set(
        self,
        key: str,
        value: Any,
        ttl: int = None,
        layer: CacheLayer = CacheLayer.REDIS,
    ) -> bool:
        """Cache genérico com diferentes camadas"""

        try:
            if layer == CacheLayer.REDIS:
                ttl = ttl or self.config.cache_ttl_medium
                if isinstance(value, (dict, list)):
                    value = json_utils.dumps(value)
                await self.redis_cluster.setex(key, ttl, value)
                return True

        except Exception as e:
            logger.error(f"❌ Erro ao salvar cache {key}: {e}")
            return False

    async def cache_get(
        self, key: str, layer: CacheLayer = CacheLayer.REDIS
    ) -> Optional[Any]:
        """Buscar no cache"""

        try:
            if layer == CacheLayer.REDIS:
                result = await self.redis_cluster.get(key)
                if result:
                    self.metrics["cache_hits"] += 1
                    try:
                        return json_utils.loads(result)
                    except:
                        return result
                else:
                    self.metrics["cache_misses"] += 1

        except Exception as e:
            logger.error(f"❌ Erro ao buscar cache {key}: {e}")

        return None

    async def get_health_status(self) -> dict[str, Any]:
        """Status de saúde do sistema de persistência"""

        status = {
            "postgresql": {"status": "unknown", "latency_ms": None},
            "redis": {"status": "unknown", "latency_ms": None},
            "cache_metrics": self.metrics,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Test PostgreSQL
        try:
            start_time = asyncio.get_event_loop().time()
            async with self.get_session() as session:
                await session.execute("SELECT 1")
            pg_latency = (asyncio.get_event_loop().time() - start_time) * 1000

            status["postgresql"] = {
                "status": "healthy",
                "latency_ms": round(pg_latency, 2),
            }
        except Exception as e:
            status["postgresql"] = {"status": "unhealthy", "error": str(e)}

        # Test Redis
        try:
            start_time = asyncio.get_event_loop().time()
            await self.redis_cluster.ping()
            redis_latency = (asyncio.get_event_loop().time() - start_time) * 1000

            status["redis"] = {
                "status": "healthy",
                "latency_ms": round(redis_latency, 2),
            }
        except Exception as e:
            status["redis"] = {"status": "unhealthy", "error": str(e)}

        return status

    async def cleanup(self):
        """Cleanup de recursos"""

        try:
            if self.redis_cluster:
                await self.redis_cluster.close()

            if self.pg_engine:
                await self.pg_engine.dispose()

            logger.info("✅ Cleanup do sistema de persistência concluído")

        except Exception as e:
            logger.error(f"❌ Erro no cleanup: {e}")


# Singleton instance
_db_manager: Optional[DatabaseManager] = None
_db_pool: Optional[asyncpg.Pool] = None


async def get_database_manager() -> DatabaseManager:
    """Obter instância singleton do database manager"""

    global _db_manager

    if _db_manager is None or not _db_manager._initialized:
        config = DatabaseConfig()
        _db_manager = DatabaseManager(config)
        await _db_manager.initialize()

    return _db_manager


async def get_db_pool() -> asyncpg.Pool:
    """Get PostgreSQL connection pool for direct queries"""
    global _db_pool

    if _db_pool is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        _db_pool = await asyncpg.create_pool(
            database_url,
            min_size=10,
            max_size=20,
            command_timeout=60,
            max_queries=50000,
            max_inactive_connection_lifetime=300,
        )

    return _db_pool


async def cleanup_database():
    """Cleanup global do sistema de banco"""

    global _db_manager

    if _db_manager:
        await _db_manager.cleanup()
        _db_manager = None


if __name__ == "__main__":
    # Teste do sistema
    import asyncio

    async def test_database_system():
        """Teste completo do sistema de persistência"""

        print("🧪 Testando sistema de persistência...")

        # Inicializar
        db = await get_database_manager()

        # Teste de investigação
        investigation = Investigation(
            id="test_001",
            user_id="user_123",
            query="Contratos suspeitos de 2024",
            status="completed",
            results={"anomalies": 5, "contracts": 100},
            confidence_score=0.89,
            anomalies_found=5,
            processing_time_ms=1250,
        )

        # Salvar
        success = await db.save_investigation(investigation)
        print(f"✅ Salvar investigação: {success}")

        # Buscar
        retrieved = await db.get_investigation("test_001")
        print(f"✅ Buscar investigação: {retrieved is not None}")

        # Cache test
        await db.cache_set("test_key", {"data": "test"}, ttl=60)
        cached_data = await db.cache_get("test_key")
        print(f"✅ Cache funcionando: {cached_data is not None}")

        # Health check
        health = await db.get_health_status()
        print(f"✅ Health status: {health}")

        # Cleanup
        await cleanup_database()
        print("✅ Teste concluído!")

    asyncio.run(test_database_system())
