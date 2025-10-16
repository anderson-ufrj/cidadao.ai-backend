# 📋 Como Ver Logs no Railway

**Data:** 2025-10-16
**Projeto:** cidadao.ai (56a814f2-e891-4b63-b20f-1dd8f8b356fc)

---

## 🌐 Opção 1: Railway Dashboard (Mais Fácil)

### Via Web Browser

1. **Acesse:** https://railway.app/project/56a814f2-e891-4b63-b20f-1dd8f8b356fc

2. **Clique no serviço** que quer ver logs:
   - `cidadao-api` - API principal
   - `Postgres` - PostgreSQL
   - `cidadao-redis` - Redis
   - `cidadao.ai-worker` - Celery Worker
   - `cidadao.ai-beat` - Celery Beat

3. **Vá na aba "Deployments"**

4. **Clique no deployment mais recente**

5. **Veja os logs em tempo real**

**Filtros úteis:**
- Procure por `🐘` para ver se está usando PostgreSQL
- Procure por `error` para ver erros
- Procure por `investigation` para ver criação de investigações
- Procure por `PostgreSQL` para ver conexão com banco

---

## 💻 Opção 2: Via Railway CLI (Limitações)

### ⚠️ Problema Atual

O Railway CLI v4.10.0 tem um **bug de autenticação** conhecido:
- `railway login` funciona no browser ✅
- Mas CLI não reconhece o token ❌
- Mesmo com `RAILWAY_TOKEN` exportado ❌

### Tentativas que NÃO funcionaram:

```bash
# ❌ Não funciona
export RAILWAY_TOKEN=9c8d2a3d-bf20-454e-8fe1-8296c5e57fa7
railway logs

# ❌ Não funciona
railway logs --service cidadao-api

# ❌ Não funciona
railway whoami
```

**Erro retornado:**
```
Unauthorized. Please login with `railway login`
```

### ✅ O que FUNCIONA via CLI:

**1. Ver status do projeto:**
```bash
export RAILWAY_TOKEN=9c8d2a3d-bf20-454e-8fe1-8296c5e57fa7
railway status
```

**Saída:**
```
Project: cidadao.ai
Environment: production
Service: None
```

**2. Ver variáveis de ambiente:**
```bash
export RAILWAY_TOKEN=9c8d2a3d-bf20-454e-8fe1-8296c5e57fa7
railway run --service Postgres env | grep DATABASE
```

**Saída:**
```
DATABASE_URL=postgresql://postgres:...@postgres.railway.internal:5432/railway
```

---

## 🔍 Opção 3: Verificar Logs Via API em Produção

### Testar se PostgreSQL está funcionando:

```bash
# 1. Health check
curl https://cidadao-api-production.up.railway.app/health/

# 2. API info
curl https://cidadao-api-production.up.railway.app/api/v1/info

# 3. Verificar banco diretamente (via script Python)
venv/bin/python << 'EOF'
import asyncio
import asyncpg

async def main():
    conn = await asyncpg.connect(
        "postgresql://postgres:***REDACTED-PG-PASSWORD***@centerbeam.proxy.rlwy.net:38094/railway"
    )
    count = await conn.fetchval("SELECT COUNT(*) FROM investigations")
    print(f"Total investigations: {count}")

    rows = await conn.fetch("""
        SELECT id::text, user_id, query, created_at
        FROM investigations
        ORDER BY created_at DESC
        LIMIT 5
    """)

    for r in rows:
        print(f"{r['user_id']:20} | {r['query'][:40]:40} | {r['created_at']}")

    await conn.close()

asyncio.run(main())
EOF
```

---

## 📊 O que Procurar nos Logs

### ✅ Sinais de Sucesso (PostgreSQL):

```
✅ "🐘 Using PostgreSQL direct connection for investigations (Railway/VPS)"
✅ "Database connection established"
✅ "Redis connection successful"
✅ "Application startup complete"
```

### ⚠️ Sinais de Problema:

```
❌ "⚠️ Using IN-MEMORY investigation service (no persistence!)"
❌ "connection to database failed"
❌ "Redis connection refused"
❌ "relation 'investigations' does not exist"
```

### 🔍 Logs Importantes para Debug:

```bash
# Startup
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000

# PostgreSQL Connection
🐘 Using PostgreSQL direct connection for investigations (Railway/VPS)

# Investigation Created
investigation_created investigation_id=... user_id=... data_source=contracts

# Investigation Completed
investigation_completed investigation_id=... anomalies_found=5 confidence_score=0.87
```

---

## 🐛 Troubleshooting Railway CLI

### Se quiser tentar forçar autenticação:

```bash
# 1. Fazer login novamente
railway login

# 2. Verificar se token foi salvo
cat ~/.railway/config.json

# 3. Tentar listar projetos
railway list

# 4. Vincular ao projeto
railway link
```

**Se ainda não funcionar:**

Use o **Railway Dashboard** no navegador. É mais confiável e tem interface melhor.

---

## 🚀 Verificação Rápida (30 segundos)

Execute este script para ver tudo de uma vez:

```bash
cat > /tmp/quick_check.sh << 'EOF'
#!/bin/bash

echo "🔍 Verificação Rápida - cidadao.ai Railway"
echo "==========================================="
echo ""

echo "1. API Health:"
curl -s https://cidadao-api-production.up.railway.app/health/ | python3 -m json.tool
echo ""

echo "2. API Info:"
curl -s https://cidadao-api-production.up.railway.app/api/v1/info | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"API: {d['api']['name']}\"); print(f\"Agents: {len([x for x in d.get('agents', {})])} disponíveis\")"
echo ""

echo "3. PostgreSQL Railway:"
venv/bin/python -c "
import asyncio, asyncpg
async def main():
    conn = await asyncpg.connect('postgresql://postgres:***REDACTED-PG-PASSWORD***@centerbeam.proxy.rlwy.net:38094/railway')
    count = await conn.fetchval('SELECT COUNT(*) FROM investigations')
    print(f'   Investigações: {count}')
    await conn.close()
asyncio.run(main())
"

echo ""
echo "✅ Verificação concluída!"
EOF

chmod +x /tmp/quick_check.sh
/tmp/quick_check.sh
```

---

## 📝 Resumo

**Para ver logs:**
- ✅ **Use Railway Dashboard** (recomendado)
- ❌ **Railway CLI** tem bugs de autenticação
- ✅ **Teste direto via API** funciona sempre

**URLs importantes:**
- Dashboard: https://railway.app/project/56a814f2-e891-4b63-b20f-1dd8f8b356fc
- API: https://cidadao-api-production.up.railway.app/
- Docs: https://cidadao-api-production.up.railway.app/docs

---

**Última Atualização:** 2025-10-16
**Status:** ✅ PostgreSQL Railway funcionando perfeitamente
