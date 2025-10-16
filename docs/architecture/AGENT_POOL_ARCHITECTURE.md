# Agent Pool Architecture

## Overview

Cidadão.AI uses two distinct agent pool implementations, each optimized for different use cases:

1. **SimpleAgentPool** (`src/agents/simple_agent_pool.py`) - Direct instance management
2. **DistributedAgentPool** (`src/infrastructure/distributed_agent_pool.py`) - Task-based execution

Both implement the `AgentPoolInterface` contract but serve different architectural needs.

---

## SimpleAgentPool

### Purpose
Manages reusable agent instances with direct acquisition and release patterns. Optimized for synchronous request-response patterns in web APIs.

### Key Features
- **Instance Reuse**: Pre-warmed agents ready for immediate use
- **Lifecycle Management**: Automatic cleanup of idle agents
- **Memory Integration**: Built-in support for agent memory systems
- **Lazy Loading**: Optional delayed initialization
- **Thread-Safe**: Concurrent access via asyncio locks

### Architecture
```
┌─────────────────────────────────────┐
│      FastAPI Request Handler        │
└───────────────┬─────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│         SimpleAgentPool               │
│                                       │
│  ┌─────────┐  ┌─────────┐           │
│  │ Agent 1 │  │ Agent 2 │  ...      │
│  │ (idle)  │  │ (busy)  │           │
│  └─────────┘  └─────────┘           │
│                                       │
│  - Min Size: 2 agents                │
│  - Max Size: 10 agents               │
│  - Idle Timeout: 5 minutes           │
└───────────────────────────────────────┘
```

### Use Cases

#### 1. Web API Request Handling (PRIMARY)
**Current Implementation**: Used by all API endpoints

```python
from src.agents.simple_agent_pool import get_agent_pool

@app.post("/api/v1/investigations")
async def create_investigation(request: InvestigationRequest):
    pool = await get_agent_pool()

    # Acquire agent for this request
    agent = await pool.acquire(InvestigatorAgent, context)

    try:
        result = await agent.investigate(request.query)
        return result
    finally:
        # Agent automatically returned to pool
        pass
```

**Why SimpleAgentPool?**
- Low latency: Pre-warmed agents respond immediately
- Resource efficient: Reuses instances across requests
- Simple lifecycle: One agent per request, automatic cleanup

#### 2. Chat Service
**Location**: `src/services/chat_service_with_cache.py`

```python
async def process_message(session_id: str, message: str):
    pool = await get_agent_pool()

    # Get appropriate agent based on intent
    agent_type = await detect_intent(message)
    agent = await pool.acquire(agent_type, context)

    # Process message
    response = await agent.respond(message)
    return response
```

**Why SimpleAgentPool?**
- Interactive response times required
- Each message is independent
- Direct agent-to-user communication

#### 3. Investigation Service
**Location**: `src/services/investigation_service_supabase_rest.py`

Synchronous investigation flow where results are needed immediately.

**Why SimpleAgentPool?**
- Request-scoped operations
- Direct result retrieval
- No need for task queuing

### Configuration

```python
pool = SimpleAgentPool(
    min_size=2,           # Always keep 2 agents ready
    max_size=10,          # Scale up to 10 concurrent requests
    idle_timeout=300,     # Cleanup after 5 minutes idle
    max_agent_lifetime=3600,  # Recreate after 1 hour
    use_lazy_loading=True     # Create on demand
)
```

### Performance Characteristics
- **Latency**: < 10ms (agent already initialized)
- **Memory**: ~50MB per agent instance
- **Concurrency**: Up to max_size concurrent requests
- **Scaling**: Vertical (within single process)

---

## DistributedAgentPool

### Purpose
Task-based execution system with priority queues, auto-scaling, and distributed worker management. Optimized for background jobs and batch processing.

### Key Features
- **Task Queue**: FIFO with priority levels (HIGH, NORMAL, LOW)
- **Auto-Scaling**: Dynamic pool size based on load
- **Worker Management**: Thread or process-based execution
- **Health Monitoring**: Automatic agent health checks
- **Timeout Handling**: Per-task timeout and retry logic
- **Metrics**: Comprehensive performance tracking

