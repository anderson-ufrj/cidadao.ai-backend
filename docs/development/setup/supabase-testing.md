# 🧪 Teste do Sistema Supabase + Katana + Alertas

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

## ✅ Pré-requisitos

- [x] Schema SQL executado no Supabase
- [x] Variáveis configuradas no Railway:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `ALERT_WEBHOOKS` (opcional - Discord/Slack)

## 🚀 Teste Manual Completo

### 1. Trigger Manual do Katana Monitor

```bash
# Endpoint do Railway
RAILWAY_URL="https://seu-app.railway.app"

# Trigger manual (requer autenticação)
curl -X POST "$RAILWAY_URL/api/v1/tasks/trigger/katana-monitor" \
  -H "Authorization: Bearer seu-token-jwt" \
  -H "Content-Type: application/json"
```

**Resposta esperada:**
```json
{
  "task_id": "abc-123-def-456",
  "task_name": "monitor_katana_dispensas",
  "status": "queued",
  "message": "Katana monitoring task has been queued."
}
```

### 2. Verificar Status da Task

```bash
curl "$RAILWAY_URL/api/v1/tasks/status/abc-123-def-456"
```

**Resposta esperada:**
```json
{
  "task_id": "abc-123-def-456",
  "status": "SUCCESS",
  "ready": true,
  "result": {
    "dispensas_fetched": 50,
    "anomalies_detected": 3,
    "investigations_created": 3,
    "anomalies": [...]
  }
}
```

### 3. Verificar Dados no Supabase

#### 3.1. Verificar Auto Investigations

```sql
-- No Supabase SQL Editor
SELECT
    id,
    query,
    initiated_by,
    status,
    created_at
FROM auto_investigations
ORDER BY created_at DESC
LIMIT 10;
```

#### 3.2. Verificar Anomalias Detectadas

```sql
SELECT
    a.id,
    a.title,
    a.severity,
    a.anomaly_score,
    a.source,
    a.created_at,
    ai.query as investigation_query
FROM anomalies a
LEFT JOIN auto_investigations ai ON a.auto_investigation_id = ai.id
ORDER BY a.created_at DESC
LIMIT 10;
```

#### 3.3. Verificar Dispensas Salvas

```sql
SELECT
    id,
    numero,
    objeto,
    valor,
    fornecedor_nome,
    created_at
FROM katana_dispensas
ORDER BY created_at DESC
LIMIT 10;
```

#### 3.4. Verificar Alertas Enviados

```sql
SELECT
    al.id,
    al.alert_type,
    al.severity,
    al.title,
    al.status,
    al.sent_at,
    a.anomaly_score
FROM alerts al
JOIN anomalies a ON al.anomaly_id = a.id
ORDER BY al.created_at DESC
LIMIT 10;
```

### 4. Usar Views Criadas

#### View: High Severity Anomalies

```sql
SELECT * FROM high_severity_anomalies
LIMIT 10;
```

#### View: Anomaly Stats by Source

```sql
SELECT * FROM anomaly_stats_by_source;
```

#### View: Auto Investigation Summary

```sql
SELECT * FROM auto_investigation_summary
LIMIT 10;
```

### 5. Teste de Função Helper

```sql
-- Estatísticas dos últimos 7 dias
SELECT * FROM get_anomaly_stats(7);

-- Estatísticas dos últimos 30 dias
SELECT * FROM get_anomaly_stats(30);
```

## 📊 Verificar Logs do Celery

### No Railway Dashboard:

1. Acesse o serviço **Worker**
2. Veja os logs em tempo real
3. Procure por:

```
katana_monitor_started
Fetched X dispensas from Katana API
auto_investigation_and_anomaly_created_in_supabase
alerts_sent_for_anomaly
```

### No serviço **Beat**:

Procure pelos schedules executando:

```
Scheduler: Sending due task katana-monitor-dispensas-6h
Scheduler: Sending due task auto-monitor-new-contracts-6h
```

## 🔔 Teste de Webhooks

### Se configurou Discord Webhook:

1. Vá no canal do Discord
2. Aguarde alertas aparecerem quando anomalias forem detectadas
3. Formato esperado:

```
🚨 ALERTA DE ANOMALIA - CRITICAL

Anomalia detectada: Dispensa 123/2025

📊 Score: 0.9234
📍 Fonte: katana_scan
🔍 Tipo: price_deviation

⚠️ Indicadores:
- Valor 300% acima da média
- Fornecedor novo sem histórico

💡 Recomendações:
- Investigar histórico do fornecedor
- Verificar justificativa técnica
```

## 🐛 Troubleshooting

### Erro: "Column 'initiated_by' does not exist"

**Causa**: Você executou o schema antigo que tentava recriar a tabela investigations

**Solução**: Você já executou `supabase_schema_compatible.sql` ✅

### Erro: "No module named 'supabase'"

**Causa**: Dependência não instalada

**Solução**:
```bash
pip install supabase
```

### Erro: "Service role key not found"

**Causa**: Variável `SUPABASE_SERVICE_ROLE_KEY` não configurada

**Solução**: Configure no Railway dashboard

### Task retorna erro 500

**Passos**:
1. Verifique logs do Worker no Railway
2. Confirme que `GROQ_API_KEY` está configurada
3. Verifique se Katana API está acessível
4. Teste manualmente: `curl http://katanascan.xenoumena.com/get-all -H "Authorization: Bearer qa5oAa2WvJl"`

## 📈 Métricas de Sucesso

Após rodar o teste manual, você deve ter:

- ✅ Auto investigations criadas na tabela `auto_investigations`
- ✅ Anomalias detectadas e salvas na tabela `anomalies`
- ✅ Dispensas cacheadas na tabela `katana_dispensas`
- ✅ Alertas enviados para webhooks (se configurado)
- ✅ Alertas registrados na tabela `alerts`
- ✅ Logs do Celery mostrando sucesso

## 🎯 Próximos Passos

1. **Aguardar Execução Automática**: O Celery Beat executará automaticamente a cada 6 horas
2. **Configurar Dashboard**: Criar visualizações no Supabase ou Grafana
3. **Expandir Fontes**: Adicionar Portal da Transparência quando endpoints funcionarem
4. **Email Alerts**: Configurar SendGrid/AWS SES para alertas por email

## 📚 Queries Úteis

### Top 10 Anomalias por Score

```sql
SELECT
    title,
    anomaly_score,
    severity,
    source,
    created_at
FROM anomalies
WHERE status != 'false_positive'
ORDER BY anomaly_score DESC
LIMIT 10;
```

### Anomalias por Dia (últimos 7 dias)

```sql
SELECT
    DATE(created_at) as date,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE severity = 'critical') as critical,
    COUNT(*) FILTER (WHERE severity = 'high') as high
FROM anomalies
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### Taxa de Sucesso de Alertas

```sql
SELECT
    alert_type,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'sent') as sent,
    COUNT(*) FILTER (WHERE status = 'failed') as failed,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'sent')::numeric /
        COUNT(*)::numeric * 100,
        2
    ) as success_rate
FROM alerts
GROUP BY alert_type;
```
