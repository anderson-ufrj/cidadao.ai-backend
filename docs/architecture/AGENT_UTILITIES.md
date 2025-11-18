# Agent System Utilities

**Location**: `src/agents/`
**Purpose**: Support files that enable agent functionality without being agents themselves

---

## 📋 Overview

The agent system includes 8 utility files that provide infrastructure, optimization, and tooling for the 16 operational agents:

| Category | Files | Purpose |
|----------|-------|---------|
| **Base Framework** | 1 file | Core agent architecture |
| **Lazy Loading** | 1 file | Import optimization (367x faster) |
| **Agent Pools** | 2 files | Agent lifecycle management |
| **Performance** | 2 files | Monitoring and optimization |
| **Simplified Versions** | 1 file | Lightweight deployments |
| **Legacy** | 1 file | Deprecated wrapper |

**Total**: 8 utility files + 16 operational agents = 24 agent-related files

---

## 🏗️ Base Framework

### `deodoro.py` (478 lines)
**Type**: Base Framework
**Status**: ✅ Production - 96.45% coverage
**Purpose**: Foundation for all agents

**What it provides**:
- `BaseAgent`: Abstract base class for all agents
- `ReflectiveAgent`: Self-improving agent with quality threshold
- `AgentMessage`: Standard message format
- `AgentContext`: Execution context and metadata
- `AgentResponse`: Standardized response structure
- `AgentStatus`: Enum for agent states (IDLE, THINKING, ACTING, etc.)

**Key Features**:
- Quality threshold (0.8 default) triggers self-reflection
- Max 3 reflection iterations for continuous improvement
- Built-in retry logic with exponential backoff
- Structured logging with correlation IDs
- State machine for agent lifecycle

**Usage**:
```python
from src.agents.deodoro import ReflectiveAgent, AgentMessage, AgentContext

class MyAgent(ReflectiveAgent):
    def __init__(self):
        super().__init__(
            name="MyAgent",
            capabilities=["cap1", "cap2"],
            quality_threshold=0.8
        )

    async def process(self, message: AgentMessage, context: AgentContext):
        # Implementation
        pass
```

**Dependencies**: None (base framework)
**Dependents**: All 16 operational agents

---

## ⚡ Lazy Loading System

### `__init__lazy.py` (149 lines)
**Type**: Import Optimization
**Status**: ✅ Production
**Purpose**: Dramatically improve startup time (367x faster)

**Performance Impact**:
- **Before**: 1460.41ms to import agents module
- **After**: 3.81ms to import agents module
- **Speedup**: 367.6x faster (1456.44ms saved)
- **First access overhead**: 0.17ms (negligible)

**How it works**:
```python
# Magic __getattr__ implementation
def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        module_path, class_name = _LAZY_IMPORTS[name]

        # Import only when needed
        module = importlib.import_module(module_path)
        agent_class = getattr(module, class_name)

        # Cache for future use
        _IMPORT_CACHE[name] = agent_class
        return agent_class

    raise AttributeError(f"module has no attribute '{name}'")
```

**Features**:
- Lazy loading of all 16 agents
- Import caching (no re-imports)
- Full alias support (ZumbiAgent → InvestigatorAgent)
- `__dir__` support for IDE autocomplete
- Backward compatible with eager imports

**Testing**:
- Created `test_lazy_loading.py` for verification
- All 889 agent tests pass with lazy loading
- No regressions detected

**Documentation**: See `docs/architecture/LAZY_LOADING.md` (if exists)

---

## 🎱 Agent Pool Management

### `agent_pool_interface.py` (257 lines)
**Type**: Interface Definition
**Status**: ⚠️ Deprecated (use `src/infrastructure/agent_pool.py`)
**Purpose**: Abstract interface for agent pools

**What it defines**:
- `AgentPoolInterface`: ABC for pool implementations
- `PoolMetrics`: Performance tracking
- `AgentPoolConfig`: Configuration dataclass
- Standard lifecycle methods (get_agent, release_agent, cleanup)

**Why deprecated**:
- Moved to `src/infrastructure/agent_pool.py` for better organization
- Current location maintained for backward compatibility
- Will be removed in future version

