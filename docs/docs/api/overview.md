---
title: "API Overview"
sidebar_position: 1
description: "Comprehensive technical overview of the Cidadão.AI REST API architecture"
---

# API Overview

## Architecture

The Cidadão.AI API is built on a **microservice-oriented architecture** using FastAPI, designed for high performance, scalability, and real-time data processing. The system implements a **layered architecture pattern** with clear separation of concerns.

### Core Components

```mermaid
graph TB
    Client[Client Applications]
    Gateway[API Gateway]
    Auth[Authentication Service]
    Core[Core API]
    Agents[Multi-Agent System]
    ML[ML Pipeline]
    DB[(PostgreSQL)]
    Cache[(Redis)]
    Vector[(ChromaDB)]
    
    Client --> Gateway
    Gateway --> Auth
    Gateway --> Core
    Core --> Agents
    Core --> ML
    Core --> DB
    Core --> Cache
    Agents --> Vector
    ML --> Vector
```

## Technical Specifications

### Protocol & Standards
- **Protocol**: HTTPS/2 with TLS 1.3
- **API Style**: RESTful with JSON:API compliance
- **Versioning**: URI-based versioning (`/api/v1/`)
- **Authentication**: OAuth 2.0 + JWT (RFC 7519)
- **Documentation**: OpenAPI 3.0 Specification

### Performance Characteristics
- **Response Time**: p95 < 100ms, p99 < 500ms
- **Throughput**: 10,000+ requests/second
- **Concurrency**: Async/await with connection pooling
- **Caching**: Multi-layer (Redis + In-memory)

## API Lifecycle

### Request Flow

```mermaid
sequenceDiagram
    participant Client
    participant Gateway
    participant Auth
    participant API
    participant Agent
    participant DB
    
    Client->>Gateway: HTTP Request
    Gateway->>Auth: Validate Token
    Auth-->>Gateway: Token Valid
    Gateway->>API: Forward Request
    API->>Agent: Process with Agents
    Agent->>DB: Query Data
    DB-->>Agent: Return Results
    Agent-->>API: Processed Data
    API-->>Client: JSON Response
```

### Middleware Stack

1. **CORS Middleware**: Cross-origin resource sharing
2. **Security Middleware**: Headers, XSS protection
3. **Authentication Middleware**: JWT validation
4. **Rate Limiting Middleware**: Token bucket algorithm
5. **Logging Middleware**: Structured JSON logs
6. **Error Handling Middleware**: Consistent error responses

## Data Models

### Core Entities

```python
# Investigation Entity
class Investigation:
    id: UUID
    user_id: UUID
    query: str
    status: InvestigationStatus
    anomalies_found: int
    confidence_score: float
    created_at: datetime
    completed_at: Optional[datetime]
    
# Analysis Entity  
class Analysis:
    id: UUID
    type: AnalysisType
    data_source: DataSource
    results: Dict[str, Any]
    metadata: AnalysisMetadata
    
# Report Entity
class Report:
    id: UUID
    title: str
    content: str
    format: ReportFormat
    investigations: List[UUID]
    generated_at: datetime
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "query",
      "reason": "Query parameter is required"
    },
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-01-30T10:15:30Z"
  }
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid parameters |
| 401 | Unauthorized | Missing/invalid authentication |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |

## Rate Limiting

### Limits by Tier

| Tier | Requests/Hour | Burst | Concurrent |
|------|---------------|-------|------------|
| Anonymous | 100 | 10 | 2 |
| Authenticated | 1,000 | 100 | 10 |
| Premium | 10,000 | 1,000 | 50 |
| Admin | Unlimited | - | - |

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
X-RateLimit-Retry-After: 3600
```

## Security

### Authentication Flow

1. **Initial Authentication**: POST `/api/v1/auth/login`
2. **Token Response**: Access token (15min) + Refresh token (7d)
3. **Request Authentication**: `Authorization: Bearer <access_token>`
4. **Token Refresh**: POST `/api/v1/auth/refresh`

