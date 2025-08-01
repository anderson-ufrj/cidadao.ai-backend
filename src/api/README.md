# 🚀 Cidadão.AI API Layer

## 📋 Overview

The **API Layer** is the primary interface for the Cidadão.AI platform, providing RESTful endpoints for transparency analysis, multi-agent orchestration, and real-time monitoring. Built with **FastAPI** and async/await patterns for high-performance concurrent processing.

## 🏗️ Architecture

```
src/api/
├── app.py              # FastAPI application entry point
├── auth.py             # OAuth2 authentication
├── oauth.py            # OAuth provider integration  
├── websocket.py        # Real-time WebSocket communication
├── middleware/         # Security & logging middleware
│   ├── authentication.py    # JWT authentication middleware
│   ├── logging_middleware.py # Structured request logging
│   ├── rate_limiting.py     # Rate limiting with Redis
│   └── security.py          # Security headers & CORS
└── routes/             # API endpoints organized by domain
    ├── investigations.py    # Anomaly detection endpoints
    ├── analysis.py         # Pattern analysis endpoints  
    ├── reports.py          # Report generation endpoints
    ├── health.py           # Health checks & monitoring
    ├── auth.py             # Authentication endpoints
    ├── oauth.py            # OAuth2 flow endpoints
    ├── audit.py            # Audit logging endpoints
    └── websocket.py        # WebSocket event handlers
```

## 🔌 API Endpoints

### Core Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/` | GET | API information | Public |
| `/docs` | GET | Swagger UI documentation | Public |
| `/health` | GET | Basic health check | Public |
| `/health/detailed` | GET | Comprehensive system status | Public |
| `/health/live` | GET | Kubernetes liveness probe | Public |
| `/health/ready` | GET | Kubernetes readiness probe | Public |

### Authentication

| Endpoint | Method | Description | 
|----------|--------|-------------|
| `/auth/login` | POST | User authentication |
| `/auth/refresh` | POST | Token refresh |
| `/auth/logout` | POST | Session termination |
| `/auth/oauth/google` | GET | Google OAuth2 flow |
| `/auth/oauth/github` | GET | GitHub OAuth2 flow |

### Investigations 🔍

| Endpoint | Method | Description | Agent |
|----------|--------|-------------|-------|
| `/api/v1/investigations/start` | POST | Start anomaly investigation | InvestigatorAgent |
| `/api/v1/investigations/{id}` | GET | Get investigation results | - |
| `/api/v1/investigations/{id}/status` | GET | Check investigation progress | - |
| `/api/v1/investigations/stream` | GET | Stream real-time results | InvestigatorAgent |

**Anomaly Types Supported:**
- `price` - Price anomalies using statistical methods
- `vendor` - Vendor concentration analysis  
- `temporal` - Suspicious timing patterns
- `payment` - Payment irregularities
- `duplicate` - Duplicate contract detection
- `pattern` - Custom pattern matching

### Analysis 📊

| Endpoint | Method | Description | Agent |
|----------|--------|-------------|-------|
| `/api/v1/analysis/trends` | POST | Spending trend analysis | AnalystAgent |
| `/api/v1/analysis/patterns` | POST | Pattern correlation analysis | AnalystAgent |
| `/api/v1/analysis/efficiency` | POST | Efficiency metrics calculation | AnalystAgent |
| `/api/v1/analysis/{id}` | GET | Get analysis results | - |

**Analysis Types:**
- `spending_trends` - Linear regression trend analysis
- `vendor_patterns` - Vendor behavior analysis
- `organizational_behavior` - Cross-org pattern comparison
- `seasonal_analysis` - Seasonal pattern detection
- `efficiency_metrics` - Performance indicators
- `correlation_analysis` - Multi-dimensional correlations

### Reports 📝

| Endpoint | Method | Description | Agent |
|----------|--------|-------------|-------|
| `/api/v1/reports/generate` | POST | Generate investigation report | ReporterAgent |
| `/api/v1/reports/{id}` | GET | Retrieve generated report | - |
| `/api/v1/reports/{id}/download` | GET | Download report (PDF/HTML) | - |

