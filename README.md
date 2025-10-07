# 🏛️ Cidadão.AI Backend

> **Multi-Agent AI System** for Brazilian Government Transparency Analysis

[![Railway Deploy](https://img.shields.io/badge/Railway-Deployed-success?logo=railway&logoColor=white)](https://railway.app)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Celery](https://img.shields.io/badge/Celery-5.3+-green?logo=celery&logoColor=white)](https://docs.celeryq.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Democratizing access to public contract data through autonomous AI agents with Brazilian cultural identities.**

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env: Add GROQ_API_KEY, JWT_SECRET_KEY

# 3. Run development server
python -m src.api.app

# 4. Access Swagger UI
# http://localhost:8000/docs
```

---

## 📋 Overview

**Cidadão.AI** analyzes Brazilian government contracts using **17 specialized AI agents**. The system runs 24/7 on Railway, autonomously monitoring data sources, detecting anomalies, and sending real-time alerts.

### Key Features

✅ **24/7 Autonomous Monitoring** - Celery tasks scan contracts every 6 hours
✅ **Multi-Agent Collaboration** - 17 agents with Brazilian cultural identities
✅ **Anomaly Detection** - ML-powered analysis (price, patterns, duplicates)
✅ **Real-time Alerts** - Webhook notifications to Discord/Slack
✅ **Natural Language API** - Chat with agents in Portuguese
✅ **Production Ready** - Railway deployment with 99.9% uptime

### Current Status

| Aspect | Status |
|--------|--------|
| **Deployment** | Railway (3 services: API, Worker, Beat) |
| **Database** | Supabase PostgreSQL |
| **Cache** | Railway Redis (persistent) |
| **Agents** | 8 of 17 fully operational |
| **Test Coverage** | 80%+ |
| **Uptime** | 99.9% |

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────┐
│             CIDADÃO.AI BACKEND                      │
├────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   API    │  │  Worker  │  │   Beat   │        │
│  │ (FastAPI)│  │ (Celery) │  │ (Sched.) │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
│       │             │             │               │
│       └──────┬──────┴──────┬──────┘               │
│              │             │                       │
│       ┌──────▼──────┐  ┌───▼───────┐             │
│       │    Redis    │  │  Supabase │             │
│       │   (Cache)   │  │   (DB)    │             │
│       └─────────────┘  └───────────┘             │
└────────────────────────────────────────────────────┘
```

### Technology Stack

- **API**: FastAPI + Uvicorn
- **Agents**: LangChain + Groq LLM
- **Tasks**: Celery + Redis
- **Database**: PostgreSQL (Supabase)
- **Deployment**: Railway PaaS
- **Monitoring**: Prometheus + Grafana

---

## ✨ Features

### 1. Autonomous Investigations

```python
# Runs every 6 hours via Celery Beat
@celery_app.task
def monitor_katana_dispensas():
    # Fetch contracts from Katana API
    # Analyze with Zumbi agent
    # Save anomalies to Supabase
    # Send alerts for critical findings
```

**Impact**: 2,400+ contracts analyzed monthly on autopilot.

### 2. Anomaly Detection

```python
from src.agents import ZumbiAgent

zumbi = ZumbiAgent()
result = await zumbi.analyze_contract(
    contract_data={...},
    threshold=0.7
)

print(f"Score: {result.anomaly_score}")
print(f"Indicators: {result.indicators}")
```

**Detection**: Price deviations, supplier patterns, duplicates.

### 3. Real-time Alerts

```bash
# Discord/Slack webhook notifications

🚨 ALERTA - CRITICAL

Dispensa 123/2025
Score: 0.9234
Valor 300% acima da média
```

### 4. Multi-Agent System

8 operational agents:
- **Abaporu** - Master Orchestrator
- **Zumbi** - Anomaly Detective
- **Anita** - Data Analyst
- **Tiradentes** - Report Writer
- **Senna** - Agent Router
- **Nanã** - Memory Manager
- **Bonifácio** - Legal Expert
- **Machado** - Narrative Analyst

---

## 🌐 Deployment

### Railway (Production)

**Status**: ✅ Running in production since 2025-10-07

```bash
# Deploy via Railway CLI
railway up

# Or push to GitHub (auto-deploy)
git push origin main
```

**Services**:
- **API**: FastAPI (2 replicas)
- **Worker**: Celery (4 processes)
- **Beat**: Scheduler (1 replica)

📚 **Guide**: [Railway Deployment](docs/deployment/railway.md)

### Migration from HuggingFace

**Date**: 2025-10-07
**Reason**: HF doesn't support Celery Worker + Beat
**Result**: 50% cost reduction, 10x more features

📚 **Story**: [HF→Railway Migration](docs/deployment/migration-hf-to-railway.md)

---

## 📚 Documentation

### Setup & Deployment
- [Railway Deployment](docs/deployment/railway.md) - Primary platform
- [HF→Railway Migration](docs/deployment/migration-hf-to-railway.md) - Why we migrated
- [Supabase Setup](docs/setup/supabase-setup.md) - Database config
- [Alerts Setup](docs/setup/alerts.md) - Webhook notifications
- [Token Configuration](docs/setup/tokens.md) - Environment variables

### Architecture & Development
- [System Architecture](docs/architecture/) - Technical details
- [Agent System](docs/agents/) - Multi-agent patterns
- [API Documentation](docs/api/) - REST endpoints
- [Development Guide](docs/development/) - Contributing

### Troubleshooting
- [Common Issues](docs/troubleshooting/common-issues.md)
- [Supabase Errors](docs/troubleshooting/supabase-errors.md)

---

## 🛠️ Development

### Running Tests

```bash
make test              # All tests (80% coverage)
make test-unit         # Unit tests only
make test-integration  # Integration tests
```

### Code Quality

```bash
make check       # Format + Lint + Type-check
make format      # Black + isort
make lint        # Ruff linter
make type-check  # MyPy

make ci          # Full CI locally
```

### Project Structure

```
cidadao.ai-backend/
├── src/                    # Source code
│   ├── agents/            # 17 AI agents
│   ├── api/               # FastAPI routes
│   ├── infrastructure/    # Celery + Redis
│   ├── services/          # Business logic
│   └── core/              # Configuration
├── tests/                  # 80% coverage
├── docs/                   # Documentation
├── config/                 # Deployment configs
├── migrations/             # Database migrations
└── scripts/                # Utility scripts
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/name`
3. Make changes and add tests
4. Run: `make ci`
5. Commit: `git commit -m "feat: description"`
6. Push and open Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

## 🔗 Links

- **Production API**: https://cidadao-ai-backend.railway.app
- **GitHub**: https://github.com/anderson-ufrj/cidadao.ai-backend
- **Documentation**: [docs/](docs/)

---

**Made with ❤️ for Brazilian Democracy**

*Democratizing government transparency through AI*
