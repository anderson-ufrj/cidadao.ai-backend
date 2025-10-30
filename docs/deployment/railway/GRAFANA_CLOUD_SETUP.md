# Configuração Grafana Cloud para Produção Railway

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Data**: 2025-10-30
**Versão**: 1.0

---

## 📋 Visão Geral

Guia completo para integrar o backend Cidadão.AI (Railway) com Grafana Cloud para monitoramento em produção.

**Benefícios**:
- ✅ Monitoramento 24/7 gratuito (até 10k séries métricas)
- ✅ Dashboards profissionais prontos
- ✅ Alertas por email/Slack/Discord
- ✅ Zero infraestrutura para gerenciar
- ✅ Retenção de 13 meses de dados

---

## 🚀 Passo 1: Configurar Grafana Cloud

### 1.1 Criar Conta (se ainda não tiver)

1. Acesse: https://grafana.com/auth/sign-up
2. Crie conta gratuita (Forever Free tier)
3. Ative sua stack (ex: `cidadaoai.grafana.net`)

### 1.2 Obter Credenciais Prometheus

1. **Login** no Grafana Cloud: https://grafana.com/login
2. **Menu lateral** → "Connections" → "Add new connection"
3. Procure por **"Prometheus"**
4. Clique em **"Via Grafana Alloy"** ou **"Self-hosted Prometheus"**
5. Copie as credenciais:

```bash
# Exemplo das credenciais que você verá:
Remote Write Endpoint: https://prometheus-prod-13-prod-us-east-0.grafana.net/api/prom/push
Username/Instance ID: 123456
Password/API Key: glc_xxx...xxx
```

**⚠️ IMPORTANTE**: Salve estas credenciais em um local seguro!

---

## 🔧 Passo 2: Configurar Railway

### 2.1 Adicionar Variáveis de Ambiente

No Railway Dashboard:

1. Acesse seu projeto: https://railway.app/project/cidadao-ai-backend
2. Clique em **"Variables"**
3. Adicione as seguintes variáveis:

```bash
# Grafana Cloud Prometheus Remote Write
GRAFANA_CLOUD_ENABLED=true
GRAFANA_CLOUD_URL=https://prometheus-prod-XX-prod-us-east-0.grafana.net/api/prom/push
GRAFANA_CLOUD_USER=123456
GRAFANA_CLOUD_KEY=glc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Configurações de Push (opcional)
METRICS_PUSH_INTERVAL=60  # Segundos entre pushes (padrão: 60)
METRICS_PUSH_TIMEOUT=10   # Timeout em segundos (padrão: 10)
```

**Substitua** pelos valores que você copiou do Grafana Cloud!

### 2.2 Verificar Configuração

```bash
# Via Railway CLI (se tiver configurado)
railway variables

# Ou pelo Dashboard Railway → Variables tab
```

---

## 💻 Passo 3: Implementar Push de Métricas

### 3.1 Instalar Dependência

Adicione ao `pyproject.toml` (se ainda não tiver):

```toml
[tool.poetry.dependencies]
prometheus-client = "^0.19.0"
```

Ou via pip:
```bash
pip install prometheus-client
```

### 3.2 Criar Módulo de Push

Crie o arquivo `src/infrastructure/observability/grafana_cloud_pusher.py`:

