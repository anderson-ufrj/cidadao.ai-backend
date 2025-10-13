# 🚂 Railway Deployment Guide

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

**Author**: Anderson Henrique da Silva
**Date**: 2025-10-07 21:40:00

## 🎯 Estratégia de Deploy

O Railway possui uma **ordem de prioridade** para detectar como executar sua aplicação:

1. **Procfile** ← **USAMOS ESTE** ✅
2. railway.toml / railway.json
3. nixpacks.toml
4. Dockerfile
5. Auto-detecção de arquivos Python

## ⚠️ Problema Comum: Porta Errada

### Sintoma
```
🚀 Starting Cidadão.AI Full API - VERSION 2025-09-20 13:46:00
🌐 Running on 0.0.0.0:7860  # ❌ ERRADO - porta do HuggingFace
```

### Causa
Railway está executando `start_hf.py` ou `app.py` ao invés do Procfile porque:
- Existem arquivos de configuração conflitantes (railway.toml, railway.json, nixpacks.toml)
- Railway tenta "adivinhar" o melhor método e escolhe errado

### Solução
**Remova TODOS os arquivos de configuração exceto o Procfile:**

```bash
# Fazer backup dos arquivos conflitantes
mv railway.toml railway.toml.backup
mv railway.json railway.json.backup
mv nixpacks.toml nixpacks.toml.backup

# Railway agora usará APENAS o Procfile
git add .
git commit -m "fix(deploy): force Railway to use Procfile for correct PORT"
git push origin main
```

## 📋 Procfile Correto

```procfile
# Main API server - usa $PORT do Railway
web: uvicorn src.api.app:app --host 0.0.0.0 --port $PORT

# Celery worker para tasks em background
worker: celery -A src.infrastructure.queue.celery_app worker --loglevel=info --queues=critical,high,default,low,background --concurrency=4

# Celery beat para investigações 24/7
beat: celery -A src.infrastructure.queue.celery_app beat --loglevel=info
```

## 🔧 Variáveis de Ambiente Necessárias

Configure no Railway Dashboard (Settings → Variables):

### Obrigatórias
```bash
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
JWT_SECRET_KEY=ZreYJKfHts0RU3EU...  # Gerar com: python3 -c "import secrets; print(secrets.token_urlsafe(64))"
SECRET_KEY=gm_vrQ054CziyUEWbV...     # Gerar com: python3 -c "import secrets; print(secrets.token_urlsafe(64))"
ENVIRONMENT=production
APP_ENV=production
```

### Opcionais
```bash
TRANSPARENCY_API_KEY=e24f842355f72...
DADOS_GOV_API_KEY=eyJhbGciOiJIUzI...
REDIS_URL=redis://...  # Railway auto-provisiona se adicionar Redis
```

### Auto-Provisionadas pelo Railway
```bash
PORT=8000  # Railway injeta automaticamente
RAILWAY_ENVIRONMENT=production
```

## ✅ Verificação de Deploy Correto

### Logs Esperados
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000  # ✅ CORRETO - porta dinâmica
```

### Healthcheck
```bash
# Teste manual
curl https://seu-app.railway.app/health

# Resposta esperada
{
  "status": "healthy",
  "timestamp": "2025-10-07T21:40:00",
  "version": "1.0.0"
}
```

## 🚀 Deploy de Múltiplos Serviços

O Procfile define 3 serviços, mas Railway inicialmente cria apenas o `web`. Para adicionar worker e beat:

### Via Dashboard
1. New Service → "Create service from Procfile"
2. Selecione o repositório
3. Escolha o processo type: `worker` ou `beat`
4. Configure as mesmas variáveis de ambiente

### Via CLI
```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Criar serviço worker
railway service create --name cidadao-ai-worker --process worker

# Criar serviço beat
railway service create --name cidadao-ai-beat --process beat
```

## 🔍 Troubleshooting

### Deploy falha com "Invalid PORT"
**Causa**: Arquivos de configuração conflitantes
**Solução**: Remova railway.toml, railway.json, nixpacks.toml

### App roda na porta 7860
**Causa**: Railway está executando start_hf.py ou app.py
**Solução**: Force uso do Procfile (veja seção "Solução" acima)

### Healthcheck falha
**Causa**: Variáveis de ambiente faltando ou incorretas
**Solução**: Verifique todas as variáveis obrigatórias no Dashboard

### Worker não inicia
**Causa**: REDIS_URL não configurado
**Solução**:
```bash
# Via Dashboard
Add Redis service → Copy URL → Add to env vars

# Via CLI
railway add redis
```

## 📊 Monitoramento

### Metrics no Railway
- Acesse: Dashboard → Metrics
- CPU, Memory, Network usage
- Request rate e latency

### Logs em Tempo Real
```bash
# Via CLI
railway logs

# Via Dashboard
Dashboard → Logs → Live logs
```

### Grafana (Opcional)
```bash
# Configurar variáveis para métricas externas
PROMETHEUS_PUSHGATEWAY_URL=https://...
GRAFANA_CLOUD_API_KEY=...
```

## 💰 Custos Estimados

### Hobby Plan (Recomendado para desenvolvimento)
- **$5/mês**: 500h de execução + $5 de créditos
- **Redis gratuito**: 100MB
- **Total**: ~$5-10/mês

### Pro Plan (Produção)
- **$20/mês**: Execução ilimitada
- **Redis**: $10/mês (1GB)
- **Total**: ~$30/mês

## 🔄 CI/CD Automático

Railway faz deploy automaticamente quando você push para main:

```bash
git add .
git commit -m "feat: add new feature"
git push origin main

# Railway detecta push → Build → Deploy → Healthcheck
```

## 📚 Recursos

- [Railway Docs](https://docs.railway.app)
- [Procfile Reference](https://docs.railway.app/deploy/deployments#procfile)
- [Environment Variables](https://docs.railway.app/develop/variables)
- [Multiple Services](https://docs.railway.app/deploy/monorepo)

---

**🎯 Regra de Ouro**: Mantenha APENAS o Procfile para Railway. Remova todos os outros arquivos de configuração para evitar conflitos!
