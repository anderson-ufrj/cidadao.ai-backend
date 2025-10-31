# 📚 Cidadão.AI Backend Documentation

**Author**: Anderson Henrique da Silva
**Location**: Minas Gerais, Brasil
**Last Updated**: 2025-10-31

## 🚀 Quick Start

| Resource | Link |
|----------|------|
| **Production API** | https://cidadao-api-production.up.railway.app |
| **API Docs** | https://cidadao-api-production.up.railway.app/docs |
| **Installation** | [Development Setup](development/setup.md) |
| **Deploy** | [Railway Guide](deployment/railway/README.md) |

## 📊 Current Status

- **16 Operational Agents** + 1 framework base
- **266+ API Endpoints** across 36 modules
- **35 Test Files** with 78.3% agent coverage
- **Production**: Railway (99.9% uptime since Oct 7, 2025)

## 📖 Core Documentation

### [🤖 Agents](agents/)
Complete multi-agent system with Brazilian cultural identities
- [All Agents Overview](agents/README.md) - 16 operational agents
- [Zumbi](agents/zumbi.md) - Anomaly detection (1,427 lines)
- [Anita](agents/anita.md) - Statistical analysis (1,566 lines)
- [Tiradentes](agents/tiradentes.md) - Report generation (1,934 lines)

### [🏗️ Architecture](architecture/)
System design and technical architecture
- [Multi-Agent System](architecture/multi-agent-architecture.md)
- [API Integration](architecture/MULTI_API_INTEGRATION.md) - 30+ government APIs
- [Orchestration](architecture/ORCHESTRATION_SYSTEM.md)
- [Performance](architecture/PERFORMANCE_OPTIMIZATION.md)

### [🌐 API Reference](api/)
Complete API documentation
- [Chat API](api/CHAT_API_DOCUMENTATION.md) - SSE streaming
- [REST Endpoints](api/ENDPOINTS_CONNECTION_STATUS.md) - 266+ endpoints
- [WebSocket](api/WEBSOCKET_API_DOCUMENTATION.md) - Real-time
- [Portal da Transparência](api/PORTAL_TRANSPARENCIA_INTEGRATION.md)

### [🚀 Deployment](deployment/)
Production deployment guides
- [Railway](deployment/railway/README.md) - Primary platform
- [Docker](deployment/docker.md) - Container setup
- [Environment](deployment/environment.md) - Configuration

### [💻 Development](development/)
Developer guides
- [Setup Guide](development/setup.md)
- [Code Standards](development/code-standards.md)
- [Frontend Integration](development/FRONTEND_INTEGRATION_GUIDE.md)
- [Contributing](development/contributing.md)

### [📊 Monitoring](monitoring/)
Production monitoring
- [Grafana Dashboards](monitoring/GRAFANA_DASHBOARDS_GUIDE.md)
- [Prometheus Metrics](monitoring/README.md)
- [Alerts Setup](setup/alerts.md)

### [🧪 Testing](testing/)
Test documentation
- [Test Strategy](testing/TEST_DEVELOPMENT_STRATEGY.md)
- [Coverage Report](testing/TEST_COVERAGE_REPORT_2025_10_22.md) - 62.84%
- [Performance Tests](testing/PERFORMANCE_TESTING.md)

## 🛠️ Development Commands

```bash
# Development
make run-dev        # Start server (localhost:8000)
make test           # Run all tests
make check          # Lint + format + type-check

# Monitoring
make monitoring-up  # Grafana + Prometheus
# Grafana: localhost:3000 (admin/cidadao123)

# Validation
python3 scripts/validate_documentation.py
python3 scripts/update_agent_line_counts.py
```

## 📁 Repository Structure

```
cidadao.ai-backend/
├── src/
│   ├── agents/       # 16 AI agents
│   ├── api/          # FastAPI routes
│   └── services/     # Core services
├── tests/            # 35 test files
├── docs/             # This documentation
├── config/           # Configuration
└── scripts/          # Utility scripts
```

## 🔑 Key Features

### Multi-Agent System
- **16 specialized agents** with Brazilian identities
- **Reflection pattern** for quality control (0.8 threshold)
- **Lazy loading** for performance
- **Agent pool** management

### Government Data Integration
- **30+ APIs** integrated
- Portal da Transparência
- IBGE, DataSUS, INEP
- State TCEs (6 states)

### Performance
- Redis caching (multi-layer)
- Connection pooling
- Async throughout
- SSE streaming

## 📈 Metrics & Performance

| Metric | Current | Target |
|--------|---------|--------|
| Test Coverage | 62.84% | 80% |
| API Response (p95) | 145ms | <200ms |
| Agent Processing | 3.2s | <5s |
| Tests Passing | 251 | - |

## 🔍 Quick Links

### Frontend Integration
- [API Guide](frontend-integration/COMPREHENSIVE_API_GUIDE.md) - 90+ endpoints
- [Executive Summary](frontend-integration/EXECUTIVE_SUMMARY.md)
- [Code Examples](examples/)

### Project Status
- [Current Status](project/current/CURRENT_STATUS_2025_10.md)
- [Roadmap](project/planning/ROADMAP.md)
- [Changelog](project/current/CHANGELOG.md)

### Troubleshooting
- [Production Fixes](troubleshooting/PRODUCTION_FIXES_2025_10_29.md)
- [Common Issues](troubleshooting/common-issues.md)
- [Railway Issues](deployment/railway/README.md#troubleshooting)

## 📝 Recent Updates

### 2025-10-31
- ✅ Documentation cleanup - removed 823MB node_modules
- ✅ Updated agent line counts (12,290 lines drift fixed)
- ✅ Created validation scripts
- ✅ Archived old session files
- ✅ Consolidated test reports

### 2025-10-30
- Voice integration completed
- Railway deployment optimized
- Health endpoint enhanced

## 📮 Contact

**Developer**: Anderson Henrique da Silva
**Email**: andersonhs27@gmail.com
**Location**: Minas Gerais, Brasil

---

*Historical documentation in [archive/](archive/)*
