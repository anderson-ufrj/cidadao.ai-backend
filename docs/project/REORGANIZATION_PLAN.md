# 🗂️ Plano de Reorganização do Repositório - Cidadão.AI Backend

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

## 📋 Situação Atual

**Problemas Identificados:**
- 62 arquivos na raiz do projeto (muito poluído)
- Múltiplos READMEs dispersos (README.md, README-DOCKERFILES.md, README_SUPABASE.md)
- Arquivos de configuração misturados com documentação
- Scripts de teste na raiz em vez de scripts/
- Arquivos de backup (.backup) commitados
- Documentação de deployment espalhada
- Falta documentação sobre migração HF → Railway

## 🎯 Estrutura Alvo (Profissional)

```
cidadao.ai-backend/
├── .github/                    # GitHub workflows, templates
│   ├── workflows/             # CI/CD pipelines
│   └── ISSUE_TEMPLATE/        # Issue templates
│
├── docs/                       # 📚 TODA documentação centralizada
│   ├── deployment/            # Deployment guides
│   │   ├── railway.md         # Railway deployment (PRIMARY)
│   │   ├── huggingface.md     # HuggingFace (DEPRECATED)
│   │   ├── docker.md          # Docker deployment
│   │   └── migration-hf-to-railway.md  # Migration guide
│   ├── setup/                 # Setup guides
│   │   ├── supabase.md        # Supabase setup
│   │   ├── alerts.md          # Alert system setup
│   │   ├── environment.md     # Environment variables
│   │   └── tokens.md          # Token configuration
│   ├── architecture/          # Architecture docs
│   │   ├── overview.md        # System overview
│   │   ├── agents.md          # Multi-agent system
│   │   ├── celery.md          # Task queue system
│   │   └── database.md        # Database schema
│   ├── api/                   # API documentation
│   │   ├── endpoints.md       # API endpoints
│   │   └── authentication.md  # Auth guide
│   ├── development/           # Developer guides
│   │   ├── getting-started.md # Quick start
│   │   ├── testing.md         # Testing guide
│   │   └── contributing.md    # Contribution guide
│   └── troubleshooting/       # Problem solving
│       └── common-issues.md   # FAQ
│
├── scripts/                    # 🔧 Utility scripts
│   ├── deployment/            # Deployment scripts
│   │   ├── deploy.sh          # Main deploy script
│   │   ├── check_deploy.sh    # Deployment verification
│   │   └── start.sh           # Start script
│   ├── database/              # Database scripts
│   │   └── create_tables.py   # Table creation
│   ├── monitoring/            # Monitoring scripts
│   │   └── manage-monitoring.sh
│   └── testing/               # Testing scripts
│       ├── test_*.py          # Test scripts
│       └── test_*.sh          # Shell test scripts
│
├── config/                     # ⚙️ Configuration files
│   ├── docker/                # Docker configs
│   │   ├── Dockerfile         # Main Dockerfile
│   │   ├── Dockerfile.hf      # HuggingFace (deprecated)
│   │   ├── docker-compose.yml # Production compose
│   │   └── docker-compose.monitoring.yml
│   ├── deployment/            # Deployment configs
│   │   ├── Procfile           # Railway/Heroku
│   │   ├── render.yaml        # Render.com
│   │   └── railway.json       # Railway config
│   └── monitoring/            # Monitoring configs
│       └── prometheus/
│
├── migrations/                 # 🗄️ Database migrations
│   ├── alembic/               # Alembic migrations
│   └── supabase/              # Supabase migrations
│       ├── schema.sql         # Main schema
│       └── 001_*.sql          # Versioned migrations
│
├── src/                        # 💻 Source code (unchanged)
│   ├── agents/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── infrastructure/
│   ├── services/
│   └── ...
│
├── tests/                      # 🧪 Tests (unchanged)
│
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── CHANGELOG.md               # Version history
├── CLAUDE.md                  # Claude Code instructions
├── LICENSE                    # MIT License
├── Makefile                   # Development commands
├── pyproject.toml             # Python project config
├── pytest.ini                 # Pytest configuration
├── README.md                  # Main README (comprehensive)
└── requirements.txt           # Python dependencies

```

## 📦 Ações de Reorganização

### 1️⃣ Criar Estrutura de Diretórios

```bash
mkdir -p .github/workflows
mkdir -p docs/{deployment,setup,architecture,api,development,troubleshooting}
mkdir -p scripts/{deployment,database,monitoring,testing}
mkdir -p config/{docker,deployment,monitoring}
```

### 2️⃣ Mover Arquivos de Documentação

**Para `docs/deployment/`:**
- RAILWAY-DEPLOY.md → docs/deployment/railway.md
- README-DOCKERFILES.md → docs/deployment/docker.md
- Criar docs/deployment/huggingface.md (marcar DEPRECATED)
- Criar docs/deployment/migration-hf-to-railway.md (NOVO - explicar migração)

