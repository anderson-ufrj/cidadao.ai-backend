# Connection Pool Management Guide

## Overview

The Cidadão.AI backend uses advanced connection pooling for both PostgreSQL and Redis to ensure optimal performance and resource utilization.

## Features

- **Dynamic Pool Sizing**: Automatically adjusts pool sizes based on usage patterns
- **Health Monitoring**: Real-time health checks for all connections
- **Performance Metrics**: Detailed statistics on connection usage
- **Read Replica Support**: Automatic routing of read-only queries
- **Connection Recycling**: Prevents stale connections and memory leaks

## Database Connection Pools

### Configuration

Default PostgreSQL pool settings:

```python
{
    "pool_size": 10,              # Base number of connections
    "max_overflow": 20,           # Additional connections when needed
    "pool_timeout": 30,           # Seconds to wait for connection
    "pool_recycle": 3600,         # Recycle connections after 1 hour
    "pool_pre_ping": True,        # Test connections before use
    "pool_use_lifo": True         # LIFO for better cache locality
}
```

### Usage

The system automatically manages database connections:

```python
# Automatic connection pooling
async with get_session() as session:
    # Your database operations
    result = await session.execute(query)

# Read-only queries use replica pool if available
async with get_session(read_only=True) as session:
    # Queries routed to read replica
    data = await session.execute(select_query)
```

## Redis Connection Pools

### Configuration

Default Redis pool settings:

```python
{
    "max_connections": 10,
    "socket_keepalive": True,
    "retry_on_timeout": True,
    "health_check_interval": 30
}
```

### Multiple Pools

The system maintains separate pools for different purposes:

- **Main Pool**: General purpose operations
- **Cache Pool**: High-throughput caching with larger pool size

## Monitoring

### API Endpoints

Monitor connection pools through admin API:

```bash
# Get pool statistics
GET /api/v1/admin/connection-pools/stats

# Check pool health
GET /api/v1/admin/connection-pools/health

# Get optimization suggestions
GET /api/v1/admin/connection-pools/optimize

# Get current configurations
GET /api/v1/admin/connection-pools/config

# Reset statistics
POST /api/v1/admin/connection-pools/reset-stats
```

### Key Metrics

1. **Active Connections**: Currently in-use connections
2. **Peak Connections**: Maximum concurrent connections
3. **Wait Time**: Average time waiting for connections
4. **Connection Errors**: Failed connection attempts
5. **Recycle Rate**: How often connections are recycled

### Example Response

```json
{
  "database_pools": {
    "main": {
      "active_connections": 5,
      "peak_connections": 12,
      "connections_created": 15,
      "connections_closed": 3,
      "average_wait_time": 0.02,
      "pool_size": 10,
      "overflow": 2
    }
  },
  "redis_pools": {
    "cache": {
      "in_use_connections": 3,
      "available_connections": 7,
      "created_connections": 10
    }
  },
  "recommendations": [
    {
      "pool": "db_main",
      "issue": "High wait times",
      "suggestion": "Increase pool_size to 15"
    }
  ]
}
```

## Optimization

### Automatic Optimization

The system provides optimization suggestions based on:

- **Usage Patterns**: Adjusts pool sizes based on peak usage
- **Wait Times**: Recommends increases when waits are detected
- **Error Rates**: Alerts on connection stability issues
- **Idle Connections**: Suggests reductions for underutilized pools

### Manual Tuning

Environment variables for fine-tuning:

```bash
# Database pools
DATABASE_POOL_SIZE=20
DATABASE_POOL_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600

# Redis pools
REDIS_POOL_SIZE=15
REDIS_MAX_CONNECTIONS=50
```

## Best Practices

1. **Monitor Regularly**: Check pool stats during peak hours
2. **Set Appropriate Sizes**: Start conservative and increase based on metrics
3. **Use Read Replicas**: Route read-only queries to reduce main DB load
4. **Enable Pre-ping**: Ensures connections are valid before use
5. **Configure Recycling**: Prevents long-lived connections from degrading

## Troubleshooting

### High Wait Times

**Symptoms**: Slow response times, timeout errors

**Solutions**:
- Increase `pool_size` or `max_overflow`
- Check for long-running queries blocking connections
- Verify database server capacity

### Connection Errors

**Symptoms**: Intermittent failures, connection refused

**Solutions**:
- Check database server health
- Verify network connectivity
- Review firewall/security group rules
- Check connection limits on database server

### Memory Issues

**Symptoms**: Growing memory usage over time

**Solutions**:
- Enable connection recycling
- Reduce pool sizes if over-provisioned
- Check for connection leaks in application code

## Performance Impact

Proper connection pooling provides:

- **50-70% reduction** in connection overhead
- **Sub-millisecond** connection acquisition
- **Better resource utilization** on database server
- **Improved application scalability**

## Monitoring Script

Use this script to monitor pools:

```python
import asyncio
from src.services.connection_pool_service import connection_pool_service

async def monitor_pools():
    while True:
        stats = await connection_pool_service.get_pool_stats()
        
        # Alert on issues
        for rec in stats["recommendations"]:
            if rec["severity"] == "high":
                print(f"ALERT: {rec['pool']} - {rec['issue']}")
        
        # Log metrics
        for name, pool in stats["database_pools"].items():
            print(f"{name}: {pool['active_connections']}/{pool['pool_size']}")
        
        await asyncio.sleep(60)  # Check every minute

asyncio.run(monitor_pools())
```

## Integration with Other Services

Connection pools integrate with:

- **Cache Warming**: Pre-establishes connections
- **Health Checks**: Validates pool health
- **Metrics**: Exports pool statistics to Prometheus
- **Alerts**: Triggers alerts on pool issues