# 📊 Agent Metrics Dashboard

**Created**: 2025-10-31
**Status**: ✅ Implemented
**API Version**: v1

## Overview

The Agent Metrics Dashboard provides real-time performance monitoring and analytics for all 16 agents in the Cidadão.AI system. It tracks response times, success rates, error patterns, and usage statistics.

## Features

### ✅ Implemented

1. **Real-time Metrics Collection**
   - Request counts per agent
   - Response time tracking (avg, p95, p99)
   - Success/failure rates
   - Error tracking with timestamps
   - Quality score monitoring

2. **Prometheus Integration**
   - Native Prometheus metrics export
   - Pre-configured Grafana dashboards
   - Time-series data collection
   - Histogram and gauge metrics

3. **API Endpoints**
   - `/api/v1/metrics/health` - Health check
   - `/api/v1/metrics/agents/summary` - All agents summary
   - `/api/v1/metrics/agents/{name}/stats` - Individual agent stats
   - `/api/v1/metrics/prometheus` - Prometheus format export
   - `/api/v1/metrics/reset` - Reset metrics

## Metrics Collected

### Per-Agent Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `agent_requests_total` | Counter | Total requests by agent, action, and status |
| `agent_request_duration_seconds` | Histogram | Request duration distribution |
| `agent_active_requests` | Gauge | Currently active requests |
| `agent_error_rate` | Gauge | Error rate (last 5 minutes) |
| `agent_memory_usage_bytes` | Gauge | Memory usage per agent |
| `agent_reflection_iterations` | Histogram | Reflection iterations distribution |
| `agent_quality_score` | Histogram | Response quality scores |

### System-Wide Metrics

| Metric | Description |
|--------|-------------|
| Total Requests | Sum of all agent requests |
| Overall Success Rate | System-wide success percentage |
| Average Response Time | Mean response time across all agents |
| Active Agents | Number of agents currently processing |
| Error Trends | Error rate changes over time |

## API Usage

### Get All Agents Summary

```bash
GET /api/v1/metrics/agents/summary
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "data": {
    "total_agents": 16,
    "total_requests": 10000,
    "total_successes": 9500,
    "total_failures": 500,
    "overall_success_rate": 0.95,
    "agents": {
      "zumbi": {
        "requests": 1500,
        "successes": 1450,
        "failures": 50,
        "avg_response_time": 1.2,
        "error_rate": 0.033
      },
      ...
    }
  }
}
```

### Get Individual Agent Stats

```bash
GET /api/v1/metrics/agents/zumbi/stats
Authorization: Bearer <token>

Response:
{
  "status": "success",
  "data": {
    "agent_name": "zumbi",
    "total_requests": 1500,
    "successful_requests": 1450,
    "failed_requests": 50,
    "average_response_time": 1.2,
    "p95_response_time": 2.5,
    "p99_response_time": 3.8,
    "error_rate": 0.033,
    "quality_score": 0.85,
    "last_used": "2025-10-31T19:00:00Z",
    "actions_breakdown": {
      "anomaly_detection": 800,
      "pattern_analysis": 500,
      "fraud_detection": 200
    }
  }
}
```

### Prometheus Metrics Export

```bash
GET /api/v1/metrics/prometheus

Response (text/plain):
# HELP agent_requests_total Total number of agent requests
# TYPE agent_requests_total counter
agent_requests_total{agent_name="zumbi",action="analyze",status="success"} 1450.0
agent_requests_total{agent_name="zumbi",action="analyze",status="failure"} 50.0
...

# HELP agent_request_duration_seconds Agent request duration in seconds
# TYPE agent_request_duration_seconds histogram
agent_request_duration_seconds_bucket{agent_name="zumbi",action="analyze",le="0.1"} 100.0
agent_request_duration_seconds_bucket{agent_name="zumbi",action="analyze",le="0.25"} 300.0
...
```

## Grafana Dashboard

### Pre-configured Panels

1. **Agent Overview**
   - Total requests per agent (bar chart)
   - Success rates comparison (gauge)
   - Average response times (line chart)

