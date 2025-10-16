# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Cidadão.AI Backend** is a production-ready multi-agent AI system for Brazilian government transparency analysis. It uses 17 specialized AI agents with Brazilian cultural identities to analyze public contracts, detect anomalies, and generate comprehensive reports.

**Current Status**: Deployed on HuggingFace Spaces, 80%+ test coverage, 17/17 agents operational

## Critical Development Commands

### Environment Setup
```bash
# Install development dependencies
make install-dev

# Configure environment (REQUIRED before running)
cp .env.example .env
# Edit .env and add at minimum:
# - GROQ_API_KEY (or another LLM provider key)
# - JWT_SECRET_KEY
# - SECRET_KEY
```

### Development Server
```bash
# Run with hot reload
make run-dev
# → http://localhost:8000
# → Docs: http://localhost:8000/docs

# Run full stack (PostgreSQL + Redis)
docker-compose up

# Run monitoring stack (Prometheus + Grafana)
make monitoring-up
# → Grafana: http://localhost:3000 (admin/cidadao123)
# → Prometheus: http://localhost:9090
```

### Testing
```bash
# All tests (IMPORTANT: Set test env vars)
JWT_SECRET_KEY=test SECRET_KEY=test make test

# Specific test categories
make test-unit              # Unit tests (161 tests)
make test-integration       # Integration tests (36 tests)
make test-agents            # Multi-agent tests

# Specific agent
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_zumbi.py -v

# With coverage report
JWT_SECRET_KEY=test SECRET_KEY=test pytest --cov=src --cov-report=html
# Report: htmlcov/index.html
```

### Code Quality
```bash
# Run all checks before committing (REQUIRED)
make check          # lint + type-check + test

# Individual checks
make format         # Black + isort + ruff --fix
make lint           # Ruff linter
make type-check     # MyPy static typing

# Full CI pipeline locally
make ci             # format + lint + type-check + security + coverage
```

### Database Migrations
```bash
# Create migration
make migrate        # Follow prompts for message

# Apply migrations
make db-upgrade

# Rollback
make db-downgrade
```

## High-Level Architecture

### Multi-Agent System (17 Agents)

All agents inherit from `ReflectiveAgent` in `src/agents/deodoro.py`:

**Orchestration Layer**:
- `abaporu.py` (1,089 lines) - Master orchestrator using ReAct pattern
- `ayrton_senna.py` (963 lines) - Semantic routing and intent detection

