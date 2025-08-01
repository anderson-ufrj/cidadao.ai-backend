---
title: "Endpoints Reference"
sidebar_position: 1
description: "Complete reference for all API endpoints with examples and specifications"
---

# Endpoints Reference

## Overview

The Cidadão.AI API provides **50+ endpoints** organized into functional modules. Each endpoint is documented with request/response schemas, authentication requirements, and practical examples.

## Endpoint Categories

### Core Functionality

| Module | Description | Endpoints |
|--------|-------------|-----------|
| [**Investigations**](./investigations.md) | Anomaly detection in government data | 6 endpoints |
| [**Analysis**](./analysis.md) | Pattern analysis and correlations | 7 endpoints |
| [**Reports**](./reports.md) | Automated report generation | 7 endpoints |
| [**Multi-Agent**](./multi-agent.md) | Agent orchestration system | 4 endpoints |

### Authentication & Security

| Module | Description | Endpoints |
|--------|-------------|-----------|
| [**Authentication**](./authentication.md) | User authentication and JWT | 9 endpoints |
| [**OAuth**](./oauth.md) | Third-party authentication | 9 endpoints |
| [**Audit**](./audit.md) | Security audit logs | 10 endpoints |

### System & Monitoring

| Module | Description | Endpoints |
|--------|-------------|-----------|
| [**Health**](./health.md) | System health monitoring | 4 endpoints |
| [**WebSocket**](./websocket.md) | Real-time communications | 3 endpoints |

## Common Patterns

### Request Format

All endpoints accept JSON payloads with the following structure:

```json
{
  "data": {
    "type": "investigation",
    "attributes": {
      "query": "Suspicious contracts in 2024",
      "filters": {
        "year": 2024,
        "min_value": 1000000
      }
    }
  }
}
```

### Response Format

Successful responses follow JSON:API specification:

```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "type": "investigation",
    "attributes": {
      "status": "completed",
      "anomalies_found": 12
    },
    "relationships": {
      "report": {
        "data": { "type": "report", "id": "123" }
      }
    }
  },
  "meta": {
    "request_id": "req_123",
    "duration_ms": 245
  }
}
```

### Pagination

List endpoints support pagination:

```http
GET /api/v1/investigations?page[number]=2&page[size]=20
```

### Filtering

Complex filtering via query parameters:

```http
GET /api/v1/investigations?filter[status]=completed&filter[anomalies_found][gte]=5
```

### Sorting

Multi-field sorting:

```http
GET /api/v1/investigations?sort=-anomalies_found,created_at
```

### Field Selection

Sparse fieldsets for optimization:

```http
GET /api/v1/investigations?fields[investigation]=id,status,anomalies_found
```

## Authentication Requirements

| Symbol | Requirement | Description |
|--------|-------------|-------------|
| 🔓 | Public | No authentication required |
| 🔐 | Authenticated | Valid JWT token required |
| 👤 | User | Standard user permissions |
| 👨‍💼 | Analyst | Analyst role required |
| 🛡️ | Admin | Administrator role required |

## Rate Limiting

All endpoints are subject to rate limiting:

| Tier | Limit | Window | Burst |
|------|-------|--------|-------|
| Anonymous | 100 | 1 hour | 10 |
| Authenticated | 1,000 | 1 hour | 100 |
| Premium | 10,000 | 1 hour | 1,000 |

## Error Responses

Consistent error format across all endpoints:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Investigation not found",
    "details": {
      "id": "550e8400-e29b-41d4-a716-446655440000"
    },
    "request_id": "req_123",
    "timestamp": "2025-01-30T10:15:30Z"
  }
}
```

## SDK Examples

### Python

```python
from cidadao_ai import Client

client = Client(api_key="your-key")

# Create investigation
investigation = client.investigations.create(
    query="Contratos suspeitos",
    data_source="portal_transparencia"
)

# Check status
status = client.investigations.get_status(investigation.id)
```

### JavaScript/TypeScript

```typescript
import { CidadaoAI } from '@cidadao-ai/sdk';

const client = new CidadaoAI({ apiKey: 'your-key' });

// Create investigation
const investigation = await client.investigations.create({
  query: 'Contratos suspeitos',
  dataSource: 'portal_transparencia'
});

// Stream results
const stream = client.investigations.stream(investigation.id);
stream.on('data', (chunk) => console.log(chunk));
```

## Webhook Integration

Configure webhooks for async events:

```json
{
  "url": "https://your-app.com/webhooks/cidadao-ai",
  "events": [
    "investigation.completed",
    "anomaly.detected",
    "report.generated"
  ],
  "secret": "whsec_..."
}
```

---

Navigate to specific endpoint documentation for detailed specifications and examples.