# 🚀 Cidadão.AI Backend - Quick Start Guide

**Author**: Anderson Henrique da Silva
**Location**: Minas Gerais, Brazil
**Created**: 2025-08-13
**Last Updated**: 2025-11-18

---

Get up and running with Cidadão.AI backend in **less than 5 minutes**!

---

## Prerequisites

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **PostgreSQL** (optional - uses SQLite by default)
- **Redis** (optional - in-memory cache fallback available)

---

## ⚡ 60-Second Setup

```bash
# 1. Clone repository
git clone https://github.com/anderson-ntlabs/cidadao.ai-backend.git
cd cidadao.ai-backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies (this takes ~2 minutes)
make install-dev

# 4. Configure environment
cp .env.example .env
# Edit .env and add your API keys (see below)

# 5. Start development server
make run-dev
```

**That's it!** 🎉 API is now running at http://localhost:8000

---

## 🔑 Required API Keys

Edit `.env` and configure these **required** keys:

```bash
# Security (generate with: python scripts/generate_secrets.py)
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# LLM Provider (choose ONE):
# Option 1: Maritaca AI (recommended - Brazilian Portuguese native)
LLM_PROVIDER=maritaca
MARITACA_API_KEY=your-maritaca-key  # Get from: https://maritaca.ai

# Option 2: Anthropic Claude (backup)
# LLM_PROVIDER=anthropic
# ANTHROPIC_API_KEY=your-anthropic-key  # Get from: https://console.anthropic.com
```

---

## 📊 Verify Installation

### 1. Check API Health

```bash
curl http://localhost:8000/health/
# Expected: {"status": "healthy", ...}
```

### 2. Test Chat Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá! Liste os últimos contratos do governo federal"}'
```

### 3. Open Interactive Docs

Visit http://localhost:8000/docs for **Swagger UI** with Brazilian theme!

---

## 🧪 Run Tests

```bash
# All tests
make test

# Just unit tests
make test-unit

# With coverage report
make test-coverage
# Report: htmlcov/index.html

# Specific agent
JWT_SECRET_KEY=test SECRET_KEY=test \
  pytest tests/unit/agents/test_zumbi.py -v
```

---

## 🗂️ Project Structure

```
cidadao.ai-backend/
├── src/
│   ├── agents/          # 16 AI agents (Zumbi, Anita, Tiradentes, etc.)
│   ├── api/             # FastAPI routes (266+ endpoints)
│   ├── services/        # Business logic layer
│   ├── models/          # SQLAlchemy models
│   ├── core/            # Configuration & utilities
│   └── infrastructure/  # Observability, queue, resilience
├── tests/               # 116+ test files
├── docs/                # 344+ documentation files
├── scripts/             # Automation & deployment scripts
└── config/              # Docker & deployment configs
```

---

## 🤖 Available Agents

Test the multi-agent system:

```python
# List all agents
GET /api/v1/agents/

# Chat with specific agent
POST /api/v1/chat/message
{
  "message": "Detecte anomalias em contratos do ministério da saúde",
  "agent": "zumbi"  # Anomaly detection specialist
}

# Available agents:
# - zumbi: Anomaly detection (FFT spectral analysis)
# - anita: Pattern analysis & correlations
# - tiradentes: Report generation (PDF, Excel, HTML)
# - oxossi: Fraud detection (7+ patterns)
# - bonifacio: Legal compliance analysis
# - maria_quiteria: Security auditing
# - lampiao: Regional inequality analysis
# - oscar_niemeyer: Data visualization
# - machado: Textual analysis & NER
# - ayrton_senna: Intent detection & routing
# ... and 6 more!
```

---

## 📈 Monitor Performance

### Prometheus Metrics

```bash
# View all metrics
curl http://localhost:8000/health/metrics

# Start monitoring stack (Grafana + Prometheus)
make monitoring-up

# Access dashboards:
# - Grafana: http://localhost:3000 (admin/cidadao123)
# - Prometheus: http://localhost:9090
```

### LLM Cost Tracking

```bash
# Today's LLM cost
GET /api/v1/llm-costs/daily

# Cost by agent (last 24h)
GET /api/v1/llm-costs/by-agent

# Cost by provider
GET /api/v1/llm-costs/by-provider
```

---

## 🔧 Common Commands

```bash
# Development
make run-dev              # Start dev server with hot reload
make format               # Format code (Black + isort)
make lint                 # Run linter (Ruff)
make type-check           # Type checking (MyPy)
make check                # Lint + Type-check + Test

# Database
make migrate              # Create new migration
make db-upgrade           # Apply migrations
make db-reset             # Reset database (dev only)

# Background Jobs
make celery               # Start Celery worker
make celery-beat          # Start scheduled tasks
make celery-flower        # Flower monitoring UI (http://localhost:5555)

# Monitoring
make monitoring-up        # Start observability stack
make monitoring-down      # Stop observability stack

# CI/CD
make ci                   # Run full CI pipeline locally
make roadmap-progress     # Check v1.0 progress
```

---

## 🌐 Production Deployment

### Railway (Recommended)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Link project
railway link

# 4. Set environment variables
railway variables set LLM_PROVIDER=maritaca
railway variables set MARITACA_API_KEY=xxx
railway variables set JWT_SECRET_KEY=xxx
railway variables set SECRET_KEY=xxx

# 5. Deploy
railway up
```

Production URL: https://cidadao-api-production.up.railway.app/docs

### Docker

```bash
# Development
docker-compose up

# Production
docker-compose -f config/docker/docker-compose.production.yml up -d
```

---

## 📚 Next Steps

1. **Read Architecture**: `docs/architecture/multi-agent-architecture.md`
2. **Explore Agents**: `docs/agents/` (16 agent docs)
3. **API Integration**: `docs/FRONTEND-BACKEND-INTEGRATION-STATUS.md`
4. **Deployment**: `docs/deployment/railway/`
5. **Testing Guide**: `docs/testing/`

---

## 🐛 Troubleshooting

### Tests Failing?

```bash
# Ensure env vars are set
export JWT_SECRET_KEY=test
export SECRET_KEY=test

# Run tests again
make test
```

### Import Errors?

```bash
# Reinstall dependencies
make install-dev
```

### Database Issues?

```bash
# Reset database (loses data!)
make db-reset

# Or just apply migrations
make db-upgrade
```

### Redis Connection Failed?

```bash
# Redis is optional - app works without it
# To use Redis, install and start:
redis-server

# Or use Docker:
docker run -d -p 6379:6379 redis:alpine
```

---

## 💬 Support

- **Documentation**: Full docs in `docs/` folder
- **Issues**: [GitHub Issues](https://github.com/anderson-ntlabs/cidadao.ai-backend/issues)
- **Architecture**: See `CLAUDE.md` for comprehensive guide
- **Status**: Check `docs/project/CURRENT_STATUS_2025_10.md`

---

## 🏆 Key Features

✅ **16 AI Agents** with Brazilian cultural identities
✅ **266+ API Endpoints** for transparency data
✅ **Real Government Data** integration (Portal da Transparência + 7 federal APIs)
✅ **Enterprise Observability** (Prometheus + Grafana + OpenTelemetry)
✅ **LLM Cost Tracking** with budget limits
✅ **Multi-Layer Caching** (Memory → Redis → DB)
✅ **Automated Backups** with disaster recovery
✅ **99.9% Uptime** on Railway production

---

**Happy Coding!** 🚀🇧🇷

For detailed information, see the main [README.md](README.md) and [CLAUDE.md](CLAUDE.md).
