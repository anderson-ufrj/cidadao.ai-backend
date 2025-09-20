# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Author**: Anderson Henrique da Silva  
**Last Updated**: 2025-09-20 07:28:07 -03 (São Paulo, Brazil)

## Project Overview

Cidadão.AI Backend is an **enterprise-grade multi-agent AI system** for Brazilian government transparency analysis. It specializes in detecting anomalies, irregular patterns, and potential fraud in public contracts, expenses, and government data using advanced AI techniques including spectral analysis, machine learning, and explainable AI.

### Key Capabilities
- **Anomaly Detection**: Price anomalies, vendor concentration, temporal patterns using Z-score, Isolation Forest, spectral analysis (FFT)
- **Multi-Agent System**: 17 specialized AI agents with Brazilian cultural identities (8 fully operational, 7 in development)
- **Portal da Transparência Integration**: Real data with API key, demo data without
- **Enterprise Security**: JWT authentication, OAuth2, audit logging, rate limiting, circuit breakers
- **Performance**: Cache hit rate >90%, agent response <2s, API latency P95 <200ms, throughput >10k req/s

### Recent Enhancements (Sprint 2-5)
- **Performance Optimizations**: orjson (3x faster JSON), Brotli compression, advanced caching, connection pooling
- **Scalability**: Agent pooling, parallel processing, batch APIs, GraphQL, WebSocket batching
- **Event Architecture**: CQRS pattern, Redis Streams, async task queues, message prioritization
- **Observability**: OpenTelemetry tracing, Prometheus metrics, structured logging, Grafana dashboards
- **Resilience**: Circuit breakers, bulkheads, health checks, SLA/SLO monitoring, chaos engineering

## Development Commands

### Essential Commands
```bash
# Quick development setup
make dev                 # Complete development setup (alias for install-dev)
make install-dev         # Install all dependencies + pre-commit hooks

# Running the application
python app.py            # Run HuggingFace-optimized version (port 7860)
make run-dev             # Run full FastAPI with hot reload (port 8000)

# Code quality - MUST pass before committing
make format              # Auto-format with black, isort, fix ruff issues
make lint                # Run ruff linter
make type-check          # Run strict mypy type checking
make check               # Run all checks (lint, type-check, test)

# Testing - Target: 80% coverage
make test                # Run all tests
make test-unit           # Run unit tests only
make test-multiagent     # Run multi-agent coordination tests
make test-coverage       # Generate coverage report (htmlcov/index.html)
pytest tests/unit/test_specific.py::TestClass::test_method  # Run single test

# Database operations
make db-upgrade          # Apply migrations
make migrate             # Create new migration (interactive)
make db-reset            # Reset database (confirms before deleting)
make setup-db            # Initialize with seed data

# Monitoring & debugging
make monitoring-up       # Start Prometheus + Grafana stack
make shell               # IPython with app context loaded
make logs                # Tail application logs
```

### Additional Commands
```bash
# Security & CI
make security-check      # Run safety + bandit checks
make ci                  # Complete CI pipeline locally

# Docker operations
make docker-up           # Start all services
make docker-build        # Build images

# ML & Performance
make fine-tune           # ML model fine-tuning
make benchmark           # Run performance tests
```

## Architecture Overview

### Dual Deployment Architecture
- **HuggingFace Spaces** (`app.py`): Simplified, minimal dependencies, port 7860
- **Full Production** (`src/api/app.py`): Complete multi-agent system, port 8000

### Multi-Agent System Design
The system follows a **hierarchical multi-agent architecture** with Brazilian cultural identities:

#### Fully Operational Agents (8/17)
- **Abaporu** (Master): Orchestrates investigations, coordinates agents
- **Zumbi dos Palmares** (Investigator): Anomaly detection with statistical/ML methods
- **Anita Garibaldi** (Analyst): Pattern analysis and correlations
- **Tiradentes** (Reporter): Natural language report generation
- **Nanã** (Memory): Multi-layer memory (episodic, semantic, conversational)
- **Ayrton Senna** (Router): Semantic routing with intent detection
- **Machado de Assis** (Textual): Document analysis with NER
- **Dandara** (Social Justice): Equity analysis

### Core Technical Stack
- **Backend**: Python 3.11+, FastAPI, async/await throughout
- **Database**: PostgreSQL + async SQLAlchemy, Alembic migrations
- **Cache**: Redis cluster (3-node), multi-layer strategy (L1: Memory, L2: Redis, L3: DB)
- **ML/AI**: LangChain, Transformers, scikit-learn, SHAP/LIME for explainability
- **Monitoring**: Prometheus metrics at `/health/metrics`, Grafana dashboards

### Key Technical Patterns

#### Agent Development
```python
# All agents inherit from BaseAgent in src/agents/deodoro.py
class MyAgent(BaseAgent):
    async def execute(self, context: AgentContext) -> AgentResponse:
        # Main agent logic here
        pass

# Inter-agent communication
message = AgentMessage(
    type=MessageType.TASK,
    content="Analyze contract #12345",
    metadata={"priority": "high"}
)
```

