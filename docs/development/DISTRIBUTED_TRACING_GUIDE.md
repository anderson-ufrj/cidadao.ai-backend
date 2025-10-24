# Distributed Tracing Guide

**Date**: 2025-10-24
**Status**: Production-Ready
**OpenTelemetry Version**: 1.22.0+

---

## Overview

Cidadão.AI backend has **comprehensive OpenTelemetry distributed tracing** already implemented and operational. This guide shows developers how to leverage the existing infrastructure for debugging, performance analysis, and production observability.

## What's Already Working ✅

The system has **complete auto-instrumentation** for:

- **FastAPI**: All HTTP requests automatically traced
- **SQLAlchemy**: Database queries with execution time
- **Redis**: Cache operations (GET, SET, HGET, etc.)
- **httpx**: External API calls (30+ transparency sources)
- **PostgreSQL**: AsyncPG instrumentation enabled

### Architecture

```
User Request
    ↓
[FastAPI Auto-Instrumentation] ← HTTP spans
    ↓
[Agent Processing] ← Manual spans (optional)
    ↓
[Database Queries] ← SQLAlchemy auto-instrumentation
    ↓
[Cache Operations] ← Redis auto-instrumentation
    ↓
[External APIs] ← httpx auto-instrumentation
    ↓
Response
```

All spans are:
- **Correlated by trace_id**: Follow requests across components
- **Enriched with context**: Investigation ID, user ID, agent name
- **Exported to OTLP**: Ready for Jaeger, Tempo, or cloud backends

---

## Configuration

### Environment Variables

```bash
# Core OpenTelemetry Configuration
OTEL_SERVICE_NAME=cidadao-ai-backend
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317  # Jaeger/Tempo/etc
OTEL_TRACES_EXPORTER=otlp
OTEL_METRICS_EXPORTER=otlp

# Optional: Enable console exporter for debugging
DEBUG=true  # Enables console span export
```

### Railway Production Setup

```bash
# In Railway dashboard, set:
railway variables set OTEL_EXPORTER_OTLP_ENDPOINT=https://your-collector:4317
railway variables set OTEL_SERVICE_NAME=cidadao-ai-backend
railway restart
```

---

## Using Distributed Tracing

### 1. Auto-Instrumentation (Already Working)

**Zero code changes required!** The following are automatically traced:

#### HTTP Endpoints
```python
# In src/api/routes/chat.py
@router.post("/message")
async def send_message(request: ChatRequest):
    # Automatically creates span: "POST /api/v1/chat/message"
    # Includes: status_code, headers, request_id
    ...
```

#### Database Queries
```python
# Any SQLAlchemy query
async with db.session() as session:
    results = await session.execute(
        select(Investigation).where(Investigation.id == inv_id)
    )
    # Automatically creates span: "SELECT investigations"
    # Includes: query (sanitized), execution_time, rows_returned
```

#### Cache Operations
```python
# src/core/cache.py
await cache.get("contracts:123")
# Automatically creates span: "redis.GET"
# Includes: key, hit/miss, duration
```

#### External API Calls
```python
# httpx requests
async with httpx.AsyncClient() as client:
    response = await client.get(api_url)
    # Automatically creates span: "GET {api_url}"
    # Includes: status_code, retry_attempts, headers
```

### 2. Manual Spans for Agent Logic

For **custom operations**, add manual spans to track agent-specific logic:

#### Example: Zumbi Anomaly Detection

