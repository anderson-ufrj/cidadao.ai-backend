# 📊 Guia Completo de Dashboards Grafana - Cidadão.AI

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Data**: 2025-10-30
**Versão**: 1.0
**Status**: Documentação de Monitoramento

---

## 🎯 Visão Geral

Este documento descreve a configuração completa de monitoramento do backend Cidadão.AI usando **Grafana + Prometheus**, incluindo todos os dashboards, métricas disponíveis e como utilizá-los para monitorar a saúde do sistema em produção.

### Informações de Produção
- **URL**: https://cidadao-api-production.up.railway.app
- **Uptime**: 99.9% desde 07/10/2025
- **Stack**: FastAPI + PostgreSQL + Redis + Celery
- **Monitoramento**: Prometheus + Grafana
- **Localização**: Railway (us-west)

---

## 📁 Estrutura de Arquivos

```
monitoring/
├── grafana/
│   ├── dashboards/                    # Dashboards JSON
│   │   ├── cidadao-ai-overview.json           # ⭐ Dashboard principal
│   │   ├── cidadao-ai-agents.json             # Monitoramento de agentes
│   │   ├── federal-apis-dashboard.json        # APIs federais
│   │   ├── slo-sla-dashboard.json             # SLA/SLO tracking
│   │   ├── system-performance.json            # Performance do sistema
│   │   └── zumbi-agent-dashboard.json         # Agente Zumbi específico
│   ├── provisioning/
│   │   ├── dashboards/
│   │   │   └── dashboards.yml         # Auto-provisioning
│   │   └── datasources/
│   │       └── prometheus.yml         # Datasource config
│   └── grafana.ini                    # Configuração do Grafana
├── prometheus/
│   └── prometheus.yml                 # Configuração do Prometheus
└── docker-compose.monitoring.yml      # Stack completo
```

---

## 🚀 Quick Start

### Iniciar Stack de Monitoramento

```bash
# 1. Subir Prometheus + Grafana
docker-compose -f docker-compose.monitoring.yml up -d

# 2. Acessar Grafana
# URL: http://localhost:3000
# Login: admin / cidadao123

# 3. Verificar Prometheus
# URL: http://localhost:9090
# Targets: http://localhost:9090/targets
```

### Verificar Métricas do Backend

```bash
# Endpoint de métricas Prometheus
curl http://localhost:8000/health/metrics

# Exemplo de saída:
# cidadao_ai_agent_tasks_total{agent_name="zumbi",status="success"} 142.0
# cidadao_ai_investigations_total{status="completed"} 37.0
```

---

## 📊 Dashboards Disponíveis

### 1. **Overview - Dashboard Principal** ⭐

**Arquivo**: `cidadao-ai-overview.json`
**Propósito**: Visão geral de saúde e performance do sistema
**Atualização**: Tempo real (5 segundos)

#### Painéis Principais:

**Linha 1: Métricas de Saúde**
- 🟢 **Uptime** - Porcentagem de disponibilidade (Meta: 99.9%)
- 📊 **Requests/sec** - Taxa de requisições (tempo real)
- ⚠️ **Error Rate** - Porcentagem de erros (Meta: <1%)
- ⏱️ **Response Time (p95)** - Tempo de resposta 95º percentil (Meta: <200ms)

**Linha 2: Atividade de Investigações**
- 📈 **Investigações Ativas** - Número de investigações em andamento
- ✅ **Taxa de Conclusão** - Porcentagem de investigações completadas
- ⏰ **Tempo Médio** - Tempo médio de processamento
- 👥 **Usuários Ativos** - Número de usuários simultâneos

**Linha 3: Agentes Multi-Agent**
- 🤖 **Agentes Ativos** - Número de agentes processando tarefas
- 📊 **Tarefas/min** - Taxa de execução de tarefas
- ✅ **Taxa de Sucesso** - Porcentagem de tarefas bem-sucedidas
- ⚡ **Performance** - Tempo médio de execução

**Linha 4: Infraestrutura**
- 💾 **PostgreSQL** - Conexões ativas, query time, locks
- 🔴 **Redis** - Hit rate, memória usada, evictions
- 📮 **Celery** - Workers ativos, fila, tarefas falhadas
- 🖥️ **Sistema** - CPU, memória (se disponível)

