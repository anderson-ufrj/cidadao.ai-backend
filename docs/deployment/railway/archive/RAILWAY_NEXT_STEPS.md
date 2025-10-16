# 🚀 Railway Deployment - Próximos Passos

**Data:** 2025-10-16 15:05 BRT
**Status:** 🔴 AÇÃO NECESSÁRIA

---

## 🎯 O QUE ACONTECEU

### 1. Erro Anterior (Resolvido)
- ❌ **Alembic falhava**: `ModuleNotFoundError: No module named 'psycopg2'`
- ✅ **Corrigido**: Adicionado `psycopg2-binary>=2.9.9` ao `requirements.txt`
- ✅ **Commit**: `13859dc` - `fix(deps): add psycopg2-binary for Alembic migrations`
- ✅ **Pushed**: Código enviado para GitHub

### 2. Problema Atual (Não Resolvido)
- ❌ **DATABASE_URL** e **REDIS_URL** ainda estão **VAZIAS** no cidadao-api
- ❌ **Você fez redeploy ANTES de configurar** as variáveis
- ❌ **Resultado**: API usando in-memory (sem persistência)

---

## ✅ AÇÃO NECESSÁRIA AGORA

### PASSO 1: Aguarde Deploy Atual Terminar (2-3 minutos)

O Railway está fazendo build com o `psycopg2-binary` agora. **Aguarde esse deploy completar**.

Você vai ver no log:
```
✅ Successfully installed psycopg2-binary-2.9.9
✅ python -m alembic upgrade head (vai passar)
```

### PASSO 2: Configure DATABASE_URL e REDIS_URL no Dashboard

**DEPOIS** que o deploy acima completar:

1. **Acesse:** https://railway.app/project/56a814f2-e891-4b63-b20f-1dd8f8b356fc

2. **Clique em "cidadao-api"**

3. **Vá em "Variables"**

4. **Configure DATABASE_URL:**
   - Se a variável existe mas está vazia: Clique na caixa VALUE
   - Se não existe: Clique em "+ New Variable"
   - **Nome**: `DATABASE_URL`
   - **Valor**: `postgresql://postgres:ymDpsVmsGYUCTVSNHJXVnHszSAKHCevH@postgres.railway.internal:5432/railway`

5. **Configure REDIS_URL:**
   - **Nome**: `REDIS_URL`
   - **Valor**: `redis://default:ixPHfkkBJfSZgIVmmAFnQxTSWzqFipEm@cidadao-redis.railway.internal:6379`

6. **NÃO clique em Redeploy ainda!**

### PASSO 3: Aguarde Redeploy Automático (1-2 minutos)

Ao salvar as variáveis, Railway **automaticamente** faz redeploy.

### PASSO 4: Verifique os Logs

**Procure por:**
```
✅ 🐘 Using PostgreSQL direct connection for investigations (Railway/VPS)
✅ Database connection established
✅ Redis connection successful
```

**NÃO deve aparecer:**
```
❌ ⚠️  Using IN-MEMORY investigation service (no persistence!)
```

---

## 📋 Checklist

- [ ] Deploy atual (com psycopg2-binary) completou?
- [ ] DATABASE_URL configurado no cidadao-api?
- [ ] REDIS_URL configurado no cidadao-api?
- [ ] Redeploy automático completou?
- [ ] Logs mostram "🐘 Using PostgreSQL direct connection"?

---

## 🎉 Quando Funcionar

### Teste de Persistência

```bash
# 1. Health check
curl https://cidadao-api-production.up.railway.app/health/

# 2. Criar investigação (se tiver JWT)
curl -X POST "https://cidadao-api-production.up.railway.app/api/v1/investigations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{"query": "Teste PostgreSQL persistência", "data_source": "contracts"}'

# 3. Verificar no PostgreSQL Railway
# Dashboard → Postgres → Query:
SELECT COUNT(*) FROM investigations;
# Deve retornar > 0
```

---

## 🔧 Próximos Passos (Depois)

Quando cidadao-api estiver funcionando com PostgreSQL:

### Configure Workers (Optional)

Se você tiver os serviços `cidadao.ai-worker` e `cidadao.ai-beat`:

1. **cidadao.ai-worker** → Variables:
   - DATABASE_URL = `postgresql://postgres:ymDpsVmsGYUCTVSNHJXVnHszSAKHCevH@postgres.railway.internal:5432/railway`
   - REDIS_URL = `redis://default:ixPHfkkBJfSZgIVmmAFnQxTSWzqFipEm@cidadao-redis.railway.internal:6379`

2. **cidadao.ai-beat** → Variables:
   - Mesmas configurações acima

---

## 🆘 Se Algo Der Errado

### Railway ainda mostrando in-memory?

Verifique que as variáveis foram salvas:

```bash
export RAILWAY_TOKEN=9c8d2a3d-bf20-454e-8fe1-8296c5e57fa7
railway variables --service cidadao-api | grep -E "(DATABASE_URL|REDIS_URL)"
```

Deve mostrar as URLs completas (não vazias).

### Alembic ainda falhando?

Veja o log de build procurando por:
```
Successfully installed psycopg2-binary-2.9.9
```

Se não estiver lá, o código ainda não foi atualizado.

---

## 📊 Resumo Visual

```
Estado Atual:
┌─────────────────────────────────────┐
│ ✅ psycopg2-binary adicionado       │
│ ✅ Código pushed para GitHub        │
│ 🔄 Railway fazendo build agora      │
│ ❌ DATABASE_URL ainda vazio         │
│ ❌ REDIS_URL ainda vazio            │
└─────────────────────────────────────┘

Próximo Estado (Após configurar):
┌─────────────────────────────────────┐
│ ✅ psycopg2-binary instalado        │
│ ✅ DATABASE_URL configurado         │
│ ✅ REDIS_URL configurado            │
│ ✅ PostgreSQL funcionando! 🐘        │
│ ✅ Persistência ativa               │
└─────────────────────────────────────┘
```

---

**Status Atual:** Aguardando você configurar DATABASE_URL e REDIS_URL no Railway Dashboard
**ETA:** 5 minutos para resolução completa
**Última Atualização:** 2025-10-16 15:05 BRT
