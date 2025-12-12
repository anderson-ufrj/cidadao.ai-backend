# 🏗️ Architecture Overview

**Cidadão.AI Backend** - Multi-Agent AI System for Brazilian Government Transparency

---

## 🎯 Quick Summary

Production-ready FastAPI application with **16 specialized AI agents** analyzing Brazilian government contracts using **30+ transparency APIs**. Built with async/await patterns, multi-layer caching, and comprehensive observability.

**Live Production**: https://cidadao-api-production.up.railway.app/

---

## 📊 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER LAYER                           │
│  (Portuguese/English Natural Language Queries)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     API GATEWAY (FastAPI)                   │
│  • 323 REST endpoints across 36 routers                     │
│  • SSE/WebSocket streaming                                  │
│  • JWT authentication + rate limiting                       │
│  • CORS, compression, security middleware                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATION LAYER (Multi-Agent)              │
│                                                             │
│  Intent Detection → Entity Extraction → Execution Planning  │
│         ↓                   ↓                    ↓          │
│  Data Federation ← Entity Graph (NetworkX) ← Agent Router   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   16 AI AGENTS (Specialized)                │
│                                                             │
│  Tier 1 (Excellent):                                        │
│  • Zumbi - Anomaly Detection (96.32%)                       │
│  • Anita - Pattern Analysis (94.87%)                        │
│  • Oxóssi - Data Hunting (94.44%)                           │
│  • Lampião - Regional Analysis (93.75%)                     │
│  • Senna - Semantic Routing (92.31%)                        │
│  • Tiradentes - Reporting (91.67%)                          │
│  • Niemeyer - Aggregation (89.47%)                          │
│  • Machado - Textual Analysis (88.24%)                      │
│  • Bonifácio - Legal Analysis (87.50%)                      │
│  • Maria Quitéria - Security (86.96%)                       │
│                                                             │
│  Tier 2 (Near-Complete):                                    │
│  • Abaporu - Master Orchestrator (85.71%)                   │
│  • Nanã - Memory Management (84.62%)                        │
│  • Drummond - Communication (83.33%)                        │
│  • Céuci - ETL & Predictive (82.76%)                        │
│  • Obaluaiê - Corruption Detection (81.25%)                 │
│                                                             │
│  Tier 3 (Framework Ready):                                  │
│  • Dandara - Social Equity (86.32%)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES (30+ APIs)                  │
│                                                             │
│  Federal (8):                                               │
│  • IBGE, DataSUS, INEP, PNCP, Compras.gov                  │
│  • Portal da Transparência, Banco Central, CNPJ            │
│                                                             │
│  State (5):                                                 │
│  • TCE-CE, TCE-PE, TCE-MG, SICONFI, CKAN                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧩 Core Components

### 1. **Agent Framework** (`src/agents/`)
- **Base**: `deodoro.py` - `ReflectiveAgent` with quality threshold (0.8)
- **Pool**: `simple_agent_pool.py` - Singleton lifecycle manager
- **Lazy Loading**: 367x faster imports (3.81ms vs 1460ms)
- **Files**: 24 agent files (16 operational + utilities)

### 2. **Orchestration** (`src/services/orchestration/`)
- **Planner**: Intent classification, entity extraction
- **Federation**: Parallel API calls with circuit breakers
- **Graph**: NetworkX-based entity relationships
- **Registry**: Centralized API catalog (30+ sources)

### 3. **API Layer** (`src/api/`)
- **Routes**: 36 router files, 323 total endpoints
- **Middleware** (LIFO execution):
  1. IPWhitelist → CORS → Logging → Security
  2. RateLimit → Compression → Correlation → Metrics
- **Streaming**: SSE (Server-Sent Events) + WebSocket support

### 4. **Data Layer** (`src/infrastructure/`)
- **Database**: PostgreSQL with async SQLAlchemy
- **Cache**: Redis (multi-layer: memory → Redis → DB)
- **Queue**: Celery for async task processing
- **Monitoring**: Prometheus metrics, Grafana dashboards

---

## 🔄 Request Flow

### Example: Contract Anomaly Investigation

```
1. User Query (Portuguese)
   "Analise contratos de 2024 em Minas Gerais"

2. API Gateway
   POST /api/v1/chat/stream
   → Authentication (JWT)
   → Rate limiting (per-user)
   → SSE connection established

3. Intent Classification
   Intent: "contract_analysis"
   Entities: {year: 2024, state: "MG"}
   Action: "detect_anomalies"

4. Execution Planning
   Agents: [Zumbi, Anita, Lampião]
   APIs: [Portal Transparência, TCE-MG]
   Parallel: True

5. Data Federation
   → TCE-MG API (contracts 2024)
   → Portal Transparência (federal data)
   → Circuit breaker: 3 failures = open
   → Timeout: 30s per API

6. Agent Processing
   Zumbi → Statistical analysis (FFT, Z-score)
   Anita → Pattern detection (ML models)
   Lampião → Regional context (MG specifics)

7. Result Consolidation
   Quality check: confidence >= 0.8
   Entity graph: relationships mapped
   Cache: TTL 1h (investigation results)

8. SSE Streaming
   event: thinking → chunk → chunk → complete
   → Real-time updates to frontend
   → Total time: ~3.2s
```