#### Queries PromQL Importantes:

```promql
# Uptime (últimas 24h)
avg_over_time(up{job="cidadao-ai-backend"}[24h]) * 100

# Requests por segundo
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100

# Response time p95
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Investigações ativas
cidadao_ai_investigations_total{status="in_progress"}

# Taxa de sucesso de agentes
rate(cidadao_ai_agent_tasks_total{status="success"}[5m]) /
rate(cidadao_ai_agent_tasks_total[5m]) * 100
```

---

### 2. **Agents Performance - Monitoramento de Agentes** 🤖

**Arquivo**: `cidadao-ai-agents.json`
**Propósito**: Monitorar performance de todos os 16 agentes
**Atualização**: 10 segundos

#### Painéis por Agente:

Para cada um dos 16 agentes (Zumbi, Anita, Tiradentes, etc.):

**Métricas Individuais**:
- 📊 **Tarefas Executadas** - Total por tipo de tarefa
- ⏱️ **Tempo de Execução** - Distribuição de latência (p50, p95, p99)
- ✅ **Taxa de Sucesso** - % de tarefas bem-sucedidas
- 🔄 **Tarefas Concorrentes** - Número de tarefas simultâneas
- 📈 **Throughput** - Tarefas por minuto
- ⚠️ **Erros** - Taxa de erro e tipos de falha

**Visualizações**:
- Time series para tendências
- Heatmap para distribuição de latência
- Tabela com detalhes de falhas
- Gauge para taxa de sucesso

#### Queries por Agente:

```promql
# Total de tarefas do Zumbi
sum(cidadao_ai_agent_tasks_total{agent_name="zumbi"})

# Tempo médio de execução
rate(cidadao_ai_agent_task_duration_seconds_sum{agent_name="zumbi"}[5m]) /
rate(cidadao_ai_agent_task_duration_seconds_count{agent_name="zumbi"}[5m])

# Taxa de sucesso
rate(cidadao_ai_agent_tasks_total{agent_name="zumbi",status="success"}[5m]) /
rate(cidadao_ai_agent_tasks_total{agent_name="zumbi"}[5m]) * 100

# p95 latency
histogram_quantile(0.95,
  rate(cidadao_ai_agent_task_duration_seconds_bucket{agent_name="zumbi"}[5m])
)
```

**Alertas Configurados**:
- ⚠️ Taxa de erro > 5% (Warning)
- 🚨 Taxa de erro > 10% (Critical)
- ⚠️ p95 latency > 5s (Warning)
- 🚨 p95 latency > 10s (Critical)

---

### 3. **Federal APIs - Monitoramento de APIs Externas** 🌐

**Arquivo**: `federal-apis-dashboard.json`
**Propósito**: Monitorar integrações com APIs governamentais (30+ APIs)
**Atualização**: 30 segundos

#### APIs Monitoradas:

**APIs Federais** (7):
1. IBGE - Geografia e estatísticas
2. DataSUS - Dados de saúde
3. INEP - Educação
4. PNCP - Contratos públicos
5. Compras.gov.br - Compras governamentais
6. Minha Receita - Receita federal
7. BCB - Banco Central

**Portal da Transparência**:
- Contratos
- Despesas
- Convênios
- Licitações
- Servidores

**APIs Estaduais** (11):
- TCEs: 6 tribunais (SP, RJ, MG, BA, PE, CE)
- CKAN: 5 portais (SP, RJ, RS, SC, BA)

#### Métricas por API:

- 📊 **Request Rate** - Requisições por minuto
- ⏱️ **Response Time** - Latência (p50, p95, p99)
- ✅ **Success Rate** - Taxa de sucesso (2xx responses)
- ⚠️ **Error Rate** - Erros 4xx e 5xx
- 🚦 **Rate Limit Status** - Uso de quota
- 📈 **Availability** - Uptime da API externa

#### Queries para APIs:

```promql
# Request rate por API
rate(external_api_requests_total{api_name="ibge"}[5m])

# Response time médio
rate(external_api_duration_seconds_sum{api_name="ibge"}[5m]) /
rate(external_api_duration_seconds_count{api_name="ibge"}[5m])

# Taxa de erro
rate(external_api_requests_total{api_name="ibge",status=~"5.."}[5m]) /
rate(external_api_requests_total{api_name="ibge"}[5m]) * 100

# Disponibilidade (últimas 24h)
avg_over_time(up{job="external-api",api="ibge"}[24h]) * 100
```

