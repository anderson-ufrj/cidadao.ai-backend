# Grafana Dashboards - Quick Start Guide

Get your Cidadão.AI monitoring dashboards up and running in 5 minutes.

## Prerequisites

- Grafana 10.x+ running (via Docker or standalone)
- Prometheus configured and scraping backend metrics
- Backend running with metrics endpoint `/health/metrics`

## Quick Import (3 Steps)

### Option 1: Automated Import Script (Recommended)

```bash
# From project root
cd cidadao.ai-backend

# Using API key (recommended)
./scripts/monitoring/import_dashboards.sh http://localhost:3000 YOUR_API_KEY

# Using default credentials
./scripts/monitoring/import_dashboards.sh http://localhost:3000
```

The script will import all 6 dashboards automatically.

### Option 2: Manual Import via Grafana UI

1. **Open Grafana** → Navigate to http://localhost:3000
2. **Go to Dashboards** → Click "New" → "Import"
3. **Upload Files** → Upload each JSON file:
   - `1-production-overview.json`
   - `2-agents-performance.json`
   - `3-investigations.json`
   - `4-anomaly-detection.json`
   - `5-api-performance.json`
   - `6-infrastructure.json`
4. **Select Data Source** → Choose "Prometheus"
5. **Click Import**

### Option 3: Using Docker Provisioning

```bash
# Copy dashboards to Grafana provisioning directory
docker cp monitoring/grafana/dashboards/1-production-overview.json grafana:/etc/grafana/provisioning/dashboards/
docker cp monitoring/grafana/dashboards/2-agents-performance.json grafana:/etc/grafana/provisioning/dashboards/
docker cp monitoring/grafana/dashboards/3-investigations.json grafana:/etc/grafana/provisioning/dashboards/
docker cp monitoring/grafana/dashboards/4-anomaly-detection.json grafana:/etc/grafana/provisioning/dashboards/
docker cp monitoring/grafana/dashboards/5-api-performance.json grafana:/etc/grafana/provisioning/dashboards/
docker cp monitoring/grafana/dashboards/6-infrastructure.json grafana:/etc/grafana/provisioning/dashboards/

# Restart Grafana
docker restart grafana
```

## First Look (Start Here)

### 1. Production Overview Dashboard
**Your main entry point for system monitoring**

Navigate to: **Dashboards** → **Cidadão.AI - Production Overview**

**What to check:**
- System Uptime gauge (should be >99.5%)
- Requests per minute (current load)
- Response time p95 (should be <200ms)
- Any error spikes in error panels

**When to use:**
- Daily operations monitoring
- Incident detection
- SLA verification
- Executive reporting

### 2. Multi-Agent Performance Dashboard
**Deep dive into AI agent execution**

Navigate to: **Dashboards** → **Cidadão.AI - Multi-Agent Performance**

**What to check:**
- Agent success rate (should be >95%)
- Individual agent performance table
- Agent workload distribution heatmap
- Any agents with high failure rates

**When to use:**
- Agent optimization
- Performance tuning
- Identifying bottlenecks
- Capacity planning

### 3. Investigation Analytics Dashboard
**Track investigation workflow and throughput**

Navigate to: **Dashboards** → **Cidadão.AI - Investigation Analytics**

**What to check:**
- Investigation completion rate (should be >90%)
- Processing time trends
- Priority queue distribution
- Any investigation failures

**When to use:**
- Workflow analysis
- Throughput optimization
- User experience monitoring
- Priority queue tuning

## Common Tasks

### Monitor Production Health
1. Open **Production Overview**
2. Check uptime gauge is green (>99.5%)
3. Verify response time p95 is <200ms
4. Look for error spikes in error panels
5. Check active investigations count

### Investigate Performance Issues
1. Open **API Performance**
2. Filter by slow endpoints using variable `$endpoint`
3. Check "Top 15 Endpoints by Error Count" table
4. Review "Slow Requests by Duration Bucket"
5. Cross-reference with agent performance

### Debug Agent Problems
1. Open **Multi-Agent Performance**
2. Use `$agent_name` variable to filter specific agent
3. Check agent success rate
4. Review task duration trends
5. Analyze task type distribution

### Monitor Anomaly Detection
1. Open **Anomaly Detection**
2. Check critical anomalies count
3. Review confidence score trends
4. Analyze severity heatmap
5. Verify data source distribution

### Check Infrastructure Health
1. Open **Database & Infrastructure**
2. Verify database connections are stable
3. Check cache hit rate (should be >90%)
4. Monitor Celery worker count (should be ≥3)
5. Review circuit breaker status table

## Dashboard Navigation Flow

```
Start Here
    ↓
Production Overview (system health)
    ↓
    ├─→ High Error Rate? → API Performance
    ├─→ Slow Response? → API Performance + Multi-Agent Performance
    ├─→ Agent Issues? → Multi-Agent Performance
    ├─→ Investigation Problems? → Investigation Analytics
    ├─→ Anomaly Alerts? → Anomaly Detection
    └─→ Infrastructure Issues? → Database & Infrastructure
```