**Report Formats:**
- `json` - Structured data format
- `markdown` - Human-readable markdown
- `html` - Web-formatted report
- `pdf` - Professional PDF document (planned)

### Audit & Security 🛡️

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/audit/events` | GET | Audit event history |
| `/audit/security` | GET | Security event analysis |
| `/audit/compliance` | GET | Compliance status |

## 🔐 Security Features

### Authentication & Authorization
```python
# JWT-based authentication with refresh tokens
Authentication: Bearer <jwt_token>

# API Key authentication for service-to-service
X-API-Key: <api_key>

# OAuth2 providers supported
- Google OAuth2
- GitHub OAuth2
```

### Security Middleware Stack
```python
# Middleware execution order (LIFO)
1. SecurityMiddleware      # Security headers, CORS
2. LoggingMiddleware       # Request/response logging  
3. RateLimitMiddleware     # Rate limiting per IP/user
4. AuthenticationMiddleware # JWT validation
5. TrustedHostMiddleware   # Host validation (production)
```

### Rate Limiting
```python
# Default limits per authenticated user
- 60 requests/minute
- 1000 requests/hour  
- 10000 requests/day

# Configurable per endpoint
investigations: 10/minute  # CPU-intensive operations
analysis: 20/minute       # Medium complexity
reports: 5/minute         # Resource-intensive generation
```

## 📊 Request/Response Models

### Investigation Request
```json
{
  "query": "Analyze contracts from Ministry of Health 2024",
  "data_source": "contracts",
  "filters": {
    "year": "2024",
    "orgao": "20000",
    "valor_min": 100000
  },
  "anomaly_types": ["price", "vendor", "temporal"],
  "include_explanations": true,
  "stream_results": false
}
```

### Investigation Response
```json
{
  "investigation_id": "uuid4-string",
  "status": "completed",
  "query": "Analyze contracts...",
  "data_source": "contracts",
  "started_at": "2025-01-24T10:00:00Z",
  "completed_at": "2025-01-24T10:05:30Z",
  "anomalies_found": 23,
  "total_records_analyzed": 15420,
  "results": [
    {
      "anomaly_id": "uuid4-string",
      "type": "price",
      "severity": "high",
      "confidence": 0.92,
      "description": "Price 340% above expected range",
      "explanation": "Statistical analysis shows...",
      "affected_records": [...],
      "suggested_actions": [...]
    }
  ],
  "summary": "Found 23 anomalies across 15,420 records...",
  "confidence_score": 0.87,
  "processing_time": 330.5
}
```

## 🔄 Async Processing Patterns

### Background Tasks
```python
# Long-running investigations use background tasks
@router.post("/investigations/start")
async def start_investigation(
    request: InvestigationRequest,
    background_tasks: BackgroundTasks
):
    investigation_id = str(uuid4())
    
    # Start investigation in background
    background_tasks.add_task(
        run_investigation,
        investigation_id,
        request
    )
    
    return {"investigation_id": investigation_id, "status": "started"}
```

### Real-time Streaming
```python
# Stream results as they're discovered
@router.get("/investigations/stream")
async def stream_investigation(investigation_id: str):
    async def generate():
        async for result in investigate_with_streaming(investigation_id):
            yield f"data: {json.dumps(result)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")
