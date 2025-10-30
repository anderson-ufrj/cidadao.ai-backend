# Cidadão.AI Grafana Dashboards

Comprehensive production monitoring dashboards for the Cidadão.AI backend multi-agent transparency platform.

## Dashboard Overview

| Dashboard | File | Purpose | Key Metrics |
|-----------|------|---------|-------------|
| **Production Overview** | `1-production-overview.json` | System health & SLA monitoring | Uptime, request rate, response time, errors |
| **Multi-Agent Performance** | `2-agents-performance.json` | Agent execution analytics | Task success rate, duration, workload distribution |
| **Investigation Analytics** | `3-investigations.json` | Investigation throughput | Completion rate, processing time, priority queue |
| **Anomaly Detection** | `4-anomaly-detection.json` | Real-time fraud alerts | Anomaly types, confidence scores, severity heatmap |
| **API Performance** | `5-api-performance.json` | Endpoint latency analysis | p50/p95/p99 latency, error rates, slow requests |
| **Database & Infrastructure** | `6-infrastructure.json` | Infrastructure health | PostgreSQL, Redis, Celery, circuit breakers |

---

## 1. Production Overview Dashboard

**File:** `1-production-overview.json`
**UID:** `cidadao-ai-production-overview`
**Refresh:** 10 seconds

### Purpose
Main operational dashboard for monitoring overall system health, SLA compliance, and business metrics in production.

### Key Panels

#### System Health Overview (Row 1)
- **System Uptime** (Gauge) - Success rate percentage (target: >99.5%)
- **Requests per Minute** (Stat) - Current throughput
- **Response Time p95** (Stat) - 95th percentile latency (target: <200ms)
- **Total Errors** (Stat) - Error count over time range
- **Active Investigations** (Stat) - Currently running investigations
- **Anomalies Detected** (Stat) - Total anomalies in time range

#### Request Analytics (Row 2)
- **Request Rate** (Time Series) - Successful vs error requests per second
- **Response Time Percentiles** (Time Series) - p50, p95, p99 latency trends

#### Business Metrics (Row 3)
- **Investigations by Status** (Pie Chart) - Created, completed, failed distribution
- **Anomalies by Type** (Time Series) - Fraud patterns detected over time
- **Transparency API Requests** (Time Series) - Government API usage by source

#### Error Analysis (Row 4)
- **Error Rate by Type** (Time Series) - Client vs server errors
- **Top 10 Endpoints by Error Count** (Pie Chart) - Problem endpoint identification

### Metrics Used
```promql
# Uptime
(sum(rate(cidadao_ai_http_requests_total{status="success"}[$__rate_interval])) /
 sum(rate(cidadao_ai_http_requests_total[$__rate_interval]))) * 100

# Response Time p95
histogram_quantile(0.95, sum(rate(cidadao_ai_request_duration_seconds_bucket[$__rate_interval])) by (le))

# Anomalies
sum(increase(cidadao_ai_anomalies_detected_total[$__range]))
```

### Alert Thresholds
- **Critical:** Uptime < 99.5%, Response time > 1s, Error rate > 5%
- **Warning:** Uptime < 99.9%, Response time > 200ms, Error rate > 1%

---

## 2. Multi-Agent Performance Dashboard

**File:** `2-agents-performance.json`
**UID:** `cidadao-ai-agents-performance`
**Refresh:** 10 seconds

### Purpose
Monitor the performance and health of all 16 AI agents in the system, including task execution times, success rates, and workload distribution.

### Key Panels

#### Multi-Agent Performance Overview (Row 1)
- **Total Agent Tasks** (Stat) - Sum of all agent executions
- **Agent Success Rate** (Gauge) - Percentage of successful tasks (target: >95%)
- **Agent Task Duration p95** (Stat) - 95th percentile execution time (target: <5s)
- **Failed Agent Tasks** (Stat) - Total failures in time range

#### Agent Execution Metrics (Row 2)
- **Agent Task Rate by Agent** (Time Series) - Individual agent activity levels
- **Agent Task Duration p95 by Agent** (Time Series) - Performance comparison across agents

#### Agent Task Types (Row 3)
- **Tasks by Type** (Stacked Bars) - Distribution of task types over time
- **Task Type Distribution** (Donut Chart) - Overall breakdown by type

#### Individual Agent Performance (Row 4)
- **Agent Performance Summary** (Table) - Comprehensive table showing:
  - Agent name
  - Total tasks executed
  - Success rate (with gauge visualization)
  - Average duration (color-coded)

