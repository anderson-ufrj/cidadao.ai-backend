# Grafana Cloud Integration

> Monitoramento de produção do Cidadão.AI usando Grafana Cloud Free Tier

**Data**: 2025-12-12
**Status**: Operacional
**Dashboard**: https://andersonhenrique.grafana.net

---

## Visão Geral

O Cidadão.AI Backend envia métricas Prometheus diretamente para o Grafana Cloud usando o protocolo **Remote Write**. Isso permite monitoramento completo da aplicação em produção no Railway sem necessidade de infraestrutura adicional.

### Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                     Railway Production                           │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Cidadão.AI Backend                          │    │
│  │                                                          │    │
│  │  ┌──────────────┐    ┌─────────────────────────────┐    │    │
│  │  │ Prometheus   │───▶│ GrafanaCloudPusher          │    │    │
│  │  │ Registry     │    │ (Remote Write every 15s)    │    │    │
│  │  └──────────────┘    └─────────────────────────────┘    │    │
│  │         │                         │                      │    │
│  │         ▼                         │                      │    │
│  │  /health/metrics                  │                      │    │
│  │  (Prometheus format)              │                      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                      │                           │
└──────────────────────────────────────│───────────────────────────┘
                                       │
                                       ▼ HTTPS + Basic Auth
                    ┌──────────────────────────────────────┐
                    │         Grafana Cloud                 │
                    │  ┌─────────────────────────────┐     │
                    │  │ Prometheus (Mimir)          │     │
                    │  │ prometheus-prod-40-prod-    │     │
                    │  │ sa-east-1.grafana.net       │     │
                    │  └─────────────────────────────┘     │
                    │              │                        │
                    │              ▼                        │
                    │  ┌─────────────────────────────┐     │
                    │  │ Grafana Dashboards          │     │
                    │  │ andersonhenrique.grafana.net│     │
                    │  └─────────────────────────────┘     │
                    └──────────────────────────────────────┘
```

---

## Configuração

### 1. Variáveis de Ambiente (Railway)

Adicione as seguintes variáveis no Railway:

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `GRAFANA_REMOTE_WRITE_URL` | URL do endpoint Remote Write | `https://prometheus-prod-40-prod-sa-east-1.grafana.net/api/prom/push` |
| `GRAFANA_REMOTE_WRITE_USER` | ID da instância Prometheus | `2768861` |
| `GRAFANA_REMOTE_WRITE_TOKEN` | Token de API (write scope) | `glc_eyJvIjoiMTU3...` |

### 2. Obter Credenciais do Grafana Cloud

1. Acesse https://grafana.com e faça login
2. Vá para **My Account** → **Grafana Cloud**
3. Na seção **Prometheus**, clique em **Send Metrics**
4. Copie:
   - **Remote Write Endpoint** → `GRAFANA_REMOTE_WRITE_URL`
   - **Username / Instance ID** → `GRAFANA_REMOTE_WRITE_USER`
   - Gere um novo token → `GRAFANA_REMOTE_WRITE_TOKEN`

### 3. Intervalo de Push

Por padrão, métricas são enviadas a cada **15 segundos**. Para alterar:

```bash
GRAFANA_METRICS_PUSH_INTERVAL=30  # segundos
```

---

## Métricas Disponíveis

### Métricas da Aplicação

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `cidadao_ai_requests_total` | Counter | Total de requisições HTTP |
| `cidadao_ai_request_duration_seconds` | Histogram | Duração das requisições |
| `cidadao_ai_agent_tasks_total` | Counter | Total de tarefas dos agentes |
| `cidadao_ai_agent_task_duration_seconds` | Histogram | Duração das tarefas dos agentes |
| `cidadao_ai_database_queries_total` | Counter | Total de queries no banco |
| `cidadao_ai_database_query_duration_seconds` | Histogram | Duração das queries |
| `cidadao_ai_transparency_api_calls_total` | Counter | Chamadas à API de transparência |
| `cidadao_ai_cache_hits_total` | Counter | Cache hits |
| `cidadao_ai_cache_misses_total` | Counter | Cache misses |

### Métricas do Sistema

| Métrica | Tipo | Descrição |
|---------|------|-----------|
| `process_resident_memory_bytes` | Gauge | Memória RAM utilizada |
| `process_cpu_seconds_total` | Counter | Tempo de CPU utilizado |
| `process_open_fds` | Gauge | File descriptors abertos |
| `python_gc_collections_total` | Counter | Coletas do garbage collector |

### Labels Padrão

Todas as métricas incluem:

```
job="cidadao-ai-backend"
instance="railway-production"
```

---

## Acessando o Grafana

### URL
https://andersonhenrique.grafana.net

### Explorando Métricas

1. Menu lateral → **Explore** (ícone de bússola)
2. Selecione o data source: **grafanacloud-andersonhenrique-prom**
3. Queries úteis:

```promql
# Todas as métricas do Cidadão.AI
{job="cidadao-ai-backend"}

# Requisições por segundo
rate(cidadao_ai_requests_total[5m])

# Latência p95 das requisições
histogram_quantile(0.95, rate(cidadao_ai_request_duration_seconds_bucket[5m]))

# Uso de memória em MB
process_resident_memory_bytes / 1024 / 1024

# Taxa de cache hit
rate(cidadao_ai_cache_hits_total[5m]) /
(rate(cidadao_ai_cache_hits_total[5m]) + rate(cidadao_ai_cache_misses_total[5m]))
```

---

## Criando Dashboards

### Dashboard Básico - Visão Geral

1. Menu lateral → **Dashboards** → **New** → **New Dashboard**
2. Adicione painéis com as seguintes queries:

#### Painel 1: Requisições/segundo
```promql
rate(cidadao_ai_requests_total[5m])
```
- Visualização: **Time series**
- Título: "Requisições por Segundo"

#### Painel 2: Latência p95
```promql
histogram_quantile(0.95, rate(cidadao_ai_request_duration_seconds_bucket[5m]))
```
- Visualização: **Time series**
- Título: "Latência p95 (segundos)"

#### Painel 3: Uso de Memória
```promql
process_resident_memory_bytes / 1024 / 1024
```
- Visualização: **Stat**
- Unidade: MB
- Título: "Memória RAM"

#### Painel 4: Tarefas de Agentes
```promql
rate(cidadao_ai_agent_tasks_total[5m])
```
- Visualização: **Time series**
- Título: "Tarefas de Agentes/segundo"

---

## Alertas

### Configurando Alertas no Grafana Cloud

1. Menu lateral → **Alerting** → **Alert rules**
2. Crie regras para:

#### Alerta de Memória Alta
```promql
process_resident_memory_bytes > 1073741824  # > 1GB
```

#### Alerta de Latência Alta
```promql
histogram_quantile(0.95, rate(cidadao_ai_request_duration_seconds_bucket[5m])) > 2
```

#### Alerta de Erros
```promql
rate(cidadao_ai_requests_total{status=~"5.."}[5m]) > 0.1
```

---

## Implementação Técnica

### Arquivo Principal
`src/infrastructure/observability/grafana_cloud_pusher.py`

### Como Funciona

1. **Coleta**: Usa `prometheus_client.REGISTRY` para coletar métricas
2. **Conversão**: Converte formato texto Prometheus para protobuf
3. **Compressão**: Comprime com Snappy (requisito do Remote Write)
4. **Envio**: POST para Grafana Cloud com Basic Auth

### Código Relevante

```python
# Inicialização automática no startup do app
# src/api/app.py

from src.infrastructure.observability.grafana_cloud_pusher import grafana_pusher

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await grafana_pusher.start()  # Inicia push de métricas

    yield

    # Shutdown
    await grafana_pusher.stop()   # Para push de métricas
```

### Dependências

```toml
# pyproject.toml
"python-snappy>=0.7.0"  # Compressão para Remote Write
"prometheus-client>=0.19.0"  # Métricas Prometheus
"httpx>=0.26.0"  # Cliente HTTP async
```

---

## Troubleshooting

### Métricas não aparecem no Grafana

1. **Verificar variáveis de ambiente**:
   ```bash
   # No Railway, confirme que estão configuradas:
   GRAFANA_REMOTE_WRITE_URL
   GRAFANA_REMOTE_WRITE_USER
   GRAFANA_REMOTE_WRITE_TOKEN
   ```

2. **Verificar logs do Railway**:
   ```
   grafana_cloud_pusher_started  # Deve aparecer no startup
   grafana_metrics_pushed        # A cada 15 segundos
   ```

3. **Testar endpoint de métricas**:
   ```bash
   curl -sL https://cidadao-api-production.up.railway.app/health/metrics
   ```

### Erro de autenticação

- Verifique se o token tem escopo de **write**
- Confirme que o User ID está correto (é numérico)
- Regenere o token no Grafana Cloud se necessário

### Métricas atrasadas

- O intervalo padrão é 15 segundos
- Grafana Cloud pode ter delay de até 1 minuto para exibir
- Use "Last 5 minutes" no time range do Grafana

---

## Custos

### Grafana Cloud Free Tier

| Recurso | Limite Gratuito |
|---------|-----------------|
| Métricas | 10.000 séries ativas |
| Logs | 50GB/mês |
| Traces | 50GB/mês |
| Usuários | 3 |
| Retenção | 14 dias |

O Cidadão.AI usa aproximadamente **50-100 séries** de métricas, bem dentro do limite gratuito.

---

## Referências

- [Grafana Cloud Docs](https://grafana.com/docs/grafana-cloud/)
- [Prometheus Remote Write](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#remote_write)
- [PromQL Basics](https://prometheus.io/docs/prometheus/latest/querying/basics/)
