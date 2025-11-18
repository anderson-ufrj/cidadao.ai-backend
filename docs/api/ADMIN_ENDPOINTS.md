# Admin Endpoints Documentation

**Base Path**: `/api/v1/admin`
**Authentication**: Requires admin privileges (via `require_admin` dependency)
**Total Endpoints**: 36 endpoints across 6 modules

---

## 📋 Table of Contents

1. [Agent Lazy Loading](#agent-lazy-loading) - 7 endpoints
2. [Cache Warming](#cache-warming) - 5 endpoints
3. [Compression](#compression) - 4 endpoints
4. [Connection Pools](#connection-pools) - 6 endpoints
5. [Database Optimization](#database-optimization) - 5 endpoints
6. [IP Whitelist](#ip-whitelist) - 9 endpoints

---

## 🤖 Agent Lazy Loading

**Module**: `src/api/routes/admin/agent_lazy_loading.py`
**Purpose**: Manage agent lazy loading, memory optimization, and performance

### Endpoints

#### `GET /agent-lazy-loading/status`
Get lazy loading status and statistics.

**Response**:
```json
{
  "loaded_agents": ["zumbi", "anita"],
  "total_loaded": 2,
  "total_available": 16,
  "memory_usage_mb": 245.6,
  "config": {
    "unload_after_minutes": 15,
    "max_loaded_agents": 10
  },
  "statistics": {
    "total_loads": 45,
    "total_unloads": 23,
    "cache_hits": 892,
    "cache_misses": 12
  }
}
```

#### `POST /agent-lazy-loading/load`
Load a specific agent into memory.

**Request Body**:
```json
{
  "agent_name": "tiradentes"
}
```

**Response**:
```json
{
  "success": true,
  "agent_name": "tiradentes",
  "load_time_ms": 234.5,
  "memory_usage_mb": 12.3
}
```

#### `POST /agent-lazy-loading/unload`
Unload an agent from memory.

**Request Body**:
```json
{
  "agent_name": "tiradentes",
  "force": false
}
```

**Response**:
```json
{
  "success": true,
  "agent_name": "tiradentes",
  "freed_memory_mb": 12.3
}
```

#### `POST /agent-lazy-loading/preload-all`
Preload all agents into memory (useful for warming up after deployment).

**Response**:
```json
{
  "success": true,
  "loaded_agents": ["zumbi", "anita", "tiradentes", ...],
  "total_loaded": 16,
  "total_time_ms": 1234.5
}
```

#### `PUT /agent-lazy-loading/config`
Update lazy loading configuration.

**Request Body**:
```json
{
  "unload_after_minutes": 20,
  "max_loaded_agents": 12,
  "preload_agents": ["zumbi", "anita"]
}
```

#### `POST /agent-lazy-loading/cleanup`
Force cleanup of inactive agents.

**Response**:
```json
{
  "unloaded_agents": ["drummond", "nana"],
  "freed_memory_mb": 24.6
}
```

#### `GET /agent-lazy-loading/memory-usage`
Get detailed memory usage by agent.

**Response**:
```json
{
  "total_memory_mb": 245.6,
  "agents": [
    {"name": "zumbi", "memory_mb": 15.2, "last_used": "2025-11-18T12:30:00Z"},
    {"name": "anita", "memory_mb": 12.8, "last_used": "2025-11-18T12:25:00Z"}
  ]
}
```

---

## 🔥 Cache Warming

**Module**: `src/api/routes/admin/cache_warming.py`
**Purpose**: Proactive cache warming for improved performance

### Endpoints

#### `POST /cache-warming/trigger`
Trigger cache warming process.

**Response**:
```json
{
  "success": true,
  "items_warmed": 1234,
  "cache_types": ["query_results", "agent_responses", "api_data"],
  "duration_ms": 2345.6
}
```

#### `POST /cache-warming/warm-specific`
Warm specific cache entries.

**Request Body**:
```json
{
  "cache_keys": ["contract:12345", "investigation:abc123"],
  "cache_type": "query_results"
}
```

#### `GET /cache-warming/status`
Get cache warming status.

**Response**:
```json
{
  "is_warming": false,
  "last_warming": "2025-11-18T10:00:00Z",
  "total_warmed": 5678,
  "success_rate": 0.98
}
```

#### `POST /cache-warming/strategies/{strategy}`
Execute specific warming strategy.

**Path Parameters**:
- `strategy`: `popular_queries`, `recent_investigations`, `frequent_agents`

**Response**:
```json
{
  "strategy": "popular_queries",
  "items_warmed": 456,
  "success": true
}
```

#### `GET /cache-warming/strategies`
List available warming strategies.

**Response**:
```json
{
  "strategies": [
    {
      "name": "popular_queries",
      "description": "Warm most popular query patterns",
      "estimated_items": 500
    },
    {
      "name": "recent_investigations",
      "description": "Warm recent investigation data",
      "estimated_items": 250
    }
  ]
}
```

---

## 📦 Compression

**Module**: `src/api/routes/admin/compression.py`
**Purpose**: Response compression optimization and monitoring

### Endpoints

#### `GET /compression/metrics`
Get compression metrics and statistics.

**Response**:
```json
{
  "total_requests": 10000,
  "compressed_requests": 8500,
  "compression_ratio": 0.85,
  "avg_compression_ratio": 0.68,
  "bytes_saved": 45678900,
  "algorithms": {
    "gzip": 7000,
    "brotli": 1500
  }
}
```

#### `GET /compression/optimize`
Get compression optimization recommendations.

**Response**:
```json
{
  "recommendations": [
    {
      "type": "algorithm",
      "message": "Switch to brotli for 15% better compression",
      "potential_savings_mb": 123.4
    },
    {
      "type": "threshold",
      "message": "Increase min size threshold to 1KB",
      "reasoning": "Reduce CPU overhead for small responses"
    }
  ]
}
```

#### `GET /compression/algorithms`
List available compression algorithms and their performance.

**Response**:
```json
{
  "algorithms": [
    {
      "name": "gzip",
      "level": 6,
      "avg_ratio": 0.65,
      "avg_time_ms": 2.3,
      "supported": true
    },
    {
      "name": "brotli",
      "level": 4,
      "avg_ratio": 0.72,
      "avg_time_ms": 4.5,
      "supported": true
    }
  ]
}
```

#### `GET /compression/test`
Test compression on sample data.

**Query Parameters**:
- `algorithm`: `gzip`, `brotli`, `deflate`
- `level`: Compression level (1-9 for gzip, 1-11 for brotli)

**Response**:
```json
{
  "algorithm": "gzip",
  "level": 6,
  "original_size": 10240,
  "compressed_size": 3456,
  "compression_ratio": 0.66,
  "compression_time_ms": 2.1
}
```

---

## 🔌 Connection Pools

**Module**: `src/api/routes/admin/connection_pools.py`
**Purpose**: Monitor and optimize database/Redis connection pools

### Endpoints

#### `GET /connection-pools/stats`
Get connection pool statistics.

**Response**:
```json
{
  "database": {
    "active": 5,
    "idle": 10,
    "total": 15,
    "max_size": 20,
    "wait_count": 3,
    "avg_wait_time_ms": 12.5
  },
  "redis": {
    "active": 2,
    "idle": 8,
    "total": 10,
    "max_size": 10
  }
}
```

#### `GET /connection-pools/health`
Health check for all connection pools.

**Response**:
```json
{
  "healthy": true,
  "pools": {
    "database": {"status": "healthy", "response_time_ms": 5.2},
    "redis": {"status": "healthy", "response_time_ms": 1.1}
  }
}
```

#### `GET /connection-pools/optimize`
Get pool optimization recommendations.

**Response**:
```json
{
  "recommendations": [
    {
      "pool": "database",
      "action": "increase_pool_size",
      "current": 20,
      "suggested": 25,
      "reason": "High wait times detected"
    }
  ]
}
```

#### `GET /connection-pools/config`
Get current pool configuration.

**Response**:
```json
{
  "database": {
    "min_size": 5,
    "max_size": 20,
    "timeout": 30,
    "recycle_time": 3600
  },
  "redis": {
    "min_size": 2,
    "max_size": 10,
    "timeout": 10
  }
}
```

#### `POST /connection-pools/reset-stats`
Reset connection pool statistics.

**Response**:
```json
{
  "success": true,
  "message": "Statistics reset for all pools"
}
```

#### `GET /connection-pools/recommendations`
Get detailed performance recommendations.

**Response**:
```json
{
  "recommendations": [
    {
      "priority": "high",
      "pool": "database",
      "metric": "wait_time",
      "suggestion": "Increase pool size from 20 to 25",
      "expected_improvement": "30% reduction in wait time"
    }
  ]
}
```

---

## 💾 Database Optimization

**Module**: `src/api/routes/admin/database_optimization.py`
**Purpose**: Database performance analysis and optimization

### Endpoints

#### `GET /database/analyze-slow-queries`
Analyze slow queries and get optimization suggestions.

**Response**:
```json
{
  "slow_queries": [
    {
      "query": "SELECT * FROM investigations WHERE...",
      "avg_time_ms": 1234.5,
      "call_count": 456,
      "total_time_ms": 563472,
      "suggestion": "Add index on (user_id, created_at)"
    }
  ],
  "total_slow_queries": 5
}
```

#### `GET /database/missing-indexes`
Identify missing database indexes.

**Response**:
```json
{
  "missing_indexes": [
    {
      "table": "investigations",
      "columns": ["user_id", "created_at"],
      "estimated_impact": "high",
      "affected_queries": 23
    }
  ],
  "total_missing": 3
}
```

#### `POST /database/create-indexes`
Create recommended indexes.

**Request Body**:
```json
{
  "indexes": [
    {
      "table": "investigations",
      "columns": ["user_id", "created_at"],
      "name": "idx_investigations_user_created"
    }
  ]
}
```

**Response**:
```json
{
  "created_indexes": 1,
  "failed_indexes": 0,
  "details": [
    {
      "name": "idx_investigations_user_created",
      "status": "created",
      "time_ms": 234.5
    }
  ]
}
```

#### `POST /database/optimize-statistics`
Update database statistics for query planner.

**Response**:
```json
{
  "success": true,
  "tables_optimized": 15,
  "total_time_ms": 1234.5
}
```

#### `GET /database/database-stats`
Get comprehensive database statistics.

**Response**:
```json
{
  "total_tables": 20,
  "total_size_mb": 1234.5,
  "total_rows": 1500000,
  "cache_hit_ratio": 0.95,
  "transactions_per_second": 150,
  "active_connections": 5
}
```

---

## 🛡️ IP Whitelist

**Module**: `src/api/routes/admin/ip_whitelist.py`
**Purpose**: Manage IP address whitelist for enhanced security

### Endpoints

#### `POST /ip-whitelist/add`
Add IP address to whitelist.

**Request Body**:
```json
{
  "ip_address": "192.168.1.100",
  "description": "Production server",
  "expires_at": "2026-12-31T23:59:59Z"
}
```

**Response**:
```json
{
  "id": 123,
  "ip_address": "192.168.1.100",
  "description": "Production server",
  "added_at": "2025-11-18T12:00:00Z",
  "expires_at": "2026-12-31T23:59:59Z",
  "is_active": true
}
```

#### `DELETE /ip-whitelist/remove/{ip_address}`
Remove IP from whitelist.

**Path Parameters**:
- `ip_address`: IP address to remove

**Response**:
```json
{
  "success": true,
  "message": "IP 192.168.1.100 removed from whitelist"
}
```

#### `GET /ip-whitelist/list`
List all whitelisted IPs.

**Response**:
```json
[
  {
    "id": 123,
    "ip_address": "192.168.1.100",
    "description": "Production server",
    "added_at": "2025-11-18T12:00:00Z",
    "expires_at": "2026-12-31T23:59:59Z",
    "is_active": true
  }
]
```

#### `GET /ip-whitelist/check/{ip_address}`
Check if IP is whitelisted.

**Path Parameters**:
- `ip_address`: IP to check

**Response**:
```json
{
  "ip_address": "192.168.1.100",
  "is_whitelisted": true,
  "entry": {
    "id": 123,
    "description": "Production server",
    "expires_at": "2026-12-31T23:59:59Z"
  }
}
```

#### `PUT /ip-whitelist/update/{ip_address}`
Update whitelist entry.

**Path Parameters**:
- `ip_address`: IP to update

**Request Body**:
```json
{
  "description": "Updated description",
  "expires_at": "2027-12-31T23:59:59Z",
  "is_active": true
}
```

#### `POST /ip-whitelist/cleanup`
Remove expired whitelist entries.

**Response**:
```json
{
  "removed_count": 3,
  "removed_ips": ["192.168.1.50", "192.168.1.51", "192.168.1.52"]
}
```

#### `POST /ip-whitelist/initialize-defaults`
Initialize default whitelist entries (localhost, common development IPs).

**Response**:
```json
{
  "added_count": 4,
  "added_ips": ["127.0.0.1", "::1", "0.0.0.0", "localhost"]
}
```

#### `GET /ip-whitelist/stats`
Get whitelist statistics.

**Response**:
```json
{
  "total_entries": 15,
  "active_entries": 12,
  "expired_entries": 3,
  "most_recent": {
    "ip_address": "192.168.1.100",
    "added_at": "2025-11-18T12:00:00Z"
  }
}
```

---

## 🔐 Authentication

All admin endpoints require authentication with admin privileges:

```python
# Example request with admin token
headers = {
    "Authorization": "Bearer <admin_jwt_token>"
}
```

**Admin Role Requirements**:
- User must have `is_admin=True` in database
- Valid JWT token with admin claims
- IP address may need to be whitelisted (if IP whitelist is active)

---

## 📊 Usage Examples

### Python (httpx)

```python
import httpx

async with httpx.AsyncClient() as client:
    # Get lazy loading status
    response = await client.get(
        "https://api.example.com/api/v1/admin/agent-lazy-loading/status",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    status = response.json()
    print(f"Loaded agents: {status['loaded_agents']}")

    # Preload all agents
    response = await client.post(
        "https://api.example.com/api/v1/admin/agent-lazy-loading/preload-all",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    result = response.json()
    print(f"Preloaded {result['total_loaded']} agents in {result['total_time_ms']}ms")
```

### cURL

```bash
# Add IP to whitelist
curl -X POST https://api.example.com/api/v1/admin/ip-whitelist/add \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "192.168.1.100",
    "description": "Production server"
  }'

# Get database stats
curl -X GET https://api.example.com/api/v1/admin/database/database-stats \
  -H "Authorization: Bearer ${ADMIN_TOKEN}"
```

---

## 🎯 Best Practices

1. **Agent Lazy Loading**:
   - Use `preload-all` after deployment to ensure fast first requests
   - Monitor memory usage regularly via `/memory-usage`
   - Adjust `max_loaded_agents` based on available RAM

2. **Cache Warming**:
   - Schedule cache warming during low-traffic periods
   - Use `popular_queries` strategy for production deployments
   - Monitor `success_rate` to ensure effective warming

3. **Database Optimization**:
   - Run `analyze-slow-queries` weekly
   - Create missing indexes during maintenance windows
   - Update statistics after bulk data imports

4. **Connection Pools**:
   - Check `/health` endpoint in monitoring systems
   - Review `/recommendations` monthly
   - Increase pool size gradually based on metrics

5. **IP Whitelist**:
   - Use `cleanup` endpoint monthly to remove expired entries
   - Set expiration dates for temporary access
   - Document all whitelist entries with clear descriptions

---

## 📝 Notes

- All endpoints return JSON responses
- Admin endpoints are rate-limited separately from public endpoints
- Failed admin operations are logged with full audit trail
- Most endpoints support pagination (use `?page=1&limit=50`)
- All timestamps are in ISO 8601 format (UTC)

---

**Last Updated**: 2025-11-18
**Version**: 1.0.0
**Maintainer**: Anderson Henrique da Silva
