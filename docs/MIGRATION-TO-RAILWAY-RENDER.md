# 🚀 Migração para Railway ou Render (Guia Completo)

**Author**: Anderson Henrique da Silva
**Date**: 2025-10-07 18:30:00
**Dificuldade**: ⭐ Fácil (15-30 minutos)

## 🎯 Por Que Migrar?

### Problema Atual (HuggingFace Spaces)
- ❌ Sem suporte a Celery workers
- ❌ Sem Redis incluso
- ❌ Impossível rodar 24/7 auto-investigations
- ✅ API funciona perfeitamente

### Solução (Railway/Render)
- ✅ Workers 24/7 automáticos
- ✅ Redis incluído
- ✅ Deploy com 1 clique
- ✅ Logs centralizados
- ✅ Scaling automático
- ✅ Git push = deploy automático

## 💰 Comparação de Custos

### Opção 1: 🚂 Railway (RECOMENDADO)

| Serviço | Preço |
|---------|-------|
| FastAPI API | Incluído no plano |
| Celery Worker | Incluído no plano |
| Celery Beat | Incluído no plano |
| Redis | **GRÁTIS** (incluído) |
| **Total** | **~$10-15/mês** |

**Crédito grátis**: $5/mês

### Opção 2: 🎨 Render

| Serviço | Preço |
|---------|-------|
| FastAPI API | $7/mês |
| Celery Worker | $7/mês |
| Celery Beat | $7/mês |
| Redis | $10/mês |
| **Total** | **$31/mês** |

**Free tier**: 750h grátis/mês (mas limitado)

### Opção 3: Híbrido (Mais Barato)

| Serviço | Provider | Preço |
|---------|----------|-------|
| FastAPI API | HuggingFace | GRÁTIS |
| Workers + Redis | Railway | $10/mês |
| **Total** | | **$10/mês** |

## 🏆 Recomendação: Railway

**Por quê?**
1. ✅ Mais barato ($10-15 vs $31)
2. ✅ Redis grátis incluído
3. ✅ Interface mais simples
4. ✅ Deploy mais rápido
5. ✅ $5 crédito grátis/mês

---

# 🚂 Migração para Railway (PASSO A PASSO)

## Preparação (5 minutos)

### 1. Criar Conta Railway

1. Acesse https://railway.app
2. Sign up com GitHub
3. Conecte seu cartão (não será cobrado nos primeiros $5)

### 2. Preparar Variáveis de Ambiente

Tenha em mãos (do HuggingFace Spaces):
```bash
SUPABASE_URL=https://xxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJI...
GROQ_API_KEY=gsk_xxxxxxx
TRANSPARENCY_API_KEY=xxxxxxx (opcional)
```

## Deploy (10 minutos)

### Método 1: CLI (Mais Rápido) ⚡

```bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# ou
brew install railway

# 2. Login
railway login

# 3. Inicializar projeto
cd cidadao.ai-backend
railway init

# 4. Adicionar Redis
railway add redis

# 5. Adicionar variáveis de ambiente
railway variables set SUPABASE_URL="https://xxxxxxx.supabase.co"
railway variables set SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJI..."
railway variables set GROQ_API_KEY="gsk_xxxxxxx"

# 6. Deploy!
railway up

# 7. Ver logs
railway logs
```

### Método 2: Dashboard (Mais Visual) 🖱️

#### Passo 1: Criar Novo Projeto

1. Acesse https://railway.app/new
2. Clique em **"Deploy from GitHub repo"**
3. Selecione `anderson-ufrj/cidadao.ai-backend`
4. Clique em **"Deploy Now"**

#### Passo 2: Adicionar Redis

1. No dashboard do projeto, clique **"+ New"**
2. Selecione **"Database" → "Redis"**
3. Railway cria automaticamente e conecta com `REDIS_URL`

#### Passo 3: Configurar Variáveis

1. Clique no service **cidadao-ai-backend**
2. Vá em **"Variables"** tab
3. Adicione cada variável:

