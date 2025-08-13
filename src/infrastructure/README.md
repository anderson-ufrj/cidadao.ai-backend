# 🏗️ Cidadão.AI Infrastructure Layer

## 📋 Overview

The **Infrastructure Layer** provides enterprise-grade **distributed persistence**, **caching**, and **system orchestration** for the Cidadão.AI platform. Built with **PostgreSQL**, **Redis Cluster**, and **advanced caching strategies** to support high-performance, scalable transparency analysis.

## 🏗️ Architecture

```
src/infrastructure/
├── database.py          # Distributed persistence manager
├── cache_system.py      # Multi-layer caching system
├── monitoring.py        # System health & metrics
├── orchestrator.py      # Agent orchestration
└── agent_pool.py        # Agent pool management
```

## 💾 Database Architecture (database.py)

### Enterprise Distributed Persistence System

The database system implements a **sophisticated multi-layer architecture** designed for:
- **High Availability**: PostgreSQL with connection pooling
- **Distributed Caching**: Redis Cluster with intelligent fallback
- **Performance**: Multi-layer cache with configurable TTLs
- **Reliability**: Automatic retry mechanisms and circuit breakers

### Core Components

#### 1. **DatabaseManager** - Central Persistence Controller
```python
class DatabaseManager:
    """
    Advanced database manager with distributed persistence
    
    Features:
    - PostgreSQL async connection pooling
    - Redis Cluster with automatic failover
    - Multi-layer caching (memory + distributed)
    - Performance metrics and monitoring
    - Automatic retry and circuit breaking
    - Health checks and diagnostics
    """
    
    def __init__(self, config: DatabaseConfig):
        self.pg_engine = None              # PostgreSQL async engine
        self.redis_cluster = None          # Redis Cluster client
        self.session_factory = None        # SQLAlchemy session factory
        self.metrics = {                   # Performance tracking
            "queries_executed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_query_time": 0.0
        }
```

#### 2. **DatabaseConfig** - Configuration Management
```python
class DatabaseConfig(BaseModel):
    """Comprehensive database configuration"""
    
    # PostgreSQL Configuration
    postgres_url: str = "postgresql+asyncpg://user:pass@localhost:5432/cidadao_ai"
    postgres_pool_size: int = 20           # Connection pool size
    postgres_max_overflow: int = 30        # Additional connections allowed
    postgres_pool_timeout: int = 30        # Connection timeout (seconds)
    
    # Redis Cluster Configuration
    redis_nodes: List[Dict[str, Union[str, int]]] = [
        {"host": "localhost", "port": 7000},
        {"host": "localhost", "port": 7001},
        {"host": "localhost", "port": 7002}
    ]
    redis_password: Optional[str] = None
    redis_decode_responses: bool = True
    
    # Cache TTL Strategies
    cache_ttl_short: int = 300             # 5 minutes - Frequently changing data
    cache_ttl_medium: int = 3600           # 1 hour - Moderately stable data
    cache_ttl_long: int = 86400            # 24 hours - Stable reference data
    
    # Performance Tuning
    connection_retry_attempts: int = 3
    connection_retry_delay: float = 1.0
    query_timeout: int = 30
```

### Data Models

#### **Investigation** - Core Investigation Entity
```python
class Investigation(BaseModel):
    """Primary data model for transparency investigations"""
    
    # Identity & Ownership
    id: str                                # Unique investigation ID (UUID)
    user_id: Optional[str] = None          # User who initiated
    
    # Investigation Details
    query: str                             # Original query/request
    status: str = "pending"                # Current status
    results: Optional[Dict[str, Any]] = None  # Analysis results
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional context
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Analysis Results
    error_message: Optional[str] = None    # Error details if failed
    confidence_score: Optional[float] = None  # Result confidence (0-1)
    anomalies_found: int = 0               # Number of anomalies detected
    processing_time_ms: Optional[int] = None  # Processing duration
```

**Investigation Status Lifecycle:**
```
pending → processing → completed
                   ↓
                 error
```

### Database Tables

