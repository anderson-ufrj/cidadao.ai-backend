# Status de Implementação - Mapa de Transparência

## 📊 Visão Geral

**Feature**: Mapa Interativo de Cobertura de APIs de Transparência do Brasil
**Abordagem**: Híbrida com cache (6 horas de TTL)
**Status Geral**: 🟡 **EM DESENVOLVIMENTO** (Backend e Frontend em paralelo)

**Data de Início**: 2025-10-23
**Última Atualização**: 2025-10-23

---

## 🎯 Progresso Geral

| Componente | Status | Progresso | Responsável |
|------------|--------|-----------|-------------|
| **Documentação Técnica** | ✅ Completo | 100% | Claude |
| **Backend - Modelo DB** | 🟡 Em Andamento | 0% | Backend Team |
| **Backend - Task Celery** | 🟡 Em Andamento | 0% | Backend Team |
| **Backend - Endpoint API** | 🟡 Em Andamento | 0% | Backend Team |
| **Frontend - Componente Mapa** | 🟡 Em Andamento | 0% | Frontend Team |
| **Frontend - Integração API** | 🟡 Em Andamento | 0% | Frontend Team |
| **Testes** | ⏳ Aguardando | 0% | QA Team |
| **Deploy** | ⏳ Aguardando | 0% | DevOps |

---

## 📋 Checklist de Implementação

### Backend Tasks

#### 1. Database Model & Migration
- [ ] Criar modelo `TransparencyCoverageSnapshot` em `src/models/transparency_coverage.py`
- [ ] Criar migration Alembic `008_transparency_coverage_snapshots.py`
- [ ] Executar migration em development
- [ ] Testar queries de performance (indexes)
- [ ] Validar estrutura JSON no PostgreSQL

**Arquivos**:
- `src/models/transparency_coverage.py` (novo)
- `migrations/versions/008_transparency_coverage_snapshots.py` (novo)

**Comandos**:
```bash
# Criar migration
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/alembic revision --autogenerate -m "Add transparency coverage snapshots"

# Aplicar
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/alembic upgrade head

# Verificar
psql $DATABASE_URL -c "\d transparency_coverage_snapshots"
```

#### 2. Celery Task Implementation
- [ ] Criar `src/infrastructure/queue/tasks/coverage_tasks.py`
- [ ] Implementar `update_transparency_coverage()` task
- [ ] Implementar helper `transform_to_map_format()`
- [ ] Implementar helper `extract_api_detail()`
- [ ] Implementar helper `calculate_summary_stats()`
- [ ] Implementar helper `extract_known_issues()`
- [ ] Adicionar schedule ao `celeryconfig.py` (a cada 6 horas)
- [ ] Testar task manualmente

**Arquivos**:
- `src/infrastructure/queue/tasks/coverage_tasks.py` (novo)
- `src/infrastructure/queue/celeryconfig.py` (modificar)

**Comandos de Teste**:
```bash
# Executar task manualmente
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/celery -A src.infrastructure.queue.celery_app call update_transparency_coverage

# Verificar schedule
JWT_SECRET_KEY=test SECRET_KEY=test venv/bin/celery -A src.infrastructure.queue.celery_app inspect scheduled

# Ver logs
tail -f logs/celery.log | grep coverage
```

#### 3. API Endpoint Implementation
- [ ] Adicionar endpoint `GET /api/v1/transparency/coverage/map` em `transparency.py`
- [ ] Adicionar endpoint `GET /api/v1/transparency/coverage/state/{code}`
- [ ] Implementar lógica de cache (retornar snapshot mais recente)
- [ ] Implementar fallback (gerar on-demand se não houver cache)
- [ ] Adicionar parâmetro `include_history` (opcional)
- [ ] Implementar helper `analyze_trend()` para histórico
- [ ] Adicionar documentação OpenAPI/Swagger
- [ ] Testar endpoint com curl