### Architecture
```
┌─────────────────────────────────────────┐
│       Background Job System             │
└───────────────┬─────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────┐
│       DistributedAgentPool                    │
│                                               │
│  ┌─────────────────────────────┐            │
│  │     Priority Task Queue     │            │
│  │  HIGH  │ NORMAL │  LOW      │            │
│  └────┬───────┬────────┬───────┘            │
│       │       │        │                     │
│       ▼       ▼        ▼                     │
│  ┌─────────────────────────────┐            │
│  │    Worker Pool (4-20)       │            │
│  │  Worker1  Worker2  Worker3  │            │
│  │    ▼         ▼        ▼     │            │
│  │  Agent1   Agent2  Agent3    │            │
│  └─────────────────────────────┘            │
│                                               │
│  - Min Workers: 4                            │
│  - Max Workers: 20                           │
│  - Auto-scale based on queue depth          │
└───────────────────────────────────────────────┘
```

### Use Cases

#### 1. Celery Background Tasks (PLANNED)
**Location**: `src/infrastructure/queue/tasks/`

```python
from src.infrastructure.distributed_agent_pool import get_pool_manager

@celery.task
async def analyze_contract_batch(contract_ids: list[str]):
    pool = await get_pool_manager()

    # Submit high-priority analysis tasks
    task_ids = []
    for contract_id in contract_ids:
        task_id = await pool.submit_task(
            agent_type="zumbi",
            method="analyze_contract",
            contract_id=contract_id,
            priority="HIGH"
        )
        task_ids.append(task_id)

    # Wait for all results
    results = []
    for task_id in task_ids:
        result = await pool.get_task_result(task_id, timeout=300)
        results.append(result)

    return results
```

**Why DistributedAgentPool?**
- Batch processing of hundreds/thousands of contracts
- Priority-based execution (urgent vs routine)
- Independent task lifecycle
- Result caching and retry logic

#### 2. Auto-Investigation System (PLANNED)
**Location**: `src/infrastructure/queue/tasks/auto_investigation_tasks.py`

24/7 monitoring of government contracts with automatic anomaly detection.

```python
@celery.task
async def auto_monitor_new_contracts():
    pool = await get_pool_manager()

    # Fetch recent contracts
    contracts = await fetch_new_contracts(hours=24)

    # Submit analysis tasks for each
    for contract in contracts:
        await pool.submit_task(
            agent_type="zumbi",
            method="detect_anomalies",
            contract=contract,
            priority="NORMAL"
        )

    # Results collected asynchronously
```

**Why DistributedAgentPool?**
- Long-running background operations
- No user waiting for response
- Scalable to thousands of contracts per day
- Automatic retry on failure

#### 3. Report Generation (PLANNED)
**Location**: `src/infrastructure/queue/tasks/report_tasks.py`

Generating comprehensive PDF/Excel reports from investigation results.

```python
async def generate_monthly_report(month: int, year: int):
    pool = await get_pool_manager()

    task_id = await pool.submit_task(
        agent_type="tiradentes",
        method="generate_report",
        month=month,
        year=year,
        priority="LOW",
        timeout=600  # 10 minutes
    )

    # User can check status or be notified when complete
    return {"task_id": task_id, "status": "processing"}
```

**Why DistributedAgentPool?**
- Resource-intensive operations
- Async user experience (notify when ready)
- Can run during off-peak hours
- Separate process avoids blocking web workers

### Configuration

```python
from src.infrastructure.distributed_agent_pool import PoolConfig

config = PoolConfig(
    min_workers=4,
    max_workers=20,
    worker_idle_timeout=600,  # 10 minutes
    task_timeout=300,         # 5 minutes default
    queue_max_size=1000,
    enable_auto_scaling=True,
    health_check_interval=60,
    scale_up_threshold=0.7,   # Scale at 70% queue capacity
    scale_down_threshold=0.2  # Scale down at 20% capacity
)

pool = AgentPoolManager(config)
```

### Performance Characteristics
- **Latency**: Variable (queued, not immediate)
- **Throughput**: High (parallel worker execution)
- **Memory**: ~100MB per worker (includes agent + task state)
- **Concurrency**: Up to max_workers parallel tasks
- **Scaling**: Horizontal (can span multiple processes/machines)

---

## Comparison Matrix

