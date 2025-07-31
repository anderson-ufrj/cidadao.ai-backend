# Cidadão.AI Observability Stack

## Overview

The Cidadão.AI observability stack provides comprehensive monitoring, logging, and tracing capabilities for the entire system. This enterprise-grade setup includes metrics collection, visualization, alerting, distributed tracing, and centralized logging.

## Components

### Metrics & Monitoring
- **Prometheus**: Time-series database for metrics collection
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert routing and notification
- **Node Exporter**: System-level metrics
- **cAdvisor**: Container metrics
- **PostgreSQL Exporter**: Database metrics
- **Redis Exporter**: Cache metrics

### Distributed Tracing
- **Jaeger**: End-to-end distributed tracing
- **OpenTelemetry**: Instrumentation and trace collection

### Logging
- **Loki**: Log aggregation system
- **Promtail**: Log shipping agent

## Quick Start

### 1. Start the Observability Stack

```bash
cd deployment/
./observability.sh start
```

Or manually:

```bash
docker-compose -f docker-compose.observability.yml up -d
```

### 2. Access Services

- **Grafana**: http://localhost:3001 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686
- **Alertmanager**: http://localhost:9093

### 3. Verify Everything is Working

```bash
./observability.sh status
```

## Architecture

### Metrics Flow
```
Application → Prometheus Metrics → Prometheus Server → Grafana
     ↓
OpenTelemetry → Jaeger (Tracing)
     ↓
Structured Logs → Promtail → Loki → Grafana
```

### Alert Flow
```
Prometheus → Alert Rules → Alertmanager → Email/Webhook
```

## Dashboards

Two pre-configured Grafana dashboards are included:

### 1. Cidadão.AI Overview
- API request rate and response times
- System resource usage (CPU, Memory, Disk)
- Cache hit rates
- Database performance
- Overall system health

### 2. Agent Performance
- Agent task throughput
- Task duration by agent type
- Failure rates per agent
- Active tasks monitoring
- Memory usage by agents
- Investigation statistics

## Alerts

Pre-configured alerts include:

### API Alerts
- High response time (P95 > 500ms warning, > 1s critical)
- High error rate (> 5%)
- API downtime

### Agent Alerts
- Slow agent execution (P95 > 30s)
- High failure rate (> 10%)
- Slow ML inference (> 5s)

### Infrastructure Alerts
- Database connection pool exhaustion
- Slow database queries (P95 > 1s)
- High Redis latency (> 100ms)
- Low cache hit rate (< 50%)

### System Alerts
- High CPU usage (> 80%)
- High memory usage (> 85%)
- High disk usage (> 80%)
- Container restarts

### Business Alerts
- Low investigation rate
- High anomaly detection rate
- External API downtime

## Configuration

### Adding New Metrics

1. In your Python code:
```python
from prometheus_client import Counter, Histogram

# Define metric
my_metric = Counter('my_metric_total', 'Description', ['label1', 'label2'])

# Use metric
my_metric.labels(label1='value1', label2='value2').inc()
```

2. The metric will automatically be scraped by Prometheus

### Creating Custom Dashboards

1. Create dashboard in Grafana UI
2. Export as JSON
3. Save to `grafana/dashboards/`
4. Restart Grafana to auto-provision

### Adding Alerts

1. Edit `prometheus/alerts/cidadao_alerts.yml`
2. Add new alert rule:
```yaml
- alert: MyNewAlert
  expr: my_metric > 100
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "My metric is too high"
```
3. Restart Prometheus

### Configuring Alert Notifications

Edit `alertmanager/alertmanager.yml` to add new receivers:

```yaml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
```

## Troubleshooting

### Check Service Health
```bash
# All services
./observability.sh status

# Specific service logs
./observability.sh logs prometheus
```

### Common Issues

1. **Prometheus can't scrape metrics**
   - Ensure the backend API is running
   - Check if `/metrics` endpoint is accessible
   - Verify network connectivity

2. **Grafana dashboards not loading**
   - Check data source configuration
   - Verify Prometheus is running
   - Look for errors in Grafana logs

3. **No traces in Jaeger**
   - Verify OTEL_EXPORTER_JAEGER_ENDPOINT is set
   - Check if tracing is enabled in the application
   - Look for errors in application logs

4. **Alerts not firing**
   - Check alert rules syntax
   - Verify metrics exist in Prometheus
   - Check Alertmanager logs

## Performance Considerations

- **Retention**: Default 30 days for Prometheus, adjust in `prometheus.yml`
- **Storage**: Monitor disk usage, especially for Prometheus and Loki
- **Memory**: Prometheus and Elasticsearch are memory-intensive
- **CPU**: cAdvisor and exporters add minimal CPU overhead

## Security

- Change default passwords in production
- Use TLS for external access
- Implement authentication for all services
- Restrict network access to monitoring endpoints

## Maintenance

### Backup
```bash
# Backup Prometheus data
docker exec cidadao-prometheus tar -czf - /prometheus > prometheus-backup.tar.gz

# Backup Grafana dashboards
docker exec cidadao-grafana tar -czf - /var/lib/grafana > grafana-backup.tar.gz
```

### Updates
```bash
# Update services
docker-compose -f docker-compose.observability.yml pull
./observability.sh stop
./observability.sh start
```

## Integration with CI/CD

Add monitoring checks to your pipeline:

```yaml
- name: Check API Health
  run: |
    curl -f http://localhost:8000/health || exit 1
    
- name: Check Metrics Endpoint
  run: |
    curl -f http://localhost:8000/metrics || exit 1
```

## Further Reading

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)