**Migration path**:
```python
# Old (deprecated)
from src.agents.agent_pool_interface import AgentPoolInterface

# New (current)
from src.infrastructure.agent_pool import AgentPool
```

### `simple_agent_pool.py` (312 lines)
**Type**: Lightweight Pool Implementation
**Status**: ⚠️ Legacy (use full AgentPool)
**Purpose**: Simple agent lifecycle management

**Features**:
- Basic agent initialization/cleanup
- No connection pooling
- No advanced metrics
- Synchronous operations only

**Use cases**:
- Testing environments
- Simple scripts
- Prototyping

**Limitations**:
- No async support
- No retry logic
- No circuit breakers
- No performance monitoring

**Replacement**:
```python
# Use full-featured pool instead
from src.infrastructure.agent_pool import AgentPool

pool = AgentPool()
await pool.initialize()
agent = await pool.get_agent("zumbi")
```

---

## 📊 Performance & Monitoring

### `metrics_wrapper.py` (189 lines)
**Type**: Performance Monitoring
**Status**: ✅ Production
**Purpose**: Automatic metrics collection for agents

**What it provides**:
- `@metrics_wrapper` decorator
- Automatic Prometheus metrics
- Execution time tracking
- Error rate monitoring
- Success/failure counters

**Metrics exported**:
```python
# Agent execution time
agent_execution_duration_seconds{agent_name="zumbi"}

# Agent execution counter
agent_executions_total{agent_name="zumbi", status="success"}

# Agent errors
agent_errors_total{agent_name="zumbi", error_type="timeout"}
```

**Usage**:
```python
from src.agents.metrics_wrapper import metrics_wrapper

class ZumbiAgent(ReflectiveAgent):
    @metrics_wrapper
    async def process(self, message, context):
        # Automatically tracked
        pass
```

**Integration**:
- Works with Grafana dashboards
- Prometheus `/metrics` endpoint
- Real-time alerting
- Historical analysis

### `parallel_processor.py` (234 lines)
**Type**: Parallel Execution
**Status**: ✅ Production
**Purpose**: Execute multiple agents concurrently

**Features**:
- Async parallel execution
- Rate limiting per agent
- Error isolation (one agent fail ≠ all fail)
- Result aggregation
- Timeout handling

**Use cases**:
- Batch investigations (100+ contracts)
- Multi-agent collaboration
- Data pipeline processing

**Example**:
```python
from src.agents.parallel_processor import ParallelProcessor

processor = ParallelProcessor(max_concurrent=5)

results = await processor.execute_parallel(
    agents=["zumbi", "anita", "tiradentes"],
    data=[contract1, contract2, contract3, ...]
)
```

**Performance**:
- 5x faster than sequential for 100 contracts
- Automatic retry on transient failures
- Memory-efficient streaming

---

## 📦 Lightweight Versions

### `drummond_simple.py` (149 lines)
**Type**: Simplified Agent
**Status**: ✅ Production (HuggingFace Spaces)
**Purpose**: Lightweight version of Drummond (Communication Agent)

**Comparison**:

| Feature | `drummond.py` (Full) | `drummond_simple.py` |
|---------|---------------------|---------------------|
| **Size** | 1,707 lines | 149 lines |
| **Memory** | ~200MB | ~50MB |
| **Dependencies** | Many (MaritacaClient, etc.) | Minimal |
| **NLG** | Template + Neural | Pre-defined only |
| **Channels** | 10 notification channels | Chat only |
| **Maritaca API** | Required | Optional |
| **Personalization** | User segmentation | Generic |
| **A/B Testing** | Built-in | None |
| **Scheduling** | Full support | None |

**When to use**:
- ✅ HuggingFace Spaces deployment
- ✅ Environments with memory constraints
- ✅ Quick prototyping
- ✅ Chat-only interfaces
- ✅ No Maritaca API available

**When NOT to use**:
- ❌ Production backend (use full version)
- ❌ Multi-channel notifications needed
- ❌ User personalization required
- ❌ A/B testing active