```
SUPABASE_URL=https://xxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
TRANSPARENCY_API_KEY=xxxxxxxxxxxxxxxx
ENVIRONMENT=production
```

**⚠️ IMPORTANTE**: `REDIS_URL` é criada automaticamente, não adicione manualmente!

#### Passo 4: Criar Services Separados

Railway detecta automaticamente o `Procfile`, mas vamos garantir:

1. No dashboard, clique **"+ New" → "Empty Service"**
2. Conecte ao mesmo repositório GitHub
3. Configure cada service:

**Service 1: API** (já criado)
- Start Command: `uvicorn src.api.app:app --host 0.0.0.0 --port $PORT`
- Healthcheck: `/health`

**Service 2: Worker**
- Start Command: `celery -A src.infrastructure.queue.celery_app worker --loglevel=info --queues=critical,high,default,low,background --concurrency=4`
- Copie todas variáveis de ambiente do API

**Service 3: Beat**
- Start Command: `celery -A src.infrastructure.queue.celery_app beat --loglevel=info`
- Copie `REDIS_URL` do Redis service

#### Passo 5: Deploy

1. Cada service fará deploy automático
2. Aguarde ~2-3 minutos
3. Railway mostrará URLs públicas

#### Passo 6: Verificar

```bash
# Testar API
curl https://cidadao-ai-backend-production.up.railway.app/health

# Ver logs Worker
railway logs --service worker

# Ver logs Beat
railway logs --service beat
```

---

# 🎨 Migração para Render (ALTERNATIVA)

## Deploy (10 minutos)

### Método 1: Blueprint (Automático) 🚀

```bash
# 1. Commit render.yaml (já está no repo)
git add render.yaml
git commit -m "feat: add Render blueprint"
git push

# 2. Acesse Render Dashboard
# https://dashboard.render.com

# 3. New → Blueprint
# Conecte repositório GitHub
# Render lê render.yaml e cria tudo automaticamente!

# 4. Configurar variáveis manualmente no dashboard
# (Render não pode ler secrets de arquivo)
```

### Método 2: Manual (Mais Controle) 🖱️

#### Passo 1: Criar Redis

1. Dashboard → **New** → **Redis**
2. Nome: `cidadao-ai-redis`
3. Plan: **Starter** ($10/mês) ou **Free** (limitado)
4. Região: **Oregon**
5. Create

Copie a **Internal Redis URL** (formato: `redis://...`)

#### Passo 2: Criar Web Service (API)

1. Dashboard → **New** → **Web Service**
2. Conecte repositório GitHub
3. Configure:
   - **Name**: `cidadao-ai-api`
   - **Region**: Oregon
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.api.app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Starter ($7/mês)
4. Environment Variables:
   ```
   SUPABASE_URL=https://xxxxxxx.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJhbG...
   GROQ_API_KEY=gsk_xxx
   REDIS_URL=redis://internal-redis-url
   ```

#### Passo 3: Criar Background Worker

1. Dashboard → **New** → **Background Worker**
2. Conecte mesmo repositório
3. Configure:
   - **Name**: `cidadao-ai-worker`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `celery -A src.infrastructure.queue.celery_app worker --loglevel=info --queues=critical,high,default,low,background --concurrency=4`
   - **Plan**: Starter ($7/mês)
4. Copie mesmas environment variables do API

#### Passo 4: Criar Beat Service

1. Dashboard → **New** → **Background Worker**
2. Configure:
   - **Name**: `cidadao-ai-beat`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `celery -A src.infrastructure.queue.celery_app beat --loglevel=info`
   - **Plan**: Starter ($7/mês)
3. Adicione apenas `REDIS_URL`

---

# ✅ Validação Pós-Deploy

## 1. Testar API

```bash
# Testar health
curl https://your-app.railway.app/health
# ou
curl https://your-app.onrender.com/health

# Deve retornar:
# {"status": "healthy", ...}
```

## 2. Testar Workers

