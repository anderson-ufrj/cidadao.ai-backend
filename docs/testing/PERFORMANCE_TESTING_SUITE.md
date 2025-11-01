# 🚀 Performance Testing Suite Documentation

**Created**: 2025-11-01
**Version**: 1.0
**Status**: ✅ Implemented

## Overview

The Cidadão.AI Performance Testing Suite provides comprehensive performance validation for the backend system, including API endpoints, agent processing, and system resources.

## Test Categories

### 1. API Performance Tests (`test_api_performance.py`)

Tests API endpoint response times and throughput.

#### Features:
- **Concurrent Request Testing**: Measures endpoint performance under concurrent load
- **Response Time Validation**: Ensures endpoints meet SLA requirements
- **Throughput Measurement**: Calculates requests per second
- **Percentile Analysis**: P50, P95, P99 response times

#### Key Endpoints Tested:
- `/health/` - Health check endpoint
- `/api/v1/agents/` - Agent listing
- `/api/v1/chat/message` - Chat processing
- `/graphql` - GraphQL queries

#### Performance Thresholds:
```python
RESPONSE_TIME_THRESHOLD = 0.5  # 500ms for standard endpoints
CHAT_THRESHOLD = 5.0           # 5s for chat processing
SUCCESS_RATE_THRESHOLD = 95    # 95% success rate required
```

### 2. System Benchmarks (`test_benchmark.py`)

Measures execution time and resource usage for critical operations.

#### Features:
- **Agent Initialization**: Benchmarks agent startup times
- **Anomaly Detection**: Measures processing time for contract analysis
- **Statistical Analysis**: Benchmarks data analysis operations
- **Report Generation**: Measures report creation performance
- **Concurrent Processing**: Tests multi-agent parallel execution
- **Memory Leak Detection**: Monitors for memory leaks
- **CPU Usage Tracking**: Measures CPU utilization

#### Performance Requirements:
- Agent initialization: < 100ms
- Anomaly detection (100 contracts): < 2s
- Statistical analysis: < 3s
- Report generation: < 1s
- Memory growth: < 50MB over 100 iterations

### 3. Load Testing (`test_load.py`)

Simulates multiple users and high traffic scenarios.

#### Features:
- **Virtual Users**: Simulates concurrent user sessions
- **Ramp-up Control**: Gradual user increase
- **Scenario Testing**: User journey simulation
- **Think Time**: Realistic user behavior modeling

#### Test Scenarios:

##### Basic Load Test
- **Users**: 10 concurrent
- **Ramp-up**: 5 seconds
- **Duration**: 30 seconds
- **Success Rate Target**: ≥ 95%

##### Spike Test
- **Users**: 50 concurrent
- **Ramp-up**: 2 seconds (fast)
- **Duration**: 20 seconds
- **Success Rate Target**: ≥ 80%

##### Sustained Load Test
- **Users**: 20 concurrent
- **Ramp-up**: 10 seconds
- **Duration**: 120 seconds
- **Success Rate Target**: ≥ 90%

### 4. Existing Agent Performance Tests (`test_agent_performance.py`)

Comprehensive agent-specific performance validation.

## Running Performance Tests

### Prerequisites
```bash
# Install required packages
pip install pytest pytest-asyncio httpx psutil memory-profiler

# Ensure server is running
make run-dev
```

### Running Individual Test Categories

```bash
# API Performance Tests
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/performance/test_api_performance.py -v

# System Benchmarks
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/performance/test_benchmark.py -v

# Load Tests
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/performance/test_load.py -v

# Agent Performance Tests
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/performance/test_agent_performance.py -v
```

### Running Complete Suite

```bash
# Run all performance tests
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/performance/ -v -m performance

# Run with detailed output
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/performance/ -v -s

# Generate performance report
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/performance/ --html=performance_report.html
```

### Standalone Execution

Each test file can also be run standalone:

```bash
# API Performance
python tests/performance/test_api_performance.py

# Benchmarks
python tests/performance/test_benchmark.py

# Load Tests
python tests/performance/test_load.py
```

## Performance Metrics

### Key Performance Indicators (KPIs)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| API Response Time (P95) | < 500ms | TBD | 🔄 |
| Agent Processing Time | < 3s | TBD | 🔄 |
| Chat Response Time | < 5s | TBD | 🔄 |
| GraphQL Query Time | < 1s | TBD | 🔄 |
| Success Rate | > 95% | TBD | 🔄 |
| Memory Usage | < 500MB | TBD | 🔄 |
| CPU Usage | < 70% | TBD | 🔄 |
| Concurrent Users | 50+ | TBD | 🔄 |