**Deployment example**:
```python
# app.py (HuggingFace Spaces)
from src.agents.drummond_simple import SimpleDrummondAgent

drummond = SimpleDrummondAgent()

@app.post("/chat")
async def chat(user_message: str):
    message = AgentMessage(
        sender="user",
        recipient="drummond",
        action="chat",
        payload={"user_message": user_message}
    )
    response = await drummond.process(message, AgentContext())
    return {"message": response.result["message"]}
```

**Documentation**: See `docs/agents/drummond.md` for full comparison

---

## 🔧 Legacy / Deprecated

### `zumbi_wrapper.py` (78 lines)
**Type**: Compatibility Wrapper
**Status**: ⚠️ Deprecated
**Purpose**: Backward compatibility for old Zumbi API

**Why deprecated**:
- Zumbi agent refactored to use standard ReflectiveAgent pattern
- Old wrapper maintained for existing integrations
- Will be removed in v4.0.0

**Migration**:
```python
# Old (deprecated)
from src.agents.zumbi_wrapper import ZumbiWrapper
wrapper = ZumbiWrapper()

# New (current)
from src.agents import ZumbiAgent
agent = ZumbiAgent()
```

**Removal timeline**:
- **v3.x**: Deprecated warnings logged
- **v4.0.0**: Complete removal (Q2 2026)

---

## 📊 Utility Summary

| File | Type | Lines | Status | Coverage | Purpose |
|------|------|-------|--------|----------|---------|
| `deodoro.py` | Base | 478 | ✅ Prod | 96.45% | Core framework |
| `__init__lazy.py` | Optimizer | 149 | ✅ Prod | N/A | Import speed (367x) |
| `agent_pool_interface.py` | Interface | 257 | ⚠️ Deprecated | N/A | Pool ABC (moved) |
| `simple_agent_pool.py` | Pool | 312 | ⚠️ Legacy | N/A | Simple pool |
| `metrics_wrapper.py` | Monitor | 189 | ✅ Prod | N/A | Prometheus metrics |
| `parallel_processor.py` | Executor | 234 | ✅ Prod | N/A | Parallel execution |
| `drummond_simple.py` | Agent | 149 | ✅ Prod | N/A | Lightweight Drummond |
| `zumbi_wrapper.py` | Wrapper | 78 | ⚠️ Deprecated | N/A | Legacy API |

**Total**: 1,846 lines of utility code
**Production Ready**: 5/8 (62.5%)
**Deprecated**: 3/8 (37.5%)

---

## 🎯 Best Practices

### Using Utilities

1. **Always use lazy loading** (automatic via `__init__lazy.py`)
   ```python
   from src.agents import ZumbiAgent  # Lazy loaded!
   ```

2. **Extend ReflectiveAgent for new agents**
   ```python
   from src.agents.deodoro import ReflectiveAgent

   class NewAgent(ReflectiveAgent):
       # Implementation
       pass
   ```

3. **Use metrics wrapper for monitoring**
   ```python
   from src.agents.metrics_wrapper import metrics_wrapper

   @metrics_wrapper
   async def process(self, message, context):
       # Auto-tracked
       pass
   ```

4. **Parallel processing for batch operations**
   ```python
   from src.agents.parallel_processor import ParallelProcessor

   processor = ParallelProcessor(max_concurrent=10)
   results = await processor.execute_parallel(...)
   ```

### Avoiding Deprecated Code

❌ **Don't use**:
- `agent_pool_interface.py` → Use `src/infrastructure/agent_pool.py`
- `simple_agent_pool.py` → Use full `AgentPool`
- `zumbi_wrapper.py` → Use `ZumbiAgent` directly

✅ **Do use**:
- `deodoro.py` for all agent bases
- `__init__lazy.py` (automatic)
- `metrics_wrapper.py` for monitoring
- `parallel_processor.py` for batch jobs
- `drummond_simple.py` only for HF Spaces

---

## 🔗 Related Documentation

- [Multi-Agent Architecture](./multi-agent-architecture.md)
- [Lazy Loading Performance](./LAZY_LOADING.md)
- [Agent Pool Management](../infrastructure/AGENT_POOL.md)
- [Drummond Documentation](../agents/drummond.md)
- [Prometheus Metrics](../monitoring/METRICS.md)

---

**Last Updated**: 2025-11-18
**Version**: 1.0.0
**Maintainer**: Anderson Henrique da Silva