#### Agent Workload Distribution (Row 5)
- **Agent Activity Heatmap** (Heatmap) - Visual representation of agent workload over time

### Metrics Used
```promql
# Agent success rate
(sum(rate(cidadao_ai_agent_tasks_total{status="success"}[$__rate_interval])) /
 sum(rate(cidadao_ai_agent_tasks_total[$__rate_interval]))) * 100

# Per-agent duration
histogram_quantile(0.95, sum by (agent_name, le) (rate(cidadao_ai_agent_task_duration_seconds_bucket[$__rate_interval])))

# Task type distribution
sum by (task_type) (increase(cidadao_ai_agent_tasks_total[$__range]))
```

### Variables
- `$agent_name` - Filter by specific agent(s) or view all

### Agents Monitored
- **Tier 1 (Operational):** Zumbi, Anita, Tiradentes, Machado, Senna, Bonifácio, Maria Quitéria, Oxóssi, Lampião, Oscar Niemeyer
- **Tier 2 (Framework):** Abaporu, Nanã, Drummond, Céuci, Obaluaiê
- **Tier 3 (Minimal):** Dandara

---

## 3. Investigation Analytics Dashboard

**File:** `3-investigations.json`
**UID:** `cidadao-ai-investigations`
**Refresh:** 10 seconds

### Purpose
Track investigation workflow, throughput, completion rates, and priority queue performance.

### Key Panels

#### Investigation Overview (Row 1)
- **Total Investigations** (Stat) - All investigations created
- **Completed** (Stat) - Successfully finished investigations
- **In Progress** (Stat) - Currently active investigations
- **Failed** (Stat) - Failed or errored investigations
- **Processing Time p95** (Gauge) - Investigation duration (target: <30s)

#### Investigation Throughput & Performance (Row 2)
- **Investigation Rate by Status** (Time Series) - Created, completed, failed trends
- **Investigation Duration Percentiles** (Time Series) - p50, p95, p99 processing times

#### Investigation Analytics (Row 3)
- **Investigations by Priority** (Donut Chart) - High, medium, low distribution
- **Investigations by User Type** (Donut Chart) - Regular vs admin vs API users
- **Investigations by Type** (Donut Chart) - Contract analysis, fraud detection, etc.

#### Priority Queue Analysis (Row 4)
- **Priority Queue Throughput** (Stacked Bars) - Investigations processed by priority
- **Processing Time by Investigation Type** (Time Series) - Duration comparison

#### Completion Trends (Row 5)
- **Investigation Completion Rate** (Stat) - Percentage completed successfully (target: >95%)
- **Completion Rate Trend** (Time Series) - Historical completion rate

### Metrics Used
```promql
# Completion rate
(sum(increase(cidadao_ai_investigations_total{status="completed"}[$__range])) /
 sum(increase(cidadao_ai_investigations_total[$__range]))) * 100

# Duration by type
histogram_quantile(0.95, sum by (investigation_type, le) (rate(cidadao_ai_investigation_duration_seconds_bucket[$__rate_interval])))

# Priority distribution
sum by (priority) (increase(cidadao_ai_investigations_total[$__range]))
```

### Variables
- `$priority` - Filter by investigation priority (high, medium, low)

---

## 4. Anomaly Detection Dashboard

**File:** `4-anomaly-detection.json`
**UID:** `cidadao-ai-anomaly-detection`
**Refresh:** 10 seconds

### Purpose
Real-time monitoring of anomaly detection system, fraud patterns, and confidence scoring for transparency analysis.

### Key Panels

#### Anomaly Detection Overview (Row 1)
- **Total Anomalies Detected** (Stat) - All anomalies found
- **Critical Anomalies** (Stat) - High-severity alerts
- **High Severity** (Stat) - Medium-high severity anomalies
- **Avg Confidence Score p95** (Gauge) - Confidence in detections (target: >0.8)

#### Real-Time Anomaly Detection (Row 2)
- **Anomaly Detection Rate by Severity** (Time Series) - Critical, high, medium, low trends
- **Confidence Score Trends by Anomaly Type** (Time Series) - p50 and p95 confidence

#### Anomaly Type Analysis (Row 3)
- **Anomaly Detection by Type** (Stacked Bars) - Price manipulation, bid rigging, phantom vendors, etc.
- **Anomaly Type Distribution** (Donut Chart) - Overall breakdown