### Response Time Targets

| Endpoint | P50 | P95 | P99 |
|----------|-----|-----|-----|
| `/health/` | 50ms | 100ms | 200ms |
| `/api/v1/agents/` | 100ms | 500ms | 1s |
| `/api/v1/chat/message` | 1s | 3s | 5s |
| `/graphql` | 200ms | 1s | 2s |

## Test Output Examples

### API Performance Test Output
```
=== Load Test Results ===
Total Requests: 30
Success Rate: 96.7%
Avg Response Time: 0.234s
P50: 0.198s
P95: 0.456s
P99: 0.512s
```

### Benchmark Test Output
```
BENCHMARK RESULTS SUMMARY
========================================
Zumbi Init:
  Total Time: 1.234s
  Avg Time: 0.062s
  Memory: 12.34 MB
  CPU: 45.2%
  Iterations: 20

Anomaly Detection (100 contracts):
  Total Time: 8.456s
  Avg Time: 1.691s
  Memory: 34.56 MB
  CPU: 62.3%
  Iterations: 5
========================================
```

### Load Test Output
```
🚀 Starting load test with 20 users
   Ramp-up time: 10s
   Test duration: 120s
   Spawned 20/20 users...

📊 Sustained Load Test Results:
   Duration: 120.5s
   Total Requests: 240
   Success Rate: 92.5%
   RPS: 1.99
   Avg Response Time: 1.234s
   P95 Response Time: 2.456s
```

## Performance Optimization Tips

### 1. Database Optimization
- Use connection pooling
- Optimize queries with indexes
- Implement query result caching
- Use batch operations

### 2. Agent Optimization
- Implement agent pooling
- Use async processing
- Cache agent results
- Optimize reflection iterations

### 3. API Optimization
- Enable response compression
- Implement request throttling
- Use CDN for static content
- Enable HTTP/2

### 4. System Optimization
- Configure worker processes
- Tune garbage collection
- Monitor memory usage
- Profile CPU hotspots

## Continuous Performance Testing

### Integration with CI/CD

```yaml
# .github/workflows/performance.yml
name: Performance Tests
on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  workflow_dispatch:

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Performance Tests
        run: |
          make run-dev &
          sleep 10
          pytest tests/performance/ -v --tb=short
```

### Performance Regression Detection

Set up alerts for performance degradation:

```python
# In test files
assert stats["avg"] < BASELINE * 1.1, \
    f"Performance regression: {stats['avg']} > {BASELINE * 1.1}"
```

## Troubleshooting

### Common Issues

#### 1. Connection Refused
```bash
# Ensure server is running
make run-dev
# Or
uvicorn src.api.app:app --reload
```

#### 2. Timeout Errors
- Increase timeout values in test configuration
- Check server resource limits
- Review agent processing logic

#### 3. Memory Issues
- Monitor with `htop` or `top`
- Check for memory leaks
- Increase system memory limits

#### 4. Inconsistent Results
- Run tests multiple times
- Check system load
- Isolate test environment

## Future Enhancements

### Planned Improvements
1. **Grafana Dashboard**: Real-time performance monitoring
2. **JMeter Integration**: Advanced load testing scenarios
3. **Database Performance**: Query optimization tests
4. **WebSocket Testing**: Real-time connection performance
5. **Cache Performance**: Redis benchmark tests
6. **ML Model Performance**: Inference time benchmarks

### Proposed Metrics
- Database query performance
- Cache hit rates
- WebSocket message latency
- ML model inference time
- Background job processing time

## Related Documentation

- [Testing Guide](./TESTING_GUIDE.md)
- [API Documentation](../api/API_DOCUMENTATION.md)
- [Agent Documentation](../agents/README.md)
- [Performance Optimization](../architecture/PERFORMANCE_OPTIMIZATION.md)

## Summary

The Performance Testing Suite provides comprehensive validation of system performance across multiple dimensions:

✅ **API Performance**: Response time and throughput validation
✅ **System Benchmarks**: Resource usage and execution time measurement
✅ **Load Testing**: Multi-user scenario simulation
✅ **Agent Performance**: Agent-specific processing validation

The suite ensures the Cidadão.AI backend maintains high performance standards and can handle production workloads effectively.
