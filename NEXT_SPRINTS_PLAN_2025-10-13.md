# 🚀 Próximos Sprints - Plano de Melhorias

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Data**: 2025-10-13 (Continuação do SPRINT_PLAN_2025-10-13.md)
**Status**: 📋 ROADMAP DE MELHORIAS

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Status Atual do Sistema](#status-atual-do-sistema)
3. [Priorização Estratégica](#priorização-estratégica)
4. [SPRINT 6: Completar Análise Layer (Lampião + Oscar)](#sprint-6-completar-análise-layer)
5. [SPRINT 7: Infraestrutura Crítica (PostgreSQL + CI/CD)](#sprint-7-infraestrutura-crítica)
6. [SPRINT 8: Frontend Testing Suite](#sprint-8-frontend-testing-suite)
7. [SPRINT 9: Dandara - Social Justice Agent](#sprint-9-dandara---social-justice-agent)
8. [SPRINT 10: Obaluaie - Corruption Detector](#sprint-10-obaluaie---corruption-detector)
9. [SPRINT 11: Ceuci - Predictive AI](#sprint-11-ceuci---predictive-ai)
10. [Melhorias Adicionais](#melhorias-adicionais)

---

## 🎯 Visão Geral

### Objetivo Estratégico

Evoluir o Cidadão.AI de uma **MVP funcional** para uma **plataforma enterprise-ready** com:
- 17 agentes 100% operacionais
- Infraestrutura robusta e escalável
- Cobertura de testes completa (backend + frontend)
- Dados reais integrados
- CI/CD automatizado

### Contexto Pós-Sprint 5

**✅ Completado (Sprints 1-5)**:
- Federal APIs funcionais e monitoradas
- REST endpoints documentados
- Prometheus + Grafana configurado
- Alertas proativos configurados
- Warm-up job mantendo métricas

**🎯 Próximos Desafios**:
- 5 agentes parcialmente implementados (29% pendentes)
- Infraestrutura in-memory (precisa PostgreSQL)
- Frontend sem testes automatizados (0% coverage)
- Portal da Transparência 78% bloqueado
- CI/CD manual

---

## 📊 Status Atual do Sistema

### Agentes (17 total)

#### ✅ Totalmente Operacionais (12 agentes - 71%)

**Camada de Orquestração**:
- ✅ Deodoro (Base Architecture) - 100%
- ✅ Abaporu (Master Orchestrator) - 100%
- ✅ Senna (Agent Router) - 100%

**Camada de Análise**:
- ✅ Zumbi (Anomaly Detective) - 100%
- ✅ Anita (Data Analyst) - 100%
- ✅ Oxóssi (Fraud Hunter) - 100%

**Camada de Comunicação**:
- ✅ Drummond (Communicator) - 100%
- ✅ Tiradentes (Report Writer) - 100%

**Camada de Governança**:
- ✅ Maria Quitéria (Security Guardian) - 100%
- ✅ Bonifácio (Legal Expert) - 100%

**Camada de Suporte**:
- ✅ Nanã (Memory Manager) - 100%
- ✅ Machado (Narrative Analyst) - 100%

#### 🔶 Parcialmente Implementados (5 agentes - 29%)

| Agente | Status | O Que Falta | Prioridade |
|--------|--------|-------------|------------|
| 🟡 Lampião (Regional Analyst) | **95%** | Testes finais, integração | 🔥 Crítica |
| 🟡 Oscar Niemeyer (Visualizer) | **40%** | Network graphs, geo maps | 🔥 Crítica |
| 🟡 Dandara (Social Justice) | **30%** | Integração dados reais | ⚡ Alta |
| 🔴 Obaluaie (Corruption Detector) | **15%** | Lei de Benford, graph analysis | 🌟 Média |
| 🔴 Ceuci (Predictive AI) | **10%** | Treinar modelos ML | 🌟 Média |

### Infraestrutura

| Componente | Status | Notas |
|-----------|--------|-------|
| **Database** | ⚠️ In-memory | PostgreSQL pronto mas não integrado |
| **Cache** | ⚠️ In-memory | Redis opcional |
| **CI/CD** | ❌ Manual | GitHub Actions não configurado |
| **Frontend Tests** | ❌ 0% | Apenas scripts manuais |
| **Backend Tests** | ✅ 80%+ | 197 testes, cobertura alta |
| **Monitoring** | ✅ Configurado | Prometheus + Grafana |
| **Portal APIs** | ⚠️ 22% | 78% endpoints retornam 403 |

### Qualidade de Código

| Métrica | Backend | Frontend |
|---------|---------|----------|
| **Test Coverage** | 80%+ ✅ | 0% ❌ |
| **CI/CD** | Manual ⚠️ | Manual ⚠️ |
| **Linting** | Ruff ✅ | ESLint ✅ |
| **Type Checking** | MyPy ✅ | TypeScript ✅ |
| **Pre-commit Hooks** | Configured ✅ | Missing ❌ |

---

## 🎯 Priorização Estratégica

### Critérios de Priorização

1. **Impacto no Usuário**: Visibilidade e valor para o usuário final
2. **Bloqueador Técnico**: Impede outras funcionalidades
3. **Debt Técnico**: Risco de acumulação de problemas
4. **Alinhamento Missão**: Relevância para objetivos do projeto

### Matriz de Priorização

```
┌─────────────────────────────────────────────┐
│ Alto Impacto + Alta Urgência               │
│ - Sprint 6: Lampião + Oscar (Quick Wins)   │
│ - Sprint 7: PostgreSQL + CI/CD              │
│ - Sprint 8: Frontend Testing                │
└─────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────┐
│ Alto Impacto + Média Urgência              │
│ - Sprint 9: Dandara (Missão-crítico)       │
│ - Network Graph Integration                 │
│ - WebSocket Completion                      │
└─────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────┐
│ Médio Impacto + Baixa Urgência             │
│ - Sprint 10: Obaluaie (Avançado)           │
│ - Sprint 11: Ceuci (ML Models)             │
│ - A/B Testing Documentation                 │
└─────────────────────────────────────────────┘
```

---

## 🎯 SPRINT 6: Completar Análise Layer (Lampião + Oscar)

**Duração Estimada**: 1 semana (5 dias úteis)
**Prioridade**: 🔥 Crítica
**Objetivo**: Completar a camada de análise e habilitar visualizações avançadas

### Por Que Fazer Agora?

1. **Quick Wins**: Lampião está 95% pronto
2. **Alto Valor**: Visualizações são altamente demandadas
3. **Integração Recente**: Network graph API acabou de ser implementado
4. **Completa Layer**: Finaliza camada de análise inteira

### Estrutura do Sprint

```
Sprint 6 (1 semana)
├── Fase 1: Lampião 95% → 100% (2 dias)
├── Fase 2: Oscar Niemeyer 40% → 80% (2 dias)
└── Fase 3: Integração e Testes (1 dia)
```

---

### SPRINT 6.1: Finalizar Lampião (Regional Analyst)

**Duração**: 2 dias
**Status Atual**: 95% implementado

#### O Que Já Existe
- ✅ Spatial autocorrelation (Moran's I, LISA)
- ✅ Hotspot analysis (Getis-Ord G*)
- ✅ Geographic disparities detection
- ✅ Regional inequality metrics (Gini regional, Williamson)

#### O Que Falta

**Dia 1: Testes e Validação**
- [ ] Criar testes unitários completos
- [ ] Testar com dados reais de IBGE
- [ ] Validar cálculos estatísticos (comparar com R/GeoDa)
- [ ] Adicionar casos de teste edge cases

**Dia 2: Integração e Documentação**
- [ ] Integrar com Abaporu (orchestrator)
- [ ] Adicionar métricas Prometheus
- [ ] Documentar em docs/agents/lampiao.md
- [ ] Criar exemplos de uso no README

#### Checklist de Implementação

```bash
# Passo 1: Verificar estado atual
cd src/agents
grep -n "TODO\|FIXME" lampiao.py

# Passo 2: Rodar testes existentes
pytest tests/unit/agents/test_lampiao.py -v --cov=src.agents.lampiao

# Passo 3: Adicionar testes faltantes
# - Test spatial autocorrelation com datasets sintéticos
# - Test hotspot detection com pontos conhecidos
# - Test regional inequality metrics com valores validados

# Passo 4: Integração final
# - Registrar no AgentPool
# - Adicionar ao Senna router
# - Testar via chat API
```

#### Arquivos a Modificar
```
src/agents/lampiao.py                    # Últimos ajustes
tests/unit/agents/test_lampiao.py       # Testes completos
docs/agents/lampiao.md                   # Documentação
README.md                                 # Adicionar exemplos
```

#### Validação de Sucesso
- [ ] Coverage de testes > 90%
- [ ] Todos os testes passando
- [ ] Documentação completa
- [ ] Exemplos funcionando
- [ ] Integrado com outros agentes

---

### SPRINT 6.2: Enhançar Oscar Niemeyer (Visualizer)

**Duração**: 2 dias
**Status Atual**: 40% implementado

#### O Que Já Existe
- ✅ Framework base de visualização
- ✅ Integração com Plotly
- ✅ Charts básicos (line, bar, scatter)

#### O Que Implementar

**Dia 1: Network Graphs (Fraud Relationships)**
- [ ] Integrar com Network Graph API recém-implementada
- [ ] Visualizar relações entre entidades suspeitas
- [ ] Detectar clusters de fraude
- [ ] Interactive exploration (zoom, pan, filtering)

**Dia 2: Geographic Maps**
- [ ] Mapas choropleth (estados/municípios)
- [ ] Bubble maps para valores
- [ ] Heatmaps de anomalias
- [ ] Integração com dados IBGE

#### Implementação Detalhada

**Network Graphs**:
```python
async def create_fraud_network(
    self,
    entities: List[Dict],
    relationships: List[Dict],
    threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Create interactive fraud relationship network.

    Args:
        entities: List of entities (suppliers, contracts, etc.)
        relationships: Connections between entities
        threshold: Minimum relationship strength to display

    Returns:
        Plotly network graph with interactive features
    """
    import networkx as nx
    import plotly.graph_objects as go

    # Build graph
    G = nx.Graph()

    # Add nodes (entities)
    for entity in entities:
        G.add_node(
            entity["id"],
            label=entity["name"],
            suspicion_score=entity.get("score", 0)
        )

    # Add edges (relationships)
    for rel in relationships:
        if rel["strength"] >= threshold:
            G.add_edge(
                rel["source"],
                rel["target"],
                weight=rel["strength"]
            )

    # Detect communities (fraud rings)
    communities = nx.community.louvain_communities(G)

    # Create visualization
    pos = nx.spring_layout(G, k=0.5, iterations=50)

    # Build Plotly figure
    edge_trace = go.Scatter(
        x=[], y=[],
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # Add edges
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

    # Add nodes
    node_trace = go.Scatter(
        x=[], y=[],
        mode='markers+text',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlOrRd',
            size=10,
            colorbar=dict(
                thickness=15,
                title='Suspicion Score',
                xanchor='left',
                titleside='right'
            )
        )
    )

    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])

    # Add suspicion scores as color
    node_suspicion = [G.nodes[node]['suspicion_score'] for node in G.nodes()]
    node_trace.marker.color = node_suspicion

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title='Fraud Relationship Network',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False)
        )
    )

    return {
        "type": "network_graph",
        "fig": fig,
        "communities": len(communities),
        "nodes": G.number_of_nodes(),
        "edges": G.number_of_edges()
    }
```

**Geographic Maps**:
```python
async def create_choropleth_map(
    self,
    data: List[Dict],
    geojson_url: str = None,
    color_column: str = "value",
    location_column: str = "state_code"
) -> Dict[str, Any]:
    """
    Create choropleth map for Brazilian states/municipalities.

    Args:
        data: Data with geographic info
        geojson_url: URL to GeoJSON boundaries
        color_column: Column to use for coloring
        location_column: Column with location codes

    Returns:
        Plotly choropleth map
    """
    import plotly.express as px

    # Default to Brazilian states GeoJSON
    if not geojson_url:
        geojson_url = (
            "https://raw.githubusercontent.com/codeforamerica/"
            "click_that_hood/master/public/data/brazil-states.geojson"
        )

    # Load GeoJSON
    import requests
    geojson = requests.get(geojson_url).json()

    # Create choropleth
    fig = px.choropleth(
        data,
        geojson=geojson,
        locations=location_column,
        color=color_column,
        color_continuous_scale="Reds",
        scope="south america",
        labels={color_column: 'Value'},
        hover_data=data.keys()
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig.update_layout(
        title_text='Geographic Distribution',
        geo_scope='south america',
    )

    return {
        "type": "choropleth",
        "fig": fig,
        "data_points": len(data)
    }
```

#### Arquivos a Modificar
```
src/agents/oscar_niemeyer.py                 # Network + Geo maps
tests/unit/agents/test_oscar_niemeyer.py    # Testes
docs/agents/oscar_niemeyer.md                # Documentação
```

#### Validação de Sucesso
- [ ] Network graphs funcionando
- [ ] Mapas geográficos renderizando
- [ ] Integração com Network Graph API
- [ ] Testes passando
- [ ] Documentação com exemplos visuais

---

### SPRINT 6.3: Integração e Testes

**Duração**: 1 dia

#### Checklist Final
- [ ] Ambos agentes integrados com Abaporu
- [ ] Testes end-to-end funcionando
- [ ] Performance benchmarks
- [ ] Documentação completa
- [ ] Exemplos no README

#### Comandos de Validação
```bash
# 1. Rodar todos os testes da camada de análise
pytest tests/unit/agents/ -k "test_zumbi or test_anita or test_oxossi or test_lampiao or test_oscar" -v

# 2. Testar integração via chat
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analise padrões regionais de contratos de saúde e crie um mapa",
    "session_id": "test_session"
  }'

# 3. Verificar métricas
curl http://localhost:8000/health/metrics | grep agent_tasks

# 4. Coverage final
pytest --cov=src.agents --cov-report=html
```

#### Commit Final
```bash
git add src/agents/lampiao.py src/agents/oscar_niemeyer.py
git add tests/unit/agents/
git add docs/agents/

git commit -m "feat(agents): complete Analysis Layer with Lampião and Oscar Niemeyer

Lampião (Regional Analyst) - 95% → 100%:
- Add comprehensive unit tests with real IBGE data
- Validate statistical calculations (Moran's I, LISA, Getis-Ord)
- Complete integration with multi-agent orchestration
- Add Prometheus metrics for spatial analysis
- Document usage examples and API

Oscar Niemeyer (Visualizer) - 40% → 80%:
- Implement fraud network graphs with NetworkX + Plotly
- Add geographic choropleth maps for Brazil
- Integrate with recently implemented Network Graph API
- Create interactive visualizations (zoom, pan, filter)
- Support heatmaps for anomaly visualization

Integration:
- Both agents fully integrated with Abaporu orchestrator
- Registered in AgentPool and Senna router
- End-to-end tests via chat API
- Performance benchmarks (Lampião: 1.5s avg, Oscar: 2.2s avg)

Testing:
- Analysis Layer coverage: 85%+
- All 5 analysis agents now 100% operational
- Visual regression tests for charts

Documentation:
- Updated docs/agents/ for both agents
- Added visual examples to README
- Created usage tutorials

Completes Analysis Layer: Zumbi, Anita, Oxóssi, Lampião, Oscar ✅"
```

---

## 🏗️ SPRINT 7: Infraestrutura Crítica (PostgreSQL + CI/CD)

**Duração Estimada**: 1 semana
**Prioridade**: 🔥 Crítica
**Objetivo**: Estabelecer infraestrutura sólida para produção

### Por Que Fazer Agora?

1. **Bloqueador de Escala**: In-memory não escala
2. **Perda de Dados**: Dados perdidos a cada restart
3. **CI/CD Manual**: Risco de bugs em produção
4. **Debt Técnico**: Quanto mais tarde, mais custoso

### Estrutura do Sprint

```
Sprint 7 (1 semana)
├── Fase 1: PostgreSQL Integration (3 dias)
├── Fase 2: CI/CD com GitHub Actions (2 dias)
└── Fase 3: Validação e Deploy (1 dia)
```

---

### SPRINT 7.1: PostgreSQL Integration

**Duração**: 3 dias
**Status**: Database models prontos, falta integração

#### Dia 1: Alembic Migrations

**O Que Existe**:
- ✅ Models SQLAlchemy definidos
- ✅ Alembic configurado
- ⚠️ Migrations não testadas

**Checklist**:
- [ ] Revisar todos os models em `src/database/models.py`
- [ ] Criar migration inicial: `alembic revision --autogenerate -m "initial schema"`
- [ ] Aplicar migration local: `alembic upgrade head`
- [ ] Verificar schema no PostgreSQL
- [ ] Criar seeds para dados de teste

**Comandos**:
```bash
# 1. Setup PostgreSQL local
docker run -d \
  --name cidadao-postgres \
  -e POSTGRES_DB=cidadao_ai \
  -e POSTGRES_USER=cidadao \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  postgres:15

# 2. Configurar .env
DATABASE_URL=postgresql://cidadao:secure_password@localhost:5432/cidadao_ai

# 3. Gerar migrations
alembic revision --autogenerate -m "initial_schema"

# 4. Aplicar migrations
alembic upgrade head

# 5. Verificar tabelas
psql -h localhost -U cidadao -d cidadao_ai -c "\dt"
```

#### Dia 2: Adaptar Services para PostgreSQL

**Services a Atualizar**:
- [ ] `src/services/agent_pool.py` - Persistir agent state
- [ ] `src/services/chat_service.py` - Salvar histórico de chat
- [ ] `src/api/routes/investigations.py` - CRUD completo
- [ ] `src/memory/conversational.py` - Persistir conversas

**Pattern de Migração**:
```python
# ANTES (in-memory):
class InMemoryStore:
    def __init__(self):
        self._data = {}

    async def save(self, key, value):
        self._data[key] = value

# DEPOIS (PostgreSQL):
from src.database.session import get_db_session
from src.database.models import Investigation

class DatabaseStore:
    async def save(self, investigation: Investigation):
        async with get_db_session() as session:
            session.add(investigation)
            await session.commit()
            return investigation

    async def get(self, investigation_id: str):
        async with get_db_session() as session:
            result = await session.execute(
                select(Investigation).where(
                    Investigation.id == investigation_id
                )
            )
            return result.scalar_one_or_none()
```

#### Dia 3: Testes e Performance

**Checklist**:
- [ ] Atualizar testes para usar PostgreSQL de teste
- [ ] Adicionar fixtures para database setup
- [ ] Benchmark: comparar performance in-memory vs PostgreSQL
- [ ] Adicionar connection pooling
- [ ] Configurar indexes para queries frequentes

**Test Setup**:
```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from src.database.base import Base

@pytest.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine(
        "postgresql+asyncpg://cidadao:test@localhost:5433/test_db"
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

**Validação**:
```bash
# 1. Rodar testes com PostgreSQL
pytest tests/ -v --db=postgresql

# 2. Benchmark
python scripts/benchmark/db_performance.py

# 3. Verificar migrations
alembic current
alembic history

# 4. Test rollback
alembic downgrade -1
alembic upgrade head
```

---

### SPRINT 7.2: CI/CD com GitHub Actions

**Duração**: 2 dias

#### Dia 1: GitHub Actions Workflows

**Workflows a Criar**:
1. **CI Pipeline** (`ci.yml`): Testes + Linting
2. **CD Pipeline** (`deploy.yml`): Deploy automático
3. **Security Scan** (`security.yml`): Bandit + Dependabot

**ci.yml**:
```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run linting
        run: |
          black --check .
          isort --check .
          ruff check .
          mypy src/

      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
        run: |
          pytest tests/ -v --cov=src --cov-report=xml --cov-report=html

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          fail_ci_if_error: true

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Bandit
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json

      - name: Run Safety
        run: |
          pip install safety
          safety check --json
```

**deploy.yml** (HuggingFace):
```yaml
name: Deploy to HuggingFace

on:
  push:
    branches: [main]
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to HuggingFace Spaces
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: |
          git remote add hf https://huggingface.co/spaces/neural-thinker/cidadao.ai-backend
          git push hf main --force
```

#### Dia 2: Branch Protection + Pre-commit

**Branch Protection Rules**:
- [ ] Require pull request reviews (min 1)
- [ ] Require status checks to pass
- [ ] Require branches to be up to date
- [ ] Require conversation resolution
- [ ] Dismiss stale reviews on new pushes

**Pre-commit CI**:
```yaml
# .github/workflows/pre-commit.yml
name: Pre-commit

on:
  pull_request:

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - uses: pre-commit/action@v3.0.0
```

**Documentação**:
```bash
git add .github/workflows/
git add docs/development/ci-cd.md

git commit -m "ci: add GitHub Actions CI/CD pipelines

Configure comprehensive CI/CD automation:

CI Pipeline (ci.yml):
- Automated testing on push/PR
- Linting with black, isort, ruff, mypy
- Test coverage reporting to Codecov
- PostgreSQL and Redis services for integration tests
- Python 3.11 with dependency caching

CD Pipeline (deploy.yml):
- Automatic deployment to HuggingFace Spaces on main branch
- Tag-based releases (v*)
- Secure token management via GitHub Secrets

Security Pipeline (security.yml):
- Bandit security scanner
- Safety dependency vulnerability checker
- Automated security reports

Branch Protection:
- Require PR reviews before merge
- Require all CI checks to pass
- Auto-dismiss stale reviews
- Require conversation resolution

Benefits:
- Catch bugs before production
- Ensure code quality standards
- Automated security scanning
- Zero-downtime deployments
- Full test coverage enforcement"
```

---

### SPRINT 7.3: Validação e Deploy

**Duração**: 1 dia

**Checklist Final**:
- [ ] CI pipeline passando em todas as branches
- [ ] PostgreSQL funcionando local e produção
- [ ] Migrations aplicadas com sucesso
- [ ] Performance benchmarks aceitáveis
- [ ] Documentação de deploy atualizada

**Comandos de Validação**:
```bash
# 1. Testar CI localmente com act
act -j test

# 2. Verificar PostgreSQL produção
psql $DATABASE_URL -c "SELECT version();"

# 3. Aplicar migrations em staging
alembic --name staging upgrade head

# 4. Load test
locust -f tests/load/locustfile.py --headless -u 100 -r 10 -t 5m

# 5. Deploy
git push origin main  # Triggers CI/CD
```

---

## 🧪 SPRINT 8: Frontend Testing Suite

**Duração Estimada**: 1 semana
**Prioridade**: ⚡ Alta
**Objetivo**: Estabelecer cobertura de testes no frontend (0% → 60%+)

### Por Que Fazer Agora?

1. **0% Coverage**: Frontend totalmente sem testes
2. **Debt Acumulando**: Cada feature sem teste aumenta risco
3. **Backend 80%**: Manter paridade de qualidade
4. **CI/CD Pronto**: Pode ser integrado ao pipeline

### Estrutura do Sprint

```
Sprint 8 (1 semana)
├── Fase 1: Setup Testing Infrastructure (1 dia)
├── Fase 2: Component Tests (2 dias)
├── Fase 3: Integration Tests (2 dias)
└── Fase 4: CI Integration (1 dia)
```

---

### SPRINT 8.1: Setup Testing Infrastructure

**Duração**: 1 dia

#### Tools Stack
- **Vitest**: Test runner (faster than Jest for Vite projects)
- **React Testing Library**: Component testing
- **MSW** (Mock Service Worker): API mocking
- **Playwright**: E2E tests

#### Setup Checklist
- [ ] Install dependencies
- [ ] Configure Vitest
- [ ] Setup React Testing Library
- [ ] Configure MSW for API mocking
- [ ] Create test utilities
- [ ] Setup coverage reporting

**Installation**:
```bash
cd cidadao.ai-frontend

npm install -D vitest @vitest/ui @testing-library/react \
  @testing-library/jest-dom @testing-library/user-event \
  msw happy-dom
```

**vitest.config.ts**:
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'happy-dom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData'
      ],
      statements: 60,
      branches: 60,
      functions: 60,
      lines: 60
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
});
```

**tests/setup.ts**:
```typescript
import '@testing-library/jest-dom';
import { afterAll, afterEach, beforeAll } from 'vitest';
import { setupServer } from 'msw/node';
import { handlers } from './mocks/handlers';

// Setup MSW server
export const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

---

### SPRINT 8.2: Component Tests

**Duração**: 2 dias

#### Componentes Prioritários

**Dia 1: Core Components**
- [ ] `Button.test.tsx`
- [ ] `Card.test.tsx`
- [ ] `Modal.test.tsx`
- [ ] `Form.test.tsx`

**Dia 2: Domain Components**
- [ ] `AgentCard.test.tsx`
- [ ] `ChatMessage.test.tsx`
- [ ] `InvestigationCard.test.tsx`
- [ ] `ContractList.test.tsx`

#### Exemplo de Test

**src/components/AgentCard.test.tsx**:
```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { AgentCard } from './AgentCard';

describe('AgentCard', () => {
  const mockAgent = {
    id: 'zumbi',
    name: 'Zumbi dos Palmares',
    role: 'Anomaly Detective',
    status: 'idle',
    avatar: '/agents/zumbi.png'
  };

  it('renders agent information', () => {
    render(<AgentCard agent={mockAgent} />);

    expect(screen.getByText('Zumbi dos Palmares')).toBeInTheDocument();
    expect(screen.getByText('Anomaly Detective')).toBeInTheDocument();
  });

  it('shows status indicator', () => {
    render(<AgentCard agent={mockAgent} />);

    const statusBadge = screen.getByTestId('agent-status');
    expect(statusBadge).toHaveTextContent('idle');
  });

  it('calls onSelect when clicked', () => {
    const handleSelect = vi.fn();
    render(<AgentCard agent={mockAgent} onSelect={handleSelect} />);

    const card = screen.getByTestId('agent-card');
    fireEvent.click(card);

    expect(handleSelect).toHaveBeenCalledWith('zumbi');
  });

  it('displays avatar image', () => {
    render(<AgentCard agent={mockAgent} />);

    const avatar = screen.getByAltText('Zumbi dos Palmares');
    expect(avatar).toHaveAttribute('src', '/agents/zumbi.png');
  });
});
```

---

### SPRINT 8.3: Integration Tests

**Duração**: 2 dias

#### Fluxos Críticos

**Dia 1: Chat Flow**
- [ ] Send message to agent
- [ ] Receive streaming response
- [ ] Display chat history
- [ ] Error handling

**Dia 2: Investigation Flow**
- [ ] Create investigation
- [ ] View investigation details
- [ ] Download report
- [ ] Share investigation

**tests/integration/chat-flow.test.tsx**:
```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ChatPage } from '@/pages/chat';
import { server } from '../setup';
import { rest } from 'msw';

describe('Chat Flow Integration', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    // Setup API mocks
    server.use(
      rest.post('/api/v1/chat/send', (req, res, ctx) => {
        return res(
          ctx.json({
            message: 'Olá! Sou o Zumbi dos Palmares.',
            agent: 'zumbi',
            session_id: 'test-session'
          })
        );
      })
    );
  });

  it('complete chat interaction', async () => {
    render(<ChatPage />);

    // 1. User types message
    const input = screen.getByPlaceholderText('Digite sua mensagem...');
    await user.type(input, 'Analise contratos de saúde');

    // 2. User sends message
    const sendButton = screen.getByRole('button', { name: /enviar/i });
    await user.click(sendButton);

    // 3. Message appears in chat
    expect(screen.getByText('Analise contratos de saúde')).toBeInTheDocument();

    // 4. Wait for response
    await waitFor(() => {
      expect(screen.getByText(/Olá! Sou o Zumbi/)).toBeInTheDocument();
    });

    // 5. Agent card is displayed
    expect(screen.getByText('Zumbi dos Palmares')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    // Mock error response
    server.use(
      rest.post('/api/v1/chat/send', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }));
      })
    );

    render(<ChatPage />);

    const input = screen.getByPlaceholderText('Digite sua mensagem...');
    await user.type(input, 'Test message');

    const sendButton = screen.getByRole('button', { name: /enviar/i });
    await user.click(sendButton);

    // Error message displayed
    await waitFor(() => {
      expect(screen.getByText(/erro ao enviar mensagem/i)).toBeInTheDocument();
    });
  });
});
```

---

### SPRINT 8.4: CI Integration

**Duração**: 1 dia

**GitHub Actions Workflow**:
```yaml
# .github/workflows/frontend-ci.yml
name: Frontend CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'cidadao.ai-frontend/**'
  pull_request:
    branches: [main]
    paths:
      - 'cidadao.ai-frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: cidadao.ai-frontend/package-lock.json

      - name: Install dependencies
        working-directory: cidadao.ai-frontend
        run: npm ci

      - name: Run linting
        working-directory: cidadao.ai-frontend
        run: |
          npm run lint
          npm run type-check

      - name: Run tests
        working-directory: cidadao.ai-frontend
        run: npm run test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./cidadao.ai-frontend/coverage/coverage-final.json
          flags: frontend

      - name: Build
        working-directory: cidadao.ai-frontend
        run: npm run build
```

**package.json scripts**:
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:watch": "vitest --watch",
    "lint": "eslint . --ext .ts,.tsx",
    "type-check": "tsc --noEmit"
  }
}
```

---

## 👩‍⚖️ SPRINT 9: Dandara - Social Justice Agent

**Duração Estimada**: 1 semana
**Prioridade**: ⚡ Alta
**Objetivo**: Implementar monitoramento de justiça social com dados reais

### Por Que Fazer Agora?

1. **Alinha com Missão**: Core do projeto Cidadão.AI
2. **Diferenciador Único**: Nenhuma plataforma faz isso
3. **Dados Disponíveis**: IBGE, DataSUS, INEP APIs funcionando
4. **Framework Completo**: 30% já implementado

### Status Atual

**O Que Existe (30%)**:
- ✅ Framework de métricas de equidade (Gini, Atkinson, Theil, Palma, Quintile)
- ✅ Cálculos matemáticos implementados
- ✅ Estrutura de análise
- ⚠️ Usa dados simulados

**O Que Falta (70%)**:
- ❌ Integração com APIs reais (IBGE, DataSUS, INEP)
- ❌ Pipeline de coleta de dados
- ❌ Análise temporal (trends)
- ❌ Comparação entre regiões
- ❌ Dashboards de visualização

---

### SPRINT 9.1: Integração de Dados Reais

**Duração**: 3 dias

#### Dia 1: IBGE Data Integration

**Dados a Coletar**:
- [ ] População por estado/município
- [ ] Renda per capita
- [ ] Índice de Desenvolvimento Humano (IDH)
- [ ] Taxa de desemprego
- [ ] Acesso a saneamento básico

**Implementação**:
```python
async def fetch_demographic_data(
    self,
    state_code: Optional[str] = None,
    year: int = 2023
) -> Dict[str, Any]:
    """
    Fetch demographic data from IBGE.

    Returns:
        Dict with population, income, HDI, unemployment, etc.
    """
    async with IBGEClient() as ibge:
        # Get population
        pop_data = await ibge.get_population(state_code=state_code)

        # Get income data (from PNAD Contínua)
        income_data = await ibge.get_income_data(
            state_code=state_code,
            year=year
        )

        # Get HDI data
        hdi_data = await ibge.get_hdi_data(
            state_code=state_code,
            year=year
        )

        return {
            "state_code": state_code,
            "year": year,
            "population": pop_data,
            "income": income_data,
            "hdi": hdi_data,
            "timestamp": datetime.now()
        }
```

#### Dia 2: DataSUS + INEP Integration

**DataSUS (Saúde)**:
- [ ] Taxa de mortalidade infantil
- [ ] Cobertura de vacinação
- [ ] Acesso a UBS (Unidades Básicas de Saúde)
- [ ] Leitos hospitalares per capita

**INEP (Educação)**:
- [ ] Taxa de alfabetização
- [ ] IDEB (Índice de Desenvolvimento da Educação Básica)
- [ ] Escolas por habitante
- [ ] Taxa de evasão escolar

#### Dia 3: Data Pipeline e Cache

**Pipeline ETL**:
```python
class SocialDataPipeline:
    """ETL pipeline for social justice data."""

    async def extract(self, state_code: str) -> Dict[str, Any]:
        """Extract data from all sources."""
        ibge_data, datasus_data, inep_data = await asyncio.gather(
            self.fetch_ibge_data(state_code),
            self.fetch_datasus_data(state_code),
            self.fetch_inep_data(state_code)
        )

        return {
            "demographic": ibge_data,
            "health": datasus_data,
            "education": inep_data
        }

    async def transform(self, raw_data: Dict) -> Dict[str, Any]:
        """Transform and normalize data."""
        normalized = {}

        # Normalize demographic data
        normalized["population"] = self._normalize_population(
            raw_data["demographic"]
        )

        # Calculate composite indicators
        normalized["composite_index"] = self._calculate_composite_index(
            raw_data
        )

        return normalized

    async def load(self, data: Dict, state_code: str):
        """Load data to database with caching."""
        # Cache for fast access
        await cache.set(
            f"social_data:{state_code}",
            data,
            ttl=86400  # 24 hours
        )

        # Store in database for historical analysis
        await db.save_social_metrics(data)
```

---

### SPRINT 9.2: Análise e Métricas

**Duração**: 2 dias

#### Métricas de Equidade

**1. Gini Coefficient** (0.0-1.0):
```python
def calculate_gini(self, income_distribution: List[float]) -> float:
    """
    Calculate Gini coefficient.

    Brasil: ~0.53 (2023)
    Target: <0.40 (OECD average)
    """
    n = len(income_distribution)
    sorted_income = sorted(income_distribution)

    cumsum = 0
    for i, income in enumerate(sorted_income):
        cumsum += (n - i) * income

    gini = (2 * cumsum) / (n * sum(sorted_income)) - (n + 1) / n
    return gini
```

**2. Palma Ratio**:
```python
def calculate_palma_ratio(
    self,
    income_distribution: List[float]
) -> float:
    """
    Palma Ratio: Top 10% / Bottom 40%

    Higher values = more inequality
    Brasil: ~2.5 (2023)
    """
    sorted_income = sorted(income_distribution, reverse=True)
    n = len(sorted_income)

    top_10_pct = sum(sorted_income[:int(n * 0.1)])
    bottom_40_pct = sum(sorted_income[-int(n * 0.4):])

    return top_10_pct / bottom_40_pct if bottom_40_pct > 0 else float('inf')
```

**3. Composite Social Justice Index**:
```python
def calculate_social_justice_index(
    self,
    demographic_data: Dict,
    health_data: Dict,
    education_data: Dict
) -> Dict[str, Any]:
    """
    Composite index (0-100) measuring social justice.

    Components:
    - Income equality (30%)
    - Health access (25%)
    - Education quality (25%)
    - Basic services (20%)
    """
    # Income equality score
    gini = self.calculate_gini(demographic_data["income"])
    income_score = (1 - gini) * 100

    # Health access score
    health_coverage = health_data["vaccination_coverage"]
    hospital_access = health_data["hospitals_per_capita"]
    health_score = (health_coverage * 0.6 + hospital_access * 0.4) * 100

    # Education quality score
    ideb = education_data["ideb_score"]
    literacy = education_data["literacy_rate"]
    education_score = (ideb / 10 * 0.5 + literacy * 0.5) * 100

    # Basic services score
    sanitation = demographic_data["sanitation_access"]
    services_score = sanitation * 100

    # Weighted composite
    composite = (
        income_score * 0.30 +
        health_score * 0.25 +
        education_score * 0.25 +
        services_score * 0.20
    )

    return {
        "composite_index": composite,
        "components": {
            "income_equality": income_score,
            "health_access": health_score,
            "education_quality": education_score,
            "basic_services": services_score
        },
        "classification": self._classify_index(composite)
    }
```

---

### SPRINT 9.3: Visualizações e Dashboard

**Duração**: 2 dias

#### Integração com Oscar Niemeyer

**Geographic Heatmaps**:
```python
async def create_social_justice_map(self) -> Dict[str, Any]:
    """Create choropleth map of social justice index by state."""
    # Get data for all states
    states_data = []
    for state in BRAZILIAN_STATES:
        index = await self.calculate_social_justice_index(state)
        states_data.append({
            "state_code": state,
            "index": index["composite_index"],
            "classification": index["classification"]
        })

    # Create map via Oscar Niemeyer
    oscar = AgentPool.get_agent("oscar_niemeyer")
    map_viz = await oscar.create_choropleth_map(
        data=states_data,
        color_column="index",
        location_column="state_code",
        title="Social Justice Index by State"
    )

    return map_viz
```

**Time Series Analysis**:
```python
async def analyze_temporal_trends(
    self,
    state_code: str,
    start_year: int = 2018,
    end_year: int = 2023
) -> Dict[str, Any]:
    """Analyze how social justice metrics changed over time."""
    trends = []

    for year in range(start_year, end_year + 1):
        data = await self.fetch_historical_data(state_code, year)
        index = await self.calculate_social_justice_index(**data)
        trends.append({
            "year": year,
            "index": index["composite_index"],
            "components": index["components"]
        })

    # Calculate trend direction
    indices = [t["index"] for t in trends]
    trend_direction = "improving" if indices[-1] > indices[0] else "worsening"
    avg_change = (indices[-1] - indices[0]) / len(indices)

    return {
        "state_code": state_code,
        "period": f"{start_year}-{end_year}",
        "trend": trend_direction,
        "avg_annual_change": avg_change,
        "data_points": trends
    }
```

---

### Commit Final - Dandara

```bash
git add src/agents/dandara.py
git add tests/unit/agents/test_dandara.py
git add docs/agents/dandara.md

git commit -m "feat(agents): complete Dandara - Social Justice Agent (30% → 100%)

Integrate real data from Federal APIs:
- IBGE: population, income, HDI, unemployment, sanitation
- DataSUS: infant mortality, vaccination, hospital access
- INEP: literacy, IDEB scores, school access

Social Justice Metrics:
- Gini Coefficient (income inequality)
- Palma Ratio (top 10% / bottom 40%)
- Atkinson Index (inequality aversion)
- Theil Index (decomposed inequality)
- Quintile Ratio (top 20% / bottom 20%)

Composite Social Justice Index:
- Income equality (30% weight)
- Health access (25% weight)
- Education quality (25% weight)
- Basic services (20% weight)
- Classification: Excellent/Good/Fair/Poor/Critical

Data Pipeline:
- ETL pipeline with extract/transform/load stages
- 24-hour caching for performance
- Historical data storage for temporal analysis
- Async concurrent data fetching

Temporal Analysis:
- Trend detection (improving/worsening)
- Year-over-year comparison
- Multi-year averages
- Forecasting capabilities

Visualizations (via Oscar Niemeyer):
- Choropleth maps of social justice by state
- Time series charts of index evolution
- Component breakdown dashboards
- Regional comparison heatmaps

Testing:
- Real data integration tests
- Metric calculation validation
- Edge case handling
- Performance benchmarks

Documentation:
- Complete API reference
- Usage examples with real data
- Methodology explanation
- Data source documentation

Impact:
- First Brazilian AI agent monitoring social justice
- Unique differentiator for Cidadão.AI
- Aligns with project mission
- Enables data-driven policy insights

Dandara dos Palmares now operational at 100% ✅"
```

---

## 🕵️ SPRINT 10: Obaluaie - Corruption Detector

**Duração Estimada**: 2-3 semanas
**Prioridade**: 🌟 Média
**Status**: 15% implementado

### Complexidade Alta - Algoritmos Avançados

**Algoritmos a Implementar**:
1. **Lei de Benford** - Detect financial manipulation
2. **Graph Analysis** - Cartel detection (Louvain algorithm)
3. **Money Laundering** - Pattern detection (structuring, layering)
4. **Nepotism Analysis** - Relationship graphs

### SPRINT 10.1: Lei de Benford Implementation

**Duração**: 1 semana

**Teoria**:
```
Lei de Benford: P(d) = log₁₀(1 + 1/d)

Distribuição esperada para primeiro dígito:
1: 30.1%
2: 17.6%
3: 12.5%
...
9: 4.6%

Dados manipulados violam esta distribuição natural.
```

**Implementação**:
```python
def analyze_benford_law(
    self,
    financial_data: List[float],
    significance_level: float = 0.05
) -> Dict[str, Any]:
    """
    Test if financial data follows Benford's Law.

    Args:
        financial_data: List of financial values
        significance_level: Chi-square test threshold

    Returns:
        Analysis with suspicion score
    """
    from scipy.stats import chisquare
    import numpy as np

    # Expected Benford distribution
    benford_dist = [
        30.1, 17.6, 12.5, 9.7, 7.9,
        6.7, 5.8, 5.1, 4.6
    ]

    # Extract first digits
    first_digits = [
        int(str(abs(value))[0])
        for value in financial_data
        if value != 0
    ]

    # Observed distribution
    observed = np.zeros(9)
    for digit in first_digits:
        observed[digit - 1] += 1

    # Normalize to percentages
    observed_pct = (observed / len(first_digits)) * 100

    # Chi-square test
    chi2_stat, p_value = chisquare(
        observed,
        f_exp=np.array(benford_dist) * len(first_digits) / 100
    )

    # Suspicion score
    significant_deviation = p_value < significance_level
    suspicion_score = 1 - p_value if significant_deviation else 0

    return {
        "follows_benford": not significant_deviation,
        "p_value": p_value,
        "chi2_statistic": chi2_stat,
        "suspicion_score": suspicion_score,
        "observed_distribution": observed_pct.tolist(),
        "expected_distribution": benford_dist,
        "sample_size": len(first_digits),
        "recommendation": (
            "INVESTIGATE: Significant deviation from Benford's Law"
            if significant_deviation
            else "NORMAL: Follows expected distribution"
        )
    }
```

### SPRINT 10.2: Cartel Detection (Graph Analysis)

**Duração**: 1 semana

**Algoritmo: Louvain Community Detection**

```python
async def detect_cartels(
    self,
    contracts: List[Dict],
    threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Detect cartels using graph community detection.

    Args:
        contracts: List of government contracts
        threshold: Minimum suspicion score

    Returns:
        Detected cartel networks
    """
    import networkx as nx
    from networkx.algorithms import community

    # Build supplier network
    G = nx.Graph()

    # Add edges between suppliers that:
    # - Bid on same contracts
    # - Have similar prices
    # - Win in patterns suggesting coordination
    for i, c1 in enumerate(contracts):
        for c2 in contracts[i+1:]:
            if self._are_related(c1, c2):
                weight = self._calculate_relationship_strength(c1, c2)
                if weight > threshold:
                    G.add_edge(
                        c1["supplier"],
                        c2["supplier"],
                        weight=weight
                    )

    # Detect communities (potential cartels)
    communities_gen = community.louvain_communities(G, weight='weight')
    communities_list = list(communities_gen)

    # Analyze each community
    cartels = []
    for i, comm in enumerate(communities_list):
        if len(comm) >= 3:  # Minimum 3 suppliers for cartel
            cartel_contracts = [
                c for c in contracts
                if c["supplier"] in comm
            ]

            suspicion_indicators = self._analyze_cartel_indicators(
                cartel_contracts
            )

            if suspicion_indicators["score"] > threshold:
                cartels.append({
                    "cartel_id": f"CARTEL_{i+1}",
                    "suppliers": list(comm),
                    "contracts_count": len(cartel_contracts),
                    "total_value": sum(c["value"] for c in cartel_contracts),
                    "suspicion_score": suspicion_indicators["score"],
                    "indicators": suspicion_indicators["details"]
                })

    return {
        "cartels_detected": len(cartels),
        "cartels": cartels,
        "total_suppliers_involved": sum(len(c["suppliers"]) for c in cartels),
        "total_value_at_risk": sum(c["total_value"] for c in cartels),
        "network_density": nx.density(G)
    }

def _are_related(self, c1: Dict, c2: Dict) -> bool:
    """Check if two contracts are potentially related."""
    # Same category
    same_category = c1["category"] == c2["category"]

    # Similar dates (within 30 days)
    date_diff = abs((c1["date"] - c2["date"]).days)
    similar_dates = date_diff <= 30

    # Similar values (within 20%)
    value_ratio = min(c1["value"], c2["value"]) / max(c1["value"], c2["value"])
    similar_values = value_ratio > 0.8

    return same_category and (similar_dates or similar_values)
```

---

## 🔮 SPRINT 11: Ceuci - Predictive AI

**Duração Estimada**: 3-4 semanas
**Prioridade**: 🌟 Média
**Status**: 10% implementado

### Machine Learning Models

**7 Models Planejados**:
1. ARIMA/SARIMA (time series)
2. Prophet (Facebook - seasonality)
3. LSTM (deep learning)
4. Random Forest (regression)
5. XGBoost (gradient boosting)
6. SVR (support vector regression)
7. Ensemble Model (combining all)

### Implementação Simplificada

Devido à complexidade, documentar sem implementar completa:

**docs/agents/ceuci-ml-models.md**:
```markdown
# Ceuci - ML Models Documentation

## Architecture

```
Historical Data → Feature Engineering → Model Training → Prediction → Validation
```

## Models

### 1. ARIMA (AutoRegressive Integrated Moving Average)
- **Use Case**: Stationary time series
- **Best For**: Short-term predictions (1-3 months)
- **Training Data**: Min 24 months

### 2. Prophet (Facebook)
- **Use Case**: Data with strong seasonality
- **Best For**: Medium-term predictions (3-12 months)
- **Handles**: Missing data, outliers, holidays

### 3. LSTM (Long Short-Term Memory)
- **Use Case**: Complex patterns, long-term dependencies
- **Best For**: Long-term predictions (12+ months)
- **Requirements**: Large dataset (1000+ samples)

## Implementation Priority

1. Start with Prophet (easiest, good results)
2. Add ARIMA for short-term
3. LSTM for advanced use cases

## Next Steps

- Collect historical data (min 24 months)
- Feature engineering pipeline
- Model training infrastructure
- A/B testing framework integration
```

---

## 🔧 Melhorias Adicionais

### Network Graph Integration
**Duração**: 2-3 dias
**Status**: API pronta, falta UI

- [ ] Conectar Oscar Niemeyer visualizations
- [ ] Interactive fraud exploration
- [ ] Entity relationship discovery

### WebSocket Completion
**Duração**: 1 semana
**Status**: Parcialmente implementado

- [ ] Real-time investigation updates
- [ ] Live agent collaboration visibility
- [ ] Chat improvements

### A/B Testing Documentation
**Duração**: 2 dias
**Status**: Framework pronto, falta docs

- [ ] Usage guide
- [ ] Integration examples
- [ ] Monitoring dashboards

### Backup & Recovery
**Duração**: 3 dias
**Status**: Missing entirely

- [ ] PostgreSQL backup strategy
- [ ] Disaster recovery plan
- [ ] Data retention policies

---

## 📊 Roadmap Resumido

| Sprint | Descrição | Duração | Prioridade | Dependencies |
|--------|-----------|---------|------------|--------------|
| **Sprint 6** | Lampião + Oscar (Analysis Layer) | 1 semana | 🔥 Crítica | - |
| **Sprint 7** | PostgreSQL + CI/CD | 1 semana | 🔥 Crítica | - |
| **Sprint 8** | Frontend Testing | 1 semana | ⚡ Alta | Sprint 7 |
| **Sprint 9** | Dandara (Social Justice) | 1 semana | ⚡ Alta | Sprint 6 |
| **Sprint 10** | Obaluaie (Corruption) | 2-3 semanas | 🌟 Média | Sprint 9 |
| **Sprint 11** | Ceuci (Predictive AI) | 3-4 semanas | 🌟 Média | Sprint 10 |

**Total**: 9-12 semanas (~2-3 meses) para completar tudo

---

## 🎯 Recomendação Executiva

### Faça Agora (Próximas 3 semanas):
1. **Sprint 6**: Quick wins, completa Analysis Layer
2. **Sprint 7**: Infraestrutura crítica
3. **Sprint 8**: Frontend testing

### Faça Depois (1-2 meses):
4. **Sprint 9**: Dandara (missão-crítico)
5. Melhorias incrementais (WebSocket, Network Graph UI)

### Faça Eventualmente (3+ meses):
6. **Sprint 10**: Obaluaie (avançado)
7. **Sprint 11**: Ceuci (complexo, requer dados)

---

**FIM DO PLANO DE PRÓXIMOS SPRINTS**

Pronto para começar o Sprint 6? 🚀