```bash
# Railway
railway logs --service worker

# Render
# Ver logs no dashboard

# Deve mostrar:
# [INFO] celery@worker ready
# [INFO] Tasks: auto_monitor_new_contracts, ...
```

## 3. Testar Beat

```bash
# Ver logs
# Deve mostrar a cada 6h:
# [INFO] Scheduler: Sending due task auto-monitor-new-contracts-6h
```

## 4. Testar Investigação Automática

```bash
# Forçar execução imediata
curl -X POST https://your-app/api/v1/investigations/trigger-auto \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 5. Verificar no Supabase

```sql
-- Ver investigações criadas pelo sistema
SELECT * FROM investigations
WHERE user_id = 'system_auto_monitor'
ORDER BY created_at DESC;
```

---

# 🔄 Migração Gradual (Zero Downtime)

Se quiser migrar sem derrubar o sistema:

## Fase 1: Workers Primeiro

1. Deploy Workers + Beat no Railway/Render
2. Mantenha API no HuggingFace
3. Ambos salvam no mesmo Supabase
4. **Teste por 1 semana**

## Fase 2: Migrar API (Opcional)

1. Atualize DNS/Frontend para nova URL
2. Migre API para Railway/Render
3. Desligue HuggingFace Spaces

## Rollback (Se Necessário)

```bash
# Railway
railway rollback

# Render
# Dashboard → Deploys → Rollback to previous
```

---

# 📊 Monitoramento

## Railway

```bash
# Logs em tempo real
railway logs --service api
railway logs --service worker
railway logs --service beat

# Métricas
railway metrics

# Status
railway status
```

## Render

- Dashboard → Logs (built-in)
- Dashboard → Metrics (CPU, RAM, Network)
- Alertas por email automáticos

---

# 💡 Dicas de Otimização

## Reduzir Custos

### Railway

```bash
# Use sleep mode para serviços não-críticos
# API: Always on
# Worker: Always on
# Beat: Always on (scheduler precisa estar 24/7)
```

### Render

```bash
# Use Free tier para serviços de baixo uso
# Mas lembre: Free tier tem cold starts (delay de 30s+)
```

## Melhorar Performance

```yaml
# Aumentar concurrency do worker
--concurrency=8  # Se tiver >2GB RAM

# Usar múltiplos workers
# Railway/Render: Adicionar mais replicas
```

---

# 🆘 Troubleshooting

## Erro: Module not found

**Causa**: requirements.txt não instalado

**Solução**:
```bash
# Verificar build logs
# Adicionar ao buildCommand:
pip install --upgrade pip && pip install -r requirements.txt
```

## Erro: Redis connection failed

**Causa**: REDIS_URL incorreta

**Solução Railway**:
```bash
# Railway adiciona automaticamente
# Verificar variável está presente:
railway variables
```

**Solução Render**:
```bash
# Copiar Internal Redis URL do Redis service
# Colar em REDIS_URL dos outros services
```

## Workers não executam tasks

**Causa**: Beat não está rodando

**Solução**:
```bash
# Verificar se Beat service está UP
# Ver logs do Beat:
railway logs --service beat
# Deve mostrar: "Scheduler: Sending due task..."
```

---

# 🎉 Checklist Final

- [ ] Conta Railway/Render criada
- [ ] Repositório conectado
- [ ] Redis provisionado
- [ ] 3 services criados (API, Worker, Beat)
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy bem-sucedido
- [ ] API responde em /health
- [ ] Workers logs mostram "ready"
- [ ] Beat scheduler está ativo
- [ ] Primeira investigação automática executou
- [ ] Dados aparecem no Supabase
- [ ] Frontend atualizado com nova URL (se migrou API)

---

# 📚 Recursos

- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)
- [Celery Best Practices](https://docs.celeryq.dev/en/stable/userguide/tasks.html)

---

**Total Time**: 15-30 minutos
**Difficulty**: ⭐ Easy
**Cost**: $10-31/mês (dependendo da escolha)
**Uptime**: 99.9%+