#### **Investigations Table**
```sql
CREATE TABLE investigations (
    id VARCHAR(50) PRIMARY KEY,                    -- Investigation UUID
    user_id VARCHAR(50),                           -- User identifier
    query TEXT NOT NULL,                           -- Investigation query
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- Current status
    results JSON,                                  -- Analysis results (JSONB)
    metadata JSON,                                 -- Investigation metadata
    created_at TIMESTAMP NOT NULL,                 -- Creation timestamp
    updated_at TIMESTAMP NOT NULL,                 -- Last update
    completed_at TIMESTAMP,                        -- Completion timestamp
    error_message TEXT,                            -- Error details
    confidence_score FLOAT,                        -- Result confidence
    anomalies_found INTEGER DEFAULT 0,             -- Anomaly count
    processing_time_ms INTEGER                     -- Processing duration
);

-- Indexes for performance
CREATE INDEX idx_investigations_user_id ON investigations(user_id);
CREATE INDEX idx_investigations_status ON investigations(status);
CREATE INDEX idx_investigations_created_at ON investigations(created_at);
CREATE INDEX idx_investigations_confidence ON investigations(confidence_score);
```

#### **Audit Logs Table**
```sql
CREATE TABLE audit_logs (
    id VARCHAR(50) PRIMARY KEY,           -- Audit event UUID
    investigation_id VARCHAR(50),         -- Related investigation
    agent_name VARCHAR(100) NOT NULL,     -- Agent that performed action
    action VARCHAR(100) NOT NULL,         -- Action performed
    timestamp TIMESTAMP NOT NULL,         -- When action occurred
    data JSON,                            -- Action details
    hash_chain VARCHAR(64)                -- Cryptographic hash chain
);

-- Indexes for audit queries
CREATE INDEX idx_audit_investigation ON audit_logs(investigation_id);
CREATE INDEX idx_audit_agent ON audit_logs(agent_name);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
```

#### **Metrics Table**
```sql
CREATE TABLE metrics (
    id VARCHAR(50) PRIMARY KEY,           -- Metric event UUID
    metric_name VARCHAR(100) NOT NULL,    -- Metric identifier
    metric_value FLOAT NOT NULL,          -- Metric value
    tags JSON,                            -- Metric tags/dimensions
    timestamp TIMESTAMP NOT NULL         -- Measurement timestamp
);
```

## 🚀 Advanced Features

### 1. **Distributed Caching Strategy**

#### Multi-Layer Cache Architecture
```python
class CacheLayer(Enum):
    MEMORY = "memory"        # In-process cache (fastest, smallest)
    REDIS = "redis"          # Distributed cache (fast, shared)
    PERSISTENT = "db"        # Database cache (slow, permanent)

# Cache hierarchy with automatic fallback
async def get_cached_data(key: str) -> Optional[Any]:
    """Intelligent cache retrieval with layer fallback"""
    
    # 1. Try memory cache first (microseconds)
    result = await memory_cache.get(key)
    if result:
        return result
    
    # 2. Try Redis cache (milliseconds)
    result = await redis_cache.get(key)
    if result:
        # Populate memory cache for next time
        await memory_cache.set(key, result, ttl=300)
        return result
    
    # 3. Cache miss - fetch from database
    return None
```

#### TTL Strategy by Data Type
```python
# Strategic cache TTL based on data volatility
CACHE_STRATEGIES = {
    "investigation_results": {
        "ttl": 3600,                    # 1 hour - stable after completion
        "layer": CacheLayer.REDIS
    },
    "api_responses": {
        "ttl": 1800,                    # 30 minutes - external API data
        "layer": CacheLayer.REDIS
    },
    "user_sessions": {
        "ttl": 300,                     # 5 minutes - frequently updated
        "layer": CacheLayer.MEMORY
    },
    "reference_data": {
        "ttl": 86400,                   # 24 hours - static data
        "layer": CacheLayer.REDIS
    }
}
```

### 2. **Connection Management**

#### PostgreSQL Connection Pooling
```python
# Advanced connection pool configuration  
engine = create_async_engine(
    database_url,
    pool_size=20,                       # Base connection pool
    max_overflow=30,                    # Additional connections under load
    pool_timeout=30,                    # Wait time for connection
    pool_recycle=3600,                  # Recycle connections hourly
    pool_pre_ping=True,                 # Validate connections
    echo=False                          # SQL logging (disable in production)
)

# Session management with automatic cleanup
@asynccontextmanager
async def get_session():
    """Database session with automatic transaction management"""
    
    async with session_factory() as session:
        try:
            yield session
            await session.commit()          # Auto-commit on success
        except Exception:
            await session.rollback()        # Auto-rollback on error
            raise
        finally:
            await session.close()           # Always cleanup
```

