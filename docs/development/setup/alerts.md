# 🚨 Alert System Setup - Cidadão.AI

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

Este guia explica como configurar o sistema de alertas para anomalias detectadas pelo sistema 24/7.

## 📋 Tipos de Alertas

O sistema suporta 3 tipos de alertas:

1. **Webhook** - Envia notificações para URLs configuradas (Discord, Slack, etc.)
2. **Email** - Envia emails para endereços configurados (futuro)
3. **Dashboard** - Registra alertas no Supabase para visualização

## ⚙️ Configuração de Webhooks

### Discord Webhook

1. No Discord, vá em Server Settings → Integrations → Webhooks
2. Clique em "New Webhook"
3. Copie a Webhook URL
4. Adicione no Railway:

```bash
ALERT_WEBHOOKS=https://discord.com/api/webhooks/your-webhook-url
```

### Slack Webhook

1. Vá em https://api.slack.com/apps
2. Crie um novo app
3. Ative "Incoming Webhooks"
4. Copie a Webhook URL
5. Adicione no Railway:

```bash
ALERT_WEBHOOKS=https://hooks.slack.com/services/your-webhook-url
```

### Múltiplos Webhooks

Você pode configurar vários webhooks separados por vírgula:

```bash
ALERT_WEBHOOKS=https://discord.com/api/webhooks/xxx,https://hooks.slack.com/services/yyy
```

## 📧 Configuração de Email (Futuro)

Para configurar alertas por email:

```bash
ALERT_EMAILS=admin@example.com,security@example.com
```

**Nota**: A integração de email requer configurar um serviço como SendGrid, AWS SES, ou Mailgun.

## 🎯 Quando os Alertas são Enviados

### Alertas Automáticos

Alertas são enviados automaticamente quando:

1. **Anomalias de Alta Severidade** detectadas (score >= 0.7)
2. **Anomalias Críticas** detectadas (score >= 0.85)

### Resumos Periódicos

O sistema envia resumos diários com:

- Total de anomalias críticas nas últimas 24h
- Top 10 anomalias por score
- Estatísticas por fonte de dados

## 📊 Formato do Alerta Webhook

```json
{
  "event": "anomaly_detected",
  "timestamp": "2025-10-07T20:30:00Z",
  "anomaly": {
    "id": "uuid-da-anomalia",
    "title": "Anomalia detectada: Dispensa 123/2025",
    "severity": "critical",
    "score": 0.9234,
    "source": "katana_scan",
    "type": "price_deviation",
    "description": "Análise automática detectou anomalia...",
    "indicators": [
      "Valor 300% acima da média",
      "Fornecedor novo sem histórico"
    ],
    "recommendations": [
      "Investigar histórico do fornecedor",
      "Verificar justificativa técnica"
    ]
  },
  "contract": {
    "id": "dispensa-123",
    "numero": "123/2025",
    "objeto": "Aquisição de equipamentos",
    "valor": 500000.00,
    "fornecedor": {
      "nome": "Empresa XYZ Ltda",
      "cnpj": "12.345.678/0001-90"
    }
  }
}
```

## 🎨 Personalizando Mensagens

### Exemplo: Webhook Customizado

Você pode criar seu próprio endpoint para receber alerts:

```python
# app.py
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/alerts/webhook")
async def receive_alert(request: Request):
    data = await request.json()

    severity = data["anomaly"]["severity"]
    title = data["anomaly"]["title"]
    score = data["anomaly"]["score"]

    # Sua lógica customizada aqui
    if severity == "critical":
        # Enviar SMS
        # Acionar alarme
        # Criar ticket
        pass

    return {"status": "received"}
```

## 📱 Exemplos de Integração

### 1. Discord - Mensagem Rica

O webhook do Discord suporta embeds. O payload será convertido em:

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

### 2. Slack - Notificação Formatada

```json
{
  "text": "🚨 Anomalia Crítica Detectada",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "Anomalia detectada: Dispensa 123/2025"
      }
    },
    {
      "type": "section",
      "fields": [
        {"type": "mrkdwn", "text": "*Score:*\n0.9234"},
        {"type": "mrkdwn", "text": "*Severidade:*\nCrítica"}
      ]
    }
  ]
}
```

