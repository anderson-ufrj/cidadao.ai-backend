# Repository Structure - Cidadão.AI Backend

Estrutura organizada do repositório após refatoração de 2025-10-20.

## 📁 Root Directory

```
cidadao.ai-backend/
├── .env.example          # Template de environment variables
├── .gitignore            # Arquivos ignorados pelo git
├── alembic.ini          # Configuração Alembic migrations
├── CLAUDE.md            # Instruções para Claude Code
├── CITATION.cff         # Citation metadata
├── LICENSE              # Licença do projeto
├── Makefile             # Comandos de desenvolvimento
├── MANIFEST.in          # Arquivos para distribuição Python
├── Procfile             # Deploy Heroku/Railway
├── pyproject.toml       # Dependências e configuração Python
├── pytest.ini           # Configuração pytest
├── railway.json         # Configuração Railway
├── README.md            # Documentação principal
├── requirements.txt     # Dependências pip
├── SECURITY.md          # Políticas de segurança
└── test_single_investigation.py  # Teste end-to-end principal
```

## 📂 Main Directories

### `/src` - Source Code
```
src/
├── agents/              # 17 AI agents (Zumbi, Anita, etc.)
├── api/                 # FastAPI routes and app
├── core/                # Core configuration and constants
├── db/                  # Database session management
├── infrastructure/      # Database, queue, cache
├── llm/                 # LLM providers (Maritaca, Groq, etc.)
├── models/              # SQLAlchemy models
├── services/            # Business logic services
└── tools/               # Utility tools and helpers
```

### `/docs` - Documentation
```
docs/
├── fixes/               # System fixes documentation
│   ├── 2025-10/        # Fixes from October 2025
│   │   └── 2025-10-20-investigation-persistence-fix.md
│   └── README.md
├── architecture/        # System architecture docs
├── agents/              # Agent-specific documentation
├── api/                 # API documentation
└── guides/              # User and developer guides
```

### `/scripts` - Automation Scripts
```
scripts/
├── debug/               # Debug and diagnostic scripts
│   ├── check_database.py
│   ├── check_llm_config.py
│   ├── test_*.py
│   ├── monitor_*.py
│   └── README.md
├── sql/                 # SQL migration scripts
│   ├── CHECK_ID_TYPE.sql
│   ├── fix_db.sql
│   └── *.sql
├── railway-env-setup.sh
└── run_railway_migration.sh
```

### `/tests` - Test Suite
```
tests/
├── unit/                # Unit tests (161 tests)
│   ├── agents/         # Agent tests
│   ├── api/            # API tests
│   └── services/       # Service tests
├── integration/         # Integration tests (36 tests)
├── multiagent/         # Multi-agent coordination tests
└── performance/        # Performance benchmarks
```

### `/alembic` - Database Migrations
```
alembic/
├── versions/            # Migration files
│   ├── 002_entity_graph.py
│   ├── 003_performance_indexes.py
│   ├── 20251020_*.py   # Today's fixes
│   └── ...
└── env.py              # Alembic configuration
```

### `/config` - Configuration Files
```
config/
├── docker/              # Docker configurations
└── monitoring/          # Prometheus/Grafana configs
```

### `/logs` - Application Logs
```
logs/
├── final_test.log
└── *.log               # (gitignored)
```

### `/archive` - Archived Files
```
archive/
├── .env.railway        # Old env files
├── .env.supabase.example
└── .env.chat.example   # (gitignored)
```

## 🔍 Key Files by Purpose

### Configuration
- `.env.example` - Template for environment variables
- `pyproject.toml` - Python dependencies and tooling
- `alembic.ini` - Database migrations config
- `railway.json` - Railway deployment config

### Development
- `Makefile` - Development commands (`make test`, `make run-dev`, etc.)
- `test_single_investigation.py` - Main end-to-end test
- `pytest.ini` - Test configuration

### Documentation
- `README.md` - Main project documentation
- `CLAUDE.md` - Instructions for Claude Code AI
- `SECURITY.md` - Security policies
- `REPOSITORY_STRUCTURE.md` - This file

### Deployment
- `Procfile` - Web server startup command
- `requirements.txt` - Production dependencies
- `railway.json` - Railway service configuration

## 📊 Statistics

- **Total Lines**: ~66,000
- **Agents**: 17 (23,369 lines)
- **Services**: 60+ modules
- **API Routes**: 76+ endpoints
- **Test Files**: 128 files
- **Test Coverage**: 80.5%

## 🚀 Quick Start

### Development
```bash
# Install dependencies
make install-dev

# Run tests
make test

# Start development server
make run-dev
```

### Testing
```bash
# Run all tests
JWT_SECRET_KEY=test SECRET_KEY=test make test

# Run specific tests
pytest tests/unit/agents/test_zumbi.py -v

# Test end-to-end
python test_single_investigation.py
```

### Debug
```bash
# Check database
python scripts/debug/check_database.py

# Check LLM config
python scripts/debug/check_llm_config.py

# Monitor investigation
python scripts/debug/monitor_investigation.py <investigation_id>
```

## 📝 Documentation References

- **Architecture**: `/docs/architecture/`
- **Agents**: `/docs/agents/`
- **API**: `/docs/api/`
- **Fixes**: `/docs/fixes/`

## 🔗 Production

- **API**: https://cidadao-api-production.up.railway.app
- **Docs**: https://cidadao-api-production.up.railway.app/docs
- **Health**: https://cidadao-api-production.up.railway.app/health

## 🎯 Next Steps

1. Review `/docs/fixes/2025-10/2025-10-20-investigation-persistence-fix.md` for latest system fixes
2. Check `CLAUDE.md` for development guidelines
3. Run `make test` to verify your environment
4. Read agent documentation in `/docs/agents/`

---

**Last Updated**: 2025-10-20
**Maintainer**: Anderson Henrique da Silva
**License**: Proprietary - All rights reserved
