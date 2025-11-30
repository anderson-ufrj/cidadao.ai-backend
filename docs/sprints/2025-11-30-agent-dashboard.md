# Sprint: Dashboard de Métricas dos Agentes

**Data**: 2025-11-30
**Duração Estimada**: 5-7 horas
**Autor**: Anderson Henrique da Silva
**Status**: Em Planejamento

---

## Resumo das Fases

| Fase | Descrição | Tempo | Entregável |
|------|-----------|-------|------------|
| 1 | Dashboard Service | 1.5h | `agent_dashboard_service.py` |
| 2 | API Routes | 1h | `dashboard.py` (5 endpoints) |
| 3 | SSE Streaming | 1h | Real-time updates |
| 4 | Testes | 1.5h | Unit + Integration |
| 5 | Mini Dashboard HTML | 1h | `dashboard_view.py` |
| 6 | Documentação | 30min | OpenAPI + links |

---

## Objetivo

Criar um **Dashboard Unificado de Métricas dos Agentes** que consolide informações de performance, saúde e atividade dos 16 agentes operacionais do Cidadão.AI.

---

## Análise do Estado Atual

### O que já existe (60% da infraestrutura pronta)

| Componente | Status | Localização |
|------------|--------|-------------|
| Prometheus Metrics | ✅ Implementado | `src/infrastructure/observability/metrics.py` |
| Agent Metrics Service | ✅ Implementado | `src/services/agent_metrics.py` |
| Metrics Middleware | ✅ Implementado | `src/api/middleware/metrics_middleware.py` |
| Health Monitoring | ✅ Implementado | `src/infrastructure/health/dependency_checker.py` |
| SLO Monitor | ✅ Implementado | `src/infrastructure/monitoring/slo_monitor.py` |
| Visualization Routes | ✅ Parcial | `src/api/routes/visualization.py` |

### Gaps Identificados

1. **Sem Dashboard Unificado** - Múltiplos endpoints mas sem visão consolidada
2. **Sem Streaming Real-time** - Apenas polling (GET requests)
3. **Sem Pipeline de Investigações** - Falta visibilidade do workflow
4. **Sem Tendências Históricas** - Métricas são point-in-time apenas

---

## Escopo do Sprint

### ✅ Incluído (MVP - Hoje)

1. **Dashboard Service** - Serviço que agrega métricas de todos os agentes
2. **API REST Completa** - `/api/v1/dashboard/agents/*` para consumo futuro pelo frontend
3. **Mini Dashboard HTML** - `/dashboard/agents` página visual embutida no backend
4. **Leaderboard de Agentes** - Ranking por performance/atividade
5. **Status de Saúde** - Visão geral da saúde de cada agente
6. **Métricas em Tempo Real** - SSE endpoint para atualizações live + auto-refresh no HTML

### ❌ Fora do Escopo (Próximos Sprints)

- Persistência histórica em banco de dados
- Alertas avançados com notificações
- Dashboard customizável pelo usuário
- Integração com Grafana Cloud

---

## Arquitetura da Solução

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                        │
│                    /dashboard/agents page                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
        ┌───────────────────┐   ┌───────────────────┐
        │  GET /dashboard/  │   │ SSE /dashboard/   │
        │  agents/summary   │   │ agents/stream     │
        └─────────┬─────────┘   └─────────┬─────────┘
                  │                       │
                  └───────────┬───────────┘
                              │
                              ▼
            ┌─────────────────────────────────┐
            │      AgentDashboardService      │
            │   (src/services/dashboard/)     │
            │                                 │
            │  - aggregate_agent_metrics()    │
            │  - get_agent_leaderboard()      │
            │  - get_health_overview()        │
            │  - stream_metrics()             │
            └─────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ AgentMetrics  │   │ HealthChecker │   │ SLOMonitor    │
│   Service     │   │               │   │               │
└───────────────┘   └───────────────┘   └───────────────┘
```

---

## Plano de Implementação

### Fase 1: Dashboard Service (1.5h)

**Arquivo**: `src/services/dashboard/agent_dashboard_service.py`

```python
# Estrutura planejada
class AgentDashboardService:
    """Serviço unificado para métricas do dashboard de agentes."""

    async def get_summary(self) -> AgentDashboardSummary:
        """Retorna visão consolidada de todos os agentes."""

    async def get_leaderboard(self, metric: str, limit: int) -> List[AgentRanking]:
        """Ranking de agentes por métrica específica."""

    async def get_agent_detail(self, agent_name: str) -> AgentDetailedMetrics:
        """Métricas detalhadas de um agente específico."""

    async def get_health_matrix(self) -> AgentHealthMatrix:
        """Matriz de saúde de todos os agentes."""

    async def stream_metrics(self) -> AsyncGenerator[dict, None]:
        """Generator para streaming SSE de métricas."""
