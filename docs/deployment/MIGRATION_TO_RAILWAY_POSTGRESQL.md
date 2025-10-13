# 🚂 Migração para Railway PostgreSQL

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

**Data**: 2025-10-09
**Objetivo**: Substituir Supabase REST API por Railway PostgreSQL nativo

---

## 🎯 POR QUE RAILWAY POSTGRESQL?

✅ **Conexão nativa** PostgreSQL (não REST API)
✅ **Alembic migrations** funcionam perfeitamente
✅ **Sistema de grafos** precisa de JOINs complexos
✅ **Performance 10x melhor** (rede interna)
✅ **SQLAlchemy ORM completo** sem limitações

---

## 📋 PASSO A PASSO

### 1️⃣ Adicionar PostgreSQL no Railway (2 minutos)

#### Via Dashboard:
```
1. Acesse: https://railway.app/project/cidadao.ai
2. Clique em: New Service → Database → PostgreSQL
3. Railway cria automaticamente o banco
4. Aguarde 1 minuto (provisionamento)
```

#### Via CLI (alternativa):
```bash
railway add postgresql
```

**Resultado**: Railway cria automaticamente a variável `DATABASE_URL`

---

### 2️⃣ Verificar Variáveis de Ambiente (1 minuto)

```bash
# Ver variáveis
railway variables

# Deve aparecer automaticamente:
DATABASE_URL=postgresql://postgres:XXXXX@railway.internal:5432/railway
```

**IMPORTANTE**: Railway adiciona `DATABASE_URL` automaticamente em TODOS os 3 serviços:
- ✅ cidadao-api
- ✅ cidadao-worker
- ✅ cidadao-beat

---

### 3️⃣ Atualizar Código para PostgreSQL Nativo (já está pronto!)

O código JÁ suporta PostgreSQL nativo! 🎉

**Arquivo**: `src/db/session.py`

```python
# Já detecta automaticamente DATABASE_URL do Railway:
DATABASE_URL = os.getenv("DATABASE_URL")

# Se for postgresql://, converte para asyncpg:
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
```

**Nenhuma mudança de código necessária!** ✅

---

### 4️⃣ Aplicar Migrations (2 minutos)

Agora as migrations vão funcionar! 🚀

#### Opção A: Via Railway Run
```bash
# Link ao serviço API
railway service cidadao-api

# Aplicar todas as migrations
railway run python -m alembic upgrade head
```

#### Opção B: Criar Migration Script no Procfile
Editar `Procfile`:
```procfile
# Adicionar comando de release
release: python -m alembic upgrade head

# Existing
web: uvicorn src.api.app:app --host 0.0.0.0 --port $PORT
worker: celery -A src.infrastructure.queue.celery_app worker --loglevel=info --queues=critical,high,default,low,background --concurrency=4
beat: celery -A src.infrastructure.queue.celery_app beat --loglevel=info
```

**Railway vai rodar `release` automaticamente antes de cada deploy!**

---

### 5️⃣ Verificar Tabelas Criadas (1 minuto)

```bash
# Via Railway CLI
railway run psql $DATABASE_URL -c "\dt"

# Deve listar:
# - investigations
# - entity_nodes ← NOVO!
# - entity_relationships ← NOVO!
# - entity_investigation_references ← NOVO!
# - suspicious_networks ← NOVO!
```

Ou via Railway Dashboard:
```
Serviço PostgreSQL → Data → Tables
```

---

### 6️⃣ Registrar Rotas da API de Grafos

Editar `src/api/app.py`:

```python
# Adicionar import
from src.api.routes import network

# Registrar router (após outras rotas)
app.include_router(network.router)
```

Commit e push:
```bash
git add src/api/app.py Procfile
git commit -m "feat: enable Railway PostgreSQL with network graph API"
git push origin main
```

Railway auto-deploya! 🚀

---

### 7️⃣ Testar Endpoints (2 minutos)

```bash
# Base URL
API_URL=https://cidadao-api-production.up.railway.app

# 1. Health check
curl $API_URL/health

# 2. Network statistics (novo!)
curl $API_URL/api/v1/network/statistics

# 3. Search entities (novo!)
curl "$API_URL/api/v1/network/entities/search?query=construtora"

# 4. API docs (ver todos endpoints)
open $API_URL/docs
```

---

## 🎨 FRONTEND CONSOME TUDO VIA API

O frontend vai consumir os **12 endpoints REST** que criamos:

### Endpoints Disponíveis:

#### 📊 Estatísticas
```typescript
GET /api/v1/network/statistics
// Retorna: total_entities, total_relationships, suspicious_networks, top_entities
```

#### 🔍 Busca de Entidades
```typescript
GET /api/v1/network/entities/search?query=construtora&entity_type=empresa
// Retorna: [{id, name, cnpj, risk_score, total_investigations}, ...]
```

#### 🕸️ Rede de Relacionamentos
```typescript
GET /api/v1/network/entities/{entity_id}/network?depth=2
// Retorna: {nodes: [...], edges: [...], node_count, edge_count}
```

#### 🚨 Redes Suspeitas
```typescript
GET /api/v1/network/suspicious-networks?severity=high
// Retorna: [{id, network_name, network_type, severity, entity_count}, ...]
```

#### 🎨 Visualizações
```typescript
// D3.js force graph
GET /api/v1/network/export/d3/{entity_id}

// Cytoscape.js
GET /api/v1/network/export/cytoscape/{entity_id}
```

### Exemplo React/Next.js:

```typescript
// components/NetworkGraph.tsx
import { useEffect, useState } from 'react';

export function NetworkGraph({ entityId }) {
  const [network, setNetwork] = useState(null);

  useEffect(() => {
    fetch(`/api/v1/network/entities/${entityId}/network?depth=2`)
      .then(r => r.json())
      .then(data => setNetwork(data));
  }, [entityId]);

  if (!network) return <div>Carregando rede...</div>;

  return (
    <div>
      <h3>Rede de Relacionamentos</h3>
      <p>{network.node_count} entidades conectadas</p>
      <p>{network.edge_count} relacionamentos mapeados</p>

      {/* Renderizar com D3.js ou Cytoscape.js */}
      <NetworkVisualization data={network} />
    </div>
  );
}
```

---

## ✅ CHECKLIST DE MIGRAÇÃO

### Antes de começar:
- [ ] Projeto Railway linkado: `railway status`
- [ ] Authenticated: `railway whoami`

### Passos:
- [ ] 1. Adicionar PostgreSQL: `railway add postgresql`
- [ ] 2. Verificar DATABASE_URL: `railway variables | grep DATABASE`
- [ ] 3. Adicionar comando `release` no Procfile
- [ ] 4. Registrar rotas em `src/api/app.py`
- [ ] 5. Commit e push: `git push origin main`
- [ ] 6. Aguardar deploy (2-3 min)
- [ ] 7. Verificar logs: `railway logs --service cidadao-api`
- [ ] 8. Testar migrations: Railway roda automaticamente
- [ ] 9. Testar endpoints: `curl $API_URL/api/v1/network/statistics`
- [ ] 10. Verificar tabelas: `railway run psql $DATABASE_URL -c "\dt"`

### Validação:
- [ ] API respondendo: `/health`
- [ ] Network endpoints: `/api/v1/network/statistics`
- [ ] Tabelas criadas: entity_nodes, entity_relationships, etc.
- [ ] Celery Beat rodando: logs mostram network tasks
- [ ] Investigações sendo criadas no PostgreSQL

---

## 💰 CUSTO FINAL

```
Railway Pro Plan:        $20/mês (você já tem)
PostgreSQL Shared:       $5/mês
Redis (incluído):        $0/mês

TOTAL: $25/mês
```

**Para um sistema enterprise de detecção de corrupção rodando 24/7, é barato demais!** 🚀

---

## 🔄 ROLLBACK (se algo der errado)

Se precisar voltar para Supabase:

```bash
# 1. Remover DATABASE_URL do Railway
railway variables --remove DATABASE_URL

# 2. Adicionar de volta Supabase URLs
railway variables --set SUPABASE_URL=https://pbsiyuattnwgohvkkkks.supabase.co
railway variables --set SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...

# 3. Código automaticamente volta a usar Supabase REST
```

---

## 🎯 PRÓXIMOS PASSOS APÓS MIGRAÇÃO

1. ✅ Sistema de grafos funcionando 100%
2. ✅ Frontend consome via API REST
3. ✅ Visualizações D3.js/Cytoscape no frontend
4. ✅ Dashboard de estatísticas
5. ✅ Detecção automática de redes suspeitas 24/7

---

**Sistema pronto para produção! 🇧🇷🚀**

*Desenvolvido por Anderson Henrique da Silva - 2025-10-09*