---

## 🛠️ Technology Stack

### Core
- **Python 3.11+** - Async/await, type hints
- **FastAPI 0.109+** - High-performance async framework
- **Pydantic V2** - Data validation, settings management
- **SQLAlchemy 2.0** - Async ORM
- **Alembic** - Database migrations

### AI & ML
- **Maritaca AI** - Primary LLM (Brazilian Portuguese optimized)
- **Anthropic Claude** - Backup LLM with auto-failover
- **NetworkX** - Graph analysis
- **NumPy/SciPy** - Statistical algorithms

### Infrastructure
- **PostgreSQL 14+** - Primary database (Railway managed)
- **Redis 7+** - Multi-layer caching (Railway managed)
- **Prometheus** - Metrics collection
- **Grafana** - Observability dashboards

### Quality
- **Pytest** - 1,514 tests, 76.29% coverage
- **Ruff** - Fast linting
- **Black** - Code formatting
- **MyPy** - Static type checking

---

## 📈 Performance Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| API Response (p95) | <2000ms | ~600ms | ✅ 70% better |
| Agent Processing | <5000ms | ~3200ms | ✅ 36% better |
| Chat First Token | <500ms | ~380ms | ✅ 24% better |
| Investigation (6 agents) | <15000ms | ~12500ms | ✅ 17% better |
| Agent Import Time | <100ms | 3.81ms | ✅ 96% better |
| Uptime | 99%+ | 99.9% | ✅ Excellent |
| Cache Hit Rate | 90%+ | ~95% | ✅ Optimal |

---

## 🔐 Security

### Authentication & Authorization
- JWT tokens with RS256 signing
- Refresh token rotation
- Role-based access control (RBAC)
- OAuth2 social login (planned)

### API Protection
- Rate limiting: 100 req/min (user), 1000/min (IP)
- CORS whitelist for production domains
- IP whitelisting (production only)
- CSRF protection on state-changing operations

### Data Security
- Secrets in Railway/environment variables
- Database encryption at rest (Railway managed)
- API keys rotated regularly
- Audit logs for all sensitive operations

---

## 📊 Observability

### Metrics (Prometheus)
- Request latency (p50, p95, p99)
- Agent processing times
- Cache hit/miss rates
- API error rates
- Database connection pool

### Logs (Structlog)
- JSON structured logging
- Correlation IDs for request tracing
- Log levels: DEBUG, INFO, WARNING, ERROR
- Sensitive data redaction

### Monitoring (Grafana)
- Overview dashboard (system health)
- Agent performance dashboard
- API metrics dashboard
- Custom alerts (planned)

---

## 🚀 Deployment

### Production (Railway)
- Platform: Railway.app
- Region: US East
- Database: PostgreSQL 14 (managed)
- Cache: Redis 7 (managed)
- SSL: Automatic Let's Encrypt
- Scaling: Horizontal (planned)

### CI/CD
- GitHub Actions (planned)
- Pre-commit hooks (Ruff, Black, MyPy)
- Automated testing on PR
- Deployment on merge to main

---

## 📚 Documentation Structure

```
docs/
├── agents/           # Individual agent documentation (21 files)
├── api/             # API reference and guides (30+ files)
├── architecture/    # System design and patterns (5 files)
├── deployment/      # Railway, Docker, monitoring
├── project/         # Status, roadmaps, planning
├── reports/         # Technical reports (Nov 2025)
├── testing/         # E2E, integration test docs
└── 01-INDEX.md     # Complete documentation index
```

**Key Documents**:
- [Multi-Agent Architecture](docs/architecture/multi-agent-architecture.md) - 7 Mermaid diagrams
- [Production Ready V1.0](docs/reports/2025-11/PRODUCTION_READY_V1_0_2025_11_18.md) - Launch validation
- [E2E Testing](docs/reports/2025-11/E2E_TESTING_COMPLETE_2025_11_19.md) - Complete test report
- [Official Roadmap](docs/project/ROADMAP_OFFICIAL_2025.md) - Nov 2025 - Dec 2026

---

## 🎯 Design Principles

1. **Async First**: All I/O operations use async/await
2. **Type Safety**: Strict MyPy, comprehensive type hints
3. **Test Coverage**: Minimum 75% (current: 76.29%)
4. **API Design**: RESTful, versioned, well-documented
5. **Performance**: Sub-second responses, efficient caching
6. **Observability**: Metrics, logs, traces for all operations
7. **Security**: Defense in depth, principle of least privilege

---

## 🔗 Key Resources

- **Production API**: https://cidadao-api-production.up.railway.app
- **API Documentation**: https://cidadao-api-production.up.railway.app/docs
- **GitHub**: https://github.com/anderson-ufrj/cidadao.ai-backend
- **Full Documentation**: [docs/01-INDEX.md](docs/01-INDEX.md)

---

**Author**: Anderson Henrique da Silva
**Location**: Minas Gerais, Brasil
**Version**: 1.0.0 - Production Ready
**Last Updated**: 2025-11-22

---

**🇧🇷 Made with ❤️ in Minas Gerais, Brasil**

**🚀 Democratizing Government Transparency Through AI**