```

**Modelos** (`src/schemas/dashboard.py`):

```python
class AgentDashboardSummary(BaseModel):
    timestamp: datetime
    total_agents: int
    healthy_agents: int
    degraded_agents: int
    unhealthy_agents: int
    total_requests_24h: int
    avg_response_time_ms: float
    avg_quality_score: float
    top_performers: List[AgentRanking]
    recent_errors: List[AgentError]

class AgentRanking(BaseModel):
    rank: int
    agent_name: str
    agent_identity: str  # Ex: "Zumbi dos Palmares"
    metric_value: float
    metric_name: str
    trend: str  # "up", "down", "stable"

class AgentHealthMatrix(BaseModel):
    agents: List[AgentHealthStatus]
    overall_health: str  # "healthy", "degraded", "critical"
    last_check: datetime
```

### Fase 2: API Routes (1h)

**Arquivo**: `src/api/routes/dashboard.py`

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/dashboard/agents/summary` | GET | Visão geral consolidada |
| `/api/v1/dashboard/agents/leaderboard` | GET | Ranking de agentes |
| `/api/v1/dashboard/agents/{name}` | GET | Detalhes de um agente |
| `/api/v1/dashboard/agents/health` | GET | Matriz de saúde |
| `/api/v1/dashboard/agents/stream` | GET | SSE streaming de métricas |

**Query Parameters**:
- `leaderboard`: `metric` (response_time, quality_score, requests, success_rate), `limit` (default: 10), `order` (asc/desc)
- `summary`: `period` (1h, 6h, 24h, 7d)

### Fase 3: Streaming SSE (1h)

**Implementação de streaming real-time**:

```python
@router.get("/agents/stream")
async def stream_agent_metrics(request: Request):
    """Stream de métricas dos agentes via Server-Sent Events."""

    async def event_generator():
        dashboard_service = AgentDashboardService()

        while True:
            if await request.is_disconnected():
                break

            metrics = await dashboard_service.get_summary()
            yield {
                "event": "metrics_update",
                "data": metrics.model_dump_json()
            }

            await asyncio.sleep(5)  # Update every 5 seconds

    return EventSourceResponse(event_generator())
```

### Fase 4: Integração e Testes (1.5h)

**Testes Unitários** (`tests/unit/services/test_agent_dashboard_service.py`):
- `test_get_summary_returns_valid_data`
- `test_leaderboard_ordering`
- `test_health_matrix_calculation`
- `test_agent_detail_not_found`

**Testes de Integração** (`tests/integration/api/test_dashboard.py`):
- `test_dashboard_summary_endpoint`
- `test_leaderboard_with_filters`
- `test_sse_stream_connection`
- `test_agent_detail_endpoint`

### Fase 5: Mini Dashboard HTML (1h)

**Arquivo**: `src/api/routes/dashboard_view.py`

Página HTML embutida com:
- Cards de resumo (total agentes, healthy, degraded)
- Tabela com todos os agentes e suas métricas
- Gráfico de barras com response time por agente
- Status indicators (verde/amarelo/vermelho)
- Auto-refresh a cada 10 segundos via JavaScript

**Tecnologias**:
- HTML5 + CSS3 (Tailwind via CDN)
- JavaScript vanilla (fetch API)
- Chart.js via CDN para gráficos
- Sem dependências extras no backend

**Rotas**:
```
GET /dashboard/agents      → Página HTML completa
GET /dashboard/agents/embed → Versão para iframe (sem header)
```