```python
"""
Grafana Cloud Metrics Pusher

Envia métricas Prometheus para Grafana Cloud via Remote Write.
"""

import asyncio
import logging
import os
from typing import Optional

from prometheus_client import push_to_gateway
from prometheus_client.exposition import basic_auth_handler

from src.core.config import settings
from src.infrastructure.observability.metrics import registry

logger = logging.getLogger(__name__)


class GrafanaCloudPusher:
    """Push metrics to Grafana Cloud Prometheus."""

    def __init__(self):
        self.enabled = os.getenv("GRAFANA_CLOUD_ENABLED", "false").lower() == "true"
        self.url = os.getenv("GRAFANA_CLOUD_URL", "")
        self.user = os.getenv("GRAFANA_CLOUD_USER", "")
        self.key = os.getenv("GRAFANA_CLOUD_KEY", "")
        self.interval = int(os.getenv("METRICS_PUSH_INTERVAL", "60"))
        self.timeout = int(os.getenv("METRICS_PUSH_TIMEOUT", "10"))

        self._task: Optional[asyncio.Task] = None
        self._running = False

    def _validate_config(self) -> bool:
        """Validate Grafana Cloud configuration."""
        if not self.enabled:
            logger.info("Grafana Cloud push disabled")
            return False

        if not all([self.url, self.user, self.key]):
            logger.warning(
                "Grafana Cloud enabled but missing credentials. "
                "Set GRAFANA_CLOUD_URL, GRAFANA_CLOUD_USER, GRAFANA_CLOUD_KEY"
            )
            return False

        return True

    async def push_metrics(self) -> bool:
        """
        Push metrics to Grafana Cloud.

        Returns:
            True if successful, False otherwise
        """
        if not self._validate_config():
            return False

        try:
            # Extract hostname from URL for gateway
            # URL: https://prometheus-prod-XX.grafana.net/api/prom/push
            # Gateway: prometheus-prod-XX.grafana.net:443
            gateway = self.url.replace("https://", "").replace("http://", "")
            gateway = gateway.split("/")[0]  # Remove path

            # Create auth handler
            def auth_handler(url, method, timeout, headers, data):
                return basic_auth_handler(
                    url, method, timeout, headers, data,
                    self.user, self.key
                )

            # Push to gateway
            push_to_gateway(
                gateway=f"{gateway}:443",
                job='cidadao-ai-backend',
                registry=registry,
                handler=auth_handler,
                timeout=self.timeout
            )

            logger.debug(f"Metrics pushed to Grafana Cloud successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to push metrics to Grafana Cloud: {e}")
            return False

    async def _push_loop(self):
        """Background loop to push metrics periodically."""
        logger.info(
            f"Starting Grafana Cloud metrics push loop "
            f"(interval: {self.interval}s)"
        )

        while self._running:
            try:
                await self.push_metrics()
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                logger.info("Grafana Cloud push loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in push loop: {e}")
                await asyncio.sleep(self.interval)

    async def start(self):
        """Start periodic metrics push."""
        if not self._validate_config():
            logger.info("Grafana Cloud push not started (disabled or misconfigured)")
            return

        if self._running:
            logger.warning("Grafana Cloud pusher already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._push_loop())
        logger.info("Grafana Cloud metrics pusher started")

    async def stop(self):
        """Stop periodic metrics push."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("Grafana Cloud metrics pusher stopped")


# Global instance
grafana_pusher = GrafanaCloudPusher()
```

### 3.3 Integrar no FastAPI App

Modifique `src/api/app.py`:

```python
# No início do arquivo, adicione:
from src.infrastructure.observability.grafana_cloud_pusher import grafana_pusher

# No evento startup, adicione:
@app.on_event("startup")
async def startup_grafana_cloud():
    """Start Grafana Cloud metrics push."""
    await grafana_pusher.start()

# No evento shutdown, adicione:
@app.on_event("shutdown")
async def shutdown_grafana_cloud():
    """Stop Grafana Cloud metrics push."""
    await grafana_pusher.stop()
```

---

## 📊 Passo 4: Importar Dashboards

### 4.1 Acessar Grafana Cloud

1. Login: https://cidadaoai.grafana.net (sua stack)
2. **Menu lateral** → "Dashboards"
3. Clique em **"New"** → **"Import"**

### 4.2 Importar os 6 Dashboards

Para cada arquivo em `monitoring/grafana/dashboards/`:

1. Clique **"Upload JSON file"**
2. Selecione o arquivo (ex: `overview.json`)
3. Selecione datasource: **"grafanacloud-xxx-prom"** (auto-detectado)
4. Clique **"Import"**

**Dashboards a importar**:
- ✅ `overview.json` - Visão geral do sistema
- ✅ `agents.json` - Métricas dos agentes
- ✅ `investigations.json` - Investigações e análises
- ✅ `api.json` - Performance da API
- ✅ `infrastructure.json` - Saúde do sistema
- ✅ `alerts.json` - Dashboard de alertas

### 4.3 Configurar Data Source

Grafana Cloud já vem com Prometheus configurado, mas verifique:

1. **Menu lateral** → "Connections" → "Data sources"
2. Deve ter: **"grafanacloud-cidadaoai-prom"** (ou similar)
3. Status: ✅ **"Data source is working"**

---

## 🔔 Passo 5: Configurar Alertas

### 5.1 Criar Contact Point

1. **Menu lateral** → "Alerting" → "Contact points"
2. Clique **"Add contact point"**
3. Configure:

**Email**:
```yaml
Name: Email Alerts
Integration: Email
Addresses: seu-email@example.com
```

**Discord** (opcional):
```yaml
Name: Discord Alerts
Integration: Discord
Webhook URL: https://discord.com/api/webhooks/xxx/yyy
```

**Slack** (opcional):
```yaml
Name: Slack Alerts
Integration: Slack
Webhook URL: https://hooks.slack.com/services/xxx/yyy/zzz
```

### 5.2 Importar Regras de Alerta

Grafana Cloud permite criar alertas via UI:

**Alerta 1: API Error Rate Alto**
```yaml
Nome: High API Error Rate
Condition:
  Query: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
  For: 5m
Severity: Critical
Message: "API error rate above 5% for 5 minutes"
```

**Alerta 2: Investigation Failures**
```yaml
Nome: Investigation Failures
Condition:
  Query: rate(cidadao_ai_investigations_total{status="failed"}[10m]) > 0.1
  For: 10m
Severity: Warning
Message: "Investigation failure rate is high"
```