```

## 🚦 Error Handling

### Custom Exception Hierarchy
```python
CidadaoAIError (base)
├── ValidationError (400)
├── DataNotFoundError (404)  
├── AuthenticationError (401)
├── UnauthorizedError (403)
├── RateLimitError (429)
├── LLMError (503)
├── TransparencyAPIError (502)
└── AgentExecutionError (500)
```

### Error Response Format
```json
{
  "status": "error",
  "status_code": 400,
  "error": {
    "error": "ValidationError",
    "message": "Invalid data source provided",
    "details": {
      "field": "data_source",
      "allowed_values": ["contracts", "expenses", "agreements"]
    }
  },
  "request_id": "uuid4-string",
  "timestamp": "2025-01-24T10:00:00Z"
}
```

## 📈 Monitoring & Observability

### Health Checks
```python
# Basic health check
GET /health
{
  "status": "healthy",
  "timestamp": "2025-01-24T10:00:00Z",
  "version": "1.0.0",
  "uptime": 86400.5,
  "services": {
    "transparency_api": {"status": "healthy", "response_time": 0.145},
    "database": {"status": "healthy", "response_time": 0.003},
    "redis": {"status": "healthy", "response_time": 0.001}
  }
}
```

### Audit Logging
```python
# All API requests are automatically audited
Audit Event Types:
- AUTHENTICATION_SUCCESS/FAILURE
- API_ACCESS
- INVESTIGATION_STARTED/COMPLETED
- REPORT_GENERATED
- SECURITY_VIOLATION
- DATA_ACCESS
```

### Structured Logging
```python
# All logs use structured format
{
  "timestamp": "2025-01-24T10:00:00Z",
  "level": "INFO",
  "logger": "api.routes.investigations",
  "message": "investigation_started",
  "investigation_id": "uuid4-string",
  "user_id": "user123",
  "data_source": "contracts",
  "anomaly_types": ["price", "vendor"],
  "processing_time": 0.045
}
```

## 🧪 Testing Strategy

### Test Categories
```bash
# Unit tests - individual endpoint logic
pytest tests/unit/api/

# Integration tests - full request/response cycles  
pytest tests/integration/api/

# E2E tests - complete workflows
pytest tests/e2e/api/

# Load tests - performance validation
pytest tests/performance/api/
```

### Test Configuration
```python
# Test database isolation
@pytest.fixture
async def test_client():
    # Use TestContainers for real databases
    with TestClient(app) as client:
        yield client

# Authentication test helpers
@pytest.fixture
def authenticated_headers():
    token = create_test_jwt()
    return {"Authorization": f"Bearer {token}"}
```

## 🔧 Configuration

### Environment Variables
```bash
# Server configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cidadao_ai

# Redis  
REDIS_URL=redis://localhost:6379/0

# API Keys
TRANSPARENCY_API_KEY=your_api_key
GROQ_API_KEY=your_groq_key

# Security
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://cidadao.ai"]
```

### Feature Flags
```python
# Progressive feature rollout
ENABLE_FINE_TUNING=false
ENABLE_AUTONOMOUS_CRAWLING=false  
ENABLE_ADVANCED_VISUALIZATIONS=false
ENABLE_ETHICS_GUARD=true
```

## 🚀 Development

### Local Development
```bash
# Install dependencies
pip install -r requirements/base.txt

# Run with hot reload
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Or use Makefile
make dev
```

### Docker Development
```bash
# Build development image
docker build -f Dockerfile.api -t cidadao-api:dev .

# Run with Docker Compose
docker-compose -f docker-compose.dev.yml up api
```

### Code Quality
```bash
# Code formatting
black src/api/
ruff check src/api/

# Type checking
mypy src/api/

# Security scanning  
bandit -r src/api/

# All quality checks
make lint
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `/docs` - Interactive API explorer
- **OpenAPI Schema**: `/openapi.json` - Machine-readable spec

### Authentication for Documentation
```python
# Test authentication in Swagger UI
1. Click "Authorize" button
2. Enter: Bearer <your_jwt_token>
3. Test endpoints with authentication
```

---

## 🤝 Integration Patterns

### Frontend Integration
```typescript
// TypeScript client example
const response = await fetch('/api/v1/investigations/start', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'Analyze suspicious contracts',
    data_source: 'contracts',
    anomaly_types: ['price', 'vendor']
  })
});
```

### Webhook Integration
```python
# Receive investigation results via webhook
@app.post("/webhook/investigation-complete")
async def handle_investigation_complete(payload: dict):
    investigation_id = payload["investigation_id"]
    results = payload["results"]
    # Process results...
```

This API layer provides a robust, secure, and scalable interface for the Cidadão.AI platform, enabling efficient access to transparency analysis capabilities through well-designed RESTful endpoints.