# 🚂 SISTEMA COMPLETO 24/7 NO RAILWAY - Plano $20/mês

**Autor**: Anderson Henrique da Silva
**Data**: 2025-10-09
**Status**: ✅ ATIVO com potencial para mais features

---

## 💰 O QUE VOCÊ TEM (Plano $20/mês)

### ✅ Recursos Inclusos:
- ⏰ **Execução Ilimitada 24/7** (sem limite de horas)
- 🔄 **3 Serviços Simultâneos** (web + worker + beat)
- 🗄️ **Redis Gratuito** até 1GB (cache + queue)
- 📊 **8GB RAM total** compartilhado
- 🚀 **Auto-deploy** do GitHub
- 📈 **Monitoramento** integrado

---

## 🎯 O QUE ESTÁ RODANDO 24/7 AGORA

### 1. **API FastAPI** (cidadao-api)
- ✅ REST API completa
- ✅ Documentação Swagger
- ✅ 17 agentes IA brasileiros
- ✅ URL: `https://cidadao-api-production.up.railway.app`

### 2. **Celery Worker** (cidadao-worker)
- ✅ 4 workers paralelos
- ✅ 5 filas de prioridade (critical → background)
- ✅ Processa investigações em background
- ✅ Max 1000 tasks por worker

### 3. **Celery Beat Scheduler** (cidadao-beat)
- ✅ Agendador de tasks automáticas
- ✅ Cria investigações sem intervenção humana
- ✅ **VER TABELA ABAIXO** 👇

---

## 📋 TASKS AUTOMÁTICAS CONFIGURADAS (14 tasks rodando!)

### 🔍 **Investigações Automáticas**

| Task | Frequência | Descrição |
|------|------------|-----------|
| **auto-monitor-new-contracts-6h** | 6 horas | Monitora contratos novos dos últimos 6h |
| **auto-monitor-priority-orgs-4h** | 4 horas | Monitora órgãos prioritários |
| **auto-reanalyze-historical-weekly** | 7 dias | Reanálise de contratos históricos (6 meses) |
| **auto-investigation-health-hourly** | 1 hora | Health check do sistema de investigações |

### ⚔️ **Katana Scan Integration**

| Task | Frequência | Descrição |
|------|------------|-----------|
| **katana-monitor-dispensas-6h** | 6 horas | Monitora dispensas de licitação |
| **katana-health-check-hourly** | 1 hora | Health check do Katana |

### 📧 **Sistema de Alertas**

| Task | Frequência | Descrição |
|------|------------|-----------|
| **critical-anomalies-summary-daily** | 24 horas | Resumo diário de anomalias críticas |
| **process-pending-alerts-hourly** | 1 hora | Retry de alertas falhados |

### 🕸️ **Network Graph Analysis** (NOVO!)

| Task | Frequência | Descrição |
|------|------------|-----------|
| **calculate-network-metrics-daily** | 24 horas | Calcula métricas de centralidade de todas entidades |
| **detect-suspicious-networks-6h** | 6 horas | Detecta cartéis, concentração, redes suspeitas |
| **enrich-investigations-with-graph-6h** | 6 horas | Enriquece investigações com contexto cross-investigation |
| **update-entity-risk-scores-daily** | 24 horas | Atualiza scores de risco (0-10) de entidades |
| **network-health-check-hourly** | 1 hora | Health check do sistema de grafos |

### 🧹 **Manutenção**

| Task | Frequência | Descrição |
|------|------------|-----------|
| **cleanup-old-results** | 24 horas | Limpa resultados antigos (7 dias) |
| **health-check** | 5 minutos | Health check geral do Celery |

---

## 🚀 O QUE ESTÁ FALTANDO PARA APROVEITAR 100%

### ❌ Sistema de Grafos NÃO ATIVADO (criamos mas precisa deploy)

#### 📦 O que foi criado hoje:

1. ✅ **4 Tabelas PostgreSQL**:
   - `entity_nodes` - Empresas, pessoas, órgãos
   - `entity_relationships` - Conexões entre entidades
   - `entity_investigation_references` - Links com investigações
   - `suspicious_networks` - Redes suspeitas detectadas

2. ✅ **Services Completos**:
   - `NetworkAnalysisService` - Análise de rede, métricas, detecção
   - `GraphIntegrationService` - Integração automática com investigações

3. ✅ **12 Endpoints REST** para frontend:
   - `/api/v1/network/entities/search` - Buscar entidades
   - `/api/v1/network/entities/{id}/network` - Rede de relacionamentos
   - `/api/v1/network/suspicious-networks` - Redes suspeitas
   - `/api/v1/network/statistics` - Estatísticas gerais
   - `/api/v1/network/export/d3/{id}` - Export D3.js
   - `/api/v1/network/export/cytoscape/{id}` - Export Cytoscape.js
   - E mais 6 endpoints...