2. **Performance Metrics**
   - Response time percentiles (heatmap)
   - Request rate over time (area chart)
   - Error rate trends (line chart)

3. **Quality Metrics**
   - Quality score distribution (histogram)
   - Reflection iterations (bar chart)
   - Memory usage (line chart)

4. **Alerts & Anomalies**
   - Error spike detection
   - Performance degradation alerts
   - Memory leak warnings

### Dashboard Configuration

```yaml
# grafana/dashboards/agent-metrics.json
{
  "title": "Cidadão.AI Agent Metrics",
  "panels": [
    {
      "title": "Agent Request Rate",
      "targets": [
        {
          "expr": "rate(agent_requests_total[5m])",
          "legendFormat": "{{agent_name}}"
        }
      ]
    },
    {
      "title": "Response Time (p95)",
      "targets": [
        {
          "expr": "histogram_quantile(0.95, agent_request_duration_seconds)",
          "legendFormat": "{{agent_name}}"
        }
      ]
    }
  ]
}
```

## Monitoring Best Practices

### Key Performance Indicators (KPIs)

1. **Availability**: > 99.9% uptime per agent
2. **Response Time**: p95 < 2 seconds
3. **Success Rate**: > 95% for all agents
4. **Error Rate**: < 1% in 5-minute windows
5. **Quality Score**: > 0.8 average

### Alert Thresholds

| Alert | Condition | Severity |
|-------|-----------|----------|
| High Error Rate | > 5% errors in 5 min | Critical |
| Slow Response | p95 > 5 seconds | Warning |
| Agent Down | No requests in 10 min | Critical |
| Memory Leak | Memory growth > 100MB/hour | Warning |
| Quality Drop | Score < 0.6 | Warning |

### Performance Optimization

1. **Cache Metrics**: Metrics are cached for 5 seconds to reduce overhead
2. **Batch Updates**: Metrics are batched before writing
3. **Async Processing**: All metrics collection is non-blocking
4. **Memory Management**: Circular buffers for time-series data

## Integration with Agent Pool

The metrics service automatically integrates with the agent pool to collect:

```python
# Automatic instrumentation in agent_pool.py
async def execute_agent(agent_name: str, message: AgentMessage):
    start_time = time.time()

    # Track active requests
    agent_metrics_service.increment_active_requests(agent_name)

    try:
        result = await agent.process(message)

        # Record success
        agent_metrics_service.record_request(
            agent_name=agent_name,
            action=message.action,
            status="success",
            duration=time.time() - start_time,
            quality_score=result.quality_score
        )

    except Exception as e:
        # Record failure
        agent_metrics_service.record_request(
            agent_name=agent_name,
            action=message.action,
            status="failure",
            duration=time.time() - start_time,
            error=str(e)
        )

    finally:
        agent_metrics_service.decrement_active_requests(agent_name)
```

## Testing

### Unit Tests

```bash
# Run metrics tests
pytest tests/unit/api/test_agent_metrics.py -v

# Test coverage
pytest tests/unit/api/test_agent_metrics.py --cov=src.services.agent_metrics
```

### Load Testing

```bash
# Simulate high load
locust -f tests/load/metrics_load_test.py --host=http://localhost:8000
```

### Manual Testing

```bash
# Check metrics health
curl http://localhost:8000/api/v1/metrics/health

# Get Prometheus metrics
curl http://localhost:8000/api/v1/metrics/prometheus

# Get agent summary (requires auth)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/metrics/agents/summary
```

## Future Enhancements

1. **Advanced Analytics**
   - Trend prediction using ML
   - Anomaly detection algorithms
   - Correlation analysis between agents

2. **Custom Dashboards**
   - User-configurable dashboards
   - Export to PDF reports
   - Email alerts

3. **Historical Data**
   - Long-term storage in TimescaleDB
   - Data retention policies
   - Historical comparisons

4. **Integration**
   - Datadog export
   - New Relic integration
   - Custom webhook alerts

## Related Documentation

- [Agent Architecture](../architecture/multi-agent-architecture.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Monitoring Setup](../deployment/monitoring-setup.md)
- [Performance Tuning](../deployment/performance-tuning.md)
