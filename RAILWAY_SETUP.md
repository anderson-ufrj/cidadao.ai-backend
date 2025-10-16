# 🚂 Railway Setup Guide - Cidadão.AI Backend

## ✅ Pré-requisitos Concluídos
- ✅ LLM Providers configurados (Maritaca AI + Claude)
- ✅ Chaves de segurança geradas
- ✅ Sistema testado localmente
- ✅ Railway CLI instalado (v4.10.0)

## 🔐 Variáveis de Ambiente Necessárias

### LLM Providers
```bash
MARITACA_API_KEY=114276428450504196312_22f92d14b8c6e836
MARITACA_MODEL=sabiazinho-3
LLM_PROVIDER=maritaca

ANTHROPIC_API_KEY=***REDACTED-ANTHROPIC-KEY***
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

### Security Keys (Production)
```bash
JWT_SECRET_KEY=TOE5pPSfQRNqoQigSZmXS6xwYV4-giADkDClR-584jCUocothaIEsJbAW5vT7F8YbIXP0fcxOSVBtD_GWRT9Pg
SECRET_KEY=CPE3OM2D2Qn2ie4-lI4fqmMCm_-pCIDPduLnfe7mX-4mZowcgaaJ7YDiwF5dHH0HrKYD2YSvqRnCZXj-NRwRIQ
```

### Environment
```bash
ENVIRONMENT=production
DEBUG=false
```

### Supabase (já configurado)
```bash
SUPABASE_URL=https://pbsiyuattnwgohvkkkks.supabase.co
SUPABASE_SERVICE_ROLE_KEY=[sua-chave-service-role]
```

### APIs Governamentais (já configurado)
```bash
TRANSPARENCY_API_KEY=***REDACTED-TRANSPARENCY-KEY***
DADOS_GOV_API_KEY=[seu-token-dados-gov]
```

## 🚀 Método 1: Via Railway CLI (Recomendado)

### 1. Login
```bash
railway login
```

### 2. Vincular ao Projeto
```bash
# Liste seus projetos
railway list

# Vincule ao projeto (substitua pelo nome do seu projeto)
railway link
```

### 3. Configurar Variáveis Automaticamente
```bash
chmod +x railway-env-setup.sh
./railway-env-setup.sh
```

### 4. Verificar Deploy
```bash
# Ver logs em tempo real
railway logs

# Abrir projeto no browser
railway open

# Verificar status
railway status
```

## 🌐 Método 2: Via Dashboard Web

### 1. Acesse o Dashboard
https://railway.app/dashboard

### 2. Selecione seu Projeto
Clique no projeto do backend

### 3. Acesse Variables
Clique na aba **Variables** no menu lateral

### 4. Adicione as Variáveis
Cole todas as variáveis listadas acima, uma por vez:
- Clique em **+ New Variable**
- Cole o nome (ex: `MARITACA_API_KEY`)
- Cole o valor
- Clique em **Add**

### 5. Deploy Automático
O Railway fará redeploy automático após adicionar as variáveis

## ✅ Validação Pós-Deploy

### 1. Teste a URL Pública
```bash
# Substitua pela sua URL do Railway
export RAILWAY_URL="https://seu-projeto.up.railway.app"

# Teste endpoint raiz
curl $RAILWAY_URL/

# Teste health
curl $RAILWAY_URL/health/

# Teste info da API
curl $RAILWAY_URL/api/v1/info
```

### 2. Verifique os Logs
```bash
railway logs --tail 100
```

Procure por:
- ✅ `maritaca_client_initialized`
- ✅ `Cidadão.AI API started`
- ✅ `Application startup complete`
- ❌ Erros de autenticação ou variáveis faltando

### 3. Teste os LLM Providers
Você pode testar via Postman ou curl:
```bash
# Teste um endpoint que use o Maritaca
curl -X POST $RAILWAY_URL/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, teste do Maritaca AI"}'
```

## 🔍 Troubleshooting

### Erro: "JWT_SECRET_KEY environment variable is required"
- Verifique se as variáveis foram salvas corretamente
- Aguarde o redeploy completar (1-2 minutos)
- Verifique os logs: `railway logs`

### Erro: "Maritaca API key not configured"
- Confirme que `MARITACA_API_KEY` está configurado
- Verifique se não há espaços extras no valor
- Teste: `railway variables get MARITACA_API_KEY`

### Erro: "Circuit breaker is open"
- O sistema detectou falhas repetidas
- Verifique se as APIs externas estão acessíveis
- Aguarde 60 segundos para o circuit breaker resetar

### Deploy Não Completa
```bash
# Force novo deploy
railway up --detach

# Ou via dashboard: Settings > Deploy > Redeploy
```

## 📊 Monitoramento

### Logs em Tempo Real
```bash
railway logs --tail 100 --follow
```

### Métricas
Acesse o dashboard do Railway para ver:
- CPU usage
- Memory usage
- Request count
- Response times

### Alertas
Configure alertas no Railway para:
- Erros 5xx
- Alto uso de memória
- Deploy failures

## 🎯 Próximos Passos

1. ✅ Configurar todas as variáveis de ambiente
2. ✅ Verificar deploy bem-sucedido
3. ✅ Testar endpoints principais
4. 🔄 Configurar domínio customizado (opcional)
5. 🔄 Configurar backup automático do PostgreSQL
6. 🔄 Integrar com frontend

## 📚 Recursos

- Railway Docs: https://docs.railway.app/
- Railway CLI: https://docs.railway.app/develop/cli
- Suporte: https://railway.app/help

---

**Última atualização:** 2025-10-16
**Status:** ✅ Configuração completa local, pronto para deploy Railway