```python
from src.infrastructure.observability.tracing import (
    get_tracer,
    trace_operation,
    TraceContext,
    SpanMetrics,
)

class InvestigatorAgent(BaseAgent):
    async def process(self, message: AgentMessage, context: AgentContext):
        # Get tracer instance
        tracer = get_tracer()

        # Create top-level span for investigation
        async with trace_operation(
            "agent.zumbi.process_investigation",
            attributes={
                "agent.name": self.name,
                "investigation.id": context.investigation_id,
                "contracts.count": len(contracts),
            }
        ) as span:
            # Set investigation context (propagates to child spans)
            TraceContext.set_investigation_context(context.investigation_id)

            # Fetch data (httpx auto-traces external calls)
            contracts = await self._fetch_contracts(request)

            # Add event to current span
            TraceContext.add_event(
                "contracts_fetched",
                {"count": len(contracts), "source": "portal_transparencia"}
            )

            # Detect anomalies with nested span
            with tracer.start_as_current_span("anomaly_detection.price_analysis") as child_span:
                anomalies = self._detect_price_anomalies(contracts)

                # Add metrics to span
                SpanMetrics.record_agent_execution(
                    child_span,
                    agent_name="zumbi",
                    task_type="price_anomaly",
                    confidence_score=0.92
                )

                child_span.set_attribute("anomalies.found", len(anomalies))

            return AgentResponse(result=anomalies)
```

#### Using the @trace_function Decorator

```python
from src.infrastructure.observability.tracing import trace_function

@trace_function(
    operation_name="agent.tiradentes.generate_pdf",
    include_args=True,
    include_result=True
)
async def generate_pdf_report(investigation_id: str, format: str = "A4"):
    """
    Generate PDF report for investigation.

    Automatically creates span with:
    - function.name: generate_pdf_report
    - function.module: src.agents.tiradentes
    - args.0: investigation_id value
    - kwargs.format: "A4"
    - function.duration_ms: execution time
    - function.result_length: PDF size
    """
    pdf_bytes = await self._render_pdf(investigation_id, format)
    return pdf_bytes
```

### 3. Context Propagation

Use `TraceContext` to enrich spans with domain context:

```python
from src.infrastructure.observability.tracing import TraceContext

# Set user context (propagates to all child spans)
TraceContext.set_user_context(
    user_id="user-123",
    user_email="analista@governo.br"
)

# Set investigation context
TraceContext.set_investigation_context("inv-456")

# Add custom events
TraceContext.add_event(
    "fraud_pattern_detected",
    {
        "pattern_type": "phantom_vendor",
        "confidence": 0.89,
        "contracts_affected": 15
    }
)
```

---

## Viewing Traces

### Option 1: Jaeger (Recommended for Development)

1. **Start Jaeger** (included in docker-compose.monitoring.yml):
   ```bash
   make monitoring-up
   ```

2. **Access Jaeger UI**:
   - URL: http://localhost:16686
   - Service: `cidadao-ai-backend`

3. **Search traces**:
   - By investigation ID
   - By user ID
   - By time range
   - By latency (e.g., > 1s)

4. **Analyze trace**:
   ```
   GET /api/v1/chat/message [145ms]
   ├─ agent.zumbi.process_investigation [132ms]
   │  ├─ httpx.GET /transparency/contracts [45ms]
   │  ├─ anomaly_detection.price_analysis [38ms]
   │  ├─ redis.SET contracts:cache [2ms]
   │  └─ sqlalchemy.INSERT investigations [5ms]
   └─ POST /api/v1/investigations [8ms]
   ```

### Option 2: Grafana Tempo (Production)

For Railway production:

1. **Configure Tempo endpoint**:
   ```bash
   railway variables set OTEL_EXPORTER_OTLP_ENDPOINT=https://tempo.your-org.com:4317
   ```

2. **Query in Grafana**:
   - Use Tempo data source
   - Search by `investigation.id`, `user.id`, `agent.name`
   - Link traces to logs and metrics

### Option 3: Cloud Providers

#### AWS X-Ray
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://xray.us-east-1.amazonaws.com:4317
```

#### Google Cloud Trace
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://cloudtrace.googleapis.com:4317
```