#### Severity Heatmap & Data Sources (Row 4)
- **Anomaly Severity Heatmap** (Heatmap) - Type vs severity visualization
- **Anomalies by Data Source** (Time Series) - Portal da Transparência, PNCP, TCE, etc.

#### Confidence Score Distribution (Row 5)
- **Confidence Score Distribution** (Heatmap) - Histogram of confidence scores
- **Anomaly Summary Table** (Table) - Comprehensive table with:
  - Anomaly type
  - Total count
  - Average confidence (gauge)
  - Critical count (color-coded)

### Metrics Used
```promql
# Anomalies by severity
sum by (severity) (rate(cidadao_ai_anomalies_detected_total[$__rate_interval]))

# Confidence score
histogram_quantile(0.95, sum by (anomaly_type, le) (rate(cidadao_ai_anomaly_confidence_score_bucket[$__rate_interval])))

# Anomaly types
sum by (anomaly_type) (increase(cidadao_ai_anomalies_detected_total[$__range]))
```

### Variables
- `$severity` - Filter by severity level (critical, high, medium, low)
- `$anomaly_type` - Filter by specific anomaly pattern

### Annotations
- **Critical Anomalies** - Auto-annotates when critical anomalies are detected

### Anomaly Types Monitored
- Price manipulation
- Bid rigging
- Phantom vendors
- Contract splitting
- Supplier concentration
- Price deviation
- Time-based patterns

---

## 5. API Performance Dashboard

**File:** `5-api-performance.json`
**UID:** `cidadao-ai-api-performance`
**Refresh:** 10 seconds

### Purpose
Deep dive into API endpoint performance, latency analysis, error rates, and slow request identification.

### Key Panels

#### API Performance Overview (Row 1)
- **Response Time p50** (Gauge) - Median latency (target: <100ms)
- **Response Time p95** (Gauge) - 95th percentile (target: <200ms)
- **Response Time p99** (Gauge) - 99th percentile (target: <1s)
- **Error Rate** (Gauge) - Percentage of failed requests (target: <1%)

#### Endpoint Latency Analysis (Row 2)
- **Endpoint Latency p95** (Time Series) - Latency by endpoint (filterable)
- **Request Rate by Endpoint** (Time Series) - Traffic distribution

#### HTTP Method & Status Code Analysis (Row 3)
- **Requests by HTTP Method** (Stacked Bars) - GET, POST, PUT, DELETE, PATCH
- **Requests by Status Code** (Stacked Bars) - 2xx, 4xx, 5xx (color-coded)

#### Slow Requests & Error Analysis (Row 4)
- **Slow Requests by Duration Bucket** (Time Series) - 0-1s, 1-5s, 5-10s, 10-30s, 30s+
- **Top 15 Endpoints by Error Count** (Table) - Problem endpoint identification with:
  - Endpoint path
  - Error count (color-coded)
  - Error rate (gauge)

#### Rate Limiting & Concurrent Requests (Row 5)
- **Concurrent Requests by Method** (Time Series) - In-flight requests
- **Rate Limited Requests** (Time Series) - 429 responses

### Metrics Used
```promql
# Endpoint latency
histogram_quantile(0.95, sum by (endpoint, le) (rate(cidadao_ai_request_duration_seconds_bucket{endpoint=~"$endpoint"}[$__rate_interval])))

# Error rate
(sum(rate(cidadao_ai_http_errors_total[$__rate_interval])) /
 sum(rate(cidadao_ai_http_requests_total[$__rate_interval])))

# Slow requests
sum by (duration_bucket) (rate(cidadao_ai_slow_requests_total[$__rate_interval]))
```

### Variables
- `$endpoint` - Filter by specific endpoint(s) or view all

### Performance Targets
- **p50 latency:** <100ms
- **p95 latency:** <200ms
- **p99 latency:** <1s
- **Error rate:** <1%
- **Success rate:** >99%

---

## 6. Database & Infrastructure Dashboard

**File:** `6-infrastructure.json`
**UID:** `cidadao-ai-infrastructure`
**Refresh:** 10 seconds

### Purpose
Monitor infrastructure health including PostgreSQL, Redis, Celery workers, and resilience patterns (circuit breakers, bulkheads).

### Key Panels

#### Database Performance (PostgreSQL) (Row 1)
- **Database Connections** (Stat) - Active connections (warning at 50, critical at 80)
- **Avg Query Time** (Stat) - Average query execution time (target: <100ms)
- **Database Locks** (Stat) - Number of locks held (warning at 10, critical at 100)
- **Database Size** (Stat) - Current database size in bytes

