# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Author**: Anderson Henrique da Silva  
**Last Updated**: 2025-09-24 14:52:00 -03:00 (São Paulo, Brazil)

## Project Overview

Cidadão.AI Backend is an enterprise-grade multi-agent AI system for Brazilian government transparency analysis. It specializes in detecting anomalies, irregular patterns, and potential fraud in public contracts using advanced ML techniques including spectral analysis (FFT), machine learning models, and explainable AI.

### Key Features
- **Multi-Agent System**: 17 specialized AI agents with Brazilian cultural identities (8 fully operational)
- **Anomaly Detection**: Z-score, Isolation Forest, spectral analysis, and custom ML models
- **Portal da Transparência Integration**: Real data with API key, demo data without
- **Enterprise Features**: JWT auth, OAuth2, rate limiting, circuit breakers, caching
- **Performance**: Cache hit rate >90%, agent response <2s, API P95 <200ms

## Critical Development Commands

### Setup & Installation
```bash
# Install all dependencies including dev tools
make install-dev

# Setup database with migrations (if needed)
make db-upgrade

# Initialize database with seed data
make setup-db
```

### Development Workflow
```bash
# Run FastAPI with hot reload (port 8000)
make run-dev

# Run tests - ALWAYS run before committing
make test              # All tests
make test-unit         # Unit tests only  
make test-agents       # Multi-agent system tests
make test-coverage     # With coverage report

# Code quality - MUST pass before committing
make format            # Format with black and isort
make lint              # Run ruff linter
make type-check        # Run mypy type checking
make check             # Run all checks (lint, type-check, test)

# Quick check before pushing
make ci                # Full CI pipeline locally
```

### Running a Single Test
```bash
# Using pytest directly
python -m pytest tests/unit/agents/test_zumbi.py -v
python -m pytest tests/unit/agents/test_zumbi.py::TestZumbiAgent::test_analyze_contract -v

# With coverage for specific module
python -m pytest tests/unit/agents/test_zumbi.py --cov=src.agents.zumbi --cov-report=term-missing
```

### Other Commands
```bash
# Start monitoring stack
make monitoring-up     # Prometheus + Grafana

# Database operations
make migrate          # Create new migration
make db-reset        # Reset database (careful!)

# Interactive shell with app context
make shell

# Docker services
make docker-up       # Start all services
make docker-down     # Stop services
```

## Architecture Overview

### Multi-Agent System Structure

```
User Request → API → Master Agent (Abaporu)
                           ↓
                   Agent Orchestration
                           ↓
        Investigation (Zumbi) + Analysis (Anita)
                           ↓
                 Report Generation (Tiradentes)
                           ↓
                     User Response
```

### Agent Base Classes
- **BaseAgent**: Abstract base for all agents with retry logic and monitoring
- **ReflectiveAgent**: Adds self-reflection with quality threshold (0.8) and max 3 iterations
- **AgentMessage**: Structured communication between agents
- **AgentContext**: Shared context during investigations

### Key Agent States
- `IDLE`: Waiting for tasks
- `THINKING`: Processing/analyzing  
- `ACTING`: Executing actions
- `WAITING`: Awaiting resources
- `ERROR`: Error state
- `COMPLETED`: Task finished

### Performance Optimizations
- **Agent Pooling**: Pre-initialized instances with lifecycle management
- **Parallel Processing**: Concurrent agent execution with strategies
- **Caching**: Multi-layer (Memory → Redis → Database) with TTLs
- **JSON**: orjson for 3x faster serialization
- **Compression**: Brotli for optimal bandwidth usage

### Key Services
1. **Investigation Service**: Coordinates multi-agent investigations
2. **Chat Service**: Real-time conversation with streaming support
3. **Data Service**: Portal da Transparência integration
4. **Cache Service**: Distributed caching with Redis
5. **LLM Pool**: Connection pooling for AI providers

## Important Development Notes

### Testing Requirements
- Target coverage: 80% (currently ~80%)
- Always run `make test` before committing
- Multi-agent tests are critical: `make test-agents`
- Use markers: `@pytest.mark.unit`, `@pytest.mark.integration`

### Code Quality Standards
- Black line length: 88 characters
- Strict MyPy type checking enabled
- Ruff configured with extensive rules
- Pre-commit hooks installed with `make install-dev`

### Environment Variables
Required for full functionality:
- `DATABASE_URL`: PostgreSQL connection
- `REDIS_URL`: Redis connection
- `JWT_SECRET_KEY`, `SECRET_KEY`: Security keys
- `GROQ_API_KEY`: LLM provider
- `TRANSPARENCY_API_KEY`: Portal da Transparência (optional - uses demo data if missing)

### API Endpoints

Key endpoints:
```bash
# Chat endpoints
POST /api/v1/chat/message          # Send message
POST /api/v1/chat/stream           # Stream response (SSE)
GET  /api/v1/chat/history/{session_id}/paginated

# Investigation endpoints  
POST /api/v1/investigations/analyze
GET  /api/v1/investigations/{id}

# Agent endpoints
POST /api/agents/zumbi             # Anomaly detection
GET  /api/v1/agents/status         # All agents status

# WebSocket
WS   /api/v1/ws/chat/{session_id}
```

### Database Schema
Uses SQLAlchemy with async PostgreSQL. Key models:
- `Investigation`: Main investigation tracking
- `ChatSession`: Chat history and context
- `Agent`: Agent instances and state
- `Cache`: Distributed cache entries

Migrations managed with Alembic: `make migrate` and `make db-upgrade`

### Security Considerations
- JWT tokens with refresh support
- Rate limiting per endpoint/agent
- Circuit breakers for external APIs
- Audit logging for all operations
- Input validation with Pydantic
- CORS properly configured

### Common Issues & Solutions

1. **Import errors**: Run `make install-dev`
2. **Database errors**: Check migrations with `make db-upgrade`  
3. **Type errors**: Run `make type-check` to catch early
4. **Cache issues**: Monitor at `/api/v1/chat/cache/stats`
5. **Agent timeouts**: Check agent pool health
6. **Test failures**: Often missing environment variables

### Monitoring & Observability

```bash
# Start monitoring
make monitoring-up

# Access dashboards
Grafana: http://localhost:3000 (admin/cidadao123)
Prometheus: http://localhost:9090

# Key metrics
- Agent response times
- Cache hit rates  
- API latency (P50, P95, P99)
- Error rates by endpoint
```

### Development Tips

1. **Agent Development**:
   - Extend `BaseAgent` or `ReflectiveAgent`
   - Implement `process()` method
   - Use `AgentMessage` for communication
   - Add tests in `tests/unit/agents/`

2. **API Development**:
   - Routes in `src/api/routes/`
   - Use dependency injection
   - Add OpenAPI documentation
   - Include rate limiting

3. **Performance**:
   - Profile with `make profile`
   - Check cache stats regularly
   - Monitor agent pool usage
   - Use async operations throughout

4. **Debugging**:
   - Use `make shell` for interactive debugging
   - Check logs in structured format
   - Use correlation IDs for tracing
   - Monitor with Grafana dashboards