#### Configuration Management
```python
# Never hardcode secrets - use settings
from src.core.config import get_settings

settings = get_settings()  # Development
# OR
settings = await Settings.from_vault()  # Production with Vault
```

#### API Endpoints Pattern
- Versioned: `/api/v1/` prefix
- Pydantic models for validation
- Custom exceptions: `CidadaoAIError` hierarchy
- Real-time: SSE streaming at `/api/v1/chat/stream`, WebSocket at `/api/v1/ws/chat/{session_id}`

### Performance & Infrastructure
- **Connection Pool**: 20 base + 30 overflow connections
- **Cache TTL**: Short (5min), Medium (1hr), Long (24hr)
- **Rate Limiting**: Per-user, per-endpoint with Redis backing
- **Circuit Breakers**: Prevent cascade failures
- **Compression**: Gzip (70-90% bandwidth reduction)

## Portal da Transparência Integration

```python
from src.tools.transparency_api import TransparencyAPIClient, TransparencyAPIFilter

# Automatic fallback to demo data if no API key
async with TransparencyAPIClient() as client:
    filters = TransparencyAPIFilter(
        codigo_orgao="26000",  # Health Ministry
        ano=2024,
        valor_inicial=100000
    )
    response = await client.get_contracts(filters)
```

Available endpoints: `/contratos`, `/despesas`, `/servidores`, `/empresas-sancionadas`

## Critical Development Notes

### Testing Requirements
- **Run before commit**: `make test` (target: 80% coverage)
- **Test categories**: Unit (`tests/unit/`), Integration (`tests/integration/`), Multi-agent (`tests/multiagent/`), E2E (`tests/e2e/`)
- **Performance tests**: `pytest tests/performance/ --benchmark-only`
- **Single test**: `pytest tests/unit/test_file.py::TestClass::test_method`

### Code Quality Standards
- **Pre-commit hooks**: Auto-installed with `make install-dev`
- **Black**: 88 character line length
- **Ruff**: Extensive linting rules
- **MyPy**: Strict type checking enabled
- **Always run**: `make check` before pushing

### Security Best Practices
- **Secrets**: Use environment variables or Vault, never commit
- **Validation**: All inputs validated with Pydantic
- **SQL**: SQLAlchemy ORM only, no raw queries
- **Audit**: Comprehensive logging with correlation IDs

### Database Guidelines
- **Migrations**: Always create with `make migrate` before schema changes
- **Async**: Use async SQLAlchemy patterns throughout
- **Testing**: Test migrations locally before pushing

### Monitoring & Observability
- **Metrics exposed**: `/health/metrics` (Prometheus), `/health/metrics/json` (JSON)
- **Custom metrics**:
  - `cidadao_ai_agent_tasks_total`: Agent execution counts
  - `cidadao_ai_investigations_total`: Investigation tracking
  - `cidadao_ai_anomalies_detected_total`: Anomaly detection
  - `cidadao_ai_request_duration_seconds`: Performance histograms
- **Dashboards**: Grafana at localhost:3000 (admin/cidadao123)

## Environment Variables

Essential variables:
```bash
# Core configuration
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cidadao_ai
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=<secret>
SECRET_KEY=<secret>

# External APIs
GROQ_API_KEY=<your-key>  # LLM provider
TRANSPARENCY_API_KEY=<optional>  # Portal da Transparência (demo data if not set)

# ML Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
ANOMALY_DETECTION_THRESHOLD=0.8
VECTOR_STORE_TYPE=faiss  # or chromadb

# Performance tuning
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
REDIS_TTL_SHORT=300  # 5 minutes
REDIS_TTL_MEDIUM=3600  # 1 hour
REDIS_TTL_LONG=86400  # 24 hours
```

## Batch API Usage

The batch API allows processing multiple operations in a single request:

```python
# Example batch request
batch_request = {
    "operations": [
        {
            "operation": "chat",
            "data": {"message": "What is corruption?"},
            "priority": 10
        },
        {
            "operation": "investigate",
            "data": {"query": "contracts above 1M in 2024"},
            "priority": 8
        },
        {
            "operation": "analyze",
            "data": {"type": "trends", "data": {...}},
            "priority": 5
        }
    ],
    "strategy": "best_effort",
    "max_concurrent": 5
}

# POST to /api/v1/batch/process
```

Operations are executed in parallel when possible, significantly reducing total processing time.

## Common Troubleshooting

1. **Import errors**: Run `make install-dev` to ensure all dependencies
2. **Database errors**: Check migrations with `make db-upgrade`
3. **Type errors**: Run `make type-check` to catch issues early
4. **Test failures**: Check for missing environment variables
5. **Cache issues**: Monitor with `/api/v1/chat/cache/stats` endpoint
6. **Agent reflection loops**: Check quality threshold (0.8) and max iterations (3)

## Docker Resource Limits

For production deployments:
- `MEMORY_LIMIT=2048MB`
- `CPU_LIMIT=2.0`
- `MAX_AGENTS=10`
- `MAX_CONCURRENT_INVESTIGATIONS=5`
```

