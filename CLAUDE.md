# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Cidadão.AI Backend** is a production-ready multi-agent AI system for Brazilian government transparency analysis. It uses **16 specialized AI agents** with Brazilian cultural identities to analyze public contracts, detect anomalies, and generate comprehensive reports.

**Production Status**: Live on Railway since 07/10/2025 (99.9% uptime)
**Production URL**: https://cidadao-api-production.up.railway.app/
**Infrastructure**: PostgreSQL + Redis + Celery (24/7 monitoring)
**API Endpoints**: 266+ endpoints across 40 route modules

**⚠️ IMPORTANT - DATA MODE (Updated 2025-10-22)**:
- **Demo Mode**: `is_demo_mode: true` - Backend operates with simulated data
- **Real Data**: Only IBGE API (states/municipalities) works with real data
- **Portal da Transparência**: Not integrated (requires `TRANSPARENCY_API_KEY`)
- **Agents**: Cannot analyze real government contracts (no real data available)

**Agent Status**:
- **10 Tier 1 agents**: Fully operational (Zumbi, Anita, Tiradentes, Machado, Senna, Bonifácio, Maria Quitéria, Oxóssi, Lampião, Oscar Niemeyer)
- **5 Tier 2 agents**: Substantial framework (Abaporu, Nanã, Drummond, Céuci, Obaluaiê)
- **1 Tier 3 agent**: Minimal implementation (Dandara)

**Detailed Analysis**: See `docs/project/COMPREHENSIVE_ANALYSIS_2025_10_20.md` for complete verified metrics
**Real Data Analysis**: See `docs/backend-real-data-analysis.md` for demo mode investigation

---

## 🔍 Quick Facts (Verified 2025-10-20)

| Metric | Value | Notes |
|--------|-------|-------|
| **Total Agents** | 16 agents (26,141 LOC) | Not 17 - verified count |
| **Tier 1 (Operational)** | 10 agents (62.5%) | Zumbi, Anita, Tiradentes, Machado, Senna, Bonifácio, Maria Quitéria, Oxóssi, Lampião, Niemeyer |
| **Tier 2 (Framework)** | 5 agents (31.25%) | Abaporu, Nanã, Drummond, Céuci, Obaluaiê |
| **Tier 3 (Minimal)** | 1 agent (6.25%) | Dandara |
| **Test Files** | 24 files (9,322 LOC) | 75% agents have tests |
| **API Endpoints** | 266+ endpoints | Across 40 route modules |
| **Documentation** | 100% coverage | 21 agent docs + 8 status docs |
| **Production** | Railway (since 07/10/25) | 99.9% uptime, no HuggingFace |
| **Critical Gaps** | Oxóssi, Lampião | Tier 1 agents with ZERO tests |

---

## Critical Development Commands

### Environment Setup
```bash
# Install development dependencies
make install-dev

# Configure environment (REQUIRED before running)
cp .env.example .env
# Edit .env and add at minimum:
# - MARITACA_API_KEY (primary LLM provider)
# - ANTHROPIC_API_KEY (backup LLM provider)
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

# Single test function
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_zumbi.py::TestZumbiAgent::test_detect_anomalies -v

# With coverage report
JWT_SECRET_KEY=test SECRET_KEY=test pytest --cov=src --cov-report=html
# Report: htmlcov/index.html

# Debug specific test with output
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/agents/test_zumbi.py -v -s
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

### Project Management
```bash
# Roadmap and sprint tracking
make roadmap                # Show v1.0 roadmap summary
make roadmap-progress       # Check v1.0 progress with task counts
make sprint-status          # Show current sprint status
make v1-report              # Generate v1.0 progress report

# Celery background tasks (24/7 monitoring)
make celery                 # Start Celery worker
make celery-beat            # Start Celery Beat scheduler
make celery-flower          # Start Flower monitoring UI
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

### Multi-Agent System (16 Agents - 26,141 LOC)

All agents inherit from `ReflectiveAgent` in `src/agents/deodoro.py` (478 lines - base framework).

#### **TIER 1: Fully Operational (10 agents - 90-100% complete)**

