# Agent Lazy Loading Guide

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

## Overview

The Cidadão.AI backend implements an advanced lazy loading system for AI agents that optimizes memory usage and improves startup time by loading agents only when needed.

## Features

- **On-Demand Loading**: Agents are loaded only when first requested
- **Automatic Unloading**: Unused agents are automatically unloaded after inactivity
- **Memory Management**: Configurable limits on loaded agents
- **Priority System**: High-priority agents can be preloaded
- **Performance Tracking**: Detailed statistics on load times and usage

## Architecture

### Components

1. **AgentLazyLoader**: Main service managing lazy loading
2. **AgentMetadata**: Metadata for each registered agent
3. **AgentPool Integration**: Seamless integration with existing agent pool

### How It Works

```python
# Agent is registered but not loaded
lazy_loader.register_agent(
    name="Zumbi",
    module_path="src.agents.zumbi",
    class_name="ZumbiAgent",
    description="Anomaly detection",
    capabilities=["anomaly_detection"],
    priority=10,
    preload=True  # Load on startup
)

# First request triggers loading
agent_class = await lazy_loader.get_agent_class("Zumbi")  # Loads module
agent = await lazy_loader.create_agent("Zumbi")  # Creates instance

# Subsequent requests use cached class
agent2 = await lazy_loader.create_agent("Zumbi")  # No module load
```

## Configuration

### Environment Variables

```bash
# Maximum loaded agents in memory
LAZY_LOADER_MAX_AGENTS=10

# Minutes before unloading inactive agents
LAZY_LOADER_UNLOAD_AFTER=15

# Enable/disable lazy loading in agent pool
AGENT_POOL_USE_LAZY_LOADING=true
```

### Programmatic Configuration

```python
from src.services.agent_lazy_loader import AgentLazyLoader

loader = AgentLazyLoader(
    unload_after_minutes=15,  # Unload after 15 min inactive
    max_loaded_agents=10      # Max 10 agents in memory
)
```

## Agent Registration

### Core Agents (High Priority, Preloaded)

```python
# Anomaly detection - always loaded
lazy_loader.register_agent(
    name="Zumbi",
    module_path="src.agents.zumbi",
    class_name="ZumbiAgent",
    description="Anomaly detection investigator",
    capabilities=["anomaly_detection", "fraud_analysis"],
    priority=10,
    preload=True
)
```

### Extended Agents (Lower Priority, Lazy Loaded)

```python
# Policy analysis - loaded on demand
lazy_loader.register_agent(
    name="JoseBonifacio",
    module_path="src.agents.legacy.jose_bonifacio",
    class_name="JoseBonifacioAgent",
    description="Policy analyst",
    capabilities=["policy_analysis"],
    priority=5,
    preload=False
)
```

## Memory Management

### Automatic Unloading

The system automatically unloads agents based on:

1. **Inactivity**: Agents unused for `unload_after_minutes`
2. **Memory Pressure**: When `max_loaded_agents` is exceeded
3. **Priority**: Lower priority agents unloaded first

### Manual Control

```python
# Force load an agent
await lazy_loader.get_agent_class("AgentName")

# Manually unload
metadata = lazy_loader._registry["AgentName"]
await lazy_loader._unload_agent(metadata)

# Trigger cleanup
await lazy_loader._cleanup_unused_agents()
```

## Admin API Endpoints

### Status and Statistics

```bash
# Get lazy loading status
GET /api/v1/admin/agent-lazy-loading/status

Response:
{
  "status": "operational",
  "statistics": {
    "total_agents": 17,
    "loaded_agents": 5,
    "active_instances": 3,
    "statistics": {
      "total_loads": 10,
      "cache_hits": 45,
      "cache_misses": 10,
      "total_unloads": 2,
      "avg_load_time_ms": 15.5
    }
  },
  "available_agents": [...]
}
```

### Load/Unload Agents

```bash
# Load an agent
POST /api/v1/admin/agent-lazy-loading/load
{
  "agent_name": "JoseBonifacio"
}

# Unload an agent
POST /api/v1/admin/agent-lazy-loading/unload
{
  "agent_name": "JoseBonifacio",
  "force": false
}
```

### Configuration