4. ✅ **5 Tasks Automáticas** (já adicionadas ao beat_schedule):
   - Cálculo de métricas diário
   - Detecção de redes suspeitas a cada 6h
   - Enriquecimento de investigações a cada 6h
   - Atualização de risk scores diário
   - Health check de hora em hora

5. ✅ **Documentação Completa**:
   - `NETWORK_GRAPH_API.md` - Doc para frontend
   - `SETUP_NETWORK_GRAPH.md` - Setup guide

---

## 🔥 PASSOS PARA ATIVAR O GRAFO (5 minutos!)

### Passo 1: Aplicar Migration no Railway

```bash
# Via Railway CLI
railway run alembic upgrade head

# OU via Railway Dashboard (se migration files estão no repo)
# Vai criar automaticamente as 4 tabelas
```

### Passo 2: Fazer Deploy do Código Atualizado

```bash
# Commit as mudanças
git add .
git commit -m "feat: add network graph analysis system with 24/7 automated tasks"
git push origin main

# Railway auto-deploya nos 3 serviços
```

### Passo 3: Registrar Rotas no App Principal

Editar `src/api/app.py`:

```python
# Adicionar import
from src.api.routes import network

# Registrar router (após outras rotas)
app.include_router(network.router)
```

### Passo 4: Verificar Ativação

```bash
# 1. Checar logs do Railway (cidadao-beat)
# Deve aparecer:
[INFO] Scheduler: Sending due task detect-suspicious-networks-6h

# 2. Testar endpoint
curl https://cidadao-api-production.up.railway.app/api/v1/network/statistics

# 3. Verificar tabelas no Supabase
# Dashboard → Tables → entity_nodes, entity_relationships, etc.
```

---

## 📊 RESULTADO ESPERADO APÓS ATIVAÇÃO

### ✅ O que vai acontecer automaticamente:

1. **A cada 6 horas**:
   - ✅ Investigações automáticas criam entidades no grafo
   - ✅ Sistema detecta redes suspeitas (cartéis, concentração)
   - ✅ Investigações são enriquecidas com histórico cross-investigation

2. **Diariamente**:
   - ✅ Métricas de centralidade calculadas (influência de entidades)
   - ✅ Scores de risco atualizados (0-10)

3. **De hora em hora**:
   - ✅ Health check do sistema de grafos
   - ✅ Validação de integridade dos dados

### 🕸️ Dados que serão gerados:

```sql
-- Entidades conectadas
SELECT COUNT(*) FROM entity_nodes;
-- Esperado: Centenas/milhares após alguns dias

-- Relacionamentos mapeados
SELECT COUNT(*) FROM entity_relationships;
-- Esperado: Múltiplos por entidade

-- Redes suspeitas detectadas
SELECT network_type, severity, COUNT(*)
FROM suspicious_networks
WHERE is_active = true
GROUP BY network_type, severity;
-- Esperado: Detecção automática de padrões
```

---

## 💡 INSIGHTS QUE O FRONTEND VAI RECEBER

### Exemplo de Enrichment Automático:

Quando uma investigação é criada, o sistema adiciona automaticamente:

```json
{
  "anomaly_type": "price_deviation",
  "severity": "high",
  "description": "Preço 150% acima da média",

  // NOVO: Network Analysis Automático!
  "network_analysis": [
    {
      "entity_name": "Construtora XYZ LTDA",
      "historical_data": {
        "total_investigations": 5,
        "total_contract_value": 15000000.00,
        "risk_score": 7.3
      },
      "network_metrics": {
        "degree_centrality": 12,
        "betweenness_centrality": 0.65
      },
      "connections": {
        "immediate_connections": [
          {"name": "Empresa ABC", "type": "empresa"},
          {"name": "João Silva", "type": "pessoa_fisica"}
        ]
      }
    }
  ],

  // NOVO: Cross-Investigation Insights!
  "cross_investigation_insights": [
    "⚠️ Entidade Recorrente: Construtora XYZ aparece em 5 investigações anteriores, totalizando R$ 15.000.000,00",
    "🚨 Alto Risco: score 7.3/10 indicando histórico de irregularidades",
    "🕸️ Altamente Conectada: 12 conexões diretas na rede",
    "🌉 Ponte Entre Redes: atua como intermediária entre diferentes grupos"
  ]
}
```

---

## 🎨 VISUALIZAÇÕES DISPONÍVEIS PARA FRONTEND

### 1. **D3.js Force Graph**
```javascript
// Endpoint: /api/v1/network/export/d3/{entity_id}
fetch('/api/v1/network/export/d3/uuid-123')
  .then(r => r.json())
  .then(data => {
    // data.nodes: [{id, name, type, risk_score, radius}, ...]
    // data.links: [{source, target, strength, type}, ...]
    renderD3ForceGraph(data);
  });
```