#### Cache Performance (Redis) (Row 2)
- **Cache Hit Rate** (Gauge) - Percentage of cache hits (target: >90%)
- **Redis Memory Used** (Stat) - Current memory consumption
- **Redis Clients** (Stat) - Connected clients
- **Redis Evictions/sec** (Stat) - Cache eviction rate

#### Cache Operations (Row 2 continued)
- **Cache Operations** (Time Series) - Hits vs misses over time

#### Celery Workers & Task Queue (Row 3)
- **Active Celery Workers** (Stat) - Number of running workers (target: ≥3)
- **Pending Tasks** (Stat) - Tasks waiting in queue (warning at 100)
- **Active Tasks** (Stat) - Currently executing tasks
- **Failed Tasks** (Stat) - Failed task count

#### Celery Task Processing (Row 3 continued)
- **Celery Task Processing Rate** (Time Series) - Succeeded vs failed tasks

#### Circuit Breaker & Resilience (Row 4)
- **Circuit Breaker Status** (Table) - Per-service breaker state and failure count:
  - Service name
  - State (CLOSED=green, HALF_OPEN=yellow, OPEN=red)
  - Failures (color-coded)
- **Bulkhead Pattern** (Time Series) - Request isolation metrics:
  - Active requests by resource type
  - Queued requests by resource type

### Metrics Used
```promql
# Database connections
pg_stat_database_numbackends{datname="cidadao_ai"}

# Cache hit rate
(sum(rate(cidadao_ai_cache_operations_total{result="hit"}[$__rate_interval])) /
 sum(rate(cidadao_ai_cache_operations_total[$__rate_interval]))) * 100

# Celery workers
celery_workers_count

# Circuit breaker
cidadao_ai_circuit_breaker_state
sum by (service_name) (increase(cidadao_ai_circuit_breaker_failures_total[$__range]))
```

### Infrastructure Components Monitored
- **PostgreSQL:** Connections, query performance, locks, size
- **Redis:** Hit rate, memory, clients, evictions
- **Celery:** Workers, pending/active/failed tasks
- **Circuit Breakers:** State monitoring for external APIs
- **Bulkheads:** Request isolation and queueing

---

## Installation & Setup

### 1. Import Dashboards to Grafana

#### Via Grafana UI
1. Navigate to Grafana → Dashboards → Import
2. Upload each JSON file or paste JSON content
3. Select Prometheus data source
4. Click "Import"

#### Via API
```bash
# Import all dashboards at once
for dashboard in monitoring/grafana/dashboards/*.json; do
  curl -X POST http://localhost:3000/api/dashboards/db \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer YOUR_API_KEY" \
    -d @"$dashboard"
done
```

#### Via Provisioning (Recommended)
1. Copy dashboards to Grafana provisioning directory:
```bash
cp monitoring/grafana/dashboards/*.json /etc/grafana/provisioning/dashboards/
```

2. Create provisioning config at `/etc/grafana/provisioning/dashboards/cidadao-ai.yaml`:
```yaml
apiVersion: 1

providers:
  - name: 'Cidadão.AI Dashboards'
    orgId: 1
    folder: 'Cidadão.AI'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
      foldersFromFilesStructure: false
```

3. Restart Grafana:
```bash
docker-compose restart grafana
# or
systemctl restart grafana-server
```

### 2. Configure Data Source

Ensure Prometheus is configured as a data source in Grafana:

1. Navigate to Configuration → Data Sources
2. Add Prometheus data source
3. Set URL to: `http://prometheus:9090` (Docker) or `http://localhost:9090`
4. Set UID to: `prometheus` (must match dashboard configuration)
5. Test & Save

### 3. Verify Metrics Endpoint

Ensure backend is exposing Prometheus metrics:

```bash
curl http://localhost:8000/health/metrics
```

Should return Prometheus-formatted metrics.

---

## Metrics Reference

### Agent Metrics
```
cidadao_ai_agent_tasks_total{agent_name, task_type, status}
cidadao_ai_agent_task_duration_seconds{agent_name, task_type}
```

### Investigation Metrics
```
cidadao_ai_investigations_total{status, priority, user_type}
cidadao_ai_investigation_duration_seconds{investigation_type}
cidadao_ai_active_investigations
```

### Anomaly Detection Metrics
```
cidadao_ai_anomalies_detected_total{anomaly_type, severity, data_source}
cidadao_ai_anomaly_confidence_score{anomaly_type}
```