**Alertas de APIs**:
- ⚠️ Error rate > 10% (Warning)
- 🚨 Error rate > 25% (Critical)
- ⚠️ Response time > 2s (Warning)
- 🚨 Availability < 95% (Critical)

---

### 4. **SLO/SLA Tracking - Acordos de Nível de Serviço** 📋

**Arquivo**: `slo-sla-dashboard.json`
**Propósito**: Monitorar cumprimento de SLAs e SLOs
**Atualização**: 1 minuto

#### SLAs Definidos:

**Disponibilidade**:
- ✅ **Target**: 99.9% uptime mensal
- 📊 **Atual**: Calculado em tempo real
- ⏰ **Downtime Permitido**: 43.2 minutos/mês

**Performance**:
- ✅ **API Response (p95)**: < 200ms
- ✅ **Chat Response (p95)**: < 500ms
- ✅ **Investigation (p95)**: < 2s
- ✅ **Report Generation (p95)**: < 5s

**Qualidade**:
- ✅ **Error Rate**: < 1%
- ✅ **Agent Success Rate**: > 95%
- ✅ **Data Freshness**: < 1 hora

#### SLOs (Service Level Objectives):

**Tier 1 (Critical)**:
- Uptime: 99.95%
- P95 latency: < 150ms
- Error rate: < 0.5%

**Tier 2 (Important)**:
- Uptime: 99.9%
- P95 latency: < 200ms
- Error rate: < 1%

**Tier 3 (Standard)**:
- Uptime: 99.5%
- P95 latency: < 500ms
- Error rate: < 2%

#### Error Budget Tracking:

```promql
# Error budget mensal (99.9% SLA)
# Permitido: 0.1% de erros = 43.2 min downtime
1 - (
  sum(rate(http_requests_total{status=~"5.."}[30d])) /
  sum(rate(http_requests_total[30d]))
) * 100

# Budget consumido (%)
(1 - (uptime_atual / 99.9)) * 100

# Tempo até esgotar budget
error_budget_remaining / current_error_rate
```

**Alertas de SLA**:
- ⚠️ Uptime < 99.9% (SLA breach iminente)
- 🚨 Uptime < 99.5% (SLA breach)
- ⚠️ Error budget < 20% (Atenção)
- 🚨 Error budget < 10% (Crítico)

---

### 5. **System Performance - Performance Detalhada** ⚡

**Arquivo**: `system-performance.json`
**Propósito**: Análise profunda de performance e bottlenecks
**Atualização**: 5 segundos

#### Categorias de Análise:

**1. HTTP Performance**:
- 📊 Latency distribution (heatmap)
- 📈 Request rate por endpoint
- 🔍 Slow endpoints (p99 > 1s)
- 📊 Response size distribution

**2. Database Performance**:
- 🔍 Query time distribution
- 📊 Conexões ativas vs idle
- ⚠️ Long-running queries (> 1s)
- 🔒 Lock contention
- 💾 Cache hit rate

**3. Redis Performance**:
- 📊 Hit rate (target: > 90%)
- 💾 Memory usage
- 🔄 Evictions rate
- ⏱️ Command latency
- 📈 Keys per database

**4. Celery Workers**:
- 🔄 Active tasks
- 📮 Queue depth
- ⏱️ Task processing time
- ⚠️ Failed tasks
- 📊 Worker utilization

**5. Resource Usage** (se disponível):
- 🖥️ CPU utilization
- 💾 Memory usage
- 📊 Disk I/O
- 🌐 Network throughput

#### Queries de Performance:

```promql
# Top 10 endpoints mais lentos (p95)
topk(10,
  histogram_quantile(0.95,
    rate(http_request_duration_seconds_bucket[5m])
  )
)

# Database: queries lentas
rate(postgresql_slow_queries_total[5m])

# Redis: hit rate
rate(redis_keyspace_hits_total[5m]) /
(rate(redis_keyspace_hits_total[5m]) + rate(redis_keyspace_misses_total[5m])) * 100

# Celery: tempo médio de processamento
rate(celery_task_duration_seconds_sum[5m]) /
rate(celery_task_duration_seconds_count[5m])
```