#### Redis Cluster with Failover
```python
async def _init_redis_cluster(self):
    """Initialize Redis with cluster failover"""
    
    try:
        # Primary: Redis Cluster for high availability
        self.redis_cluster = RedisCluster(
            startup_nodes=self.config.redis_nodes,
            password=self.config.redis_password,
            decode_responses=True,
            skip_full_coverage_check=True,  # Allow partial clusters
            health_check_interval=30        # Regular health checks
        )
        
        await self.redis_cluster.ping()
        logger.info("✅ Redis Cluster connected")
        
    except Exception as e:
        logger.warning(f"⚠️ Cluster failed, using single Redis: {e}")
        
        # Fallback: Single Redis node
        node = self.config.redis_nodes[0]
        self.redis_cluster = redis.Redis(
            host=node["host"],
            port=node["port"],
            password=self.config.redis_password,
            decode_responses=True
        )
        
        await self.redis_cluster.ping()
        logger.info("✅ Redis fallback connected")
```

### 3. **High-Performance Operations**

#### Bulk Investigation Saving with UPSERT
```python
async def save_investigation(self, investigation: Investigation) -> bool:
    """
    High-performance investigation storage with UPSERT
    
    Features:
    - PostgreSQL UPSERT (INSERT ... ON CONFLICT)
    - Automatic Redis cache population
    - Performance metrics tracking
    - Error handling with rollback
    """
    
    try:
        async with self.get_session() as session:
            # UPSERT query for PostgreSQL
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
            
            await session.execute(query, [
                investigation.id,
                investigation.user_id,
                investigation.query,
                investigation.status,
                json.dumps(investigation.results) if investigation.results else None,
                json.dumps(investigation.metadata),
                investigation.created_at,
                investigation.updated_at,
                investigation.completed_at,
                investigation.error_message,
                investigation.confidence_score,
                investigation.anomalies_found,
                investigation.processing_time_ms
            ])
        
        # Cache in Redis for fast retrieval
        cache_key = f"investigation:{investigation.id}"
        await self.redis_cluster.setex(
            cache_key,
            self.config.cache_ttl_medium,  # 1 hour TTL
            investigation.model_dump_json()
        )
        
        logger.info(f"✅ Investigation {investigation.id} saved")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error saving investigation {investigation.id}: {e}")
        return False
```

#### Intelligent Cache Retrieval
```python
async def get_investigation(self, investigation_id: str) -> Optional[Investigation]:
    """
    Multi-layer investigation retrieval with cache population
    
    Strategy:
    1. Check Redis cache first (fast)
    2. If cache miss, query PostgreSQL
    3. Populate cache with result
    4. Track cache hit/miss metrics
    """
    
    cache_key = f"investigation:{investigation_id}"
    
    # Try cache first
    try:
        cached = await self.redis_cluster.get(cache_key)
        if cached:
            self.metrics["cache_hits"] += 1
            return Investigation.model_validate_json(cached)
    except Exception:
        pass  # Cache error, continue to database
    
    # Cache miss - query database
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
                    results=json.loads(row["results"]) if row["results"] else None,
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    completed_at=row["completed_at"],
                    error_message=row["error_message"],
                    confidence_score=row["confidence_score"],
                    anomalies_found=row["anomalies_found"],
                    processing_time_ms=row["processing_time_ms"]
                )
                
                # Populate cache for future requests
                await self.redis_cluster.setex(
                    cache_key,
                    self.config.cache_ttl_medium,
                    investigation.model_dump_json()
                )
                
                return investigation
                
    except Exception as e:
        logger.error(f"❌ Error retrieving investigation {investigation_id}: {e}")
    
    return None
```

### 4. **Generic Cache Operations**

```python
async def cache_set(
    self, 
    key: str, 
    value: Any, 
    ttl: int = None, 
    layer: CacheLayer = CacheLayer.REDIS
) -> bool:
    """Generic cache storage with layer selection"""
    
    try:
        if layer == CacheLayer.REDIS:
            ttl = ttl or self.config.cache_ttl_medium
            
            # Serialize complex objects
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif isinstance(value, BaseModel):
                value = value.model_dump_json()
                
            await self.redis_cluster.setex(key, ttl, value)
            return True
            
    except Exception as e:
        logger.error(f"❌ Cache set error for {key}: {e}")
        return False

async def cache_get(self, key: str, layer: CacheLayer = CacheLayer.REDIS) -> Optional[Any]:
    """Generic cache retrieval with automatic deserialization"""
    
    try:
        if layer == CacheLayer.REDIS:
            result = await self.redis_cluster.get(key)
            if result:
                self.metrics["cache_hits"] += 1
                
                # Try to deserialize JSON
                try:
                    return json.loads(result)
                except json.JSONDecodeError:
                    return result  # Return raw string if not JSON
            else:
                self.metrics["cache_misses"] += 1
                
    except Exception as e:
        logger.error(f"❌ Cache get error for {key}: {e}")
    
    return None
```