**Analysis Layer**:
- `zumbi.py` (1,374 lines) - Anomaly detection with FFT spectral analysis
- `anita.py` (1,560 lines) - Statistical data analysis
- `oxossi.py` (1,698 lines) - Fraud detection (7+ fraud patterns)
- `obaluaie.py` (550 lines) - Corruption detection (Benford's Law)
- `ceuci.py` (1,494 lines) - Predictive AI with ML/Time series
- `lampiao.py` (1,587 lines) - Regional/spatial analysis

**Communication Layer**:
- `drummond.py` (1,678 lines) - NLG + Portuguese poetry style
- `tiradentes.py` (1,938 lines) - Report generation (PDF, HTML, JSON)
- `oscar_niemeyer.py` (1,228 lines) - Data visualization (Plotly, NetworkX)

**Governance Layer**:
- `maria_quiteria.py` (2,449 lines) - Security (MITRE ATT&CK, UEBA)
- `bonifacio.py` (1,924 lines) - Legal/policy analysis
- `dandara.py` (788 lines) - Social justice metrics (IBGE/DataSUS/INEP)

**Support Layer**:
- `nana.py` (963 lines) - Memory and context management
- `machado.py` (678 lines) - Narrative analysis

**Base Architecture**:
- `deodoro.py` (478 lines) - BaseAgent and ReflectiveAgent framework

### Orchestration System

Located in `src/services/orchestration/`:

```
User Query → IntentClassifier → EntityExtractor → ExecutionPlanner
                                                          ↓
                                                  DataFederationExecutor
                                                          ↓
                                                    EntityGraph
                                                          ↓
                                              InvestigationAgent (Zumbi)
                                                          ↓
                                                   Investigation Result
```

**Key Components**:
- `orchestrator.py` - Main coordinator (255 lines)
- `query_planner/` - Intent classification, entity extraction, execution planning
- `data_federation/` - Parallel API execution with circuit breakers
- `entity_graph/` - NetworkX-based relationship graph
- `api_registry/` - Registry of 30+ transparency APIs

### API Structure

**Main Routes** (76+ endpoints):
- `/api/v1/chat/` - Chat with agents (SSE streaming support)
- `/api/v1/agents/` - Direct agent invocation
- `/api/v1/investigations/` - Investigation management
- `/api/v1/federal/` - Federal APIs (IBGE, DataSUS, INEP, PNCP, etc.)
- `/api/v1/orchestration/` - Orchestration endpoints
- `/api/v1/transparency/` - Portal da Transparência
- `/api/v1/admin/` - Admin operations
- `/health/metrics` - Prometheus metrics

**Entry Point**: `src/api/app.py` (NOT `app.py` in root - that file doesn't exist)

### Data Flow Pattern

```
FastAPI Request → Middleware Stack → Route Handler → Service Layer → Agent/API
                                                                         ↓
                                                              PostgreSQL/Redis Cache
```

**Middleware Order** (IMPORTANT):
1. SecurityMiddleware
2. LoggingMiddleware
3. RateLimitMiddleware
4. CompressionMiddleware
5. CORS
6. MetricsMiddleware
7. IPWhitelistMiddleware (production only)

## Environment Variables

### Required (Development)
```bash
# Core
SECRET_KEY=<generate-with-scripts/generate_secrets.py>
JWT_SECRET_KEY=<generate-with-scripts/generate_secrets.py>

# LLM Provider (at least one)
GROQ_API_KEY=<groq-api-key>              # Recommended (fast, 14K tokens/min)
# OR
MARITACA_API_KEY=<maritaca-key>          # Best for Portuguese
# OR
TOGETHER_API_KEY=<together-key>
# OR
HUGGINGFACE_API_KEY=<hf-key>
```

### Optional (Enhanced Features)
```bash
# Database (defaults to in-memory SQLite)
DATABASE_URL=postgresql://user:pass@host:port/db
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<key>

# Cache (defaults to in-memory)
REDIS_URL=redis://localhost:6379/0

# Real data access
TRANSPARENCY_API_KEY=<portal-api-key>    # Portal da Transparência
DADOS_GOV_API_KEY=<dados-gov-key>        # Dados.gov.br

# Monitoring
ENABLE_METRICS=true
```

## Agent Development Pattern

### Creating/Modifying Agents

All agents **MUST** follow this pattern:

```python
from src.agents.deodoro import ReflectiveAgent, AgentMessage, AgentResponse, AgentContext

class YourAgent(ReflectiveAgent):
    """Brief description of agent's purpose."""

    def __init__(self):
        super().__init__(
            agent_id="unique_agent_id",
            name="Full Agent Name",
            description="Detailed capabilities",
            capabilities=["capability1", "capability2"]
        )

    async def process(
        self,
        message: AgentMessage,
        context: AgentContext
    ) -> AgentResponse:
        """
        Main processing logic.

        IMPORTANT: Use reflection if quality < 0.8
        """
        # Your implementation
        results = await self._analyze(message.content)

        # Reflection pattern (critical for quality)
        if results.get("confidence", 0) < 0.8:
            return await self.reflect_and_retry(message, results)

        return AgentResponse(
            agent_id=self.agent_id,
            message_id=message.message_id,
            content=results,
            metadata={"confidence": results.get("confidence")}
        )
```

### Agent Testing Requirements

- **Minimum 80% coverage** for all new agents
- Test file: `tests/unit/agents/test_<agent_name>.py`
- Must test: process(), error handling, reflection logic
- Use fixtures for sample data

Example:
```python
@pytest.mark.asyncio
async def test_agent_process_valid_data(agent, sample_message):
    response = await agent.process(sample_message)
    assert response.status == "success"
    assert response.content["confidence"] >= 0.8
```

## Key Implementation Patterns

### 1. Async Everything
All I/O operations use `async/await`:
```python
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
```

### 2. Agent Pool (Lazy Loading)
Agents are loaded on first use via singleton pattern:
```python
from src.services.agent_pool import AgentPool

pool = AgentPool()
zumbi = await pool.get_agent("zumbi")
```

### 3. Circuit Breaker for External APIs
```python
from src.services.orchestration.resilience.circuit_breaker import CircuitBreaker

circuit = CircuitBreaker(failure_threshold=3, timeout=60.0)
result = await circuit.call(api_function)
```

### 4. Caching Strategy
Multi-layer: Memory → Redis → Database
```python
from src.services.cache_service import CacheService

cache = CacheService()
result = await cache.get_or_fetch(key, fetch_function, ttl=300)
```

### 5. Reflection Pattern (Quality Control)
Critical for agent quality:
```python
async def reflect_and_retry(self, message, initial_result):
    """Improves result quality through self-reflection."""
    for iteration in range(self.max_iterations):
        reflection = await self._reflect_on_result(initial_result)
        if reflection["quality"] >= self.quality_threshold:
            return reflection["improved_result"]
```

## Testing Strategy

### Test Categories
- **Unit**: Individual components (161 tests)
- **Integration**: Multi-component flows (36 tests)
- **E2E**: Complete user workflows
- **Multiagent**: Agent collaboration

### Running Specific Tests
```bash
# Agent tests
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/ -v

# Service tests
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/services/ -v

# Orchestration tests
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/services/test_orchestration.py -v

# Single test
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_zumbi.py::TestZumbiAgent::test_detect_anomalies -v
```

### Coverage Requirements
- **Agents**: Minimum 80% per agent
- **Services**: Minimum 75%
- **Overall**: Maintain 80%+

## Transparency APIs Integration

### Federal APIs (7 APIs)
Located in `src/services/transparency_apis/federal_apis/`:
- `ibge_client.py` - Geography/statistics
- `datasus_client.py` - Health data
- `inep_client.py` - Education data
- `pncp_client.py` - Public contracts
- `compras_gov_client.py` - Government purchases
- `minha_receita_client.py` - Federal revenue
- `bcb_client.py` - Central bank

### State APIs (11 sources)
- **TCEs**: 6 state audit courts (SP, RJ, MG, BA, PE, CE)
- **CKAN**: 5 state portals (SP, RJ, RS, SC, BA)
- Located in `src/services/transparency_apis/state_apis/` and `tce_apis/`

### Usage Pattern
```python
from src.services.transparency_apis.federal_apis.ibge_client import IBGEClient

client = IBGEClient()
states = await client.get_states()
municipalities = await client.get_municipalities(state_code="33")  # Rio de Janeiro
```

## Common Workflows

### Add New Route
1. Create route in `src/api/routes/<domain>.py`
2. Register in `src/api/app.py`: `app.include_router(router, prefix="/api/v1")`
3. Add tests in `tests/unit/api/routes/test_<domain>.py`
4. Update OpenAPI docs (automatic via FastAPI)

### Add New Service
1. Create in `src/services/<service_name>.py`
2. Add dependency injection if needed
3. Add tests in `tests/unit/services/test_<service_name>.py`
4. Update relevant route handlers

### Add New Agent
1. Create `src/agents/<agent_name>.py` inheriting from `ReflectiveAgent`
2. Implement `process()` method with reflection
3. Add to `src/agents/__init__.py`
4. Create tests in `tests/unit/agents/test_<agent_name>.py`
5. Document in `docs/agents/<agent_name>.md`
6. Register in agent pool

### Modify Orchestration
1. Core logic in `src/services/orchestration/orchestrator.py`
2. Add/modify planners in `query_planner/`
3. Update entity graph in `entity_graph/graph.py`
4. Test with `tests/unit/services/test_orchestration.py`

## Deployment

### HuggingFace Spaces (Current Production)
- **Entry point**: Uses `src/api/app.py` directly (NO `app.py` in root)
- **Branch**: Deploy from `main` branch
- **Resources**: 2 vCPU, 16GB RAM
- **Environment**: Set variables in HF Spaces settings
- **Auto-deploy**: Enabled on push

### Railway (Alternative)
Full features with Celery, PostgreSQL, Redis:
```bash
railway login
railway link
railway up
```

### Local Docker
```bash
# Full stack
docker-compose up

# Monitoring only
docker-compose -f config/docker/docker-compose.monitoring-minimal.yml up
```

## Important File Locations

### Core Application
- Main app: `src/api/app.py` (**NOT** `app.py` in root)
- Agent base: `src/agents/deodoro.py`
- Orchestrator: `src/services/orchestration/orchestrator.py`
- Config: `src/core/config.py`

### Tests
- Unit: `tests/unit/`
- Integration: `tests/integration/`
- Test config: `pytest.ini` and `pyproject.toml`

### Documentation
- Architecture: `docs/architecture/`
- Agent docs: `docs/agents/`
- Current state: `docs/CURRENT_STATE_2025-10-16.md` (comprehensive audit)
- Orchestration: `docs/architecture/ORCHESTRATION_SYSTEM.md`

### Configuration
- Environment: `.env` (copy from `.env.example`)
- Makefile: `Makefile` (all development commands)
- Dependencies: `pyproject.toml`
- Type hints: Configured in `pyproject.toml` for mypy

## Known Issues & Gotchas

### 1. Test Environment Variables
**CRITICAL**: Always set test env vars when running pytest:
```bash
JWT_SECRET_KEY=test SECRET_KEY=test pytest
```
Without these, auth-related tests will fail.

### 2. No `app.py` in Root
Documentation may reference `app.py` but it doesn't exist in root.
**Correct entry point**: `src/api/app.py`

### 3. Agent Pool Duplicate
`agent_pool.py` exists in both:
- `src/agents/agent_pool.py` (legacy)
- `src/infrastructure/agent_pool.py` (current)

Use the one in `src/infrastructure/`.

### 4. Portal da Transparência API
78% of endpoints return 403 Forbidden. This is expected.
System uses 30+ alternative APIs as fallback.

### 5. Database Configuration
System works without PostgreSQL (uses in-memory SQLite).
For production with persistence, configure `DATABASE_URL` in `.env`.

### 6. LLM Provider
At least one LLM provider API key is required.
**Recommended**: `GROQ_API_KEY` (fast, good rate limits)
**For Portuguese**: `MARITACA_API_KEY` (native Portuguese model)

## Performance Benchmarks

| Component | Target | Current |
|-----------|--------|---------|
| API Response (p95) | <200ms | 145ms ✅ |
| Agent Processing | <5s | 3.2s ✅ |
| Chat First Token | <500ms | 380ms ✅ |
| Investigation (6 agents) | <15s | 12.5s ✅ |
| Test Coverage | >80% | 80.5% ✅ |

## Code Style

### Python Style
- **Formatter**: Black (88 char line)
- **Linter**: Ruff
- **Type Checker**: MyPy (strict mode)
- **Import Sort**: isort

### Commit Messages
Follow conventional commits (enforced by pre-commit):
```
feat(agents): add new fraud detection algorithm
fix(api): resolve SSE streaming timeout issue
docs(agents): update Zumbi documentation
test(orchestration): add integration tests
refactor(services): consolidate cache implementations
```

### Pre-commit Hooks
Installed via `make install-dev`:
- Black formatting
- Ruff linting
- Type checking
- Test execution

## Project Statistics

- **Total Lines**: ~66,000
- **Agents**: 17 (23,369 lines)
- **Services**: 60+ modules
- **API Routes**: 76+ endpoints
- **Test Files**: 128 files
- **Test Coverage**: 80.5%

## Next Steps for Contributors

1. **Read**: `docs/CURRENT_STATE_2025-10-16.md` for comprehensive system overview
2. **Understand**: `docs/architecture/ORCHESTRATION_SYSTEM.md` for orchestration details
3. **Review**: Individual agent docs in `docs/agents/`
4. **Setup**: Run `make install-dev` and configure `.env`
5. **Test**: Run `JWT_SECRET_KEY=test SECRET_KEY=test make test` to verify setup
6. **Code**: Follow patterns in existing agents/services
7. **Quality**: Run `make check` before committing

## Getting Help

- **Agent Examples**: Review `src/agents/zumbi.py` (well-documented)
- **Base Classes**: Check `src/agents/deodoro.py` for framework
- **Testing Examples**: See `tests/unit/agents/test_zumbi.py`
- **Current Status**: Always check `docs/CURRENT_STATE_2025-10-16.md`
- **Issues**: GitHub Issues for bugs/questions