**Alerta 3: Sistema Offline**
```yaml
Nome: Backend Down
Condition:
  Query: up{job="cidadao-ai-backend"} == 0
  For: 2m
Severity: Critical
Message: "Cidadão.AI backend is down!"
```

---

## ✅ Passo 6: Validar Integração

### 6.1 Deploy e Teste

```bash
# 1. Commit das mudanças
git add .
git commit -m "feat(monitoring): integrate Grafana Cloud metrics push"

# 2. Deploy no Railway (auto-deploy no push)
git push origin main

# 3. Aguarde deploy (2-3 minutos)
# Railway → Deployments → Aguarde "Success"
```

### 6.2 Verificar Métricas no Grafana

1. Acesse Grafana Cloud: https://cidadaoai.grafana.net
2. **Menu** → "Explore"
3. Teste query:
```promql
# Verificar se métricas estão chegando
up{job="cidadao-ai-backend"}

# Requests por segundo
rate(http_requests_total[5m])

# Tarefas de agentes
rate(cidadao_ai_agent_tasks_total[5m])
```

**Resultado esperado**: Gráficos com dados dos últimos minutos

### 6.3 Verificar Logs no Railway

```bash
railway logs --follow

# Procure por logs:
# ✅ "Starting Grafana Cloud metrics push loop (interval: 60s)"
# ✅ "Metrics pushed to Grafana Cloud successfully"
```

---

## 🐛 Troubleshooting

### Problema: Métricas não aparecem no Grafana

**Verificações**:

1. **Variáveis de ambiente configuradas?**
```bash
railway variables | grep GRAFANA
```

2. **Credenciais corretas?**
```bash
# Teste manual (local)
curl -u "123456:glc_xxx" \
  https://prometheus-prod-XX.grafana.net/api/prom/push
# Deve retornar 200 ou 204
```

3. **Logs do Railway**:
```bash
railway logs | grep -i grafana
# Procure por erros de autenticação ou conexão
```

### Problema: "Authentication failed"

**Solução**: Verifique credenciais

1. Acesse Grafana Cloud → Connections → Prometheus
2. Regere API key se necessário
3. Atualize `GRAFANA_CLOUD_KEY` no Railway

### Problema: "Connection timeout"

**Solução**: Verifique URL

- URL deve incluir `/api/prom/push`
- Exemplo: `https://prometheus-prod-13-prod-us-east-0.grafana.net/api/prom/push`
- Não use apenas o hostname

### Problema: Dashboards vazios

**Causas comuns**:

1. **Time range**: Ajuste para "Last 5 minutes" no canto superior direito
2. **Data source**: Verifique se está selecionado o Prometheus correto
3. **Job label**: Métricas têm label `job="cidadao-ai-backend"`

---

## 📈 Monitoramento Diário

### Dashboards Principais

1. **Overview**: Estado geral do sistema
   - Uptime, requests/s, error rate
   - Acesse: Dashboards → Overview

2. **Agents**: Performance dos agentes
   - Tasks por agente, duração, erros
   - Acesse: Dashboards → Agents

3. **API**: Latência e throughput
   - p50/p95/p99, endpoints mais lentos
   - Acesse: Dashboards → API Performance

### Métricas Críticas

| Métrica | Threshold | Ação |
|---------|-----------|------|
| Error Rate | >5% | Investigar logs |
| p95 Latency | >2s | Otimizar queries |
| Investigation Failures | >10% | Verificar agentes |
| Uptime | <99% | Verificar Railway |

### Alertas Configurados

- 🔴 **Critical**: Sistema offline, error rate >5%
- 🟡 **Warning**: Latência alta, falhas de investigação

---

## 🎯 Próximos Passos

Após configuração básica:

1. **Customizar Dashboards**: Ajuste painéis conforme necessidade
2. **Adicionar SLOs**: Configure Service Level Objectives
3. **Integrar Logs**: Grafana Cloud também suporta Loki (logs)
4. **Traces**: Adicionar Tempo para distributed tracing

---

## 📚 Recursos

- **Grafana Cloud Docs**: https://grafana.com/docs/grafana-cloud/
- **Prometheus Remote Write**: https://prometheus.io/docs/prometheus/latest/configuration/configuration/#remote_write
- **Railway Monitoring**: https://docs.railway.app/reference/metrics

---

## 🤝 Suporte

**Problemas com esta configuração?**

1. Verifique logs no Railway: `railway logs`
2. Teste credenciais Grafana Cloud manualmente
3. Revise variáveis de ambiente no Railway
4. Consulte documentação oficial Grafana Cloud

---

**Guia criado**: 2025-10-30
**Última atualização**: 2025-10-30
**Versão**: 1.0
**Autor**: Anderson Henrique da Silva, Minas Gerais, Brasil
