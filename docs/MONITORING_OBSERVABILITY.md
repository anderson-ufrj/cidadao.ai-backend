# 📊 Monitoring & Observability Guide

**Author**: Anderson Henrique da Silva  
**Last Updated**: 2025-09-20 07:28:07 -03 (São Paulo, Brazil)

## Overview

Cidadão.AI implements a comprehensive observability stack providing real-time insights into system health, performance, and business metrics.

## 🎯 Observability Pillars

### 1. Metrics (Prometheus)
- System performance indicators
- Business KPIs
- Custom application metrics

### 2. Logs (Structured JSON)
- Centralized logging
- Correlation IDs
- Contextual information

### 3. Traces (OpenTelemetry)
- Distributed request tracking
- Service dependency mapping
- Performance bottleneck identification

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Application   │────▶│   Prometheus    │────▶│    Grafana      │
│                 │     │                 │     │                 │
│  - Metrics      │     │  - Storage      │     │  - Dashboards   │
│  - Health       │     │  - Alerting     │     │  - Alerts       │
│  - SLO/SLA      │     │  - Rules        │     │  - Reports      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## 📈 Metrics Implementation

### Business Metrics
**Location**: `src/infrastructure/observability/metrics.py`

```python
# Agent task execution
agent_tasks_total = Counter(
    'cidadao_ai_agent_tasks_total',
    'Total agent tasks executed',
    ['agent_name', 'task_type', 'status']
)

# Investigation lifecycle
investigations_total = Counter(
    'cidadao_ai_investigations_total',
    'Total investigations',
    ['status', 'investigation_type']
)

# Anomaly detection
anomalies_detected_total = Counter(
    'cidadao_ai_anomalies_detected_total',
    'Total anomalies detected',
    ['anomaly_type', 'severity', 'agent']
)
```

### System Metrics
```python
# API performance
@observe_request(
    histogram=request_duration_histogram,
    counter=request_count_counter
)
async def api_endpoint():
    # Automatic metric collection
```

### Metric Endpoints
- `/health/metrics` - Prometheus format
- `/health/metrics/json` - JSON format
- `/api/v1/observability/metrics/custom` - Custom metrics

## 🔍 Health Monitoring

### Dependency Health Checks
**Location**: `src/infrastructure/health/dependency_checker.py`

**Monitored Dependencies**:
1. **Database** - Connection pool, query performance
2. **Redis** - Cache availability, latency
3. **External APIs** - Portal da Transparência, LLM services
4. **File System** - Disk space, write permissions

**Health Check Features**:
- Parallel execution
- Configurable timeouts
- Retry logic
- Trend analysis
- Degradation detection

### Health Endpoints
```bash
GET /health                    # Basic health (for load balancers)
GET /health/detailed          # Comprehensive health report
GET /health/dependencies/{name} # Specific dependency health
POST /health/check            # Trigger manual health check
```

## 📊 SLA/SLO Monitoring

### SLO Configuration
**Location**: `src/infrastructure/monitoring/slo_monitor.py`

**Default SLOs**:
```python
# API Availability
- Target: 99.9% uptime
- Time Window: 24 hours
- Warning: 98%
- Critical: 95%

# API Response Time
- Target: P95 < 2 seconds
- Time Window: 1 hour
- Warning: 90% compliance
- Critical: 80% compliance

# Investigation Success Rate
- Target: 95% success
- Time Window: 4 hours
- Warning: 92%
- Critical: 88%

# Agent Error Rate
- Target: < 1% errors
- Time Window: 1 hour
- Warning: 0.8%
- Critical: 1.5%
```

### Error Budget Tracking
```python
# Automatic error budget calculation
error_budget_remaining = 100 - ((100 - current_compliance) / (100 - target))

# Alerts on budget consumption
if error_budget_consumed > 80%:
    alert("High error budget consumption")
```

### SLO Endpoints
```bash
GET  /api/v1/monitoring/slo                  # All SLO status
GET  /api/v1/monitoring/slo/{name}          # Specific SLO
POST /api/v1/monitoring/slo                 # Create SLO
GET  /api/v1/monitoring/error-budget        # Error budget report
GET  /api/v1/monitoring/alerts/violations   # SLO violations
```

## 📝 Structured Logging

### Implementation
**Location**: `src/infrastructure/observability/structured_logging.py`

**Log Format**:
```json
{
  "timestamp": "2025-09-20T10:28:07.123Z",
  "level": "INFO",
  "correlation_id": "uuid-1234-5678",
  "service": "cidadao-ai",
  "component": "agent.zumbi",
  "message": "Anomaly detected",
  "context": {
    "investigation_id": "inv-123",
    "anomaly_type": "price_spike",
    "confidence": 0.95
  }
}
```

**Features**:
- JSON structured format
- Correlation ID propagation
- Contextual enrichment
- Performance metrics inclusion
- Sensitive data masking

## 🔗 Distributed Tracing

### OpenTelemetry Integration
**Location**: `src/infrastructure/observability/tracing.py`

**Trace Context**:
```python
@trace_operation("investigation.analyze")
async def analyze_contracts(contracts):
    with tracer.start_span("data_validation"):
        # Automatic span creation
```

**Trace Propagation**:
- B3 headers support
- W3C Trace Context
- Baggage propagation
- Custom attributes

### Trace Visualization
- Jaeger UI integration
- Service dependency graphs
- Latency analysis
- Error tracking

## 🚨 Alerting System