---

### 6. **Zumbi Agent - Dashboard Especializado** 🔍

**Arquivo**: `zumbi-agent-dashboard.json`
**Propósito**: Monitoramento detalhado do agente de detecção de anomalias
**Atualização**: 5 segundos

#### Métricas Específicas do Zumbi:

**Detecção de Anomalias**:
- 🔍 **Anomalias Detectadas** - Total por tipo
- 📊 **Confidence Score** - Distribuição de confiança
- ⚠️ **Severity Distribution** - Low, Medium, High, Critical
- 📈 **Detection Rate** - Anomalias por hora

**Performance de Análise**:
- ⏱️ **FFT Analysis Time** - Tempo de análise espectral
- 📊 **Statistical Analysis** - Tempo de análise estatística
- 🔄 **Concurrent Analyses** - Análises simultâneas
- ✅ **Success Rate** - Taxa de análises bem-sucedidas

**Tipos de Anomalias Monitoradas**:
1. **Price Deviation** - Desvio de preço (> 2.5σ)
2. **Supplier Concentration** - Concentração > 70%
3. **Contract Similarity** - Similaridade > 85%
4. **Temporal Patterns** - Padrões sazonais anormais
5. **Spectral Anomalies** - FFT outliers

#### Queries do Zumbi:

```promql
# Total de anomalias por tipo
sum by (anomaly_type) (
  cidadao_ai_anomalies_detected_total{agent_name="zumbi"}
)

# Média de confidence score
avg(cidadao_ai_anomaly_confidence_score{agent_name="zumbi"})

# Taxa de detecção (anomalias/hora)
rate(cidadao_ai_anomalies_detected_total{agent_name="zumbi"}[1h]) * 3600

# Anomalias críticas (últimas 24h)
increase(
  cidadao_ai_anomalies_detected_total{
    agent_name="zumbi",
    severity="critical"
  }[24h]
)
```

---

## 🔔 Configuração de Alertas

### Alertas Críticos (PagerDuty/Slack)

```yaml
# monitoring/prometheus/alerts/critical.yml
groups:
  - name: critical_alerts
    interval: 1m
    rules:
      # Sistema Down
      - alert: SystemDown
        expr: up{job="cidadao-ai-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Sistema Cidadão.AI OFFLINE"
          description: "Backend não está respondendo há {{ $value }} minuto(s)"

      # SLA Breach
      - alert: SLABreach
        expr: |
          (1 - avg_over_time(up{job="cidadao-ai-backend"}[30d])) * 100 > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "SLA 99.9% violado"
          description: "Uptime atual: {{ $value }}%"

      # High Error Rate
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status=~"5.."}[5m]) /
          rate(http_requests_total[5m]) * 100 > 5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Taxa de erro acima de 5%"
          description: "Error rate: {{ $value }}%"

      # Database Down
      - alert: DatabaseDown
        expr: postgresql_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL OFFLINE"

      # Redis Down
      - alert: RedisDown
        expr: redis_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis OFFLINE"
```

### Alertas de Warning (Email/Slack)

```yaml
  - name: warning_alerts
    interval: 5m
    rules:
      # Slow Response Time
      - alert: SlowResponseTime
        expr: |
          histogram_quantile(0.95,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 0.2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Response time p95 > 200ms"
          description: "Latência: {{ $value }}s"

      # Agent High Error Rate
      - alert: AgentHighErrors
        expr: |
          rate(cidadao_ai_agent_tasks_total{status="error"}[5m]) /
          rate(cidadao_ai_agent_tasks_total[5m]) * 100 > 10
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Agente {{ $labels.agent_name }} com > 10% erros"

      # Low Redis Hit Rate
      - alert: LowCacheHitRate
        expr: |
          rate(redis_keyspace_hits_total[5m]) /
          (rate(redis_keyspace_hits_total[5m]) +
           rate(redis_keyspace_misses_total[5m])) * 100 < 70
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Redis hit rate < 70%"
          description: "Hit rate: {{ $value }}%"

      # High Memory Usage
      - alert: HighMemoryUsage
        expr: |
          (1 - (node_memory_MemAvailable_bytes /
                node_memory_MemTotal_bytes)) * 100 > 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Memória > 85% utilizada"
```

