# 🎯 Como Configurar DATABASE_URL e REDIS_URL no Railway Dashboard

**Tempo:** 5 minutos
**Método:** Railway Dashboard (100% confiável)

---

## 🎯 O QUE FAZER

Você vai **DELETAR** as Shared Variables que não funcionam e criar as variáveis **diretamente** nos serviços.

**POR QUÊ?** As Shared Variables com `${{Postgres.DATABASE_URL}}` ficam **VAZIAS** no cidadao-api (bug ou limitação do Railway).

**IMPORTANTE:** Depois de configurar, é **MUITO FÁCIL** atualizar. Se mudar a senha do Postgres, você só precisa copiar/colar a nova URL. Leva 30 segundos.

---

## 📋 PASSO 1: DELETAR SHARED VARIABLES (Não Funcionam)

1. **Acesse:** https://railway.app/project/56a814f2-e891-4b63-b20f-1dd8f8b356fc

2. **Clique em "Shared Variables"** (no menu lateral esquerdo)

3. **Delete as variáveis** (se existirem):
   - `DATABASE_URL`
   - `REDIS_URL`

   **Como deletar:**
   - Passe o mouse sobre a variável
   - Clique no ícone de **lixeira** 🗑️
   - Confirme

---

## 📋 PASSO 2: COPIAR DATABASE_URL DO POSTGRES

1. **Acesse:** https://railway.app/project/56a814f2-e891-4b63-b20f-1dd8f8b356fc

2. **Clique no serviço "Postgres"** (no sidebar)

3. **Vá na aba "Variables"**

4. **Procure a variável `DATABASE_URL`**
   O valor será algo como:
   ```
   postgresql://postgres:ymDpsVmsGYUCTVSNHJXVnHszSAKHCevH@postgres.railway.internal:5432/railway
   ```

5. **Clique no ícone de COPIAR** 📋 ao lado do valor

6. **Cole em um bloco de notas temporariamente** (vamos usar 3x)

---

## 📋 PASSO 3: COPIAR REDIS_URL DO REDIS

1. **Ainda em:** https://railway.app/project/56a814f2-e891-4b63-b20f-1dd8f8b356fc

2. **Clique no serviço "cidadao-redis"** (no sidebar)

3. **Vá na aba "Variables"**

4. **Procure a variável `REDIS_URL`**
   O valor será algo como:
   ```
   redis://default:ixPHfkkBJfSZgIVmmAFnQxTSWzqFipEm@cidadao-redis.railway.internal:6379
   ```

5. **Clique no ícone de COPIAR** 📋

6. **Cole em um bloco de notas** (vamos usar 3x)

---

## 📋 PASSO 4: CONFIGURAR CIDADAO-API (Principal)

1. **Acesse:** https://railway.app/project/56a814f2-e891-4b63-b20f-1dd8f8b356fc

2. **Clique no serviço "cidadao-api"** (no sidebar)

3. **Vá na aba "Variables"**

4. **Procure a variável `DATABASE_URL`** (deve estar vazia ou não existir)

5. **Se estiver vazia:**
   - Clique na caixa de texto do **VALUE**
   - Cole a `DATABASE_URL` que você copiou do Postgres
   - A variável será atualizada automaticamente

6. **Se não existir:**
   - Clique em **"+ New Variable"** ou **"Add Variable"**
   - **Variable Name:** `DATABASE_URL`
   - **Variable Value:** Cole a URL do Postgres
   - Clique em **"Add"**

7. **Repita para `REDIS_URL`:**
   - Procure ou crie `REDIS_URL`
   - Cole o valor que você copiou do cidadao-redis

8. **IMPORTANTE:** NÃO clique em Redeploy ainda!

---

## 📋 PASSO 5: CONFIGURAR CIDADAO.AI-WORKER (Se Existir)

1. **Clique no serviço "cidadao.ai-worker"** (no sidebar)

2. **Vá na aba "Variables"**

3. **Configure as MESMAS variáveis:**
   - `DATABASE_URL` = Cole a URL do Postgres
   - `REDIS_URL` = Cole a URL do Redis

4. **NÃO clique em Redeploy ainda!**

---

## 📋 PASSO 6: CONFIGURAR CIDADAO.AI-BEAT (Se Existir)

1. **Clique no serviço "cidadao.ai-beat"** (no sidebar)

2. **Vá na aba "Variables"**

3. **Configure as MESMAS variáveis:**
   - `DATABASE_URL` = Cole a URL do Postgres
   - `REDIS_URL` = Cole a URL do Redis

4. **NÃO clique em Redeploy ainda!**

---

## 📋 PASSO 7: FORÇAR REDEPLOY DO CIDADAO-API

1. **Volte para o serviço "cidadao-api"**

2. **Vá na aba "Deployments"**

3. **Clique em "Redeploy"** (botão no canto superior direito)

4. **Aguarde ~2 minutos** para o deploy completar

---

## 📋 PASSO 8: VERIFICAR LOGS

1. **Ainda em "cidadao-api" → "Deployments"**

2. **Clique no deployment mais recente** (topo da lista)

3. **Veja os logs em tempo real**

4. **Procure por:**

   **✅ SUCESSO - Deve Aparecer:**
   ```
   🐘 Using PostgreSQL direct connection for investigations (Railway/VPS)
   Database connection established
   Redis connection successful
   Application startup complete
   ```

   **❌ FALHA - NÃO Deve Aparecer:**
   ```
   ⚠️  Using IN-MEMORY investigation service (no persistence!)
   ```

---

## 🎉 PRONTO!

Se você viu `🐘 Using PostgreSQL direct connection` nos logs, **FUNCIONOU**!

### Como Testar Persistência:

```bash
# 1. Health check
curl https://cidadao-api-production.up.railway.app/health/

# 2. Criar investigação (se tiver JWT token)
curl -X POST "https://cidadao-api-production.up.railway.app/api/v1/investigations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -d '{"query": "Teste PostgreSQL Railway", "data_source": "contracts"}'

# 3. Verificar no Postgres Railway (Dashboard → Postgres → Query)
SELECT COUNT(*) FROM investigations;
```

---

## 🔄 COMO ATUALIZAR NO FUTURO (30 segundos)

**Se mudar senha do Postgres ou Redis:**

1. Copie a nova URL do serviço Postgres/Redis
2. Cole em cidadao-api → Variables → DATABASE_URL/REDIS_URL
3. A variável atualiza automaticamente
4. Redeploy (Railway detecta a mudança)

**Não precisa reconfigurar do zero!**

---

## 🆘 SE AINDA NÃO FUNCIONAR

Me mande os primeiros 50 linhas dos logs do deployment. Procure especialmente por:

- Mensagens com `investigation service`
- Mensagens com `database` ou `PostgreSQL`
- Qualquer erro relacionado a conexão

---

**Última Atualização:** 2025-10-16 14:58 BRT
**Status:** Aguardando configuração manual via Dashboard