**Arquivos**:
- `src/api/routes/transparency.py` (modificar)

**Comandos de Teste**:
```bash
# Testar endpoint (development)
curl http://localhost:8000/api/v1/transparency/coverage/map | jq '.summary'

# Testar com histórico
curl 'http://localhost:8000/api/v1/transparency/coverage/map?include_history=true' | jq '.history | length'

# Testar estado específico
curl http://localhost:8000/api/v1/transparency/coverage/state/SP | jq '.'
```

### Frontend Tasks

#### 4. Main Map Component
- [ ] Criar `components/TransparencyMap.tsx` (componente principal)
- [ ] Implementar fetch de dados do endpoint `/coverage/map`
- [ ] Implementar loading state (skeleton)
- [ ] Implementar error handling
- [ ] Implementar atualização periódica (opcional)
- [ ] Adicionar info de cache (age em minutos)
- [ ] Implementar seção de estatísticas (summary cards)
- [ ] Implementar seção de issues conhecidos
- [ ] Implementar call-to-action (guia LAI)

**Arquivos**:
- `frontend/src/components/TransparencyMap.tsx` (novo)
- `frontend/src/components/TransparencyMap.css` (novo)

#### 5. Brazil Map SVG Component
- [ ] Criar `components/BrazilMap.tsx` (mapa interativo)
- [ ] Implementar SVG paths para 27 estados brasileiros
- [ ] Implementar color coding por status (healthy/degraded/no_api)
- [ ] Implementar hover tooltips
- [ ] Implementar click handlers (abrir modal de detalhes)
- [ ] Adicionar legenda de cores
- [ ] Testar responsividade (mobile/tablet/desktop)

**Arquivos**:
- `frontend/src/components/BrazilMap.tsx` (novo)
- `frontend/src/components/BrazilMap.css` (novo)
- `frontend/src/assets/brazil-states.svg` (opcional - paths separados)

#### 6. State Detail Modal
- [ ] Criar `components/StateDetailModal.tsx`
- [ ] Mostrar todas as APIs do estado
- [ ] Mostrar histórico de 7 dias (trend)
- [ ] Mostrar ações recomendadas (se houver problemas)
- [ ] Mostrar base legal (se aplicável)
- [ ] Link para protocolar LAI (se sem API)
- [ ] Botão de fechar modal

**Arquivos**:
- `frontend/src/components/StateDetailModal.tsx` (novo)
- `frontend/src/components/StateDetailModal.css` (novo)

#### 7. Supporting Components
- [ ] Criar `components/StatCard.tsx` (card de estatística)
- [ ] Criar `components/IssueCard.tsx` (card de problema conhecido)
- [ ] Criar `components/LoadingSkeleton.tsx` (loading state)
- [ ] Adicionar TypeScript interfaces (`types/transparency.ts`)

**Arquivos**:
- `frontend/src/components/StatCard.tsx` (novo)
- `frontend/src/components/IssueCard.tsx` (novo)
- `frontend/src/components/LoadingSkeleton.tsx` (novo)
- `frontend/src/types/transparency.ts` (novo)

### Testing Tasks

#### 8. Backend Tests
- [ ] Testes unitários: `test_coverage_tasks.py`
  - [ ] `test_transform_to_map_format()`
  - [ ] `test_extract_api_detail()`
  - [ ] `test_calculate_summary_stats()`
- [ ] Testes de integração: `test_coverage_map_integration.py`
  - [ ] `test_celery_task_creates_snapshot()`
  - [ ] `test_endpoint_returns_valid_data()`
  - [ ] `test_endpoint_with_history()`
- [ ] Testes de performance (opcional)

**Arquivos**:
- `tests/unit/services/test_coverage_tasks.py` (novo)
- `tests/integration/test_coverage_map_integration.py` (novo)

**Comandos**:
```bash
# Rodar testes
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/unit/services/test_coverage_tasks.py -v
JWT_SECRET_KEY=test SECRET_KEY=test pytest tests/integration/test_coverage_map_integration.py -v
```

