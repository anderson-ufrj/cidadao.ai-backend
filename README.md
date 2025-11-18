# 🏛️ Cidadão.AI Backend

**Author**: Anderson Henrique da Silva
**Location**: Minas Gerais, Brasil
**Last Updated**: 2025-11-18
**Version**: 1.0.0 - **Production Ready** 🚀

> **Multi-Agent AI System** for Brazilian Government Transparency Analysis

[![Railway Deploy](https://img.shields.io/badge/Railway-Production-success?logo=railway&logoColor=white)](https://cidadao-api-production.up.railway.app)
[![Uptime](https://img.shields.io/badge/Uptime-99.9%25-brightgreen)](https://cidadao-api-production.up.railway.app/health)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Test Coverage](https://img.shields.io/badge/Coverage-76.29%25-yellow)](docs/testing/)
[![Tests Passing](https://img.shields.io/badge/Tests-97.4%25_Pass-brightgreen)](tests/)
[![Agents](https://img.shields.io/badge/Agents-16_Operational-blue)](docs/agents/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Democratizing access to Brazilian government transparency data through 16 specialized AI agents with Brazilian cultural identities.**

---

## 🎯 Production Status - V1.0

**Status**: ✅ **PRODUCTION READY** (95-100%)
**Launch Date**: 2025-11-30 (12 days)
**Uptime**: 99.9% since 2025-10-07

### Current Metrics (2025-11-18)

| Metric | Status | Details |
|--------|--------|---------|
| **Deployment** | ✅ Live | [Railway Production](https://cidadao-api-production.up.railway.app) |
| **Backend Readiness** | ✅ 100% | All must-have criteria met |
| **Frontend** | ✅ 90% | Deployed on Vercel, chat working |
| **Integration** | ✅ 85% | End-to-end functional |
| **Test Coverage** | ✅ 76.29% | 1,514 tests, 97.4% pass rate |
| **E2E Tests** | ✅ 5/5 | 100% passing |
| **Smoke Tests** | ✅ 6/6 | Production validated |
| **Performance** | ✅ Excellent | 0.6s avg response time |
| **Documentation** | ✅ Complete | 100+ docs, comprehensive |

**📊 See**: [Production Ready V1.0 Report](docs/reports/2025-11/PRODUCTION_READY_V1_0_2025_11_18.md)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (optional, uses SQLite by default)
- Redis (optional, fallback to memory cache)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/anderson-ufrj/cidadao.ai-backend
cd cidadao.ai-backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env: Add MARITACA_API_KEY or ANTHROPIC_API_KEY
# Generate secrets: python scripts/generate_secrets.py

# 4. Run database migrations (optional)
alembic upgrade head

# 5. Run development server
python -m src.api.app
```

### Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Welcome**: http://localhost:8000/api/v1/

### Production

**Live API**: https://cidadao-api-production.up.railway.app
**Health**: https://cidadao-api-production.up.railway.app/health
**Docs**: https://cidadao-api-production.up.railway.app/docs

---

## 🌐 Complete Ecosystem

This is the **Backend API** of the Cidadão.AI ecosystem, composed of **4 integrated repositories**:

| Repository | Status | Description | Links |
|------------|--------|-------------|-------|
| **🚀 Backend** | ✅ **Production** | Multi-Agent API (FastAPI) | **[You are here]** \| [Docs](docs/) |
| **⚛️ Frontend** | ✅ **Production** | PWA App (Next.js 15) | [Repo](https://github.com/anderson-ufrj/cidadao.ai-frontend) \| [Live](#) |
| **🏛️ Hub** | ✅ Ready | Landing Page | [Repo](https://github.com/anderson-ufrj/cidadao.ai-hub) \| [Site](#) |
| **🤖 Models** | 🚧 Development | ML Models & MLOps | [Repo](https://github.com/anderson-ufrj/cidadao.ai-models) |

---

## 📋 Overview

**Cidadão.AI** analyzes Brazilian government contracts using **16 specialized AI agents** with Brazilian cultural identities. The system runs 24/7 on Railway with PostgreSQL and Redis, autonomously monitoring data sources, detecting anomalies, and providing transparency insights.

### Key Features

✅ **16 Specialized Agents** - Brazilian cultural identities (Zumbi, Anita, Tiradentes, etc.)
✅ **30+ Government APIs** - Federal and state transparency data integrated
✅ **Multi-Agent Orchestration** - Coordinated investigation workflows
✅ **Real-Time Chat** - SSE streaming responses from agents
✅ **Anomaly Detection** - Statistical analysis (FFT, Z-score, IQR)
✅ **Natural Language** - Portuguese-first interface
✅ **Production Ready** - 99.9% uptime, comprehensive tests
✅ **High Performance** - 0.6s avg response time, 367x faster agent loading

---

## 🤖 Agent System

### 16 Operational Agents

**Tier 1 - Excellent** (10 agents - >75% coverage):
1. **Zumbi dos Palmares** - Anomaly Detection (96.32%)
2. **Anita Garibaldi** - Pattern Analysis (94.87%)
3. **Oxóssi** - Data Hunting (94.44%)
4. **Lampião** - Regional Analysis (93.75%)
5. **Ayrton Senna** - Semantic Routing (92.31%)
6. **Tiradentes** - Report Generation (91.67%)
7. **Oscar Niemeyer** - Data Aggregation (89.47%)
8. **Machado de Assis** - Textual Analysis (88.24%)
9. **José Bonifácio** - Legal Analysis (87.50%)
10. **Maria Quitéria** - Security Auditing (86.96%)

**Tier 2 - Near-Complete** (5 agents):
11. **Abaporu** - Master Orchestration (85.71%)
12. **Nanã** - Memory Management (84.62%)
13. **Drummond** - Communication (83.33%)
14. **Céuci** - ETL & Predictive (82.76%)
15. **Obaluaiê** - Corruption Detection (81.25%)

**Tier 3 - Complete Framework** (1 agent):
16. **Dandara** - Social Equity (86.32%)

**📚 See**: [Agent Documentation](docs/agents/) for detailed information.

---

## 📊 System Architecture

```
User Query → Intent Detection → Entity Extraction → Execution Planning
                                                            ↓
                                                    Data Federation
                                                            ↓
                                                    Entity Graph (NetworkX)
                                                            ↓
                                                    Investigation Agents
                                                            ↓
                                                    Consolidated Results
```

**Key Components**:
- **Orchestrator** - Query planning and execution coordination
- **Agent Pool** - 16 specialized agents with lazy loading (367x faster)
- **Data Federation** - Parallel API calls with circuit breakers
- **Entity Graph** - NetworkX-based relationship tracking
- **API Registry** - 30+ transparency APIs catalogued

**📚 See**: [Multi-Agent Architecture](docs/architecture/multi-agent-architecture.md) (7 Mermaid diagrams)

---

## 🔧 Technology Stack

### Core
- **Python 3.11+** - Modern async/await patterns
- **FastAPI** - High-performance async framework
- **Pydantic** - Data validation and settings
- **SQLAlchemy** - ORM with async support
- **Alembic** - Database migrations

### AI & ML
- **Maritaca AI** - Primary LLM (Brazilian Portuguese optimized)
- **Anthropic Claude** - Backup LLM with auto-fallback
- **NetworkX** - Graph analysis for entity relationships
- **NumPy/SciPy** - Statistical analysis

### Data & Storage
- **PostgreSQL** - Primary database (Railway managed)
- **Redis** - Multi-layer caching (Railway managed)
- **Supabase** - Authentication and realtime (optional)

### Monitoring & Observability
- **Prometheus** - Metrics collection
- **Grafana** - Dashboards and visualization
- **Structlog** - Structured logging
- **Sentry** - Error tracking (planned)

### Testing & Quality
- **Pytest** - Test framework (1,514 tests)
- **pytest-asyncio** - Async test support
- **Coverage.py** - Code coverage (76.29%)
- **Ruff** - Fast Python linter
- **Black** - Code formatter
- **MyPy** - Static type checking

---

## 🚀 Performance

### Response Times (Production)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| API Response (p95) | <2000ms | ~600ms | ✅ 70% better |
| Agent Processing | <5000ms | ~3200ms | ✅ 36% better |
| Chat First Token | <500ms | ~380ms | ✅ 24% better |
| Investigation (6 agents) | <15000ms | ~12500ms | ✅ 17% better |
| Agent Import Time | <100ms | 3.81ms | ✅ 96% better |

**Average Response Time**: 0.6s
**Uptime**: 99.9%
**Cache Hit Rate**: ~95%

**📊 See**: [Performance Review](docs/reports/2025-11/PERFORMANCE_REVIEW_2025_11_18.md)

---

## 🧪 Testing

### Test Statistics

- **Total Tests**: 1,514
- **Test Files**: 98
- **Pass Rate**: 97.4% (1,474 passing, 40 failing)
- **Coverage**: 76.29% (target: 75%+)
- **E2E Tests**: 5/5 passing (100%)
- **Smoke Tests**: 6/6 operational

### Test Categories

- **Unit Tests**: Agent logic, services, models
- **Integration Tests**: API endpoints, database operations
- **E2E Tests**: Complete investigation workflow
- **Performance Tests**: Load testing, benchmarks
- **Manual Tests**: Real-world scenario validation

**📚 See**: [E2E Testing Report](docs/reports/2025-11/E2E_TESTING_COMPLETE_2025_11_19.md)

---

## 📚 Documentation

### Quick Links

**Getting Started**:
- [Quick Start](#-quick-start) - Installation and setup
- [QUICKSTART.md](QUICKSTART.md) - Detailed quickstart guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute

**Architecture**:
- [Multi-Agent Architecture](docs/architecture/multi-agent-architecture.md) - System design (7 diagrams)
- [Improvement Roadmap](docs/architecture/IMPROVEMENT_ROADMAP_2025.md) - Technical improvements

**Agents**:
- [Agent Documentation](docs/agents/) - All 16 agents documented
- [Zumbi](docs/agents/zumbi.md) - Best reference implementation

**Operations**:
- [Railway Deployment](docs/deployment/railway/) - Production deployment
- [Monitoring Setup](docs/deployment/railway/monitoring-setup.md) - Grafana + Prometheus

**Reports** (November 2025):
- [Production Ready V1.0](docs/reports/2025-11/PRODUCTION_READY_V1_0_2025_11_18.md) - V1.0 validation
- [Performance Review](docs/reports/2025-11/PERFORMANCE_REVIEW_2025_11_18.md) - Performance metrics
- [E2E Testing](docs/reports/2025-11/E2E_TESTING_COMPLETE_2025_11_19.md) - End-to-end validation

**📚 Full Index**: [Documentation Index](docs/INDEX.md)

---

## 🛠️ Development

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (optional)
- Redis 7+ (optional)
- Git

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run tests
make test

# Check code quality
make check  # Format + lint + type-check + test

# Run locally
make run-dev
```

### Common Commands

```bash
# Testing
make test                # All tests
make test-unit           # Unit tests only
make test-agents         # Agent tests
make test-coverage       # With coverage report

# Code Quality
make format              # Black + isort + ruff --fix
make lint                # Ruff linter
make type-check          # MyPy strict mode
make check               # All quality checks

# Database
make migrate             # Create migration
make db-upgrade          # Apply migrations
make db-downgrade        # Rollback migration

# Monitoring
make monitoring-up       # Start Grafana + Prometheus
```

**📚 See**: [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 🌍 Government APIs Integrated

### Federal APIs (8)
1. **IBGE** - Demographics, geography
2. **DataSUS** - Health data
3. **INEP** - Education statistics
4. **PNCP** - Public contracts portal
5. **Compras.gov** - Federal procurement
6. **Portal da Transparência** - Federal transparency
7. **Banco Central** - Economic data
8. **Minha Receita** - Company data (CNPJ)

### State APIs (5)
1. **TCE-CE** - Ceará Court of Accounts
2. **TCE-PE** - Pernambuco Court of Accounts
3. **TCE-MG** - Minas Gerais Court of Accounts
4. **SICONFI** - Municipal finances
5. **CKAN** - State data portals

**📊 See**: [Government APIs Inventory](docs/api/GOVERNMENT_APIS_INVENTORY.md)

---

## 📅 Roadmap

### V1.0 - Launch (Nov 30, 2025)

**Status**: ✅ Production ready

- [x] 16 agents operational
- [x] E2E tests passing
- [x] Production deployment
- [x] Frontend integration
- [x] Documentation complete
- [ ] V1.0 launch (Nov 30)

### V1.1 - Enhancements (Dec 2025)

- [ ] OAuth social login
- [ ] WebSocket real-time updates
- [ ] Performance optimization
- [ ] Grafana production alerts
- [ ] Load testing

### V2.0 - Advanced Features (Q1 2026)

- [ ] ML models custom-trained
- [ ] Predictive analytics
- [ ] Advanced visualizations
- [ ] Multi-tenancy
- [ ] Enterprise features

**📚 See**: [Official Roadmap 2025-2026](docs/project/ROADMAP_OFFICIAL_2025.md) (5 phases, 14 months)

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Run quality checks (`make check`)
6. Commit changes (`git commit -m 'feat: add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code of Conduct

- Follow conventional commits (feat, fix, docs, etc.)
- Maintain 75%+ test coverage
- Document all new features
- Use type hints throughout
- Follow PEP 8 style guide

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

**Brazilian Cultural Icons** - Inspiration for agent identities:
- Zumbi dos Palmares - Leader of freedom
- Anita Garibaldi - Revolutionary hero
- Tiradentes - Martyr of independence
- Ayrton Senna - Champion of excellence
- And 12 more incredible Brazilians

**Open Source Community** - FastAPI, Pydantic, SQLAlchemy, and many more.

**Government Data** - Brazilian government for open data initiatives.

---

## 📞 Contact & Support

**Author**: Anderson Henrique da Silva
**Location**: Minas Gerais, Brasil

**Links**:
- **GitHub**: https://github.com/anderson-ufrj/cidadao.ai-backend
- **Issues**: https://github.com/anderson-ufrj/cidadao.ai-backend/issues
- **Discussions**: https://github.com/anderson-ufrj/cidadao.ai-backend/discussions

**Production**:
- **API**: https://cidadao-api-production.up.railway.app
- **Docs**: https://cidadao-api-production.up.railway.app/docs
- **Health**: https://cidadao-api-production.up.railway.app/health

---

## 📊 Project Statistics

**Codebase**:
- **Lines of Code**: ~133,783 (src/)
- **Test Code**: ~49,888 lines
- **Total Files**: 1,082
- **Commits**: 1,079
- **Contributors**: 1

**Development**:
- **Started**: August 13, 2025
- **Production**: October 7, 2025
- **Duration**: ~3 months
- **Commits/Day**: ~11

**Quality**:
- **Test Coverage**: 76.29%
- **Test Pass Rate**: 97.4%
- **Uptime**: 99.9%
- **Avg Response Time**: 0.6s

---

**🇧🇷 Made with ❤️ in Minas Gerais, Brasil**

**🚀 Democratizing Government Transparency Through AI**

---

*Last Updated: 2025-11-18 - Version 1.0.0 Production Ready*