### HTTP Metrics
```
cidadao_ai_http_requests_total{method, endpoint, status_code, status}
cidadao_ai_http_errors_total{method, endpoint, status_code, error_type}
cidadao_ai_request_duration_seconds{method, endpoint, status_code}
cidadao_ai_http_requests_in_progress{method}
cidadao_ai_slow_requests_total{method, endpoint, duration_bucket}
```

### Transparency API Metrics
```
cidadao_ai_transparency_api_requests_total{api_name, endpoint, status_code}
cidadao_ai_transparency_data_fetched_total{data_type, source}
```

### Cache Metrics
```
cidadao_ai_cache_operations_total{operation, cache_type, result}
```

### Circuit Breaker Metrics
```
cidadao_ai_circuit_breaker_state{service_name}
cidadao_ai_circuit_breaker_failures_total{service_name}
```

### Bulkhead Metrics
```
cidadao_ai_bulkhead_active_requests{resource_type}
cidadao_ai_bulkhead_queued_requests{resource_type}
```

---

## Dashboard Hierarchy

```
Cidadão.AI Production Monitoring
├── 1. Production Overview (entry point)
│   ├── Links to: Agents, Investigations, Anomaly Detection
│   └── SLA compliance, system health, business metrics
├── 2. Multi-Agent Performance
│   ├── Individual agent metrics
│   ├── Task type distribution
│   └── Workload heatmap
├── 3. Investigation Analytics
│   ├── Throughput and completion
│   ├── Priority queue analysis
│   └── User type breakdown
├── 4. Anomaly Detection
│   ├── Real-time fraud alerts
│   ├── Confidence scoring
│   └── Severity heatmaps
├── 5. API Performance
│   ├── Endpoint latency
│   ├── Error analysis
│   └── Rate limiting
└── 6. Database & Infrastructure
    ├── PostgreSQL health
    ├── Redis cache performance
    ├── Celery workers
    └── Resilience patterns
```

---

## Best Practices

### Dashboard Usage
1. **Start with Production Overview** - Get overall system health at a glance
2. **Drill down** - Use links to navigate to specific dashboards
3. **Use time range selector** - Adjust view from 5min to 24h as needed
4. **Leverage variables** - Filter by agent, endpoint, priority, etc.
5. **Monitor refresh rate** - 10s default, adjust based on needs

### Alert Configuration
Set up Grafana alerts for critical thresholds:
- System uptime < 99.5%
- Response time p95 > 1s
- Error rate > 1%
- Agent success rate < 95%
- Investigation completion rate < 90%
- Critical anomalies detected

### Performance Optimization
- **For high-traffic systems:** Consider using Prometheus recording rules for complex queries
- **For long-term storage:** Configure Prometheus retention and remote write
- **For large deployments:** Use Grafana dashboard folders and permissions

---

## Troubleshooting

### Dashboard shows "No data"
1. Check Prometheus is scraping backend: `curl http://localhost:9090/targets`
2. Verify metrics endpoint: `curl http://localhost:8000/health/metrics`
3. Check Prometheus query in dashboard panel
4. Verify time range includes data

### Metrics not updating
1. Check refresh rate (default 10s)
2. Verify Prometheus scrape interval (default 15s)
3. Check backend is generating metrics
4. Review Prometheus logs for scrape errors

### High cardinality warnings
If you see high cardinality warnings:
1. Review label values (avoid user IDs, UUIDs in labels)
2. Use label aggregation in queries
3. Consider using recording rules

---

## Version Information

- **Grafana Version:** 10.x+
- **Prometheus Version:** 2.x+
- **Dashboard Schema Version:** 39
- **Created:** 2025-10-30
- **Last Updated:** 2025-10-30

---

## Related Documentation

- [Prometheus Metrics Implementation](../../../src/infrastructure/observability/metrics.py)
- [Monitoring Configuration](../../prometheus/prometheus.yml)
- [Architecture Documentation](../../../docs/architecture/)
- [Agent Documentation](../../../docs/agents/)

---

## Support & Contribution

For issues, questions, or suggestions regarding these dashboards:
- Create an issue in the project repository
- Tag with `monitoring` or `grafana`
- Include dashboard UID and panel details

**Maintainer:** Cidadão.AI Infrastructure Team
**Production URL:** https://cidadao-api-production.up.railway.app/
**Monitoring Stack:** Prometheus + Grafana on Railway