## Key Metrics at a Glance

| Metric | Target | Dashboard | Panel |
|--------|--------|-----------|-------|
| **System Uptime** | >99.5% | Production Overview | System Uptime gauge |
| **Response Time p95** | <200ms | Production Overview | Response Time stat |
| **Error Rate** | <1% | API Performance | Error Rate gauge |
| **Agent Success Rate** | >95% | Multi-Agent Performance | Agent Success Rate gauge |
| **Investigation Completion** | >90% | Investigation Analytics | Completion Rate stat |
| **Cache Hit Rate** | >90% | Database & Infrastructure | Cache Hit Rate gauge |
| **Celery Workers** | ≥3 | Database & Infrastructure | Active Celery Workers stat |

## Using Dashboard Variables

Most dashboards include variables for filtering:

### Agent Performance Dashboard
```
$agent_name = Filter by specific agent(s)
Example: Select "zumbi" to see only Zumbi agent metrics
```

### API Performance Dashboard
```
$endpoint = Filter by specific endpoint(s)
Example: Select "/api/v1/chat/*" to see only chat endpoints
```

### Investigation Analytics Dashboard
```
$priority = Filter by priority level
Example: Select "high" to see only high-priority investigations
```

### Anomaly Detection Dashboard
```
$severity = Filter by severity level
$anomaly_type = Filter by anomaly pattern
Example: Select "critical" severity to see critical anomalies only
```

## Time Range Selection

Each dashboard defaults to **last 6 hours** with **10-second refresh**.

**Common time ranges:**
- **Last 5 minutes** - Real-time monitoring, incident response
- **Last 1 hour** - Recent trends, debugging
- **Last 6 hours** - Default, operational monitoring
- **Last 24 hours** - Daily analysis, pattern identification
- **Last 7 days** - Weekly reporting, capacity planning

**To change time range:**
1. Click time range selector in top-right
2. Choose preset or custom range
3. Optionally adjust refresh rate (5s, 10s, 30s, 1m)

## Alerting Setup (Recommended)

Configure Grafana alerts for critical thresholds:

### Critical Alerts (Page immediately)
```
System Uptime < 99.5%
Response Time p95 > 1s
Error Rate > 5%
Critical Anomalies detected
Circuit Breaker OPEN
```

### Warning Alerts (Notify via Slack/Email)
```
Response Time p95 > 200ms
Error Rate > 1%
Agent Success Rate < 95%
Investigation Completion < 90%
Cache Hit Rate < 80%
```

**To set up an alert:**
1. Open dashboard
2. Edit panel
3. Click "Alert" tab
4. Create alert rule
5. Configure notification channel

## Troubleshooting

### Dashboard shows "No data"
```bash
# Check Prometheus is scraping backend
curl http://localhost:9090/targets

# Verify metrics endpoint
curl http://localhost:8000/health/metrics

# Check Prometheus can reach backend
curl http://localhost:9090/api/v1/query?query=up{job="cidadao-ai-backend"}
```

### Metrics not updating
1. Check dashboard refresh rate (should be 10s)
2. Verify Prometheus scrape interval (default 15s)
3. Ensure backend is running and generating metrics
4. Review Prometheus logs for errors

### Import fails
1. Verify Grafana version is 10.x+
2. Check JSON file is valid (not corrupted)
3. Ensure Prometheus data source exists with UID "prometheus"
4. Try importing via UI instead of API

### Panels show errors
1. Check Prometheus query syntax in panel
2. Verify metric names match actual metrics
3. Ensure time range includes data
4. Check label filters are valid

## Best Practices

### Daily Operations
- ✓ Start each day reviewing Production Overview
- ✓ Set up mobile alerts for critical metrics
- ✓ Check infrastructure dashboard for resource trends
- ✓ Review anomaly detection for new patterns

### Performance Optimization
- ✓ Use variables to focus on specific components
- ✓ Correlate metrics across dashboards
- ✓ Look for patterns in time series
- ✓ Set baselines for normal operation

### Incident Response
1. Check Production Overview for scope
2. Drill down to specific dashboard (API/Agent/Infrastructure)
3. Use time range to isolate incident window
4. Cross-reference multiple panels for root cause
5. Document findings for post-mortem

## Next Steps

1. **Customize dashboards** - Adjust panels to your needs
2. **Set up alerts** - Configure notification channels
3. **Create playlists** - Rotate dashboards on TV/monitor
4. **Export data** - Use Grafana's CSV export for reports
5. **Share links** - Generate dashboard URLs for team

## Support

For dashboard issues or questions:
- Review full documentation: `README.md`
- Check metrics implementation: `src/infrastructure/observability/metrics.py`
- Open GitHub issue with tag `monitoring`

---

**Version:** 1.0
**Last Updated:** 2025-10-30
**Maintainer:** Cidadão.AI Infrastructure Team