## 📊 System Health & Monitoring

### Comprehensive Health Checks
```python
async def get_health_status(self) -> Dict[str, Any]:
    """Complete system health assessment"""
    
    status = {
        "postgresql": {"status": "unknown", "latency_ms": None},
        "redis": {"status": "unknown", "latency_ms": None},
        "cache_metrics": self.metrics,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # PostgreSQL Health Check
    try:
        start_time = asyncio.get_event_loop().time()
        async with self.get_session() as session:
            await session.execute("SELECT 1")
        pg_latency = (asyncio.get_event_loop().time() - start_time) * 1000
        
        status["postgresql"] = {
            "status": "healthy",
            "latency_ms": round(pg_latency, 2),
            "pool_size": self.pg_engine.pool.size(),
            "pool_checked_in": self.pg_engine.pool.checkedin(),
            "pool_checked_out": self.pg_engine.pool.checkedout()
        }
    except Exception as e:
        status["postgresql"] = {"status": "unhealthy", "error": str(e)}
    
    # Redis Health Check
    try:
        start_time = asyncio.get_event_loop().time()
        await self.redis_cluster.ping()
        redis_latency = (asyncio.get_event_loop().time() - start_time) * 1000
        
        # Get Redis info
        info = await self.redis_cluster.info()
        
        status["redis"] = {
            "status": "healthy",
            "latency_ms": round(redis_latency, 2),
            "connected_clients": info.get("connected_clients", 0),
            "used_memory": info.get("used_memory_human", "unknown"),
            "uptime": info.get("uptime_in_seconds", 0)
        }
    except Exception as e:
        status["redis"] = {"status": "unhealthy", "error": str(e)}
    
    return status
```

### Performance Metrics
```python
# Real-time performance tracking
class PerformanceMetrics:
    def __init__(self):
        self.metrics = {
            "queries_executed": 0,          # Total database queries
            "cache_hits": 0,                # Cache hit count
            "cache_misses": 0,              # Cache miss count
            "avg_query_time": 0.0,          # Average query time (ms)
            "total_investigations": 0,       # Total investigations processed
            "active_connections": 0,         # Current DB connections
            "error_rate": 0.0               # Error percentage
        }
    
    def calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage"""
        total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        if total == 0:
            return 0.0
        return (self.metrics["cache_hits"] / total) * 100
    
    def update_avg_query_time(self, new_time: float):
        """Update rolling average query time"""
        current_avg = self.metrics["avg_query_time"]
        queries = self.metrics["queries_executed"]
        
        self.metrics["avg_query_time"] = (
            (current_avg * queries + new_time) / (queries + 1)
        )
        self.metrics["queries_executed"] += 1
```

## 🚀 Usage Examples

### Basic Database Operations
```python
from src.infrastructure.database import get_database_manager, Investigation

async def main():
    # Get database manager (singleton pattern)
    db = await get_database_manager()
    
    # Create investigation
    investigation = Investigation(
        id="inv_001",
        user_id="user_123",
        query="Analyze Ministry of Health contracts 2024",
        status="pending",
        metadata={"priority": "high", "data_source": "contracts"}
    )
    
    # Save to database (with automatic caching)
    success = await db.save_investigation(investigation)
    print(f"Investigation saved: {success}")
    
    # Retrieve (automatic cache usage)
    retrieved = await db.get_investigation("inv_001")
    print(f"Retrieved: {retrieved.query}")
    
    # Generic caching
    await db.cache_set("analysis_results", {"anomalies": 5}, ttl=3600)
    results = await db.cache_get("analysis_results")
    print(f"Cached results: {results}")
    
    # Health check
    health = await db.get_health_status()
    print(f"System health: {health}")
```