**Preview do Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  🏛️ Cidadão.AI - Agent Metrics Dashboard                   │
│  Last updated: 10:30:45 | Auto-refresh: ON                  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │    16    │ │    14    │ │    2     │ │   97.9%  │       │
│  │  Agents  │ │ Healthy  │ │ Degraded │ │ Success  │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
├─────────────────────────────────────────────────────────────┤
│  📊 Response Time by Agent                                  │
│  [========== Bar Chart ==========]                          │
├─────────────────────────────────────────────────────────────┤
│  🏆 Agent Leaderboard                                       │
│  ┌─────┬────────────────┬──────────┬─────────┬───────────┐ │
│  │ #   │ Agent          │ Requests │ Avg RT  │ Status    │ │
│  ├─────┼────────────────┼──────────┼─────────┼───────────┤ │
│  │ 1   │ 🔍 Zumbi       │ 3,420    │ 623ms   │ 🟢 Healthy│ │
│  │ 2   │ 📊 Anita       │ 2,891    │ 712ms   │ 🟢 Healthy│ │
│  │ ... │ ...            │ ...      │ ...     │ ...       │ │
│  └─────┴────────────────┴──────────┴─────────┴───────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Fase 6: Documentação (30min)

- Atualizar CLAUDE.md com novos endpoints
- Documentar no OpenAPI (FastAPI automático)
- Adicionar link do dashboard na página inicial da API

---

## Estrutura de Arquivos

```
src/
├── services/
│   └── dashboard/
│       ├── __init__.py
│       └── agent_dashboard_service.py    # NOVO - Serviço agregador
├── schemas/
│   └── dashboard.py                       # NOVO - Modelos Pydantic
├── api/
│   └── routes/
│       ├── dashboard.py                   # NOVO - API REST endpoints
│       └── dashboard_view.py              # NOVO - Mini dashboard HTML
tests/
├── unit/
│   └── services/
│       └── test_agent_dashboard_service.py  # NOVO
└── integration/
    └── api/
        └── test_dashboard.py              # NOVO
```

---

## Dados do Dashboard

### Métricas por Agente

| Métrica | Fonte | Agregação |
|---------|-------|-----------|
| Total Requests | `AgentMetricsService` | Sum |
| Success Rate | `AgentMetricsService` | Percentage |
| Avg Response Time | `AgentMetricsService` | Mean |
| P95 Response Time | `AgentMetricsService` | Percentile |
| Quality Score | `AgentMetricsService` | Mean |
| Memory Usage | `AgentMetricsService` | Current |
| Error Rate | `AgentMetricsService` | Percentage (5min) |
| Health Status | `HealthChecker` | Current |
| Last Activity | `AgentMetricsService` | Timestamp |

### Identidades dos Agentes (para UI)

```python
AGENT_IDENTITIES = {
    "zumbi": {"name": "Zumbi dos Palmares", "role": "Investigador", "icon": "🔍"},
    "anita": {"name": "Anita Garibaldi", "role": "Analista", "icon": "📊"},
    "tiradentes": {"name": "Tiradentes", "role": "Relator", "icon": "📝"},
    "ayrton_senna": {"name": "Ayrton Senna", "role": "Roteador", "icon": "🏎️"},
    "bonifacio": {"name": "José Bonifácio", "role": "Jurídico", "icon": "⚖️"},
    "maria_quiteria": {"name": "Maria Quitéria", "role": "Segurança", "icon": "🛡️"},
    "machado": {"name": "Machado de Assis", "role": "Textual", "icon": "✍️"},
    "oxossi": {"name": "Oxóssi", "role": "Caçador de Dados", "icon": "🎯"},
    "lampiao": {"name": "Lampião", "role": "Regional", "icon": "🗺️"},
    "oscar_niemeyer": {"name": "Oscar Niemeyer", "role": "Agregador", "icon": "🏛️"},
    "abaporu": {"name": "Abaporu", "role": "Orquestrador", "icon": "🎭"},
    "nana": {"name": "Nanã", "role": "Memória", "icon": "🧠"},
    "drummond": {"name": "Drummond", "role": "Comunicação", "icon": "💬"},
    "ceuci": {"name": "Céuci", "role": "ETL/Preditivo", "icon": "🔮"},
    "obaluaie": {"name": "Obaluaiê", "role": "Corrupção", "icon": "🚨"},
    "dandara": {"name": "Dandara", "role": "Equidade Social", "icon": "⚖️"},
}
```

---

## Exemplo de Response

### GET /api/v1/dashboard/agents/summary