---

## 📖 Como Usar os Dashboards

### 1. Monitoramento Diário (Dashboard Overview)

**Rotina Matinal** (5 minutos):
1. Abrir dashboard Overview
2. Verificar uptime (deve estar verde, > 99.9%)
3. Checar error rate (deve estar < 1%)
4. Verificar response time (p95 < 200ms)
5. Revisar investigações (throughput normal)

**Indicadores de Saúde**:
- 🟢 Verde: Tudo OK
- 🟡 Amarelo: Atenção necessária
- 🔴 Vermelho: Ação imediata

### 2. Investigação de Performance (System Performance)

**Quando usar**:
- Response time aumentou
- Usuários reportam lentidão
- Error rate subiu

**Processo**:
1. Verificar heatmap de latência
2. Identificar endpoints lentos (top 10)
3. Checar database: queries lentas, locks
4. Verificar Redis: hit rate, memory
5. Analisar Celery: queue depth, failed tasks

### 3. Debug de Anomalias (Zumbi Dashboard)

**Quando usar**:
- Investigar anomalias específicas
- Validar detecção
- Ajustar thresholds

**Análise**:
1. Ver tipos de anomalias detectadas
2. Analisar confidence scores
3. Verificar severity distribution
4. Identificar padrões temporais
5. Validar com dados reais

### 4. Monitoramento de Agentes (Agents Performance)

**Quando usar**:
- Verificar saúde de agentes específicos
- Investigar falhas
- Otimizar performance

**Checklist por Agente**:
- [ ] Taxa de sucesso > 95%
- [ ] p95 latency dentro do esperado
- [ ] Sem erros recorrentes
- [ ] Throughput consistente

### 5. Rastreamento de SLA (SLO/SLA Dashboard)

**Uso Executivo**:
- Relatórios mensais de SLA
- Planejamento de capacity
- Comunicação com stakeholders

**Métricas Chave**:
- Uptime mensal
- Error budget consumido
- Tendências de performance
- Compliance com SLOs

---

## 🎨 Personalização de Dashboards

### Adicionar Novo Painel

1. **No Grafana UI**:
   - Clicar em "Add panel"
   - Selecionar visualização
   - Configurar query PromQL
   - Ajustar opções visuais
   - Salvar

2. **Exportar JSON**:
   - Dashboard settings → JSON Model
   - Copiar JSON
   - Salvar em `monitoring/grafana/dashboards/`

3. **Versionar no Git**:
   ```bash
   git add monitoring/grafana/dashboards/
   git commit -m "feat(monitoring): add new dashboard panel"
   ```

### Criar Variáveis de Dashboard

```json
{
  "templating": {
    "list": [
      {
        "name": "agent",
        "type": "query",
        "query": "label_values(cidadao_ai_agent_tasks_total, agent_name)",
        "multi": true,
        "includeAll": true
      },
      {
        "name": "interval",
        "type": "interval",
        "query": "5m,15m,1h,6h,24h",
        "current": {
          "text": "5m",
          "value": "5m"
        }
      }
    ]
  }
}
```

### Adicionar Anotações

```json
{
  "annotations": {
    "list": [
      {
        "name": "Deployments",
        "datasource": "Prometheus",
        "expr": "changes(process_start_time_seconds[5m]) > 0",
        "tagKeys": "version",
        "textFormat": "Deploy {{ version }}"
      }
    ]
  }
}
```

---

## 🔧 Troubleshooting

### Dashboard Não Carrega

**Problema**: Dashboard vazio ou erro de carregamento

**Solução**:
```bash
# 1. Verificar Prometheus está coletando métricas
curl http://localhost:9090/api/v1/query?query=up

# 2. Verificar datasource no Grafana
# Grafana → Configuration → Data Sources → Prometheus
# Test: Should return "Data source is working"

# 3. Reiniciar Grafana
docker-compose -f docker-compose.monitoring.yml restart grafana
```

### Métricas Não Aparecem

**Problema**: Query retorna "No data"