#### Azure Monitor
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=https://dc.services.visualstudio.com:4317
```

---

## Common Patterns

### Pattern 1: Multi-Agent Investigation

```python
async def run_multi_agent_investigation(query: str):
    tracer = get_tracer()

    with tracer.start_as_current_span("multi_agent.orchestration") as span:
        span.set_attribute("query", query)
        span.set_attribute("agents.count", 3)

        # Zumbi: Anomaly detection (auto-traced)
        anomalies = await zumbi.process(...)
        TraceContext.add_event("zumbi_completed", {"anomalies": len(anomalies)})

        # Anita: Statistical analysis (auto-traced)
        stats = await anita.process(...)
        TraceContext.add_event("anita_completed", {"clusters": stats.clusters})

        # Tiradentes: Report generation (auto-traced)
        report = await tiradentes.process(...)
        TraceContext.add_event("tiradentes_completed", {"pages": report.pages})

        return CombinedResult(anomalies=anomalies, stats=stats, report=report)
```

**Trace visualization**:
```
multi_agent.orchestration [3.2s]
├─ agent.zumbi.process [1.8s]
│  ├─ httpx.GET /contracts [450ms]
│  ├─ anomaly_detection [800ms]
│  └─ redis.SET [5ms]
├─ agent.anita.process [1.1s]
│  ├─ clustering.kmeans [600ms]
│  └─ sqlalchemy.SELECT [50ms]
└─ agent.tiradentes.process [300ms]
   ├─ pdf.generate [280ms]
   └─ s3.upload [18ms]
```

### Pattern 2: Error Tracking

Exceptions are automatically recorded in spans:

```python
async with trace_operation("risky_operation") as span:
    try:
        result = await external_api_call()
    except APITimeout as e:
        # Span automatically records:
        # - error.type: APITimeout
        # - error.message: "Request timed out after 30s"
        # - status: ERROR
        raise
```

### Pattern 3: Performance Monitoring

```python
from src.infrastructure.observability.tracing import SpanMetrics

async with trace_operation("batch_processing") as span:
    for batch in batches:
        with tracer.start_as_current_span(f"process_batch_{batch.id}") as batch_span:
            results = await process_batch(batch)

            # Record metrics
            SpanMetrics.record_database_operation(
                batch_span,
                operation="batch_insert",
                table="contracts",
                rows_affected=len(results)
            )