### Security Headers

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'
```

## Pagination

### Request Parameters

```http
GET /api/v1/investigations?page=2&limit=20&sort=-created_at
```

### Response Format

```json
{
  "data": [...],
  "meta": {
    "page": 2,
    "limit": 20,
    "total": 156,
    "pages": 8
  },
  "links": {
    "first": "/api/v1/investigations?page=1&limit=20",
    "prev": "/api/v1/investigations?page=1&limit=20",
    "next": "/api/v1/investigations?page=3&limit=20",
    "last": "/api/v1/investigations?page=8&limit=20"
  }
}
```

## Filtering & Sorting

### Filter Syntax

```http
GET /api/v1/investigations?filter[status]=completed&filter[anomalies_found][gte]=5
```

### Sort Syntax

```http
GET /api/v1/investigations?sort=-anomalies_found,created_at
```

## Webhooks

### Webhook Events

- `investigation.completed`
- `analysis.finished`
- `report.generated`
- `anomaly.detected`

### Webhook Payload

```json
{
  "event": "investigation.completed",
  "data": {
    "investigation_id": "550e8400-e29b-41d4-a716-446655440000",
    "anomalies_found": 12,
    "severity": "high"
  },
  "timestamp": "2025-01-30T10:15:30Z",
  "signature": "sha256=..."
}
```

## API Versioning

### Version Strategy

- **Current Version**: v1
- **Deprecation Notice**: 6 months
- **End of Life**: 12 months
- **Version Header**: `X-API-Version: 1`

### Breaking Changes Policy

1. Announce in release notes
2. Add deprecation warnings
3. Maintain backwards compatibility
4. Provide migration guide

## Performance Optimization

### Caching Strategy

1. **Browser Cache**: Static assets (1 year)
2. **CDN Cache**: API responses (5 minutes)
3. **Redis Cache**: Database queries (1 hour)
4. **Application Cache**: Computed results (15 minutes)

### Query Optimization

- **Field Selection**: `?fields=id,title,status`
- **Eager Loading**: `?include=investigations,analyses`
- **Sparse Fieldsets**: Minimize payload size
- **Compression**: gzip/brotli for responses

## Monitoring & Observability

### Metrics Exposed

- Request rate (req/s)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Active connections
- Cache hit ratio

### Health Endpoints

- `/health` - Basic health check
- `/health/detailed` - Comprehensive status
- `/health/live` - Kubernetes liveness
- `/health/ready` - Kubernetes readiness

## SDK Support

### Official SDKs

- Python: `pip install cidadao-ai-sdk`
- JavaScript/TypeScript: `npm install @cidadao-ai/sdk`
- Go: `go get github.com/cidadao-ai/go-sdk`

### Code Example

```python
from cidadao_ai import Client

client = Client(api_key="your-api-key")

# Start investigation
investigation = client.investigations.create(
    query="Contratos suspeitos em 2024",
    data_source="portal_transparencia",
    filters={"year": 2024, "min_value": 1000000}
)

# Check status
status = client.investigations.get_status(investigation.id)

# Get results
if status.completed:
    results = client.investigations.get_results(investigation.id)
    print(f"Found {results.anomalies_found} anomalies")
```

## Best Practices

### Request Optimization

1. Use field selection to reduce payload
2. Implement client-side caching
3. Batch requests when possible
4. Use webhooks for long operations

### Error Handling

1. Implement exponential backoff
2. Handle rate limits gracefully
3. Log errors with request IDs
4. Validate inputs client-side

### Security

1. Never expose API keys in code
2. Use environment variables
3. Implement request signing
4. Validate SSL certificates

## Migration Guide

### From v0 to v1

1. Update base URL to `/api/v1/`
2. Migrate from API keys to JWT
3. Update error handling for new format
4. Implement pagination for list endpoints

---

Next: [Authentication →](./authentication.md)