### Prometheus Alert Rules
**Location**: `monitoring/prometheus/rules/cidadao-ai-alerts.yml`

**Alert Categories**:

#### 1. System Health
```yaml
- alert: SystemDown
  expr: up{job="cidadao-ai-backend"} == 0
  for: 30s
  severity: critical

- alert: HighErrorRate
  expr: error_rate > 5
  for: 2m
  severity: warning
```

#### 2. Infrastructure
```yaml
- alert: DatabaseConnectionsCritical
  expr: db_connections_used / db_connections_total > 0.95
  for: 30s
  severity: critical

- alert: CacheHitRateLow
  expr: cache_hit_rate < 70
  for: 5m
  severity: warning
```

#### 3. Agent Performance
```yaml
- alert: AgentTaskFailureHigh
  expr: agent_error_rate > 10
  for: 3m
  severity: warning

- alert: AgentQualityScoreLow
  expr: agent_quality_score < 0.8
  for: 5m
  severity: warning
```

#### 4. Business Metrics
```yaml
- alert: InvestigationSuccessRateLow
  expr: investigation_success_rate < 90
  for: 10m
  severity: warning

- alert: AnomalyDetectionAccuracyLow
  expr: anomaly_accuracy < 0.85
  for: 15m
  severity: warning
```

## 📊 Grafana Dashboards

### System Overview Dashboard
**Location**: `monitoring/grafana/dashboards/cidadao-ai-overview.json`

**Panels**:
1. System health status
2. Active investigations count
3. API response time P95
4. Anomalies detected (24h)
5. Request rate graph
6. Agent tasks performance
7. SLO compliance table
8. Error budget consumption
9. Database connection pool
10. Cache hit rate
11. External API health
12. Investigation success rate
13. Top anomaly types
14. Memory/CPU usage
15. Alert status

### Agent Performance Dashboard
**Location**: `monitoring/grafana/dashboards/cidadao-ai-agents.json`

**Panels**:
1. Agent task success rate
2. Active agents count
3. Average task duration
4. Reflection iterations
5. Performance by agent type
6. Task duration percentiles
7. Agent status distribution
8. Top performing agents
9. Error distribution
10. Agent-specific metrics
11. Memory usage by agent
12. Communication matrix
13. Quality score trends

## 🔧 Monitoring Configuration

### Prometheus Configuration
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'cidadao-ai-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/health/metrics'
```

### Grafana Data Sources
```json
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://prometheus:9090",
  "access": "proxy"
}
```

## 🎯 Key Performance Indicators

### Technical KPIs
- **Uptime**: Target 99.95%
- **API Latency P99**: < 500ms
- **Error Rate**: < 0.1%
- **Cache Hit Rate**: > 90%
- **Agent Success Rate**: > 95%

### Business KPIs
- **Investigations/Day**: Track growth
- **Anomalies Detected**: Measure effectiveness
- **Report Generation Time**: < 30s
- **User Satisfaction**: Via feedback metrics

## 🚀 APM Integration

### Supported Platforms
**Location**: `src/infrastructure/apm/`

1. **New Relic**
   ```python
   apm_integrations.setup_newrelic(
       license_key="your-key",
       app_name="cidadao-ai"
   )
   ```

2. **Datadog**
   ```python
   apm_integrations.setup_datadog(
       api_key="your-api-key",
       app_key="your-app-key"
   )
   ```

3. **Elastic APM**
   ```python
   apm_integrations.setup_elastic_apm(
       server_url="http://apm-server:8200",
       secret_token="your-token"
   )
   ```

### APM Features
- Performance tracking decorators
- Error reporting with context
- Custom business metrics
- Distributed trace correlation

## 🧪 Chaos Engineering

### Chaos Experiments
**Location**: `src/api/routes/chaos.py`

**Available Experiments**:
1. **Latency Injection**
   - Configurable delays
   - Probability-based
   - Auto-expiration

2. **Error Injection**
   - HTTP error codes
   - Configurable rate
   - Multiple error types

3. **Resource Pressure**
   - Memory consumption
   - CPU load
   - Controlled intensity

### Chaos Endpoints
```bash
POST /api/v1/chaos/inject/latency
POST /api/v1/chaos/inject/errors
POST /api/v1/chaos/experiments/memory-pressure
POST /api/v1/chaos/experiments/cpu-pressure
POST /api/v1/chaos/stop/{experiment}
GET  /api/v1/chaos/status
```

## 📈 Best Practices

1. **Set Meaningful SLOs**: Based on user expectations
2. **Monitor Business Metrics**: Not just technical ones
3. **Use Correlation IDs**: For request tracing
4. **Alert on Symptoms**: Not causes
5. **Document Runbooks**: For each alert
6. **Regular Reviews**: Of metrics and thresholds
7. **Capacity Planning**: Based on trends

## 🔍 Troubleshooting

### Missing Metrics
1. Check Prometheus scrape configuration
2. Verify metrics endpoint accessibility
3. Review metric registration code

### Alert Fatigue
1. Tune alert thresholds
2. Implement alert grouping
3. Use inhibition rules

### Dashboard Performance
1. Optimize query time ranges
2. Use recording rules
3. Implement caching

## 📚 Additional Resources

- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Grafana Dashboard Guide](https://grafana.com/docs/grafana/latest/dashboards/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [SRE Workbook](https://sre.google/workbook/)

---

For monitoring questions or improvements, contact: Anderson Henrique da Silva