```

---

## Debugging with Traces

### Problem: "Why is this investigation slow?"

1. **Find the trace** in Jaeger by investigation_id
2. **Identify slowest span**:
   - `httpx.GET /transparency/contracts` → 8s (slow!)
   - External API timeout? Add retry logic
3. **Check span attributes**:
   - `http.status_code: 503` → API unavailable
   - `retry.attempts: 3` → Circuit breaker triggered

### Problem: "Agent returned wrong results"

1. **Follow trace** through agent processing
2. **Check span events**:
   ```
   contracts_fetched: count=0 ← No data fetched!
   cache.hit: false
   db.query.rows: 0
   ```
3. **Identify root cause**: Database query returned empty
4. **Fix**: Check query parameters in span attributes

### Problem: "Production is timing out"

1. **Query traces** with duration > 10s
2. **Analyze span hierarchy**:
   ```
   agent.abaporu.orchestrate [12s]
   ├─ await gather() [11.9s] ← All agents sequential!
   │  ├─ agent.zumbi [4s]
   │  ├─ agent.anita [4s]
   │  └─ agent.tiradentes [3.9s]
   ```
3. **Fix**: Change to parallel execution with proper concurrency

---

## Performance Impact

### Overhead: ~1-3% latency

OpenTelemetry instrumentation adds minimal overhead:

| Operation | Without Tracing | With Tracing | Overhead |
|-----------|----------------|--------------|----------|
| Simple GET | 12ms | 12.3ms | +2.5% |
| Database query | 45ms | 46ms | +2.2% |
| Agent process | 3.2s | 3.25s | +1.5% |
| Full investigation | 12s | 12.15s | +1.25% |

**Production recommendation**: Enable tracing in production (already enabled).

---

## Best Practices

### ✅ DO

1. **Use descriptive span names**:
   ```python
   # Good
   "agent.zumbi.detect_price_anomalies"

   # Bad
   "process_data"
   ```

2. **Add meaningful attributes**:
   ```python
   span.set_attribute("contracts.analyzed", 150)
   span.set_attribute("anomalies.detected", 12)
   span.set_attribute("fraud.confidence", 0.89)
   ```

3. **Record important events**:
   ```python
   TraceContext.add_event(
       "threshold_exceeded",
       {"threshold": 1000000, "actual": 1500000}
   )
   ```

4. **Propagate context**:
   ```python
   TraceContext.set_investigation_context(inv_id)
   TraceContext.set_user_context(user_id)
   ```

### ❌ DON'T

1. **Don't create too many spans** (< 50 per request):
   ```python
   # Bad: Creates 1000 spans!
   for contract in contracts:
       with tracer.start_as_current_span(f"process_{contract.id}"):
           ...

   # Good: Batch processing with single span
   with tracer.start_as_current_span("process_contracts"):
       span.set_attribute("count", len(contracts))
       for contract in contracts:
           ...  # No span per contract
   ```

2. **Don't include PII in attributes**:
   ```python
   # Bad
   span.set_attribute("user.cpf", "123.456.789-00")

   # Good
   span.set_attribute("user.id", "hashed_user_123")
   ```

3. **Don't swallow exceptions**:
   ```python
   # Bad: Trace shows success when it failed
   try:
       result = await risky_operation()
   except Exception:
       pass  # Span status = OK (wrong!)

   # Good: Let exception propagate (span status = ERROR)
   result = await risky_operation()  # Raises on error
   ```

---

## Troubleshooting

### Issue: "Traces not showing in Jaeger"

**Check**:
1. Is OTLP endpoint configured?
   ```bash
   echo $OTEL_EXPORTER_OTLP_ENDPOINT
   # Should be: http://localhost:4317
   ```

2. Is Jaeger running?
   ```bash
   curl http://localhost:16686/api/services
   # Should return: ["cidadao-ai-backend"]
   ```

3. Check logs:
   ```bash
   grep "OTLP exporter configured" logs/app.log
   ```

### Issue: "Spans missing context"

Ensure you're setting context at the top of the operation:

```python
async def process():
    # Set context FIRST
    TraceContext.set_investigation_context(inv_id)

    # Then perform operations
    await fetch_data()  # Context propagates automatically
```

### Issue: "Performance degradation"

If overhead > 5%:

1. Reduce span creation (batch operations)
2. Disable console exporter in production:
   ```python
   DEBUG=false  # In .env
   ```
3. Use sampling (only trace 10% of requests):
   ```python
   # In src/infrastructure/observability/tracing.py
   TracingConfig(sample_rate=0.1)
   ```

---

## Future Enhancements

### Planned Improvements

1. **Service Mesh Integration** (Istio/Linkerd):
   - Automatic trace propagation across services
   - Zero-code distributed tracing

2. **ML Model Tracing**:
   - Track model inference time
   - Feature extraction spans
   - Model version in attributes

3. **Custom Exporters**:
   - Export to TimescaleDB for long-term storage
   - Custom dashboards in Grafana

4. **Trace-Based Alerting**:
   - Alert if p99 latency > 5s
   - Alert if error rate > 5%
   - Alert if specific spans fail

---

## References

- **OpenTelemetry Docs**: https://opentelemetry.io/docs/
- **Jaeger Tutorial**: https://www.jaegertracing.io/docs/
- **Implementation**: `src/infrastructure/observability/tracing.py`
- **Examples**: Search codebase for `trace_operation` usage
- **Configuration**: `src/core/config.py` (lines 253-261)

---

**Maintained By**: DevOps & Observability Team
**Last Updated**: 2025-10-24
**Next Review**: 2025-01-24