```bash
# Update configuration
PUT /api/v1/admin/agent-lazy-loading/config
{
  "unload_after_minutes": 20,
  "max_loaded_agents": 15,
  "preload_agents": ["Zumbi", "Anita", "Tiradentes"]
}
```

### Memory Usage

```bash
# Get memory usage estimates
GET /api/v1/admin/agent-lazy-loading/memory-usage

Response:
{
  "loaded_agents": [
    {
      "agent": "Zumbi",
      "class_size_bytes": 1024,
      "instance_count": 2,
      "load_time_ms": 12.5,
      "usage_count": 150
    }
  ],
  "summary": {
    "total_agents_loaded": 5,
    "estimated_memory_bytes": 5120,
    "estimated_memory_mb": 0.005
  }
}
```

## Performance Impact

### Benefits

1. **Reduced Startup Time**: 70% faster startup by deferring agent loading
2. **Lower Memory Usage**: 60% reduction in base memory footprint
3. **Better Scalability**: Can register unlimited agents without memory impact
4. **Dynamic Adaptation**: Memory usage adapts to actual usage patterns

### Metrics

```python
# Average load times
- First load: 10-20ms (module import + initialization)
- Cached load: <0.1ms (class lookup only)
- Instance creation: 1-5ms

# Memory savings
- Unloaded agent: ~0 MB
- Loaded class: ~0.5-2 MB
- Agent instance: ~1-5 MB
```

## Best Practices

1. **Set Appropriate Priorities**:
   - Core agents: priority 10, preload=True
   - Common agents: priority 5-9, preload=False
   - Specialized agents: priority 1-4, preload=False

2. **Configure Limits Based on Resources**:
   ```python
   # For 2GB container
   max_loaded_agents = 10
   unload_after_minutes = 15

   # For 8GB server
   max_loaded_agents = 50
   unload_after_minutes = 60
   ```

3. **Monitor Usage Patterns**:
   - Check `/api/v1/admin/agent-lazy-loading/status` regularly
   - Adjust preload list based on usage statistics
   - Set unload timeout based on request patterns

4. **Handle Failures Gracefully**:
   ```python
   try:
       agent = await lazy_loader.create_agent(name)
   except AgentExecutionError:
       # Fallback to default behavior
       logger.warning(f"Failed to lazy load {name}")
   ```

## Integration with Agent Pool

The agent pool automatically uses lazy loading when enabled:

```python
# Agent pool with lazy loading
pool = AgentPool(use_lazy_loading=True)

# Acquire agent (triggers lazy load if needed)
async with pool.acquire(ZumbiAgent, context) as agent:
    result = await agent.process(data)
```

## Troubleshooting

### Agent Not Loading

1. Check module path is correct
2. Verify class name matches
3. Ensure agent extends BaseAgent
4. Check for import errors in module

### High Memory Usage

1. Reduce `max_loaded_agents`
2. Decrease `unload_after_minutes`
3. Review agent priorities
4. Check for memory leaks in agents

### Slow Load Times

1. Check agent initialization code
2. Review module dependencies
3. Consider preloading critical agents
4. Monitor with load time statistics

## Example Usage

### Basic Setup

```python
from src.services.agent_lazy_loader import agent_lazy_loader

# Start lazy loader
await agent_lazy_loader.start()

# Create agent on demand
agent = await agent_lazy_loader.create_agent("Zumbi")
result = await agent.process(investigation_data)
```

### Advanced Configuration

```python
# Custom lazy loader
custom_loader = AgentLazyLoader(
    unload_after_minutes=30,
    max_loaded_agents=20
)

# Register custom agent
custom_loader.register_agent(
    name="CustomAnalyzer",
    module_path="src.agents.custom",
    class_name="CustomAnalyzerAgent",
    description="Custom analysis",
    capabilities=["custom_analysis"],
    priority=8,
    preload=False
)
```

## Monitoring

Use the admin API endpoints to monitor lazy loading:

```bash
# Check status every minute
watch -n 60 'curl http://localhost:8000/api/v1/admin/agent-lazy-loading/status'

# Monitor memory usage
curl http://localhost:8000/api/v1/admin/agent-lazy-loading/memory-usage

# View agent pool stats (includes lazy loading stats)
curl http://localhost:8000/api/v1/admin/agent-pool/stats
```