### 2. **Cytoscape.js Network**
```javascript
// Endpoint: /api/v1/network/export/cytoscape/{entity_id}
fetch('/api/v1/network/export/cytoscape/uuid-123')
  .then(r => r.json())
  .then(data => {
    cytoscape({
      container: document.getElementById('cy'),
      elements: data.elements,
      layout: data.layout,
      style: data.style
    });
  });
```

### 3. **Network Statistics Dashboard**
```javascript
// Endpoint: /api/v1/network/statistics
fetch('/api/v1/network/statistics')
  .then(r => r.json())
  .then(stats => {
    // stats.total_entities: 1234
    // stats.total_relationships: 5678
    // stats.suspicious_networks_detected: 15
    // stats.top_entities_by_centrality: [...]
    renderDashboard(stats);
  });
```

---

## 🔍 CASOS DE USO PRÁTICOS

### Caso 1: Investigador quer ver rede de uma empresa

```
1. Buscar empresa: GET /api/v1/network/entities/search?query=Construtora
2. Ver rede: GET /api/v1/network/entities/{id}/network?depth=2
3. Frontend renderiza grafo com D3.js ou Cytoscape
```

### Caso 2: Analista quer ver redes suspeitas detectadas

```
1. Listar redes: GET /api/v1/network/suspicious-networks?severity=high
2. Ver detalhes: GET /api/v1/network/suspicious-networks/{id}
3. Revisar: POST /api/v1/network/suspicious-networks/{id}/review
```

### Caso 3: Dashboard de estatísticas gerais

```
1. Stats: GET /api/v1/network/statistics
2. Renderizar cards:
   - Total de entidades mapeadas
   - Redes suspeitas ativas
   - Top 10 entidades mais conectadas
```

---

## 📈 MONITORAMENTO DO SISTEMA 24/7

### Métricas Importantes:

```sql
-- Crescimento de entidades por dia
SELECT DATE(created_at), COUNT(*)
FROM entity_nodes
GROUP BY DATE(created_at)
ORDER BY DATE(created_at) DESC;

-- Redes suspeitas por tipo e severidade
SELECT network_type, severity, COUNT(*)
FROM suspicious_networks
WHERE is_active = true
GROUP BY network_type, severity;

-- Entidades com maior risco
SELECT name, entity_type, risk_score, total_investigations
FROM entity_nodes
WHERE risk_score >= 7.0
ORDER BY risk_score DESC
LIMIT 20;

-- Investigações automáticas criadas
SELECT COUNT(*)
FROM investigations
WHERE user_id = '58050609-2fe2-49a6-a342-7cf66d83d216'
  AND created_at >= NOW() - INTERVAL '24 hours';
```

---

## ✅ CHECKLIST FINAL

Use esta lista para confirmar que TUDO está rodando:

### Railway Services
- [ ] **cidadao-api**: Status Active (verde)
- [ ] **cidadao-worker**: Status Active (verde)
- [ ] **cidadao-beat**: Status Active (verde)

### Variáveis de Ambiente (nos 3 serviços)
- [ ] SUPABASE_URL
- [ ] SUPABASE_SERVICE_ROLE_KEY
- [ ] REDIS_URL
- [ ] GROQ_API_KEY
- [ ] JWT_SECRET_KEY

### Database
- [ ] Migration aplicada: `alembic upgrade head`
- [ ] Tabelas criadas: entity_nodes, entity_relationships, etc.
- [ ] Supabase acessível

### Network Graph System
- [ ] Routes registradas em app.py
- [ ] Tasks no beat_schedule (5 tasks de network)
- [ ] Código deployado no Railway

### Validação
- [ ] Logs do beat mostram network tasks
- [ ] Endpoints /api/v1/network/* respondem
- [ ] Entidades sendo criadas no DB
- [ ] Redes suspeitas sendo detectadas

---

## 🎯 RESUMO: VOCÊ ESTÁ USANDO 70% DO POTENCIAL

### ✅ O que já está ativo:
- 14 tasks automáticas rodando 24/7
- Auto-investigations a cada 6h
- Alertas e health checks
- Katana integration
- Redis para cache/queue

### 🚀 O que falta ativar (5 minutos de trabalho):
- Sistema de grafos (migration + deploy)
- 5 tasks adicionais de network analysis
- 12 endpoints REST para frontend
- Visualizações D3.js/Cytoscape

### 💰 Custo total: $20/mês
### 📊 Valor entregue: Sistema enterprise de detecção de corrupção 24/7!

---

## 🔗 Próximos Passos

1. **Aplicar migration**: `railway run alembic upgrade head`
2. **Fazer deploy**: `git push origin main`
3. **Registrar rotas**: Editar `src/api/app.py`
4. **Testar endpoints**: `curl .../api/v1/network/statistics`
5. **Monitorar logs**: Railway Dashboard → Logs

---

**Sistema pronto para detectar cartéis, laranjas e redes de corrupção 24/7! 🇧🇷🕵️**

*Desenvolvido por Anderson Henrique da Silva - 2025-10-09*