| Feature                  | SimpleAgentPool            | DistributedAgentPool        |
|--------------------------|----------------------------|-----------------------------|
| **Primary Use Case**     | Web API requests           | Background jobs             |
| **Execution Pattern**    | Synchronous acquire/release| Async task submission       |
| **Latency**              | Low (<10ms)                | Variable (queued)           |
| **Throughput**           | Moderate                   | High                        |
| **Priority Support**     | No                         | Yes (HIGH/NORMAL/LOW)       |
| **Auto-Scaling**         | No                         | Yes                         |
| **Task Timeout**         | No (request timeout)       | Yes (per-task)              |
| **Result Caching**       | No (handled by caller)     | Yes (built-in)              |
| **Health Monitoring**    | Basic                      | Comprehensive               |
| **Retry Logic**          | No                         | Yes                         |
| **Memory Integration**   | Yes                        | No                          |
| **Worker Modes**         | Async only                 | Thread/Process/Async        |
| **Current Status**       | ✅ Production             | 🚧 Planned                  |

---

## Migration Path

### Current State (January 2025)
- All API endpoints use **SimpleAgentPool**
- DistributedAgentPool implemented but not integrated
- No Celery background tasks yet

### Phase 1: Background Task Integration (Q1 2025)
1. Set up Celery workers
2. Integrate DistributedAgentPool with Celery
3. Migrate batch operations:
   - Auto-investigation monitoring
   - Historical contract reanalysis
   - Report generation

### Phase 2: Performance Optimization (Q2 2025)
1. Add metrics and monitoring for both pools
2. Optimize pool configurations based on production data
3. Implement intelligent agent type routing

### Phase 3: Hybrid Architecture (Q3 2025)
1. API endpoints continue using SimpleAgentPool
2. Background jobs use DistributedAgentPool
3. Shared agent registry for consistency
4. Cross-pool memory sharing via Nanã agent

---

## Best Practices

### When to Use SimpleAgentPool
✅ Synchronous web API requests
✅ Chat/interactive applications
✅ Real-time user-facing operations
✅ Operations requiring immediate response
✅ Simple request-response patterns

### When to Use DistributedAgentPool
✅ Batch processing operations
✅ Scheduled background jobs
✅ Long-running analyses (>30 seconds)
✅ Operations that can tolerate latency
✅ Tasks requiring retry logic
✅ Priority-based execution needed

### Anti-Patterns
❌ Using SimpleAgentPool for batch jobs (resource exhaustion)
❌ Using DistributedAgentPool for API requests (unnecessary complexity)
❌ Mixing pool types within a single operation (state management issues)
❌ Not monitoring pool metrics (leads to performance issues)

---

## Implementation Status

### SimpleAgentPool ✅
- [x] Core implementation
- [x] Memory integration (Nanã agent)
- [x] API integration
- [x] Chat service integration
- [x] Statistics and monitoring
- [x] Production deployment

### DistributedAgentPool 🚧
- [x] Core implementation
- [x] Task queue with priorities
- [x] Auto-scaling logic
- [x] Health monitoring
- [ ] Celery integration
- [ ] Production deployment
- [ ] Metrics dashboard
- [ ] Task retry policies

---

## Monitoring

### SimpleAgentPool Metrics
```python
stats = pool.get_stats()
{
    "total_agents": 5,
    "idle_agents": 3,
    "active_agents": 2,
    "agent_types": {"zumbi": 2, "anita": 1, ...},
    "avg_acquire_time_ms": 2.5,
    "total_acquisitions": 1234
}
```

### DistributedAgentPool Metrics
```python
status = pool.get_pool_status()
{
    "active_workers": 8,
    "queue_sizes": {"high": 2, "normal": 15, "low": 45},
    "task_stats": {
        "completed": 5432,
        "failed": 12,
        "timeout": 3
    },
    "avg_task_time_ms": 1250,
    "worker_utilization": 0.65
}
```

---

## Conclusion

The dual-pool architecture provides flexibility:

- **SimpleAgentPool** handles the majority of user-facing operations with low latency
- **DistributedAgentPool** enables scalable background processing for intensive operations

This separation of concerns allows each pool to be optimized for its specific use case while maintaining a consistent interface through `AgentPoolInterface`.