### 3. Telegram Bot

```python
import httpx

async def send_telegram_alert(anomaly_data):
    bot_token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"

    message = f"""
🚨 *ALERTA CRÍTICO*

{anomaly_data['title']}

Score: {anomaly_data['score']}
Fonte: {anomaly_data['source']}
    """

    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
        )
```

## 🔍 Monitoramento de Alertas

### Ver Alertas Enviados no Supabase

```sql
-- Alertas das últimas 24h
SELECT
    a.created_at,
    a.alert_type,
    a.severity,
    a.title,
    a.status,
    an.anomaly_score,
    an.source
FROM alerts a
JOIN anomalies an ON a.anomaly_id = an.id
WHERE a.created_at >= NOW() - INTERVAL '24 hours'
ORDER BY a.created_at DESC;

-- Taxa de sucesso de alertas
SELECT
    alert_type,
    COUNT(*) as total,
    COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
    ROUND(
        COUNT(CASE WHEN status = 'sent' THEN 1 END)::numeric /
        COUNT(*)::numeric * 100,
        2
    ) as success_rate
FROM alerts
GROUP BY alert_type;
```

### API Endpoints para Alertas

```bash
# Listar alertas pendentes
GET /api/v1/alerts?status=pending

# Reenviar alerta falhado
POST /api/v1/alerts/{alert_id}/retry

# Marcar alerta como lido
PATCH /api/v1/alerts/{alert_id}
{
  "status": "acknowledged"
}
```

## 🛡️ Segurança

### Protegendo seu Webhook

1. **Validar origem**: Verifique IP/assinatura do request
2. **Rate limiting**: Limite requests por minuto
3. **HTTPS only**: Sempre use HTTPS
4. **Tokens secretos**: Adicione tokens de verificação

### Exemplo: Webhook com Validação

```python
from fastapi import FastAPI, Request, HTTPException, Header

app = FastAPI()

@app.post("/alerts/webhook")
async def receive_alert(
    request: Request,
    x_webhook_token: str = Header(None)
):
    # Validar token
    if x_webhook_token != "seu-token-secreto":
        raise HTTPException(status_code=403, detail="Invalid token")

    data = await request.json()
    # Processar alerta
    return {"status": "received"}
```

## 📊 Métricas de Alertas

### Dashboard de Alertas (Grafana/Metabase)

```sql
-- Alertas por severidade (últimos 7 dias)
SELECT
    DATE(created_at) as date,
    severity,
    COUNT(*) as total
FROM alerts
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at), severity
ORDER BY date DESC, severity;

-- Tempo médio de resposta
SELECT
    AVG(EXTRACT(EPOCH FROM (sent_at - created_at))) as avg_seconds
FROM alerts
WHERE status = 'sent';
```

## 🔧 Troubleshooting

### Alertas não estão sendo enviados

1. **Verificar configuração**:
   ```bash
   # No Railway, confirme que a variável está definida
   echo $ALERT_WEBHOOKS
   ```

2. **Testar webhook manualmente**:
   ```bash
   curl -X POST "https://seu-webhook-url" \
     -H "Content-Type: application/json" \
     -d '{"test": "message"}'
   ```

3. **Verificar logs do Worker**:
   ```
   # Procure por:
   webhook_alert_sent
   webhook_alert_failed
   ```

### Webhook retorna erro 400/500

- Verifique o formato do payload
- Alguns serviços exigem campos específicos
- Consulte a documentação do serviço

### Muitos alertas (spam)

Ajuste o threshold de detecção:

```python
# Em katana_tasks.py, linha 172
if anomaly["severity"] in ("critical"):  # Apenas críticos
```

## 🎯 Próximos Passos

1. ✅ Configure webhook do Discord/Slack
2. ✅ Teste manualmente com trigger da API
3. ✅ Monitore alertas no Supabase
4. ✅ Crie dashboard de visualização
5. ✅ Configure integração de email (opcional)

## 📚 Referências

- [Discord Webhooks](https://discord.com/developers/docs/resources/webhook)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
- [Telegram Bot API](https://core.telegram.org/bots/api)
