> **⚠️ REPOSITÓRIO ARQUIVADO**: Este projeto foi movido para [NeuralThinkersLab/cidadao.ai](https://github.com/NeuralThinkersLab/cidadao.ai) como parte de um monorepo. Este repositório permanece disponível apenas para referência histórica e citações acadêmicas (TCC/DOI).

---

# Cidadao.AI Backend

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-12-17
**Versão**: 1.0.0 - **Produção**

> **Sistema Multi-Agente de IA** para Análise de Transparência Governamental Brasileira

<!-- Badges de Citação -->
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17911809.svg)](https://doi.org/10.5281/zenodo.17911809)

<!-- Badges de Status -->
[![CI/CD Pipeline](https://github.com/anderson-ufrj/cidadao.ai-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/anderson-ufrj/cidadao.ai-backend/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/anderson-ufrj/cidadao.ai-backend/branch/main/graph/badge.svg)](https://codecov.io/gh/anderson-ufrj/cidadao.ai-backend)
[![Railway Deploy](https://img.shields.io/badge/Railway-Produção-success?logo=railway&logoColor=white)](https://cidadao-api-production.up.railway.app)
[![Uptime](https://img.shields.io/badge/Uptime-99.9%25-brightgreen)](https://cidadao-api-production.up.railway.app/health)
[![API Status](https://img.shields.io/badge/API-Online-success)](https://cidadao-api-production.up.railway.app/docs)

<!-- Badges de Tecnologia -->
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue?logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7+-red?logo=redis&logoColor=white)](https://redis.io)

<!-- Badges de Qualidade -->
[![Code Quality](https://img.shields.io/badge/Qualidade-A+-brightgreen)](.)
[![Type Checked](https://img.shields.io/badge/Tipagem-MyPy-blue)](.)
[![Security](https://img.shields.io/badge/Segurança-Bandit-yellow)](.)
[![Pre-commit](https://img.shields.io/badge/Pre--commit-Ativo-brightgreen)](https://github.com/pre-commit/pre-commit)

<!-- Badges do Projeto -->
[![Agents](https://img.shields.io/badge/Agentes-22_Operacionais-blue)](docs/agents/)
[![Endpoints](https://img.shields.io/badge/Endpoints-323-blue)](docs/api/)
[![Gov APIs](https://img.shields.io/badge/APIs_Gov-30+-green)](docs/api/05-GOVERNMENT-apis-30plus.md)
[![License: MIT](https://img.shields.io/badge/Licença-MIT-yellow.svg)](LICENSE)

**Democratizando o acesso aos dados de transparência governamental brasileira através de 22 agentes de IA especializados com identidades culturais brasileiras.**

---

## Índice / Table of Contents

- [Português (BR)](#português-br)
- [English (US)](#english-us)

---

# Português (BR)

## Status de Produção - V1.0

**Status**: **PRODUÇÃO** (99.9% uptime desde 07/10/2025)
**Plataforma**: Railway (PostgreSQL + Redis gerenciados)

| Métrica | Status | Detalhes |
|---------|--------|----------|
| **Deploy** | Em Produção | [Railway](https://cidadao-api-production.up.railway.app) |
| **Backend** | 100% | Todos os critérios atendidos |
| **Frontend** | 90% | Vercel, chat funcionando |
| **Cobertura de Testes** | 76.29% | 1.514 testes, 97.4% passando |
| **Performance** | Excelente | 0.6s tempo médio de resposta |

---

## Início Rápido

### Pré-requisitos

- Python 3.11+
- PostgreSQL (opcional, usa SQLite por padrão)
- Redis (opcional, usa cache em memória)

### Instalação

```bash
# 1. Clonar repositório
git clone https://github.com/anderson-ufrj/cidadao.ai-backend
cd cidadao.ai-backend

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar ambiente
cp .env.example .env
# Edite .env: Adicione MARITACA_API_KEY ou ANTHROPIC_API_KEY
# Gerar secrets: python scripts/generate_secrets.py

# 4. Executar migrações (opcional)
alembic upgrade head

# 5. Rodar servidor de desenvolvimento
python -m src.api.app
```

### Acessar Documentação

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Welcome**: http://localhost:8000/api/v1/

### Produção

- **API**: https://cidadao-api-production.up.railway.app
- **Health**: https://cidadao-api-production.up.railway.app/health
- **Docs**: https://cidadao-api-production.up.railway.app/docs

---

## Ecossistema Completo

Este é o **Backend API** do ecossistema Cidadão.AI, composto por **4 repositórios integrados**:

| Repositório | Status | Descrição | Links |
|-------------|--------|-----------|-------|
| **Backend** | Produção | API Multi-Agente (FastAPI) | **[Você está aqui]** |
| **Frontend** | Produção | PWA App (Next.js 15) | [Repo](https://github.com/anderson-ufrj/cidadao.ai-frontend) |
| **Hub** | Pronto | Landing Page | [Repo](https://github.com/anderson-ufrj/cidadao.ai-hub) |
| **Models** | Desenvolvimento | ML Models & MLOps | [Repo](https://github.com/anderson-ufrj/cidadao.ai-models) |

---

## Visão Geral

**Cidadão.AI** analisa contratos governamentais brasileiros usando **22 agentes de IA especializados** com identidades culturais brasileiras. O sistema roda 24/7 no Railway com PostgreSQL e Redis, monitorando fontes de dados autonomamente, detectando anomalias e fornecendo insights de transparência.

### Principais Funcionalidades

- **22 Agentes Especializados** - Identidades culturais brasileiras (Zumbi, Anita, Tiradentes, etc.)
- **30+ APIs Governamentais** - Dados federais e estaduais integrados
- **Orquestração Multi-Agente** - Fluxos de investigação coordenados
- **Chat em Tempo Real** - Respostas SSE streaming dos agentes
- **Detecção de Anomalias** - Análise estatística (FFT, Z-score, IQR)
- **Linguagem Natural** - Interface em Português
- **Alta Performance** - 0.6s tempo médio, 367x mais rápido no carregamento de agentes

---

## Sistema de Agentes

### 22 Agentes Operacionais

**Tier 1 - Excelente** (10 agentes - >75% cobertura):
1. **Zumbi dos Palmares** - Detecção de Anomalias (96.32%)
2. **Anita Garibaldi** - Análise de Padrões (94.87%)
3. **Oxóssi** - Caça de Dados (94.44%)
4. **Lampião** - Análise Regional (93.75%)
5. **Ayrton Senna** - Roteamento Semântico (92.31%)
6. **Tiradentes** - Geração de Relatórios (91.67%)
7. **Oscar Niemeyer** - Agregação de Dados (89.47%)
8. **Machado de Assis** - Análise Textual (88.24%)
9. **José Bonifácio** - Análise Legal (87.50%)
10. **Maria Quitéria** - Auditoria de Segurança (86.96%)

**Tier 2 - Quase Completo** (6 agentes):
11. **Abaporu** - Orquestração Mestre (85.71%)
12. **Nanã** - Gerenciamento de Memória (84.62%)
13. **Drummond** - Comunicação (83.33%)
14. **Céuci** - ETL & Preditivo (82.76%)
15. **Obaluaiê** - Detecção de Corrupção (81.25%)
16. **Dandara** - Equidade Social (86.32%)

**Tier 3 - Educacional & Especializado** (6 agentes):
17. **Santos Dumont** - Educação Técnica
18. **Lina Bo Bardi** - Design Frontend
19. **Monteiro Lobato** - Programação para Crianças
20. **Tarsila do Amaral** - Arte & Design para Crianças
21. **Base Kids Agent** - Framework de Segurança Educacional
22. **Céuci ML Models** - Pipelines ML Preditivos

**Documentação**: [docs/agents/](docs/agents/)

---

## Arquitetura do Sistema

```
Consulta do Usuário → Detecção de Intenção → Extração de Entidades → Planejamento
                                                                          ↓
                                                               Federação de Dados
                                                                          ↓
                                                               Grafo de Entidades (NetworkX)
                                                                          ↓
                                                               Agentes de Investigação
                                                                          ↓
                                                               Resultados Consolidados
```

**Componentes Principais**:
- **Orquestrador** - Planejamento e coordenação de execução
- **Pool de Agentes** - 22 agentes com lazy loading (367x mais rápido)
- **Federação de Dados** - Chamadas paralelas com circuit breakers
- **Grafo de Entidades** - Rastreamento de relacionamentos via NetworkX
- **Registro de APIs** - 30+ APIs de transparência catalogadas

---

## Stack Tecnológico

### Core
- **Python 3.11+** - Padrões async/await modernos
- **FastAPI** - Framework async de alta performance
- **Pydantic** - Validação de dados e configurações
- **SQLAlchemy** - ORM com suporte async
- **Alembic** - Migrações de banco de dados

### IA & ML
- **Maritaca AI** - LLM primário (otimizado para Português Brasileiro)
- **Anthropic Claude** - LLM backup com auto-fallback
- **NetworkX** - Análise de grafos para relacionamentos
- **NumPy/SciPy** - Análise estatística

### Dados & Armazenamento
- **PostgreSQL** - Banco de dados principal (Railway gerenciado)
- **Redis** - Cache multi-camada (Railway gerenciado)

### Monitoramento
- **Prometheus** - Coleta de métricas
- **Grafana** - Dashboards e visualização
- **Structlog** - Logging estruturado

### Testes & Qualidade
- **Pytest** - Framework de testes (1.514 testes)
- **Coverage.py** - Cobertura de código (76.29%)
- **Ruff** - Linter Python rápido
- **Black** - Formatador de código
- **MyPy** - Verificação de tipos estática

---

## Performance

| Métrica | Meta | Atual | Status |
|---------|------|-------|--------|
| Resposta API (p95) | <2000ms | ~600ms | 70% melhor |
| Processamento de Agente | <5000ms | ~3200ms | 36% melhor |
| Chat First Token | <500ms | ~380ms | 24% melhor |
| Investigação (6 agentes) | <15000ms | ~12500ms | 17% melhor |
| Import de Agentes | <100ms | 3.81ms | 96% melhor |

**Tempo Médio de Resposta**: 0.6s
**Uptime**: 99.9%
**Cache Hit Rate**: ~95%

---

## APIs Governamentais Integradas

### APIs Federais (8)
1. **IBGE** - Demografia, geografia
2. **DataSUS** - Dados de saúde
3. **INEP** - Estatísticas educacionais
4. **PNCP** - Portal de contratos públicos
5. **Compras.gov** - Licitações federais
6. **Portal da Transparência** - Transparência federal
7. **Banco Central** - Dados econômicos
8. **Minha Receita** - Dados de empresas (CNPJ)

### APIs Estaduais (5)
1. **TCE-CE** - Tribunal de Contas do Ceará
2. **TCE-PE** - Tribunal de Contas de Pernambuco
3. **TCE-MG** - Tribunal de Contas de Minas Gerais
4. **SICONFI** - Finanças municipais
5. **CKAN** - Portais de dados estaduais

---

## Desenvolvimento

### Comandos Principais

```bash
# Testes
make test                # Todos os testes
make test-unit           # Apenas testes unitários
make test-agents         # Testes de agentes
make test-coverage       # Com relatório de cobertura

# Qualidade de Código
make format              # Black + isort + ruff --fix
make lint                # Ruff linter
make type-check          # MyPy modo estrito
make check               # Todas as verificações

# Banco de Dados
make migrate             # Criar migração
make db-upgrade          # Aplicar migrações
make db-downgrade        # Reverter migração

# Monitoramento
make monitoring-up       # Iniciar Grafana + Prometheus
```

**Guia completo**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Roadmap

### V1.0 - Lançamento (Nov 2025) - CONCLUÍDO

- [x] 22 agentes operacionais
- [x] Testes E2E passando
- [x] Deploy em produção
- [x] Integração frontend
- [x] Documentação completa

### V1.1 - Melhorias (Dez 2025)

- [ ] OAuth login social
- [ ] WebSocket atualizações em tempo real
- [ ] Otimização de performance
- [ ] Alertas Grafana em produção
- [ ] Testes de carga

### V2.0 - Funcionalidades Avançadas (Q1 2026)

- [ ] Modelos ML customizados
- [ ] Analytics preditivo
- [ ] Visualizações avançadas
- [ ] Multi-tenancy
- [ ] Funcionalidades enterprise

**Roadmap completo**: [docs/project/ROADMAP_OFFICIAL_2025.md](docs/project/ROADMAP_OFFICIAL_2025.md)

---

## Contribuindo

Contribuições são bem-vindas! Veja nosso [Guia de Contribuição](CONTRIBUTING.md).

### Passos Rápidos

1. Fork o repositório
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Faça suas alterações
4. Execute testes (`make test`)
5. Execute verificações (`make check`)
6. Commit (`git commit -m 'feat: adiciona nova funcionalidade'`)
7. Push (`git push origin feature/nova-funcionalidade`)
8. Abra um Pull Request

---

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## Agradecimentos

**Ícones Culturais Brasileiros** - Inspiração para identidades dos agentes:
- Zumbi dos Palmares - Líder da liberdade
- Anita Garibaldi - Heroína revolucionária
- Tiradentes - Mártir da independência
- Ayrton Senna - Campeão de excelência
- E mais 12 brasileiros incríveis

**Comunidade Open Source** - FastAPI, Pydantic, SQLAlchemy e muitos outros.

**Dados Governamentais** - Governo brasileiro pelas iniciativas de dados abertos.

---

## Contato & Suporte

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil

**Links**:
- **GitHub**: https://github.com/anderson-ufrj/cidadao.ai-backend
- **Issues**: https://github.com/anderson-ufrj/cidadao.ai-backend/issues
- **Discussions**: https://github.com/anderson-ufrj/cidadao.ai-backend/discussions

**Produção**:
- **API**: https://cidadao-api-production.up.railway.app
- **Docs**: https://cidadao-api-production.up.railway.app/docs
- **Health**: https://cidadao-api-production.up.railway.app/health

---

## Estatísticas do Projeto

| Categoria | Métrica | Valor |
|-----------|---------|-------|
| **Código** | Linhas de código | ~133.783 |
| | Código de testes | ~49.888 linhas |
| | Total de arquivos | 1.082 |
| | Commits | 1.229+ |
| **Desenvolvimento** | Início | 13/08/2025 |
| | Produção | 07/10/2025 |
| | Duração | ~3 meses |
| **Qualidade** | Cobertura de testes | 76.29% |
| | Taxa de aprovação | 97.4% |
| | Uptime | 99.9% |

---

**Feito com amor em Minas Gerais, Brasil**

**Democratizando a Transparência Governamental através da IA**

---

# English (US)

## Production Status - V1.0

**Status**: **PRODUCTION** (99.9% uptime since 07/10/2025)
**Platform**: Railway (managed PostgreSQL + Redis)

| Metric | Status | Details |
|--------|--------|---------|
| **Deployment** | Live | [Railway](https://cidadao-api-production.up.railway.app) |
| **Backend** | 100% | All criteria met |
| **Frontend** | 90% | Vercel, chat working |
| **Test Coverage** | 76.29% | 1,514 tests, 97.4% passing |
| **Performance** | Excellent | 0.6s avg response time |

---

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (optional, uses SQLite by default)
- Redis (optional, falls back to memory cache)

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

- **API**: https://cidadao-api-production.up.railway.app
- **Health**: https://cidadao-api-production.up.railway.app/health
- **Docs**: https://cidadao-api-production.up.railway.app/docs

---

## Complete Ecosystem

This is the **Backend API** of the Cidadão.AI ecosystem, composed of **4 integrated repositories**:

| Repository | Status | Description | Links |
|------------|--------|-------------|-------|
| **Backend** | Production | Multi-Agent API (FastAPI) | **[You are here]** |
| **Frontend** | Production | PWA App (Next.js 15) | [Repo](https://github.com/anderson-ufrj/cidadao.ai-frontend) |
| **Hub** | Ready | Landing Page | [Repo](https://github.com/anderson-ufrj/cidadao.ai-hub) |
| **Models** | Development | ML Models & MLOps | [Repo](https://github.com/anderson-ufrj/cidadao.ai-models) |

---

## Overview

**Cidadão.AI** analyzes Brazilian government contracts using **22 specialized AI agents** with Brazilian cultural identities. The system runs 24/7 on Railway with PostgreSQL and Redis, autonomously monitoring data sources, detecting anomalies, and providing transparency insights.

### Key Features

- **22 Specialized Agents** - Brazilian cultural identities (Zumbi, Anita, Tiradentes, etc.)
- **30+ Government APIs** - Federal and state data integrated
- **Multi-Agent Orchestration** - Coordinated investigation workflows
- **Real-Time Chat** - SSE streaming responses from agents
- **Anomaly Detection** - Statistical analysis (FFT, Z-score, IQR)
- **Natural Language** - Portuguese-first interface
- **High Performance** - 0.6s avg response, 367x faster agent loading

---

## Agent System

### 22 Operational Agents

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

**Tier 2 - Near-Complete** (6 agents):
11. **Abaporu** - Master Orchestration (85.71%)
12. **Nanã** - Memory Management (84.62%)
13. **Drummond** - Communication (83.33%)
14. **Céuci** - ETL & Predictive (82.76%)
15. **Obaluaiê** - Corruption Detection (81.25%)
16. **Dandara** - Social Equity (86.32%)

**Tier 3 - Educational & Specialized** (6 agents):
17. **Santos Dumont** - Technical Education
18. **Lina Bo Bardi** - Frontend Design
19. **Monteiro Lobato** - Kids Programming
20. **Tarsila do Amaral** - Kids Art & Design
21. **Base Kids Agent** - Educational Safety Framework
22. **Céuci ML Models** - Predictive ML Pipelines

**Documentation**: [docs/agents/](docs/agents/)

---

## System Architecture

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
- **Agent Pool** - 22 agents with lazy loading (367x faster)
- **Data Federation** - Parallel API calls with circuit breakers
- **Entity Graph** - NetworkX-based relationship tracking
- **API Registry** - 30+ transparency APIs catalogued

---

## Technology Stack

### Core
- **Python 3.11+** - Modern async/await patterns
- **FastAPI** - High-performance async framework
- **Pydantic** - Data validation and settings
- **SQLAlchemy** - ORM with async support
- **Alembic** - Database migrations

### AI & ML
- **Maritaca AI** - Primary LLM (Brazilian Portuguese optimized)
- **Anthropic Claude** - Backup LLM with auto-fallback
- **NetworkX** - Graph analysis for relationships
- **NumPy/SciPy** - Statistical analysis

### Data & Storage
- **PostgreSQL** - Primary database (Railway managed)
- **Redis** - Multi-layer caching (Railway managed)

### Monitoring
- **Prometheus** - Metrics collection
- **Grafana** - Dashboards and visualization
- **Structlog** - Structured logging

### Testing & Quality
- **Pytest** - Test framework (1,514 tests)
- **Coverage.py** - Code coverage (76.29%)
- **Ruff** - Fast Python linter
- **Black** - Code formatter
- **MyPy** - Static type checking

---

## Performance

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| API Response (p95) | <2000ms | ~600ms | 70% better |
| Agent Processing | <5000ms | ~3200ms | 36% better |
| Chat First Token | <500ms | ~380ms | 24% better |
| Investigation (6 agents) | <15000ms | ~12500ms | 17% better |
| Agent Import Time | <100ms | 3.81ms | 96% better |

**Average Response Time**: 0.6s
**Uptime**: 99.9%
**Cache Hit Rate**: ~95%

---

## Government APIs Integrated

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

---

## Development

### Main Commands

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

**Full guide**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Roadmap

### V1.0 - Launch (Nov 2025) - COMPLETED

- [x] 22 agents operational
- [x] E2E tests passing
- [x] Production deployment
- [x] Frontend integration
- [x] Documentation complete

### V1.1 - Enhancements (Dec 2025)

- [ ] OAuth social login
- [ ] WebSocket real-time updates
- [ ] Performance optimization
- [ ] Grafana production alerts
- [ ] Load testing

### V2.0 - Advanced Features (Q1 2026)

- [ ] Custom ML models
- [ ] Predictive analytics
- [ ] Advanced visualizations
- [ ] Multi-tenancy
- [ ] Enterprise features

**Full roadmap**: [docs/project/ROADMAP_OFFICIAL_2025.md](docs/project/ROADMAP_OFFICIAL_2025.md)

---

## Contributing

Contributions are welcome! See our [Contributing Guide](CONTRIBUTING.md).

### Quick Steps

1. Fork the repository
2. Create a branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`make test`)
5. Run quality checks (`make check`)
6. Commit (`git commit -m 'feat: add amazing feature'`)
7. Push (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

**Brazilian Cultural Icons** - Inspiration for agent identities:
- Zumbi dos Palmares - Leader of freedom
- Anita Garibaldi - Revolutionary hero
- Tiradentes - Martyr of independence
- Ayrton Senna - Champion of excellence
- And 12 more incredible Brazilians

**Open Source Community** - FastAPI, Pydantic, SQLAlchemy, and many more.

**Government Data** - Brazilian government for open data initiatives.

---

## Contact & Support

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

## Project Statistics

| Category | Metric | Value |
|----------|--------|-------|
| **Code** | Lines of code | ~133,783 |
| | Test code | ~49,888 lines |
| | Total files | 1,082 |
| | Commits | 1,079+ |
| **Development** | Started | Aug 13, 2025 |
| | Production | Oct 7, 2025 |
| | Duration | ~3 months |
| **Quality** | Test coverage | 76.29% |
| | Pass rate | 97.4% |
| | Uptime | 99.9% |

---

**Made with love in Minas Gerais, Brasil**

**Democratizing Government Transparency Through AI**

---

*Last Updated: 2025-12-17 - Version 1.0.0 Production*
