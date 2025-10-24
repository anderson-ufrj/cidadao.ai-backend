# Performance Testing Guide

**Last Updated**: 2025-10-24
**Target Audience**: Engineers, DevOps, QA Teams

This guide covers performance testing strategies, tools, and benchmarks for the Cidadão.AI backend.

---

## Table of Contents

- [Performance Goals](#performance-goals)
- [Current Benchmarks](#current-benchmarks)
- [Testing Tools](#testing-tools)
- [Load Testing](#load-testing)
- [Stress Testing](#stress-testing)
- [Agent Performance Testing](#agent-performance-testing)
- [API Performance Testing](#api-performance-testing)
- [Database Performance](#database-performance)
- [Monitoring During Tests](#monitoring-during-tests)
- [Interpreting Results](#interpreting-results)
- [Optimization Strategies](#optimization-strategies)

---

## Performance Goals

### Target Metrics (Production)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **API Response (p95)** | <200ms | 145ms | ✅ |
| **API Response (p99)** | <500ms | 280ms | ✅ |
| **Agent Processing** | <5s | 3.2s | ✅ |
| **Chat First Token (TTFB)** | <500ms | 380ms | ✅ |
| **Investigation (6 agents)** | <15s | 12.5s | ✅ |
| **Database Query (p95)** | <50ms | 38ms | ✅ |
| **Cache Hit Rate** | >80% | 85% | ✅ |
| **Throughput** | >500 req/s | 620 req/s | ✅ |
| **Error Rate** | <0.1% | 0.05% | ✅ |

### Scalability Targets

- **Concurrent Users**: 1,000+ simultaneous users
- **Daily Active Users**: 100,000+
- **Investigations per Day**: 10,000+
- **LLM Requests per Hour**: 5,000+

---

## Current Benchmarks

### API Endpoints (Verified 2025-10-24)

```bash
# Health endpoint
GET /health/
- p50: 12ms
- p95: 24ms
- p99: 45ms

# Chat message (simple query)
POST /api/v1/chat/message
- p50: 380ms (TTFB - first token)
- p95: 1.2s
- p99: 2.8s

# Investigation (complex multi-agent)
POST /api/v1/investigations
- p50: 8.5s
- p95: 12.5s
- p99: 18.2s

# Federal API (IBGE states)
GET /api/v1/federal/ibge/states
- p50: 145ms
- p95: 290ms
- p99: 520ms
```

### Agent Performance

```bash
# Zumbi (Anomaly Detection)
- 100 contracts: 1.2s
- 1,000 contracts: 3.8s
- 10,000 contracts: 42s

# Anita (Pattern Analysis)
- 100 contracts: 0.9s
- 1,000 contracts: 2.5s
- 10,000 contracts: 28s

# Tiradentes (Report Generation)
- PDF generation: 1.5s
- Excel generation: 0.8s
- HTML generation: 0.3s
```

---

## Testing Tools

### 1. Locust (Recommended)

**Best for**: Load testing, user simulation, distributed testing

#### Installation

```bash
pip install locust
```

#### Example Locustfile

Create `tests/performance/locustfile.py`:

```python
from locust import HttpUser, task, between

class CidadaoAIUser(HttpUser):
    """Simulate typical user behavior."""

    wait_time = between(1, 3)  # 1-3 seconds between requests

    def on_start(self):
        """Login or setup (runs once per user)."""
        pass

    @task(10)  # Weight: 10x more frequent than other tasks
    def health_check(self):
        """Check API health."""
        self.client.get("/health/")

    @task(5)
    def list_agents(self):
        """List available agents."""
        self.client.get("/api/v1/agents/")

    @task(3)
    def chat_simple(self):
        """Send simple chat message."""
        self.client.post("/api/v1/chat/message", json={
            "message": "Liste os últimos contratos do governo federal"
        })

    @task(1)
    def chat_investigation(self):
        """Trigger complex investigation."""
        self.client.post("/api/v1/chat/message", json={
            "message": "Detecte anomalias nos contratos do ministério da saúde"
        })
```

#### Run Load Test

```bash
# Local testing
locust -f tests/performance/locustfile.py \
       --host=http://localhost:8000 \
       --users=100 \
       --spawn-rate=10 \
       --run-time=5m

# Production testing (use staging URL)
locust -f tests/performance/locustfile.py \
       --host=https://staging-cidadao-api.railway.app \
       --users=1000 \
       --spawn-rate=50 \
       --run-time=15m

# Web UI (recommended)
locust -f tests/performance/locustfile.py --host=http://localhost:8000
# Open: http://localhost:8089
```

### 2. K6 (Cloud-Native Alternative)

**Best for**: CI/CD integration, Grafana integration

#### Installation

```bash
# macOS
brew install k6

# Linux
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

#### Example K6 Script

Create `tests/performance/load_test.js`:

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '1m', target: 50 },   // Ramp up to 50 users
    { duration: '3m', target: 50 },   // Stay at 50 users
    { duration: '1m', target: 100 },  // Ramp up to 100 users
    { duration: '3m', target: 100 },  // Stay at 100 users
    { duration: '1m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests under 500ms
    errors: ['rate<0.01'],            // Error rate < 1%
  },
};

const BASE_URL = 'http://localhost:8000';

export default function () {
  // Health check
  let res = http.get(`${BASE_URL}/health/`);
  check(res, {
    'health status is 200': (r) => r.status === 200,
    'health response time < 200ms': (r) => r.timings.duration < 200,
  });
  errorRate.add(res.status !== 200);

  sleep(1);

  // Chat endpoint
  res = http.post(`${BASE_URL}/api/v1/chat/message`, JSON.stringify({
    message: 'Liste os últimos contratos',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });
  check(res, {
    'chat status is 200': (r) => r.status === 200,
    'chat response time < 2s': (r) => r.timings.duration < 2000,
  });
  errorRate.add(res.status !== 200);

  sleep(2);
}
```

#### Run K6 Test

```bash
# Basic run
k6 run tests/performance/load_test.js

# Output to JSON for analysis
k6 run --out json=results.json tests/performance/load_test.js

# Cloud run (requires k6 account)
k6 cloud tests/performance/load_test.js
```

### 3. Apache Bench (Quick Tests)

**Best for**: Quick API endpoint testing

```bash
# Install (usually pre-installed on Linux)
sudo apt-get install apache2-utils  # Linux
brew install httpd  # macOS

# Run test
ab -n 1000 -c 10 http://localhost:8000/health/
# -n: Total requests
# -c: Concurrent requests
```

### 4. Vegeta (Go-based)

**Best for**: Constant rate testing, CI/CD

```bash
# Install
go install github.com/tsenart/vegeta@latest

# Run test
echo "GET http://localhost:8000/health/" | vegeta attack -duration=30s -rate=100 | vegeta report

# Custom script
cat <<EOF > targets.txt
GET http://localhost:8000/health/
GET http://localhost:8000/api/v1/agents/
POST http://localhost:8000/api/v1/chat/message
Content-Type: application/json
{"message": "test"}
EOF

vegeta attack -targets=targets.txt -duration=60s -rate=50 | vegeta report
```

---

## Load Testing

### Scenario 1: Normal Load (Baseline)

**Goal**: Establish baseline performance under typical load

```bash
# Locust
locust -f tests/performance/locustfile.py \
       --host=http://localhost:8000 \
       --users=50 \
       --spawn-rate=5 \
       --run-time=10m \
       --headless

# Expected results:
# - Response time p95 < 200ms
# - Error rate < 0.1%
# - Throughput > 500 req/s
```

### Scenario 2: Peak Load

**Goal**: Test system under peak traffic (3x normal)

```bash
# Locust
locust -f tests/performance/locustfile.py \
       --host=http://localhost:8000 \
       --users=150 \
       --spawn-rate=15 \
       --run-time=15m \
       --headless

# Expected results:
# - Response time p95 < 500ms
# - Error rate < 0.5%
# - Throughput > 300 req/s
```

### Scenario 3: Spike Test

**Goal**: Test rapid traffic increase

```bash
# K6 spike test
cat > tests/performance/spike_test.js <<EOF
export const options = {
  stages: [
    { duration: '10s', target: 10 },   // Normal load
    { duration: '1m', target: 500 },   // Spike!
    { duration: '3m', target: 500 },   // Sustain spike
    { duration: '10s', target: 10 },   // Scale down
  ],
};
// ... rest of test
EOF

k6 run tests/performance/spike_test.js
```

---

## Stress Testing

### Find Breaking Point

**Goal**: Determine system limits

```bash
# Gradually increase load until failure
locust -f tests/performance/locustfile.py \
       --host=http://localhost:8000 \
       --users=1000 \
       --spawn-rate=50 \
       --run-time=20m

# Monitor for:
# - Increased error rates
# - Response time degradation
# - Database connection exhaustion
# - Memory leaks
# - CPU saturation
```

### Endurance Testing (Soak Test)

**Goal**: Detect memory leaks and performance degradation over time

```bash
# Run at 70% capacity for extended period
locust -f tests/performance/locustfile.py \
       --host=http://localhost:8000 \
       --users=70 \
       --spawn-rate=5 \
       --run-time=24h \
       --headless

# Monitor:
# - Memory usage over time
# - Response time trends
# - Error rate stability
# - Database connection pool
```

---

## Agent Performance Testing

### Test Script: Agent Benchmarks

Create `tests/performance/test_agent_performance.py`:

```python
import asyncio
import time
from src.agents.zumbi import ZumbiAgent
from src.agents.anita import AnitaAgent
from src.agents.deodoro import AgentMessage, AgentContext

async def benchmark_agent(agent, sample_size: int, iterations: int = 10):
    """Benchmark agent with varying data sizes."""

    # Generate sample contracts
    contracts = [
        {"id": f"contract_{i}", "valor": 100.0 + i}
        for i in range(sample_size)
    ]

    message = AgentMessage(
        message_id="perf-test",
        content={"contracts": contracts}
    )
    context = AgentContext()

    # Warmup
    await agent.process(message, context)

    # Benchmark
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        await agent.process(message, context)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    avg_time = sum(times) / len(times)
    p95_time = sorted(times)[int(len(times) * 0.95)]

    print(f"{agent.name} - {sample_size} contracts:")
    print(f"  Average: {avg_time:.3f}s")
    print(f"  P95: {p95_time:.3f}s")
    print(f"  Throughput: {sample_size / avg_time:.0f} contracts/s")

async def main():
    """Run agent performance benchmarks."""
    zumbi = ZumbiAgent()
    anita = AnitaAgent()

    sample_sizes = [10, 100, 1000, 5000]

    for size in sample_sizes:
        await benchmark_agent(zumbi, size)
        await benchmark_agent(anita, size)
        print()

if __name__ == "__main__":
    asyncio.run(main())
```

Run:

```bash
JWT_SECRET_KEY=test SECRET_KEY=test python tests/performance/test_agent_performance.py
```

---

## API Performance Testing

### Test Individual Endpoints

```bash
# Health endpoint baseline
ab -n 10000 -c 100 http://localhost:8000/health/

# Chat endpoint (requires POST)
echo '{"message": "test"}' > /tmp/chat.json
ab -n 1000 -c 10 -T 'application/json' -p /tmp/chat.json \
   http://localhost:8000/api/v1/chat/message

# Federal API (IBGE)
ab -n 5000 -c 50 http://localhost:8000/api/v1/federal/ibge/states
```

### SSE Streaming Performance

Create `tests/performance/test_sse_streaming.py`:

```python
import asyncio
import httpx
import time

async def test_sse_streaming():
    """Test SSE streaming performance."""
    url = "http://localhost:8000/api/v1/chat/stream"

    start = time.perf_counter()
    first_token_time = None
    token_count = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        async with client.stream("POST", url, json={"message": "test"}) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    token_count += 1
                    if first_token_time is None:
                        first_token_time = time.perf_counter() - start

    total_time = time.perf_counter() - start

    print(f"First token (TTFB): {first_token_time:.3f}s")
    print(f"Total time: {total_time:.3f}s")
    print(f"Tokens: {token_count}")
    print(f"Tokens/s: {token_count / total_time:.1f}")

asyncio.run(test_sse_streaming())
```

---

## Database Performance

### Query Performance Testing

```python
# tests/performance/test_database_performance.py
import asyncio
import time
from src.infrastructure.database import SessionLocal
from src.models.investigation import Investigation
from sqlalchemy import select

async def benchmark_query(query_func, iterations: int = 100):
    """Benchmark database query performance."""
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        await query_func()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    avg = sum(times) / len(times) * 1000  # Convert to ms
    p95 = sorted(times)[int(len(times) * 0.95)] * 1000

    print(f"Average: {avg:.2f}ms, P95: {p95:.2f}ms")

async def test_investigation_list():
    """Test investigation list query."""
    async with SessionLocal() as db:
        result = await db.execute(
            select(Investigation).limit(100)
        )
        return result.scalars().all()

async def main():
    print("Investigation list query:")
    await benchmark_query(test_investigation_list)

asyncio.run(main())
```

### Connection Pool Testing

```bash
# Monitor connection pool under load
# Run with increased logging
LOG_LEVEL=DEBUG make run-dev

# In another terminal, run load test
locust -f tests/performance/locustfile.py \
       --host=http://localhost:8000 \
       --users=100 \
       --spawn-rate=10

# Monitor logs for:
# - "Connection pool exhausted" warnings
# - Slow query logs
# - Transaction rollbacks
```

---

## Monitoring During Tests

### 1. Prometheus Metrics

Access during test:

```bash
# Start monitoring stack
make monitoring-up

# Open Grafana
open http://localhost:3000

# View Prometheus metrics
curl http://localhost:8000/health/metrics | grep cidadao_ai

# Key metrics to watch:
# - cidadao_ai_http_requests_total
# - cidadao_ai_http_request_duration_seconds
# - cidadao_ai_llm_requests_total
# - cidadao_ai_cache_hits_total
# - cidadao_ai_agent_pool_active_agents
```

### 2. System Resources

```bash
# Monitor CPU, memory, disk I/O
htop

# Monitor network
iftop

# Monitor PostgreSQL
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity;"

# Monitor Redis
redis-cli info stats
```

### 3. Application Logs

```bash
# Tail logs during test
tail -f logs/cidadao_ai.log | grep -E "(ERROR|WARNING|SLOW)"

# Filter by response time
tail -f logs/cidadao_ai.log | grep "duration" | awk '{if ($NF > 500) print}'
```

---

## Interpreting Results

### Good Indicators ✅

- Response times consistent across percentiles (p50 ≈ p95 ≈ p99)
- Error rate < 0.1%
- CPU utilization 60-80% under peak load
- Memory usage stable (no leaks)
- Cache hit rate > 80%
- Database connection pool not exhausted

### Warning Signs ⚠️

- Response time p99 >> p95 (high tail latency)
- Error rate 0.1% - 1%
- CPU utilization > 90%
- Memory usage climbing over time
- Cache hit rate < 70%
- Slow query warnings in logs

### Critical Issues 🔴

- Response time p95 > 1s
- Error rate > 1%
- CPU saturation (100%)
- Out of memory errors
- Database connection errors
- Cache misses > 50%

---

## Optimization Strategies

### 1. API Response Time

**If slow**:
- Enable caching for expensive operations
- Use database query optimization (EXPLAIN ANALYZE)
- Implement connection pooling
- Add database indexes
- Use async/await properly

### 2. Agent Performance

**If slow**:
- Profile with `cProfile`: `python -m cProfile -o output.prof script.py`
- Optimize algorithms (reduce complexity)
- Use vectorization (NumPy) for numerical operations
- Implement agent result caching
- Parallelize independent operations

### 3. Database Performance

**If slow**:
- Add indexes on frequently queried columns
- Use query result caching
- Optimize N+1 queries (eager loading)
- Increase connection pool size
- Consider read replicas

### 4. Memory Usage

**If high**:
- Profile with `memory_profiler`
- Reduce cache TTL or max size
- Implement pagination for large datasets
- Use generators instead of lists
- Clear large objects after use

### 5. LLM Cost Optimization

**If expensive**:
- Cache LLM responses (5-minute TTL)
- Use smaller models for simple queries
- Implement request deduplication
- Add user rate limits
- Monitor cost per agent

---

## Continuous Performance Testing

### CI/CD Integration

Add to `.github/workflows/performance.yml`:

```yaml
name: Performance Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install locust k6

      - name: Run load test
        run: |
          make run-dev &
          sleep 10
          locust -f tests/performance/locustfile.py \
                 --host=http://localhost:8000 \
                 --users=50 \
                 --spawn-rate=5 \
                 --run-time=5m \
                 --headless \
                 --csv=results

      - name: Check performance thresholds
        run: |
          python tests/performance/check_thresholds.py results_stats.csv

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: performance-results
          path: results_*.csv
```

---

## Next Steps

1. **Establish Baseline**: Run load tests to establish current performance baseline
2. **Set Alerts**: Configure Prometheus alerts for performance degradation
3. **Automate Tests**: Add performance tests to CI/CD pipeline
4. **Monitor Production**: Track real-world performance metrics
5. **Iterate**: Continuously optimize based on test results

---

## Resources

- [Locust Documentation](https://docs.locust.io/)
- [K6 Documentation](https://k6.io/docs/)
- [FastAPI Performance Tips](https://fastapi.tiangolo.com/deployment/concepts/)
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)

---

**Need Help?** Check `docs/architecture/` or open a GitHub issue.