#### 9. Frontend Tests
- [ ] Testes de componente: `TransparencyMap.test.tsx`
- [ ] Testes de componente: `BrazilMap.test.tsx`
- [ ] Testes de integração: Mock API responses
- [ ] Testes E2E: Cypress/Playwright (opcional)

### Deployment Tasks

#### 10. Railway Deployment
- [ ] Aplicar migrations no Railway
- [ ] Configurar variável `ENABLE_COVERAGE_MAP=true`
- [ ] Verificar Celery Beat está rodando
- [ ] Executar task inicial manualmente (seed cache)
- [ ] Verificar endpoint retorna dados
- [ ] Monitorar logs por 24 horas

**Comandos**:
```bash
# Aplicar migration
railway run alembic upgrade head

# Executar task inicial
railway run celery -A src.infrastructure.queue.celery_app call update_transparency_coverage

# Verificar
curl https://cidadao-api-production.up.railway.app/api/v1/transparency/coverage/map | jq '.summary'

# Monitorar
railway logs -f | grep coverage
```

#### 11. Frontend Deployment
- [ ] Build production
- [ ] Deploy para Vercel/Netlify
- [ ] Testar endpoint production
- [ ] Verificar mapa carrega corretamente
- [ ] Testar em múltiplos dispositivos

---

## 🔗 Integração Backend ↔ Frontend

### Contrato de API (JSON Schema)

**Endpoint**: `GET /api/v1/transparency/coverage/map`

**Response Type**: `application/json`

**Response Structure**:
```typescript
interface CoverageMapResponse {
  last_update: string;           // ISO 8601 timestamp
  cache_info?: {
    cached: boolean;
    last_update: string;
    age_minutes: number;
  };
  states: {
    [stateCode: string]: {
      name: string;
      apis: Array<{
        id: string;
        name: string;
        type: string;
        status: 'healthy' | 'degraded' | 'unhealthy' | 'blocked' | 'no_api';
        response_time_ms?: number;
        error?: string;
        error_details?: Record<string, any>;
        action?: string;
      }>;
      overall_status: string;
      coverage_percentage: number;
      color: string;
    };
  };
  summary: {
    total_states: number;
    states_with_apis: number;
    states_working: number;
    states_degraded: number;
    states_no_api: number;
    overall_coverage_percentage: number;
  };
  issues?: Array<{
    severity: string;
    title: string;
    description: string;
    affected_states: string[];
    action: string;
  }>;
  call_to_action?: {
    title: string;
    description: string;
    guide_url: string;
  };
}
```

### Status Codes

| Status Code | Descrição |
|-------------|-----------|
| `200 OK` | Success - Retorna dados do cache ou gerados on-demand |
| `404 Not Found` | Estado não encontrado (endpoint `/state/{code}`) |
| `500 Internal Server Error` | Erro ao gerar coverage map |

---

## 📅 Timeline Estimado

### Semana 1 (2025-10-23 a 2025-10-29)
- **Backend**: Migration + Model + Task Celery (3 dias)
- **Backend**: Endpoint API (2 dias)
- **Frontend**: Componente principal + Map SVG (5 dias)

### Semana 2 (2025-10-30 a 2025-11-05)
- **Backend**: Testes unitários + integração (2 dias)
- **Frontend**: Modal de detalhes + componentes auxiliares (3 dias)
- **Frontend**: Testes (2 dias)

### Semana 3 (2025-11-06 a 2025-11-12)
- **Deploy**: Railway backend (1 dia)
- **Deploy**: Vercel frontend (1 dia)
- **QA**: Testes em produção (2 dias)
- **Docs**: Guia de usuário (1 dia)
- **Marketing**: Anúncio nas redes sociais (ongoing)

**Total Estimado**: 15-20 dias úteis

---

## 🚧 Bloqueios Conhecidos