```json
{
  "timestamp": "2025-11-30T10:30:00Z",
  "period": "24h",
  "overview": {
    "total_agents": 16,
    "healthy": 14,
    "degraded": 2,
    "unhealthy": 0,
    "overall_health": "healthy"
  },
  "performance": {
    "total_requests": 15420,
    "successful_requests": 15102,
    "failed_requests": 318,
    "success_rate": 97.94,
    "avg_response_time_ms": 847.3,
    "p95_response_time_ms": 2341.5,
    "avg_quality_score": 0.87
  },
  "top_performers": [
    {
      "rank": 1,
      "agent_name": "zumbi",
      "agent_identity": "Zumbi dos Palmares",
      "role": "Investigador",
      "icon": "🔍",
      "requests": 3420,
      "success_rate": 99.2,
      "avg_response_time_ms": 623.4,
      "quality_score": 0.96
    }
  ],
  "recent_errors": [
    {
      "agent_name": "oxossi",
      "error_type": "APITimeout",
      "message": "Portal da Transparência timeout",
      "timestamp": "2025-11-30T10:28:15Z"
    }
  ],
  "activity_heatmap": {
    "last_hour": [45, 52, 38, 67, 71, 58]
  }
}
```

---

## Critérios de Aceite

### Funcionais

- [ ] Endpoint `/summary` retorna dados de todos os 16 agentes
- [ ] Leaderboard ordena corretamente por qualquer métrica
- [ ] SSE stream atualiza a cada 5 segundos
- [ ] Detalhes do agente incluem histórico dos últimos 60 minutos
- [ ] Health matrix mostra status correto baseado em thresholds

### Não-Funcionais

- [ ] Response time do `/summary` < 500ms
- [ ] SSE não consome mais que 5% CPU em idle
- [ ] Cobertura de testes > 80% nos novos arquivos
- [ ] Documentação OpenAPI completa

### Thresholds de Saúde

| Status | Response Time | Error Rate | Quality Score |
|--------|--------------|------------|---------------|
| Healthy | < 1000ms | < 5% | > 0.8 |
| Degraded | 1000-3000ms | 5-15% | 0.6-0.8 |
| Unhealthy | > 3000ms | > 15% | < 0.6 |

---

## Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Dados insuficientes em dev | Alta | Médio | Usar mock data para testes |
| Performance do agregador | Média | Alto | Cache de 30s nas métricas |
| Complexidade do SSE | Baixa | Médio | Reutilizar padrão do chat |

---

## Checklist de Entrega

### Código - Backend

- [ ] `src/services/dashboard/__init__.py`
- [ ] `src/services/dashboard/agent_dashboard_service.py`
- [ ] `src/schemas/dashboard.py`
- [ ] `src/api/routes/dashboard.py` (API REST)
- [ ] `src/api/routes/dashboard_view.py` (Mini Dashboard HTML)
- [ ] Registro dos routers em `src/api/app.py`

### Mini Dashboard HTML

- [ ] Página principal `/dashboard/agents`
- [ ] Cards de métricas (total, healthy, degraded, success rate)
- [ ] Tabela com leaderboard dos agentes
- [ ] Gráfico de barras (response time)
- [ ] Auto-refresh a cada 10 segundos
- [ ] Versão embed para iframe

### Testes

- [ ] `tests/unit/services/test_agent_dashboard_service.py`
- [ ] `tests/integration/api/test_dashboard.py`
- [ ] Todos os testes passando

### Qualidade

- [ ] `make format` executado
- [ ] `make lint` sem erros
- [ ] `make type-check` sem erros
- [ ] Coverage > 80% nos novos arquivos

### Documentação

- [ ] Endpoints documentados no OpenAPI
- [ ] Link do dashboard na página inicial da API
- [ ] Commit messages seguindo padrão

---

## Próximos Passos (Pós-Sprint)

1. **Persistência Histórica** - Salvar métricas em TimescaleDB/InfluxDB
2. **Alertas Inteligentes** - Notificações quando agente degrada
3. **Comparativo Temporal** - Day-over-day, week-over-week
4. **Dashboard Frontend** - Componente React para visualização
5. **Grafana Dashboards** - Painéis pré-configurados

---

## Referências

- [Agent Metrics Service](../api/agent-metrics-api.md)
- [Prometheus Integration](../architecture/observability.md)
- [SSE Implementation](../api/STREAMING_IMPLEMENTATION.md)
- [Multi-Agent Architecture](../architecture/multi-agent-architecture.md)