**Analysis & Investigation**:
- `zumbi.py` (1,427 lines) ✅ - Anomaly detection with FFT spectral analysis, statistical analysis
- `anita.py` (1,560 lines) ✅ - Statistical pattern analysis, clustering, data profiling
- `oxossi.py` (1,698 lines) ✅ - Fraud detection (7+ patterns: bid rigging, phantom vendors, price fixing)
- `lampiao.py` (1,587 lines) ✅ - Regional/spatial inequality analysis

**Routing & Orchestration**:
- `ayrton_senna.py` (646 lines) ✅ - Intent detection, semantic routing, load balancing

**Communication & Reporting**:
- `tiradentes.py` (1,934 lines) ✅ - Report generation (PDF, HTML, Excel, JSON)
- `oscar_niemeyer.py` (1,228 lines) ✅ - Data visualization (Plotly, NetworkX)
- `machado.py` (678 lines) ✅ - NER, textual analysis, narrative extraction

**Governance & Security**:
- `bonifacio.py` (2,131 lines) ✅ - Legal compliance analysis, policy evaluation
- `maria_quiteria.py` (2,589 lines) ✅ - Security auditing (MITRE ATT&CK, UEBA)

#### **TIER 2: Substantial Framework (5 agents - 10-70% complete)**

- `abaporu.py` (1,089 lines) ⚠️ 70% - Multi-agent orchestration (needs real coordination)
- `nana.py` (963 lines) ⚠️ 65% - Memory system (needs persistence integration)
- `drummond.py` (1,678 lines) ⚠️ 25% - NLG communication (needs LLM integration)
- `ceuci.py` (1,697 lines) ⚠️ 10% - ML/Predictive (no trained models)
- `obaluaie.py` (829 lines) ⚠️ 15% - Corruption detection (Benford's Law partial)

#### **TIER 3: Minimal Implementation (1 agent)**

- `dandara.py` (788 lines) ⚠️ 30% - Social justice metrics (framework only)

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

# LLM Provider Configuration
LLM_PROVIDER=maritaca                    # Current provider in use

# Maritaca AI (Primary - Brazilian Portuguese model)
MARITACA_API_KEY=<maritaca-api-key>      # Required for Sabiá models
MARITACA_MODEL=sabiazinho-3              # Options: sabiazinho-3, sabia-3

# Anthropic Claude (Backup)
ANTHROPIC_API_KEY=<anthropic-key>        # Claude Sonnet 4 as fallback
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

### Optional (Enhanced Features)
```bash
# Database (defaults to in-memory SQLite)
DATABASE_URL=postgresql://user:pass@host:port/db
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<key>

# Cache (defaults to in-memory)
REDIS_URL=redis://localhost:6379/0

# Monitoring
ENABLE_METRICS=true
```

### ⚠️ Real Government Data Integration (Currently NOT Configured)
```bash
# Portal da Transparência API
TRANSPARENCY_API_KEY=<portal-api-key>    # ❌ NOT configured in production
# Get key at: https://api.portaldatransparencia.gov.br/
# Status: Without this key, backend operates in demo mode (is_demo_mode: true)

# Dados.gov.br API
DADOS_GOV_API_KEY=<dados-gov-key>        # ❌ NOT configured in production
# Optional: Additional government data sources

# Impact of missing keys:
# - Chat responses show "is_demo_mode": true
# - /api/v1/transparency/contracts returns CKAN metadata (not real contracts)
# - Agents cannot analyze real government data
# - Anomaly detection works only with simulated data
```

### How to Exit Demo Mode
1. **Get Portal da Transparência API Key**:
   - Visit https://api.portaldatransparencia.gov.br/
   - Register and obtain your API key
   - Free tier: 500 requests/hour

2. **Configure in Railway**:
   ```bash
   railway variables set TRANSPARENCY_API_KEY=your-key-here
   ```

3. **Restart Backend**:
   ```bash
   railway restart
   ```

4. **Verify Real Data**:
   ```bash
   curl https://cidadao-api-production.up.railway.app/api/v1/chat/message \
     -H 'Content-Type: application/json' \
     -d '{"message": "Mostre contratos do Ministério da Saúde"}' \
     | jq '.metadata.is_demo_mode'
   # Should return: false
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

### Test Status (Verified 2025-10-20)
- **24 test files** with **9,322 lines** of test code
- **75% of agents have tests** (12 out of 16 agents)
- **Test coverage**: Target 80%+ overall

### Test Categories
- **Unit**: Individual components (161+ tests)
- **Integration**: Multi-component flows (36+ tests)
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

### Coverage Requirements & Current Status (Measured 2025-10-20)
- **Target**: 80% overall coverage
- **Current**: **44.59%** overall (agents module)
- **Gap**: -35.41 percentage points 🔴

**✅ EXCELLENT COVERAGE (≥80% - 7 agents)**:
- Deodoro (96.45%), Oscar Niemeyer (93.78%), Parallel Processor (90.00%)
- **Oxóssi (83.80%)** - ✅ COMPLETED TODAY (43 tests, 527 statements)
- Simple Agent Pool (83.21%), Lampião (79.10%), Dandara (73.79%)

**🟡 MODERATE COVERAGE (50-79% - 3 agents)**:
- Zumbi (58.90%), Tiradentes (52.99%), Bonifácio (49.13%)

**🔴 CRITICAL GAPS (<30% - 9 agents)**:
- Anita (10.59%), Céuci (10.49%), Nanã (11.76%), Abaporu (13.37%)
- Obaluaiê (13.11%), Maria Quitéria (23.23%), Machado (24.84%)
- Drummond (35.48%), Ayrton Senna (46.59%)

**📊 Detailed Report**: See `docs/project/TEST_COVERAGE_REPORT_2025_10_20.md`

## Transparency APIs Integration

### ⚠️ Current Status: Demo Mode (Updated 2025-10-22)

**CRITICAL**: The backend currently operates in **demo mode** for government transparency data.

#### What Works (Real Data) ✅
- **IBGE API**: States and municipalities (27 states, 5,570 municipalities)
  ```bash
  curl https://cidadao-api-production.up.railway.app/api/v1/federal/ibge/states
  # Returns: Real data from IBGE
  ```

#### What Doesn't Work (Demo Mode) ❌
- **Portal da Transparência**: Contracts, servants, expenses
  ```bash
  curl https://cidadao-api-production.up.railway.app/api/v1/transparency/contracts
  # Returns: CKAN metadata (links to Excel files, not structured data)
  # Metadata shows: "is_demo_mode": true
  ```

- **Government Contracts**: No real-time queries
  ```bash
  curl -X POST https://cidadao-api-production.up.railway.app/api/v1/chat/message \
    -d '{"message": "Contratos do Ministério da Saúde"}'
  # Returns: "Desculpe, estou em manutenção"
  # Metadata shows: "is_demo_mode": true
  ```

#### Why Demo Mode?
1. **Missing API Key**: `TRANSPARENCY_API_KEY` not configured in Railway
2. **API Protection**: Backend returns generic responses instead of errors
3. **No Real Data**: Agents cannot analyze government contracts without API access

#### Impact on Features
| Feature | Status | Reason |
|---------|--------|--------|
| Contract anomaly detection | ❌ | No real contract data |
| Fraud pattern analysis | ❌ | No real contract data |
| Servant salary analysis | ❌ | Portal API not configured |
| Government expense tracking | ❌ | Portal API not configured |
| Real-time investigations | ❌ | No real-time data source |
| Source traceability | ❌ | No contract IDs from Portal |

### Federal APIs (7 APIs)
Located in `src/services/transparency_apis/federal_apis/`:
- `ibge_client.py` - Geography/statistics ✅ **Working with real data**
- `datasus_client.py` - Health data ⚠️ Demo mode
- `inep_client.py` - Education data ⚠️ Demo mode
- `pncp_client.py` - Public contracts ⚠️ Demo mode
- `compras_gov_client.py` - Government purchases ⚠️ Demo mode
- `minha_receita_client.py` - Federal revenue ⚠️ Demo mode
- `bcb_client.py` - Central bank ⚠️ Demo mode

### State APIs (11 sources)
- **TCEs**: 6 state audit courts (SP, RJ, MG, BA, PE, CE) ⚠️ Demo mode
- **CKAN**: 5 state portals (SP, RJ, RS, SC, BA) ⚠️ Returns metadata only
- Located in `src/services/transparency_apis/state_apis/` and `tce_apis/`

### Usage Pattern (IBGE - Working Example)
```python
from src.services.transparency_apis.federal_apis.ibge_client import IBGEClient

client = IBGEClient()
states = await client.get_states()  # ✅ Returns real data
municipalities = await client.get_municipalities(state_code="33")  # Rio de Janeiro
```

### How to Enable Real Data
See **"How to Exit Demo Mode"** section above for step-by-step instructions.

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

### Railway (Production)
- **URL**: https://cidadao-api-production.up.railway.app/
- **Features**: PostgreSQL, Redis, Celery workers (24/7 monitoring)
- **Environment**: Configure variables in Railway dashboard
- **Auto-deploy**: Enabled from GitHub main branch
- **Documentation**: See `docs/deployment/railway/` for detailed guides

```bash
# Deploy to Railway
railway login
railway link
railway up

# Set environment variables
railway variables set LLM_PROVIDER=maritaca
railway variables set MARITACA_API_KEY=xxx
railway variables set MARITACA_MODEL=sabiazinho-3
railway variables set ANTHROPIC_API_KEY=xxx
railway variables set ANTHROPIC_MODEL=claude-sonnet-4-20250514
railway variables set JWT_SECRET_KEY=xxx
railway variables set SECRET_KEY=xxx

# View deployment status
railway status
railway logs
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
- Agent docs: `docs/agents/` (17 agent documentation files)
- Project status: `docs/project/CURRENT_STATUS_2025_10.md` (accurate agent status)
- Planning: `docs/planning/` (sprint plans, roadmaps, v1.0 checklist)
- Project reports: `docs/project/reports/` (progress reports)
- Deployment guides: `docs/deployment/railway/`

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
System is configured to use **Maritaca AI** as primary provider and **Anthropic Claude** as backup.
**Primary**: `MARITACA_API_KEY` + `MARITACA_MODEL=sabiazinho-3` (native Brazilian Portuguese)
**Backup**: `ANTHROPIC_API_KEY` + `ANTHROPIC_MODEL=claude-sonnet-4-20250514`
**Important**: Set `LLM_PROVIDER=maritaca` in `.env`

### 7. Investigation Persistence
Investigations are now fully persisted to database with metadata tracking:
- `total_contracts_analyzed` field tracks complete investigation scope
- Context metadata stored in JSONB column
- All investigation results saved for historical analysis
- Database migrations: `004_investigation_metadata` adds tracking fields
- Debug endpoints available: `/api/v1/debug/investigations` to list all investigations

### 8. Agent Operational Status (Verified 2025-10-20)
**Not all 16 agents are fully operational**. Verified status from comprehensive analysis:
- **Tier 1** (10 agents - 90-100%): Fully functional code (Zumbi, Anita, Tiradentes, Machado, Senna, Bonifácio, Maria Quitéria, Oxóssi, Lampião, Oscar Niemeyer)
- **Tier 2** (5 agents - 10-70%): Framework exists, needs completion (Abaporu, Nanã, Drummond, Céuci, Obaluaiê)
- **Tier 3** (1 agent - 30%): Minimal implementation (Dandara)

**Testing Reality**:
- Only 12/16 agents have test files (75%)
- **Oxóssi and Lampião are Tier 1 but have ZERO tests** (critical gap!)

Always check `docs/project/COMPREHENSIVE_ANALYSIS_2025_10_20.md` for current verified status.

### 9. Demo Mode - Real Data Not Available (2025-10-22)
**CRITICAL**: Backend operates in demo mode for government transparency data.

**Evidence**:
```bash
# All transparency endpoints return demo data
curl -X POST https://cidadao-api-production.up.railway.app/api/v1/chat/message \
  -d '{"message": "Contratos do Ministério da Saúde"}'
# Response metadata: "is_demo_mode": true
```

**Root Cause**: `TRANSPARENCY_API_KEY` environment variable not configured in Railway.

**Impact**:
- ❌ No real government contracts
- ❌ No fraud detection on real data
- ❌ No anomaly analysis on real data
- ❌ No source traceability to Portal da Transparência
- ✅ Only IBGE API works with real data (states/municipalities)

**Solution**: Configure `TRANSPARENCY_API_KEY` in Railway (see "How to Exit Demo Mode" section)

**Detailed Investigation**: See `docs/backend-real-data-analysis.md` for complete analysis

### 10. Frontend Integration Considerations (2025-10-22)
**For Frontend Developers**:

1. **Always Check `is_demo_mode` Flag**:
   ```typescript
   if (response.metadata.is_demo_mode) {
     // Show warning: "Dados simulados - Configure API key para dados reais"
   }
   ```

2. **Health Endpoint Trailing Slash**:
   - Use `/health/` (with slash) or follow 307 redirects
   - `/health` → 307 redirect → `/health/`

3. **Chat Agents vs All Agents**:
   - Use `/api/v1/chat/agents` for chat (6 active agents)
   - Not `/api/v1/agents/` (returns all 16 agents, not all chat-enabled)

4. **Empty Investigations List**:
   - `/api/v1/investigations` returns `[]` (expected on fresh deployment)
   - Not a bug, just no historical data yet

**Full Frontend Integration Guide**: See `docs/FRONTEND-BACKEND-INTEGRATION-STATUS.md`

## Performance Benchmarks

| Component | Target | Current |
|-----------|--------|---------|
| API Response (p95) | <200ms | 145ms ✅ |
| Agent Processing | <5s | 3.2s ✅ |
| Chat First Token | <500ms | 380ms ✅ |
| Investigation (6 agents) | <15s | 12.5s ✅ |
| Test Coverage (Agents) | >80% | **44.59%** 🔴 |
| Tests Passing | >250 | 251 ✅ |

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

## Quick Reference: Common Tasks

### Debugging Investigation Issues
```bash
# Check investigation persistence
JWT_SECRET_KEY=test SECRET_KEY=test python -c "
from src.infrastructure.database import SessionLocal
from src.models.investigation import Investigation
with SessionLocal() as db:
    invs = db.query(Investigation).all()
    print(f'Total investigations: {len(invs)}')
    for inv in invs[-5:]:
        print(f'{inv.id}: {inv.status} - {inv.total_contracts_analyzed} contracts')
"

# Test single investigation
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/python test_single_investigation.py

# Check database migrations status
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/alembic current
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/alembic history
```

### Working with LLM Providers
```bash
# Test Maritaca integration (current primary provider)
LLM_PROVIDER=maritaca venv/bin/python test_maritaca_integration.py

# Test Claude integration (backup provider)
# Configure via ANTHROPIC_API_KEY in .env

# Check current provider configuration
grep LLM_PROVIDER .env
# Should show: LLM_PROVIDER=maritaca

# Verify API keys are set
grep MARITACA_API_KEY .env
grep ANTHROPIC_API_KEY .env
```

### Database Operations
```bash
# Check current migration head
make db-upgrade  # or: venv/bin/alembic upgrade head

# Create new migration
make migrate  # or: venv/bin/alembic revision --autogenerate -m "description"

# Merge migration heads (if multiple heads exist)
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/alembic merge -m "merge heads" <head1> <head2>

# Reset database (development only)
make db-reset
```

### Monitoring & Performance
```bash
# Start monitoring stack
make monitoring-up

# View metrics
curl http://localhost:8000/health/metrics

# Run warmup job for federal APIs
venv/bin/python scripts/monitoring/warmup_federal_apis.py --daemon

# Check API endpoint status
curl http://localhost:8000/health
```

## Next Steps for Contributors

1. **Read**: `docs/project/CURRENT_STATUS_2025_10.md` for accurate project state and agent status
2. **Understand**: `docs/architecture/multi-agent-architecture.md` for system architecture
3. **Review**: Individual agent docs in `docs/agents/`
4. **Setup**: Run `make install-dev` and configure `.env`
5. **Test**: Run `JWT_SECRET_KEY=test SECRET_KEY=test make test` to verify setup
6. **Check Progress**: Run `make roadmap-progress` to see current v1.0 status
7. **Code**: Follow patterns in existing agents/services
8. **Quality**: Run `make check` before committing

## Getting Help

- **Agent Examples**: Review `src/agents/zumbi.py` (best-documented, fully operational)
- **Base Classes**: Check `src/agents/deodoro.py` for ReflectiveAgent framework
- **Testing Examples**: See `tests/unit/agents/test_zumbi.py`
- **Current Status**: Always check `docs/project/CURRENT_STATUS_2025_10.md` for real agent metrics
- **Roadmap**: Run `make roadmap` to see v1.0 plan
- **Issues**: GitHub Issues for bugs/questions