1. **Nenhum bloqueio técnico identificado**
   - Infraestrutura já existe (PostgreSQL, Celery Beat, Railway)
   - Dependências já instaladas
   - HealthCheckService já funcional

2. **Dependências**:
   - Frontend depende do endpoint backend estar pronto
   - Deploy depende dos testes passarem

---

## 📝 Notas de Implementação

### Backend

1. **Performance do Health Check**:
   - Atual: 30-60s para checar 13 APIs
   - Task Celery roda em background (não impacta usuário)
   - Cache retorna <100ms

2. **Tamanho do Cache**:
   - ~50KB por snapshot JSON
   - 4 snapshots/dia = ~200KB/dia
   - ~73MB/ano (aceitável)

3. **Cleanup Opcional**:
   ```python
   # Script para limpar snapshots antigos (>90 dias)
   DELETE FROM transparency_coverage_snapshots
   WHERE snapshot_date < NOW() - INTERVAL '90 days';
   ```

### Frontend

1. **SVG do Brasil**:
   - Usar biblioteca `react-simple-maps` OU
   - SVG customizado com paths dos 27 estados
   - Referência: https://github.com/mapsvg/mapsvg-brazil

2. **Responsividade**:
   - Desktop: Mapa grande (800x600px)
   - Tablet: Mapa médio (600x450px)
   - Mobile: Mapa pequeno (360x270px) + lista de cards

3. **Acessibilidade**:
   - Adicionar `aria-labels` nos estados
   - Suporte a navegação por teclado (Tab)
   - Tooltips com `role="tooltip"`

---

## 🎯 Critérios de Aceitação

### Funcionalidade

- [ ] Mapa carrega em <2 segundos (cache hit)
- [ ] Mapa mostra 27 estados brasileiros
- [ ] Cores corretas por status (verde/amarelo/vermelho/cinza)
- [ ] Tooltip mostra info ao hover
- [ ] Click abre modal com detalhes
- [ ] Estatísticas calculadas corretamente
- [ ] Issues conhecidos listados
- [ ] Call-to-action visível

### Performance

- [ ] Response time <100ms (cached)
- [ ] Response time <60s (cold start)
- [ ] Task Celery completa em <60s
- [ ] Frontend carrega sem lag
- [ ] Mobile performance 60fps

### Qualidade

- [ ] Testes unitários passam (>80% coverage)
- [ ] Testes de integração passam
- [ ] Sem erros no console
- [ ] Sem warnings ESLint/TypeScript
- [ ] Código segue style guide

---

## 📞 Pontos de Contato

### Backend Team
- **Responsável**: Backend Team Lead
- **Status**: 🟡 Em desenvolvimento (migração + task + endpoint)
- **Próximo checkpoint**: Endpoint `/coverage/map` funcional

### Frontend Team
- **Responsável**: Frontend Team Lead
- **Status**: 🟡 Em desenvolvimento (componente mapa + integração)
- **Próximo checkpoint**: Mapa visual funcional (mock data)

### Documentação
- **Responsável**: Claude (Assistente)
- **Status**: ✅ Completo
- **Localização**: `docs/technical/TRANSPARENCY_COVERAGE_MAP.md`

---

## 🔄 Próximas Reuniões

1. **Daily Standup**: Atualização diária de progresso
2. **Code Review**: Quando backend endpoint estiver pronto
3. **Integration Testing**: Quando ambos estiverem prontos
4. **Deploy Planning**: 1 semana antes do deploy

---

## 📚 Referências

- **Documento Técnico**: `docs/technical/TRANSPARENCY_COVERAGE_MAP.md`
- **Issue Tracking**: GitHub Issues (criar issues para cada task)
- **API Docs**: Swagger UI em `/docs` (quando endpoint estiver pronto)

---

**Última Atualização**: 2025-10-23 16:00 BRT
**Próxima Revisão**: 2025-10-24 (daily standup)
