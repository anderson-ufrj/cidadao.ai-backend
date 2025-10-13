# Federal APIs Monitoring Dashboard

## Overview

Comprehensive Grafana dashboard for monitoring IBGE, DataSUS, and INEP API clients with real-time performance metrics, error tracking, and cache efficiency analysis.

**Dashboard UID**: `federal-apis`
**Refresh Rate**: 10 seconds
**Datasource**: Prometheus

## Dashboard Sections

### 1. Federal APIs Overview (3 panels)
- **Request Rate**: Real-time requests per second by API and status
- **Error Rate**: Overall error percentage (gauge with thresholds)
- **Request Duration Percentiles**: p50, p95, p99 latency tracking

### 2. Cache Performance (2 panels)
- **Cache Hit/Miss Ratio**: Efficiency of caching layer by API
- **Cache Size**: Current in-memory cache entries

### 3. Error Tracking (2 panels)
- **Errors by Type and Retryability**: Categorized error visualization
- **Timeout Rate**: Timeout occurrences per API

### 4. Retry Behavior (2 panels)
- **Retry Attempts by Reason**: Why requests are being retried
- **Average Retry Attempts**: Mean retries per request

### 5. Data Volume & Performance (3 panels)
- **Records Fetched**: Data volume by API and type
- **Response Size Distribution**: P50, P95, P99 response sizes
- **Active Requests**: Current concurrent requests gauge

### 6. Additional Metrics (5 panels)
- Individual API request rates (IBGE, DataSUS, INEP)
- Individual API error rates
- Rate limit tracking

## Metrics Exposed

All metrics use the `federal_api_*` prefix and include the following labels:

### Common Labels
- `api_name`: IBGE, DataSUS, or INEP
- `method`: HTTP method (GET, POST)
- `endpoint`: API endpoint called
- `status`: success, error, timeout
- `status_code`: HTTP status code

### Key Metrics

#### Request Metrics
```promql
# Request duration histogram
federal_api_request_duration_seconds{api_name="IBGE",method="GET",endpoint="states",status="success"}

# Request counter
federal_api_requests_total{api_name="IBGE",method="GET",endpoint="states",status_code="200"}
```

#### Cache Metrics
```promql
# Cache operations (hit, miss, write)
federal_api_cache_operations_total{api_name="IBGE",operation="read",result="hit"}

# Cache size gauge
federal_api_cache_size{api_name="IBGE",cache_type="memory"}
```

#### Error Metrics
```promql
# Error counter with type classification
federal_api_errors_total{api_name="IBGE",error_type="NetworkError",retryable="true"}

# Timeout tracking
federal_api_timeouts_total{api_name="IBGE",method="GET",timeout_seconds="30"}

# Rate limit tracking
federal_api_rate_limits_total{api_name="IBGE",retry_after="60"}
```

#### Retry Metrics
```promql
# Retry counter
federal_api_retries_total{api_name="IBGE",method="GET",reason="network_error"}

# Retry attempts histogram
federal_api_retry_attempts{api_name="IBGE",method="GET"}
```

#### Data Volume Metrics
```promql
# Records fetched counter
federal_api_records_fetched_total{api_name="IBGE",data_type="states"}

# Response size histogram
federal_api_response_size_bytes{api_name="IBGE",endpoint="states"}

# Active requests gauge
federal_api_active_requests{api_name="IBGE"}
```

## Installation & Setup

### Prerequisites
- Docker and Docker Compose installed
- User in docker group (for non-root access)
- Cidadão.AI backend configured

### Quick Start

1. **Validate configuration**:
   ```bash
   cd /home/anderson-henrique/Documentos/cidadao.ai/cidadao.ai-backend
   ./monitoring/test-dashboard.sh
   ```

2. **Start monitoring stack**:
   ```bash
   ./monitoring/manage-monitoring.sh start
   ```

3. **Access Grafana**:
   - URL: http://localhost:3000
   - Username: `admin`
   - Password: `cidadao123`

4. **Find the dashboard**:
   - Navigate to: Dashboards → Browse
   - Look for: "Federal APIs Monitoring"
   - Or direct URL: http://localhost:3000/d/federal-apis

### Verify Metrics Endpoint

Check that metrics are being exposed:

```bash
# Check metrics endpoint (when backend is running)
curl http://localhost:7860/health/metrics | grep federal_api

# Expected output includes:
# federal_api_requests_total
# federal_api_request_duration_seconds
# federal_api_cache_operations_total
# federal_api_errors_total
# ... and more
```

## Generating Test Data

To populate the dashboard with metrics, make API calls:

```bash
# Start the backend
make run-dev

# Or directly
python -m src.api.app

# Make test requests (from another terminal)
curl http://localhost:8000/api/v1/transparency/ibge/states
curl http://localhost:8000/api/v1/transparency/ibge/municipalities?state_code=33
curl http://localhost:8000/api/v1/transparency/datasus/health-indicators?state_code=RJ
curl http://localhost:8000/api/v1/transparency/inep/institutions?state=SP&limit=10
```

Wait 15-30 seconds for Prometheus to scrape metrics, then refresh the Grafana dashboard.

## Dashboard Configuration

### Auto-Provisioning

The dashboard is automatically loaded via Grafana provisioning:

**Provisioning Config** (`monitoring/grafana/provisioning/dashboards/dashboards.yml`):
```yaml
providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    options:
      path: /var/lib/grafana/dashboards
```

**Volume Mount** (in `config/docker/docker-compose.monitoring.yml`):
```yaml
volumes:
  - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
```

### Customization

To customize the dashboard:

1. **Edit JSON directly**:
   ```bash
   vim monitoring/grafana/dashboards/federal-apis-dashboard.json
   ```

2. **Or edit in Grafana UI**:
   - Make changes in Grafana
   - Export JSON via Share → Export → Save to file
   - Replace `federal-apis-dashboard.json` with exported version

3. **Restart Grafana** to load changes:
   ```bash
   ./monitoring/manage-monitoring.sh restart
   ```

## Prometheus Configuration

The dashboard queries Prometheus, which scrapes metrics from the backend.

**Scrape Config** (`monitoring/prometheus/prometheus.yml`):
```yaml
scrape_configs:
  - job_name: 'cidadao-ai'
    scrape_interval: 15s
    static_configs:
      - targets: ['cidadao-ai:7860']
    metrics_path: '/health/metrics'
```

**Key Settings**:
- Scrape interval: 15 seconds
- Scrape timeout: 10 seconds
- Retention: 30 days or 5GB (whichever comes first)

## Troubleshooting

### Dashboard Not Appearing

**Check provisioning logs**:
```bash
./monitoring/manage-monitoring.sh logs grafana | grep provisioning
```

**Verify file exists**:
```bash
ls -lh monitoring/grafana/dashboards/federal-apis-dashboard.json
```

**Check JSON validity**:
```bash
python3 -c "import json; json.load(open('monitoring/grafana/dashboards/federal-apis-dashboard.json'))"
```

### No Data in Panels

**Check metrics endpoint**:
```bash
curl http://localhost:7860/health/metrics
```

**Check Prometheus targets**:
- Open: http://localhost:9090/targets
- Verify `cidadao-ai` target is UP

**Check Prometheus queries**:
- Open: http://localhost:9090
- Run test query: `federal_api_requests_total`

**Verify backend is running**:
```bash
curl http://localhost:7860/health
```

### Permission Errors

**Docker permission denied**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again
# Or activate group without logout:
newgrp docker
```

**Data directory permissions**:
```bash
sudo chmod 777 monitoring/prometheus/data
sudo chmod 777 monitoring/grafana/data
```

### High Memory Usage

Prometheus data retention can be adjusted:

**Edit** `config/docker/docker-compose.monitoring.yml`:
```yaml
command:
  - '--storage.tsdb.retention.time=15d'  # Reduce from 30d
  - '--storage.tsdb.retention.size=2GB'  # Reduce from 5GB
```

**Restart**:
```bash
./monitoring/manage-monitoring.sh restart
```

## Alert Configuration

To add alerts for Federal API metrics:

1. **Create alert rules** in `monitoring/prometheus/rules/federal-apis-alerts.yml`:

```yaml
groups:
  - name: federal_apis
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(federal_api_requests_total{status="error"}[5m]))
          /
          sum(rate(federal_api_requests_total[5m]))
          > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate on Federal APIs"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(federal_api_request_duration_seconds_bucket[5m]))
            by (api_name, le)
          ) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency on {{ $labels.api_name }}"
          description: "P95 latency is {{ $value }}s"

      - alert: LowCacheHitRate
        expr: |
          sum(rate(federal_api_cache_operations_total{result="hit"}[5m]))
          /
          sum(rate(federal_api_cache_operations_total{operation="read"}[5m]))
          < 0.5
        for: 10m
        labels:
          severity: info
        annotations:
          summary: "Low cache hit rate on {{ $labels.api_name }}"
          description: "Hit rate is {{ $value | humanizePercentage }}"
```

2. **Reload Prometheus**:
```bash
curl -X POST http://localhost:9090/-/reload
```

## Performance Optimization

### For High-Traffic Scenarios

**Increase Prometheus resources**:
```yaml
services:
  prometheus:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

**Adjust scrape interval**:
```yaml
scrape_configs:
  - job_name: 'cidadao-ai'
    scrape_interval: 30s  # Increase from 15s
```

**Enable query caching in Grafana**:
```yaml
environment:
  - GF_DATAPROXY_TIMEOUT=60
  - GF_DATAPROXY_KEEP_ALIVE_SECONDS=300
```

## Validation Status

✅ **All validations passed** (2025-10-12):

- ✅ Dashboard JSON is valid (17 panels)
- ✅ Provisioning configuration correct
- ✅ All 5 key metrics registered
- ✅ All 3 API clients instrumented
- ✅ PromQL queries validated
- ✅ Docker configuration verified

**Test script location**: `monitoring/test-dashboard.sh`

## Related Documentation

- [Monitoring Stack README](README.md) - Overall monitoring documentation
- [Metrics Module](../src/services/transparency_apis/federal_apis/metrics.py) - Metrics implementation
- [IBGE Client](../src/services/transparency_apis/federal_apis/ibge_client.py) - IBGE API client
- [DataSUS Client](../src/services/transparency_apis/federal_apis/datasus_client.py) - DataSUS API client
- [INEP Client](../src/services/transparency_apis/federal_apis/inep_client.py) - INEP API client

## Next Steps

1. **Run full test**:
   ```bash
   ./monitoring/manage-monitoring.sh start
   # Wait for services to start
   ./monitoring/manage-monitoring.sh health
   # Access http://localhost:3000
   ```

2. **Configure alerts** (see Alert Configuration section above)

3. **Set up long-term storage** (optional):
   - Configure Prometheus remote write to long-term storage
   - Options: Thanos, Cortex, VictoriaMetrics

4. **Add more dashboards**:
   - Individual API deep-dive dashboards
   - SLO/SLA tracking dashboard
   - Comparative analysis dashboard

## License

Proprietary - All rights reserved
Author: Anderson Henrique da Silva
Created: 2025-10-12
