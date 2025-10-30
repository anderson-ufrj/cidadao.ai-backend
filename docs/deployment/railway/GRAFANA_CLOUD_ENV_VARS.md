# Variáveis de Ambiente - Grafana Cloud

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Data**: 2025-10-30

---

## 📋 Configuração Railway

### Passo a Passo

1. **Acesse Railway Dashboard**:
   - URL: https://railway.app/
   - Projeto: `cidadao-ai-backend`

2. **Abra as variáveis**:
   - Clique no serviço `cidadao-api-production`
   - Aba **"Variables"**

3. **Adicione as variáveis abaixo**:

---

## 🔑 Variáveis Obrigatórias

### GRAFANA_CLOUD_ENABLED
```bash
GRAFANA_CLOUD_ENABLED=true
```
**Descrição**: Ativa o push de métricas para Grafana Cloud
**Valores**: `true` ou `false`
**Padrão**: `false`

---

### GRAFANA_CLOUD_URL
```bash
GRAFANA_CLOUD_URL=https://prometheus-prod-XX-prod-us-east-0.grafana.net/api/prom/push
```
**Descrição**: Endpoint Prometheus Remote Write do Grafana Cloud
**Como obter**:
1. Login no Grafana Cloud
2. Menu → "Connections" → "Add new connection"
3. Procure "Prometheus"
4. Copie o "Remote Write Endpoint"

**⚠️ Importante**:
- Deve incluir `/api/prom/push` no final
- Região pode variar: `us-east-0`, `eu-west-0`, etc.

---

### GRAFANA_CLOUD_USER
```bash
GRAFANA_CLOUD_USER=123456
```
**Descrição**: Username/Instance ID do Grafana Cloud
**Como obter**:
1. Mesmo local do URL (Connections → Prometheus)
2. Campo "Username" ou "Instance ID"

**Formato**: Número de 6 dígitos (ex: `123456`)

---

### GRAFANA_CLOUD_KEY
```bash
GRAFANA_CLOUD_KEY=glc_eyJvIjoiMTIzNDU2IiwibiI6InRlc3QiLCJrIjoiYWJjZGVm...
```
**Descrição**: API Key do Grafana Cloud
**Como obter**:
1. Mesmo local (Connections → Prometheus)
2. Campo "Password" ou "API Key"
3. Clique em "Generate" se necessário

**⚠️ Importante**:
- Começa com `glc_`
- Token longo (~200+ caracteres)
- **Não compartilhe** este valor!

---

## ⚙️ Variáveis Opcionais

### METRICS_PUSH_INTERVAL
```bash
METRICS_PUSH_INTERVAL=60
```
**Descrição**: Intervalo em segundos entre pushes de métricas
**Padrão**: `60` (1 minuto)
**Recomendado**:
- Produção: `60` (métricas a cada 1 minuto)
- Teste: `30` (métricas a cada 30 segundos)

---

### METRICS_PUSH_TIMEOUT
```bash
METRICS_PUSH_TIMEOUT=10
```
**Descrição**: Timeout em segundos para push de métricas
**Padrão**: `10`
**Recomendado**: `10` ou `15` (ajuste se houver timeouts)

---

## 📝 Exemplo Completo

Copie e cole no Railway (ajuste os valores):

```bash
# Grafana Cloud Monitoring
GRAFANA_CLOUD_ENABLED=true
GRAFANA_CLOUD_URL=https://prometheus-prod-13-prod-us-east-0.grafana.net/api/prom/push
GRAFANA_CLOUD_USER=123456
GRAFANA_CLOUD_KEY=glc_eyJvIjoiMTIzNDU2IiwibiI6InRlc3QiLCJrIjoiYWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTYifQ==

# Optional: Push Settings
METRICS_PUSH_INTERVAL=60
METRICS_PUSH_TIMEOUT=10
```

---

## ✅ Validação

### 1. Verificar Variáveis (Railway CLI)

```bash
# Login
railway login

# Link ao projeto
railway link

# Listar variáveis
railway variables | grep GRAFANA
```

**Resultado esperado**:
```
GRAFANA_CLOUD_ENABLED=true
GRAFANA_CLOUD_URL=https://prometheus-prod-XX...
GRAFANA_CLOUD_USER=123456
GRAFANA_CLOUD_KEY=glc_...
```

### 2. Verificar no Dashboard

1. Railway Dashboard → Seu projeto
2. Aba "Variables"
3. Procure por variáveis começando com `GRAFANA_CLOUD_`

### 3. Testar Localmente (Opcional)

```bash
# Copie as variáveis para .env local
echo "GRAFANA_CLOUD_ENABLED=true" >> .env
echo "GRAFANA_CLOUD_URL=https://..." >> .env
echo "GRAFANA_CLOUD_USER=123456" >> .env
echo "GRAFANA_CLOUD_KEY=glc_..." >> .env

# Execute o script de teste
python scripts/test_grafana_cloud.py
```

**Resultado esperado**:
```
✅ All tests passed!
🎯 Grafana Cloud integration is working correctly
```

---

## 🚀 Deploy

Após configurar as variáveis:

```bash
# 1. Commit das mudanças (se houver código novo)
git add .
git commit -m "feat(monitoring): add Grafana Cloud integration"
git push origin main

# 2. Railway fará auto-deploy
# 3. Aguarde 2-3 minutos
# 4. Verifique logs
railway logs --follow
```

**Logs esperados**:
```
Starting Grafana Cloud metrics push loop (interval: 60s)
Grafana Cloud metrics pusher started
Metrics pushed to Grafana Cloud successfully
```

---

## 🐛 Troubleshooting

### Erro: "Authentication failed"

**Causa**: Credenciais incorretas

**Solução**:
1. Regere API key no Grafana Cloud
2. Atualize `GRAFANA_CLOUD_KEY` no Railway
3. Redeploy (Railway → Deployments → Redeploy)

---

### Erro: "Connection timeout"

**Causa**: URL incorreta ou firewall

**Solução**:
1. Verifique se URL inclui `/api/prom/push`
2. Teste URL manualmente:
```bash
curl -u "USER:KEY" https://prometheus-prod-XX.grafana.net/api/prom/push
# Deve retornar 200 ou 204
```

---

### Erro: "Grafana Cloud push not started"

**Causa**: `GRAFANA_CLOUD_ENABLED` não está `true`

**Solução**:
1. Verifique variável no Railway
2. Deve ser exatamente `true` (lowercase)
3. Redeploy se necessário

---

### Métricas não aparecem no Grafana

**Checklist**:

1. ✅ Variáveis configuradas corretamente?
2. ✅ Deploy bem-sucedido no Railway?
3. ✅ Logs mostram "Metrics pushed successfully"?
4. ✅ Time range no Grafana está correto? (últimos 5min)
5. ✅ Data source selecionado corretamente?

**Query de teste no Grafana**:
```promql
up{job="cidadao-ai-backend"}
```

---

## 📚 Recursos

- **Grafana Cloud Docs**: https://grafana.com/docs/grafana-cloud/
- **Prometheus Remote Write**: https://prometheus.io/docs/prometheus/latest/configuration/configuration/#remote_write
- **Railway Environment Variables**: https://docs.railway.app/develop/variables

---

**Guia criado**: 2025-10-30
**Autor**: Anderson Henrique da Silva, Minas Gerais, Brasil