**Solução**:
```bash
# 1. Verificar backend está expondo métricas
curl http://localhost:8000/health/metrics | grep cidadao_ai

# 2. Verificar Prometheus está scraping
# http://localhost:9090/targets
# cidadao-ai-backend deve estar "UP"

# 3. Testar query no Prometheus UI
# http://localhost:9090/graph
# Executar query manualmente
```

### Alertas Não Disparam

**Problema**: Alertas configurados mas não notificam

**Solução**:
```bash
# 1. Verificar regras de alerta
curl http://localhost:9090/api/v1/rules

# 2. Verificar Alertmanager
docker-compose logs alertmanager

# 3. Testar notificação manualmente
# Prometheus → Alerts → Fire test alert
```

---

## 📚 Recursos Adicionais

### Documentação Oficial
- **Grafana**: https://grafana.com/docs/
- **Prometheus**: https://prometheus.io/docs/
- **PromQL**: https://prometheus.io/docs/prometheus/latest/querying/basics/

### Exemplos de Queries PromQL

```promql
# Taxa de requisições (req/s)
rate(http_requests_total[5m])

# Latência p95 por endpoint
histogram_quantile(0.95,
  sum by (le, path) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)

# Top 5 endpoints por volume
topk(5, sum by (path) (rate(http_requests_total[5m])))

# Error rate por status code
sum by (status) (rate(http_requests_total{status=~"5.."}[5m]))

# Throughput de agentes
sum(rate(cidadao_ai_agent_tasks_total[5m])) by (agent_name)

# Anomalias por severidade (últimas 24h)
increase(cidadao_ai_anomalies_detected_total[24h]) by (severity)
```

### Integração com Alertas

```yaml
# alertmanager.yml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/XXX'
        channel: '#ops-alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ .CommonAnnotations.description }}'

  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'XXX'
        description: '{{ .CommonAnnotations.summary }}'

route:
  receiver: 'slack'
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 5m
  repeat_interval: 4h

  routes:
    - match:
        severity: critical
      receiver: pagerduty
```

---

## ✅ Checklist de Implementação

### Configuração Inicial

- [ ] Docker Compose configurado
- [ ] Prometheus coletando métricas (/health/metrics)
- [ ] Grafana acessível (http://localhost:3000)
- [ ] Datasource Prometheus configurado
- [ ] Dashboards importados

### Dashboards Funcionais

- [ ] Overview dashboard mostrando dados
- [ ] Agents dashboard com métricas de todos agentes
- [ ] Federal APIs dashboard rastreando APIs externas
- [ ] SLO/SLA dashboard calculando uptime
- [ ] System Performance com métricas de infra
- [ ] Zumbi dashboard com anomalias

### Alertas Configurados

- [ ] Regras de alerta carregadas
- [ ] Alertmanager configurado
- [ ] Notificações testadas (Slack/Email/PagerDuty)
- [ ] On-call rotation definida

### Produção

- [ ] Dashboards em produção (Railway)
- [ ] Prometheus persistence configurado
- [ ] Grafana com autenticação
- [ ] Backup de dashboards
- [ ] Documentação atualizada

---

## 🎯 Próximos Passos

### Melhorias Planejadas

1. **Tracing Distribuído** (Jaeger integration)
   - Rastreamento end-to-end de requisições
   - Visualização de latência por componente
   - Debug de performance multi-serviço

2. **Logs Centralizados** (Loki integration)
   - Agregação de logs de todos componentes
   - Busca e filtros avançados
   - Correlação com métricas e traces

3. **Alertas Preditivos** (ML-based)
   - Detecção de anomalias em métricas
   - Alertas proativos antes de SLA breach
   - Capacity planning automático

4. **Dashboard Mobile**
   - App mobile para monitoramento
   - Notificações push
   - Ações rápidas (restart, scale)

---

## 📞 Suporte

**Mantenedor**: Anderson Henrique da Silva
**Email**: [Configurar]
**Localização**: Minas Gerais, Brasil

**Reportar Problemas**:
- GitHub Issues: [Configurar]
- Slack: #ops-monitoring
- On-call: [Configurar PagerDuty]

---

**Última Atualização**: 2025-10-30
**Versão do Documento**: 1.0
**Status**: ✅ Produção
