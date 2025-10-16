# 🔧 Railway DATABASE_URL Fix - Variable Not Being Injected

**Data:** 2025-10-16 14:50 BRT
**Status:** 🔴 PROBLEMA ATIVO
**Sintoma:** Application usando in-memory storage apesar de DATABASE_URL configurado

---

## 🐛 Problema Atual

### Evidência dos Logs (17:49 UTC / 14:49 BRT)
```
[inf]  ⚠️  Using IN-MEMORY investigation service (no persistence!)
```

### O que Sabemos
- ✅ DATABASE_URL configurado nas Shared Variables: `${{Postgres.DATABASE_URL}}`
- ✅ Redeploy forçado executado (commit `0936c8f`)
- ✅ API online e funcionando
- ❌ DATABASE_URL **NÃO** sendo injetado no container
- ❌ Application caindo no fallback in-memory

### Por que Isso Acontece

O código em `src/services/investigation_service_selector.py:36` verifica:
```python
def _has_postgres_config() -> bool:
    return bool(os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL"))
```

Se `os.getenv("DATABASE_URL")` retorna `None`, significa que a variável **não existe** no ambiente do container.

---

## ✅ SOLUÇÃO 1: Variável Direta no Serviço (Recomendada)

Em vez de usar Shared Variables com referência `${{Postgres.DATABASE_URL}}`, configure a variável **diretamente** no serviço `cidadao-api`.

### Passo 1: Obter a DATABASE_URL Real do Postgres

**Via Railway Dashboard:**

1. Acesse: https://railway.app/project/56a814f2-e891-4b63-b20f-1dd8f8b356fc
2. Clique no serviço **"Postgres"**
3. Vá na aba **"Variables"** ou **"Connect"**
4. **Copie** o valor completo de `DATABASE_URL`

O formato será algo como:
```
postgresql://postgres:SENHA@HOST:PORTA/railway
```

**Via Railway CLI:**
```bash
export RAILWAY_TOKEN=9c8d2a3d-bf20-454e-8fe1-8296c5e57fa7

# Listar variáveis do Postgres
railway variables --service Postgres
```

### Passo 2: Configurar no cidadao-api

**Opção A: Via Railway Dashboard (Mais Fácil)**

1. Acesse: https://railway.app/project/56a814f2-e891-4b63-b20f-1dd8f8b356fc
2. Clique no serviço **"cidadao-api"** (NÃO Shared Variables!)
3. Vá em **"Variables"**
4. Clique em **"Add Variable"**
5. Nome: `DATABASE_URL`
6. Valor: Cole a URL completa que você copiou do Postgres
7. Clique em **"Add"**
8. Clique em **"Redeploy"** (botão no canto superior direito)

**Opção B: Via Railway CLI**
```bash
export RAILWAY_TOKEN=9c8d2a3d-bf20-454e-8fe1-8296c5e57fa7

# Vincular ao projeto e serviço
railway link 56a814f2-e891-4b63-b20f-1dd8f8b356fc
railway service cidadao-api

# Adicionar variável (substitua pela URL real)
railway variables set DATABASE_URL="postgresql://postgres:***REDACTED-PG-PASSWORD***@centerbeam.proxy.rlwy.net:38094/railway"

# Forçar redeploy
railway up
```

### Passo 3: Verificar Logs

Após o redeploy (~2 minutos), você deve ver:

```
✅ 🐘 Using PostgreSQL direct connection for investigations (Railway/VPS)
✅ Database connection established
✅ Alembic upgrade head completed
✅ Application startup complete
```

**NÃO deve aparecer:**
```
❌ ⚠️  Using IN-MEMORY investigation service
```

---

## ✅ SOLUÇÃO 2: Diagnosticar Variáveis Disponíveis

Se a Solução 1 não funcionar, precisamos ver **exatamente** quais variáveis estão disponíveis no container.

### Adicionar Endpoint de Diagnóstico (Temporário)

Adicione este endpoint ao `src/api/app.py`:

```python
@app.get("/debug/env", include_in_schema=False)
async def debug_env():
    """DEBUG ONLY - Remove in production!"""
    import os

    critical_vars = [
        "DATABASE_URL",
        "SUPABASE_DB_URL",
        "POSTGRES_URL",
        "POSTGRESQL_URL",
        "REDIS_URL",
    ]

    result = {}
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            # Mask passwords
            if "postgresql://" in value:
                parts = value.split("@")
                result[var] = f"{parts[0][:30]}...@{parts[1]}" if len(parts) > 1 else "set"
            else:
                result[var] = f"{value[:20]}..." if len(value) > 20 else "set"
        else:
            result[var] = "NOT_SET"

    return result
```

Depois do redeploy, acesse:
```bash
curl https://cidadao-api-production.up.railway.app/debug/env
```

Isso mostrará quais variáveis estão realmente disponíveis.

---

## ✅ SOLUÇÃO 3: Verificar Nome do Serviço Postgres

O problema pode ser que o serviço Postgres tem um nome diferente de "Postgres".

### Via Railway Dashboard

1. Acesse: https://railway.app/project/56a814f2-e891-4b63-b20f-1dd8f8b356fc
2. Veja a lista de serviços no sidebar esquerdo
3. **Confirme** o nome EXATO do serviço PostgreSQL
4. Se não for "Postgres", atualize a Shared Variable:

Exemplo se o nome for `postgres` (minúsculo):
```
DATABASE_URL = ${{postgres.DATABASE_URL}}
```

Ou se for `cidadao-postgres`:
```
DATABASE_URL = ${{cidadao-postgres.DATABASE_URL}}
```

---

## 🎯 Qual Solução Usar?

### Use SOLUÇÃO 1 se:
- ✅ Você quer resolver RÁPIDO (5 minutos)
- ✅ Não se importa em ter a URL hardcoded no serviço
- ✅ Quer garantia que vai funcionar

### Use SOLUÇÃO 3 se:
- ✅ Prefere manter referência dinâmica `${{...}}`
- ✅ Quer descobrir por que a referência não funciona
- ✅ Tem tempo para investigar

### Use SOLUÇÃO 2 se:
- ✅ Soluções 1 e 3 não funcionaram
- ✅ Precisa ver exatamente o que está disponível
- ✅ Quer entender o problema em profundidade

---

## 📋 Checklist de Verificação

Depois de aplicar qualquer solução:

```bash
# 1. Health check
curl https://cidadao-api-production.up.railway.app/health/

# 2. Verificar logs no Railway Dashboard
# Procurar por: "🐘 Using PostgreSQL direct connection"
# NÃO deve ter: "⚠️  Using IN-MEMORY"

# 3. Testar criação de investigação (se tiver JWT)
curl -X POST "https://cidadao-api-production.up.railway.app/api/v1/investigations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "Test Railway PostgreSQL", "data_source": "contracts"}'

# 4. Verificar no PostgreSQL Railway (via Dashboard → Postgres → Query)
SELECT COUNT(*) FROM investigations;
# Deve retornar > 0 se teve investigações criadas
```

---

## 🚨 Importante

### Para REDIS_URL

O mesmo problema pode afetar `REDIS_URL`. Aplique a mesma solução:

**Via Dashboard cidadao-api → Variables:**
```
REDIS_URL = redis://default:SENHA@HOST:PORTA
```

(Copie do serviço `cidadao-redis` → Variables → REDIS_URL)

### Para Workers (Beat e Worker)

Depois de corrigir cidadao-api, aplique as MESMAS variáveis nos serviços:
- `cidadao.ai-worker`
- `cidadao.ai-beat`

Ambos precisam de:
```
DATABASE_URL = <mesma URL do cidadao-api>
REDIS_URL = <mesma URL do cidadao-api>
```

---

## 📝 Recomendação Final

**MAIS RÁPIDO**: Use **SOLUÇÃO 1** (variável direta).

1. Copie DATABASE_URL do serviço Postgres
2. Cole no serviço cidadao-api
3. Redeploy
4. Verifique logs em 2 minutos

Se funcionar (99% de chance), repita para REDIS_URL e depois para os workers.

---

**Status:** 🔴 Aguardando aplicação da solução
**Próximo Passo:** Escolher uma solução e aplicar
**ETA:** 5-10 minutos para resolução completa