**Para `docs/setup/`:**
- SUPABASE-SETUP.md → docs/setup/supabase.md
- SUPABASE-TESTING.md → docs/setup/supabase-testing.md
- ALERTS-SETUP.md → docs/setup/alerts.md
- CONFIGURACAO_TOKENS.md → docs/setup/tokens.md
- README_SUPABASE.md → docs/setup/supabase-integration.md

**Para `docs/architecture/`:**
- Criar docs/architecture/overview.md (sistema geral)
- Criar docs/architecture/celery.md (Celery + Redis + Beat)
- Mover docs/architecture/* existentes

**Para `docs/troubleshooting/`:**
- HUGGINGFACE_SUPABASE_FIX.md → docs/troubleshooting/supabase-errors.md

### 3️⃣ Mover Scripts

**Para `scripts/deployment/`:**
- deploy.sh → scripts/deployment/
- check_deploy.sh → scripts/deployment/
- start.sh → scripts/deployment/
- start_hf.py → scripts/deployment/ (deprecated)
- manage-monitoring.sh → scripts/monitoring/

**Para `scripts/database/`:**
- create_tables.py → scripts/database/

**Para `scripts/testing/`:**
- test_*.py (raiz) → scripts/testing/
- test_*.sh (raiz) → scripts/testing/

### 4️⃣ Mover Configurações

**Para `config/docker/`:**
- Dockerfile → config/docker/
- Dockerfile.hf → config/docker/ (deprecated)
- docker-compose.*.yml → config/docker/

**Para `config/deployment/`:**
- Procfile → config/deployment/
- render.yaml → config/deployment/

**Para `migrations/supabase/`:**
- supabase_schema.sql → migrations/supabase/schema.sql
- supabase_schema_compatible.sql → migrations/supabase/002_auto_investigations.sql

### 5️⃣ Consolidar Requirements

**Manter:**
- requirements.txt (produção Railway)
- requirements/
  - base.txt
  - dev.txt
  - hf.txt (deprecated)
  - production.txt

**Remover:**
- requirements-minimal.txt (merge em base.txt)
- requirements-full.txt (merge em production.txt)
- requirements-hf.txt (mover para requirements/hf.txt)

### 6️⃣ Limpar Arquivos

**Deletar:**
- *.backup (railway.json.backup, railway.toml.backup, nixpacks.toml.backup)
- cidadao_ai.db (database local - não deve estar no git)
- .env (arquivo pessoal - não deve estar no git)
- .env.hf (deprecated)
- .env.production (usar .env.example)
- SUPABASE_SUMMARY.txt (redundante)
- SUPABASE_REST_API.md (mover para docs/api/)
- monitoring_embedded.py (não usado)
- app.py (HuggingFace - marcar deprecated e mover)

**Atualizar .gitignore:**
```
*.db
*.sqlite
*.backup
.env
.env.local
.env.*.local
```

### 7️⃣ Criar Documentação Nova

**docs/deployment/migration-hf-to-railway.md:**
```markdown
# Migração: HuggingFace Spaces → Railway

## Por que migramos?

1. **Limitações do HuggingFace Spaces:**
   - Sem suporte a Celery Worker persistente
   - Sem Celery Beat para tarefas agendadas
   - Redis efêmero (perde dados no restart)
   - Limite de recursos para aplicações 24/7

2. **Vantagens do Railway:**
   - Múltiplos serviços independentes (API, Worker, Beat)
   - Redis persistente
   - PostgreSQL nativo
   - Celery Worker + Beat em produção
   - Escalabilidade horizontal
   - Logs centralizados
   - Monitoramento built-in

## Data da Migração

**2025-10-07** - Sistema migrado completamente para Railway

## Arquitetura Anterior (HF)

- 1 dyno: FastAPI + background tasks limitados
- Redis: Upstash (externo)
- DB: In-memory

## Arquitetura Atual (Railway)

- Serviço 1: API (FastAPI)
- Serviço 2: Worker (Celery - 4 processos)
- Serviço 3: Beat (Celery Beat - scheduler)
- Redis: Railway Redis (persistente)
- DB: Supabase PostgreSQL

## Configurações Migradas

[...]
```

**README.md (reescrever completamente):**
- Foco em Railway como plataforma primária
- HuggingFace como legacy/deprecated
- Badge de status do Railway
- Links para documentação organizada

## 🚀 Ordem de Execução

1. ✅ Criar estrutura de diretórios
2. ✅ Mover documentação para docs/
3. ✅ Mover scripts para scripts/
4. ✅ Mover configs para config/
5. ✅ Atualizar .gitignore
6. ✅ Deletar arquivos obsoletos
7. ✅ Consolidar requirements
8. ✅ Criar docs/deployment/migration-hf-to-railway.md
9. ✅ Reescrever README.md (profissional)
10. ✅ Atualizar CHANGELOG.md
11. ✅ Commit final: "refactor: professional repository reorganization"

## ✨ Resultado Final

- Raiz limpa: ~15 arquivos essenciais
- Documentação centralizada em docs/
- Scripts organizados por função
- Configurações separadas por tipo
- README profissional e claro
- Fácil navegação para novos desenvolvedores