### Advanced Usage Patterns
```python
# Batch processing with connection management
async def process_investigations_batch(investigations: List[Investigation]):
    """Process multiple investigations efficiently"""
    
    db = await get_database_manager()
    
    # Process in parallel with connection pooling
    save_tasks = [
        db.save_investigation(inv) 
        for inv in investigations
    ]
    
    results = await asyncio.gather(*save_tasks, return_exceptions=True)
    
    success_count = sum(1 for r in results if r is True)
    print(f"Saved {success_count}/{len(investigations)} investigations")

# Smart caching for expensive operations
async def get_or_compute_analysis(analysis_id: str):
    """Get analysis from cache or compute if needed"""
    
    db = await get_database_manager()
    cache_key = f"analysis:{analysis_id}"
    
    # Try cache first
    cached_result = await db.cache_get(cache_key)
    if cached_result:
        return cached_result
    
    # Compute expensive analysis
    result = await perform_expensive_analysis(analysis_id)
    
    # Cache for 1 hour
    await db.cache_set(cache_key, result, ttl=3600)
    
    return result
```

## 🔧 Configuration & Deployment

### Environment Configuration
```bash
# PostgreSQL Configuration
DATABASE_URL=postgresql+asyncpg://cidadao:password@localhost:5432/cidadao_ai
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30

# Redis Cluster Configuration
REDIS_NODES=localhost:7000,localhost:7001,localhost:7002
REDIS_PASSWORD=redis_password
REDIS_DECODE_RESPONSES=true

# Cache TTL Configuration
CACHE_TTL_SHORT=300
CACHE_TTL_MEDIUM=3600
CACHE_TTL_LONG=86400

# Performance Tuning
CONNECTION_RETRY_ATTEMPTS=3
CONNECTION_RETRY_DELAY=1.0
QUERY_TIMEOUT=30
```

### Docker Deployment
```yaml
# docker-compose.yml for infrastructure services
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: cidadao_ai
      POSTGRES_USER: cidadao
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    command: |
      postgres -c max_connections=100
               -c shared_buffers=256MB
               -c effective_cache_size=1GB
               -c work_mem=4MB
  
  redis-node-1:
    image: redis:7
    ports:
      - "7000:7000"
    command: |
      redis-server --port 7000
                   --cluster-enabled yes
                   --cluster-config-file nodes.conf
                   --cluster-node-timeout 5000
                   --appendonly yes
  
  redis-node-2:
    image: redis:7
    ports:
      - "7001:7001"
    command: |
      redis-server --port 7001
                   --cluster-enabled yes
                   --cluster-config-file nodes.conf
                   --cluster-node-timeout 5000
                   --appendonly yes
  
  redis-node-3:
    image: redis:7
    ports:
      - "7002:7002"
    command: |
      redis-server --port 7002
                   --cluster-enabled yes
                   --cluster-config-file nodes.conf
                   --cluster-node-timeout 5000
                   --appendonly yes

volumes:
  postgres_data:
```

### Performance Tuning
```python
# Production-optimized configuration
PRODUCTION_CONFIG = DatabaseConfig(
    # PostgreSQL optimizations
    postgres_pool_size=50,                 # Higher connection pool
    postgres_max_overflow=50,              # More overflow connections
    postgres_pool_timeout=60,              # Longer timeout
    
    # Cache optimizations
    cache_ttl_short=600,                   # 10 minutes
    cache_ttl_medium=7200,                 # 2 hours
    cache_ttl_long=172800,                 # 48 hours
    
    # Retry configuration
    connection_retry_attempts=5,
    connection_retry_delay=2.0,
    query_timeout=60
)
```

## 🧪 Testing Infrastructure

```python
# Test database setup with TestContainers
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

@pytest.fixture
async def test_database():
    """Test database with real PostgreSQL"""
    
    with PostgresContainer("postgres:16") as postgres:
        config = DatabaseConfig(
            postgres_url=postgres.get_connection_url().replace(
                "postgresql://", "postgresql+asyncpg://"
            )
        )
        
        db = DatabaseManager(config)
        await db.initialize()
        
        yield db
        
        await db.cleanup()

@pytest.fixture
async def test_redis():
    """Test Redis with real Redis container"""
    
    with RedisContainer() as redis:
        config = DatabaseConfig(
            redis_nodes=[{
                "host": redis.get_container_host_ip(),
                "port": redis.get_exposed_port(6379)
            }]
        )
        
        db = DatabaseManager(config)
        await db._init_redis_cluster()
        
        yield db.redis_cluster
        
        await db.redis_cluster.close()
```

---

This infrastructure layer provides **enterprise-grade persistence** with **intelligent caching**, **high availability**, and **comprehensive monitoring** - essential for the demanding requirements of transparency analysis at scale.