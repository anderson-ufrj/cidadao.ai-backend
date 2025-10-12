# ⚡ ADICIONAR POSTGRESQL NO RAILWAY - GUIA RÁPIDO

**PRÓXIMO PASSO**: Você precisa adicionar PostgreSQL no Railway Dashboard (2 minutos)

---

## 🎯 PASSO ÚNICO: Adicionar PostgreSQL

### Via Dashboard (RECOMENDADO):

1. **Acesse**: https://railway.app/project/cidadao.ai

2. **Clique em**: `New Service`

3. **Selecione**: `Database → PostgreSQL`

4. **Aguarde 1 minuto**: Railway provisiona automaticamente

5. **PRONTO!** Railway adiciona `DATABASE_URL` em todos os serviços automaticamente ✅

---

## ✅ O QUE ACONTECE AUTOMATICAMENTE

### Railway vai:
- ✅ Criar banco PostgreSQL shared ($5/mês)
- ✅ Adicionar `DATABASE_URL` em cidadao-api, cidadao-worker, cidadao-beat
- ✅ Fazer redeploy dos 3 serviços
- ✅ Rodar `release: python -m alembic upgrade head` (migrations)
- ✅ Criar 4 tabelas do sistema de grafos

### Tempo total: **~3 minutos**

---

## 🔍 COMO VERIFICAR SE FUNCIONOU

### 1. Checar logs do deploy:

```
Railway Dashboard → cidadao-api → Deployments → Latest → View Logs
```

Deve aparecer:
```log
[INFO] Running release command: python -m alembic upgrade head
[INFO] Running upgrade -> 002_entity_graph, Add entity graph tables
[INFO] Migration successful
[INFO] Starting uvicorn...
[INFO]   Uvicorn running on http://0.0.0.0:8000
```

### 2. Testar endpoints:

```bash
# Estatísticas de rede (novo!)
curl https://cidadao-api-production.up.railway.app/api/v1/network/statistics

# Deve retornar:
{
  "total_entities": 0,
  "total_relationships": 0,
  "total_suspicious_networks": 0,
  "entity_types": {},
  "top_entities_by_centrality": [],
  "recent_suspicious_networks": []
}
```

### 3. Ver documentação:

```
https://cidadao-api-production.up.railway.app/docs
```

Deve aparecer nova seção: **"Network Analysis"** com 12 endpoints

---

## 💰 CUSTO FINAL

```
✅ Railway Pro (atual):    $20/mês
✅ PostgreSQL Shared:      $5/mês
✅ Redis (incluído):       $0/mês
────────────────────────────────
   TOTAL:                 $25/mês
```

**Para sistema enterprise 24/7 de detecção de corrupção, é baratíssimo!** 🚀

---

## 🎨 FRONTEND CONSOME VIA API REST

### Endpoints Disponíveis:

```typescript
// 1. Estatísticas gerais
GET /api/v1/network/statistics

// 2. Buscar entidades
GET /api/v1/network/entities/search?query=construtora

// 3. Rede de relacionamentos
GET /api/v1/network/entities/{id}/network?depth=2

// 4. Redes suspeitas
GET /api/v1/network/suspicious-networks?severity=high

// 5. Export D3.js
GET /api/v1/network/export/d3/{id}

// 6. Export Cytoscape.js
GET /api/v1/network/export/cytoscape/{id}

// ... e mais 6 endpoints!
```

### Exemplo Frontend (React/Next.js):

```typescript
// components/NetworkDashboard.tsx
import { useEffect, useState } from 'react';

export function NetworkDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetch('/api/v1/network/statistics')
      .then(r => r.json())
      .then(data => setStats(data));
  }, []);

  return (
    <div>
      <h2>Rede de Entidades</h2>
      <p>Total: {stats?.total_entities}</p>
      <p>Relacionamentos: {stats?.total_relationships}</p>
      <p>Redes Suspeitas: {stats?.total_suspicious_networks}</p>
    </div>
  );
}
```

---

## 🚀 DEPOIS DE ADICIONAR POSTGRESQL

### Tasks Automáticas vão começar a rodar:

| Task | Frequência | O que faz |
|------|------------|-----------|
| **calculate-network-metrics** | 24h | Calcula centralidade de todas entidades |
| **detect-suspicious-networks** | 6h | Detecta cartéis, concentração, laranjas |
| **enrich-investigations** | 6h | Adiciona contexto cross-investigation |
| **update-risk-scores** | 24h | Atualiza scores de risco (0-10) |
| **network-health-check** | 1h | Monitora sistema de grafos |

### Dados gerados automaticamente:

```sql
-- Entidades mapeadas
SELECT COUNT(*) FROM entity_nodes;

-- Relacionamentos
SELECT COUNT(*) FROM entity_relationships;

-- Redes suspeitas detectadas
SELECT network_type, severity, COUNT(*)
FROM suspicious_networks
WHERE is_active = true
GROUP BY network_type, severity;
```

---

## 🔄 SE QUISER VOLTAR PARA SUPABASE

Sem problemas! Basta:

```bash
# 1. Remover DATABASE_URL do Railway
railway variables --remove DATABASE_URL

# 2. Adicionar Supabase de volta
railway variables --set SUPABASE_URL=https://pbsiyuattnwgohvkkkks.supabase.co
railway variables --set SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...

# 3. Código volta automaticamente para Supabase REST
```

---

## ✅ CHECKLIST

- [ ] Acessar Railway Dashboard: https://railway.app/project/cidadao.ai
- [ ] Clicar em "New Service"
- [ ] Selecionar "Database → PostgreSQL"
- [ ] Aguardar provisionamento (1 min)
- [ ] Aguardar redeploy automático (2-3 min)
- [ ] Verificar logs: migrations rodaram?
- [ ] Testar endpoint: `/api/v1/network/statistics`
- [ ] Ver docs: `/docs` (seção Network Analysis)
- [ ] ✅ SISTEMA COMPLETO 24/7 FUNCIONANDO!

---

## 🎯 RESULTADO FINAL

### ✅ O que você terá:
- 🗄️ PostgreSQL nativo Railway
- 🕸️ Sistema de grafos completo
- 📊 19 tasks automáticas 24/7 (14 + 5 novas)
- 🚀 12 endpoints REST para frontend
- 📈 Detecção automática de redes suspeitas
- 💰 Custo: $25/mês (ainda barato!)

### 🎨 Frontend:
- ✅ Consome tudo via API REST
- ✅ D3.js / Cytoscape.js visualizations
- ✅ Dashboard de estatísticas
- ✅ Busca de entidades
- ✅ Análise de redes suspeitas

---

**🇧🇷 Sistema pronto para detectar corrupção 24/7! 🕵️**

*Último passo: Adicionar PostgreSQL no Railway Dashboard (2 minutos)* 🚂
