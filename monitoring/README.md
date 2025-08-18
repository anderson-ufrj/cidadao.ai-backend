# 📊 Cidadão.AI Monitoring Stack

Sistema completo de observabilidade para o Cidadão.AI com Prometheus + Grafana + Node Exporter + cAdvisor.

## 🚀 Quick Start

### Iniciando o Stack de Monitoramento

```bash
# Usando o script de gerenciamento
./monitoring/manage-monitoring.sh start

# Ou usando docker-compose diretamente
docker-compose -f docker-compose.monitoring.yml up -d
```

### Acessando os Serviços

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| 🏛️ Cidadão.AI Backend | http://localhost:7860 | N/A |
| 📊 Grafana Dashboard | http://localhost:3000 | admin/cidadao123 |
| 📈 Prometheus | http://localhost:9090 | N/A |
| 🖥️ Node Exporter | http://localhost:9100 | N/A |
| 📦 cAdvisor | http://localhost:8080 | N/A |

## 📊 Dashboards Disponíveis

### 1. 🏛️ Cidadão.AI - Overview Dashboard
- **UID**: `cidadao-ai-overview`
- **Descrição**: Visão geral do sistema com métricas principais
- **Painéis**:
  - Taxa de requisições da API
  - Total de investigações
  - Distribuição de investigações por status
  - Distribuição de anomalias por tipo
  - Duração das requisições
  - Taxa de processamento de dados

### 2. 🏹 Zumbi dos Palmares - Investigador Dashboard
- **UID**: `zumbi-agent-dashboard`
- **Descrição**: Métricas específicas do agente investigador Zumbi
- **Painéis**:
  - Total de investigações
  - Anomalias detectadas
  - Taxa de sucesso das investigações
  - Duração das investigações (P95)
  - Taxa de investigação por tipo e status
  - Distribuição de tipos de anomalias
  - Taxa de fetch da API de Transparência
  - Distribuição de severidade das anomalias

### 3. 🖥️ System Performance Dashboard
- **UID**: `system-performance`
- **Descrição**: Métricas de performance do sistema
- **Painéis**:
  - Uso de CPU
  - Uso de memória
  - Duração de tarefas dos agentes
  - Taxa de tarefas por status
  - I/O de rede
  - I/O de disco

## 📈 Métricas Disponíveis

### Métricas da API
- `cidadao_ai_requests_total` - Total de requisições por método/endpoint
- `cidadao_ai_request_duration_seconds` - Duração das requisições

### Métricas de Agentes
- `cidadao_ai_agent_tasks_total` - Total de tarefas dos agentes por status
- `cidadao_ai_agent_task_duration_seconds` - Duração das tarefas dos agentes

### Métricas de Investigação
- `cidadao_ai_investigations_total` - Total de investigações por tipo/status
- `cidadao_ai_investigation_duration_seconds` - Duração das investigações
- `cidadao_ai_anomalies_detected_total` - Anomalias detectadas por tipo/severidade

### Métricas de Dados
- `cidadao_ai_data_records_processed_total` - Registros processados
- `cidadao_ai_transparency_data_fetched_total` - Dados da API de Transparência

## 🚨 Alertas Configurados

### Sistema
- **HighCPUUsage**: CPU > 80% por mais de 2 minutos
- **HighMemoryUsage**: Memória > 85% por mais de 2 minutos
- **ServiceDown**: Serviço Cidadão.AI fora do ar por mais de 1 minuto

### API
- **HighAPILatency**: Latência P95 > 2s por mais de 5 minutos
- **HighAPIErrorRate**: Taxa de erro > 5% por mais de 3 minutos
- **LowAPIThroughput**: Throughput < 0.1 req/s por mais de 10 minutos

### Investigações
- **HighInvestigationFailureRate**: Taxa de falha > 10% por mais de 5 minutos
- **LongInvestigationDuration**: Duração P95 > 5 minutos
- **NoAnomaliesDetected**: Nenhuma anomalia detectada por mais de 2 horas

### Dados
- **TransparencyAPIFailures**: Falhas ao buscar dados da API de Transparência
- **LowDataProcessingRate**: Taxa de processamento < 1 registro/s por mais de 15 minutos

### Agentes
- **HighAgentTaskFailureRate**: Taxa de falha > 5% por mais de 5 minutos
- **AgentTaskRetries**: Retries frequentes de tarefas de agentes

## 🛠️ Comandos de Gerenciamento

```bash
# Iniciar o stack
./monitoring/manage-monitoring.sh start

# Parar o stack
./monitoring/manage-monitoring.sh stop

# Reiniciar o stack
./monitoring/manage-monitoring.sh restart

# Ver status dos serviços
./monitoring/manage-monitoring.sh status

# Ver logs de todos os serviços
./monitoring/manage-monitoring.sh logs

# Ver logs de um serviço específico
./monitoring/manage-monitoring.sh logs prometheus
./monitoring/manage-monitoring.sh logs grafana

# Executar health checks
./monitoring/manage-monitoring.sh health

# Limpar todos os dados (cuidado!)
./monitoring/manage-monitoring.sh cleanup

# Ver ajuda
./monitoring/manage-monitoring.sh help
```

## 📁 Estrutura de Arquivos

```
monitoring/
├── README.md                           # Este arquivo
├── manage-monitoring.sh                # Script de gerenciamento
├── prometheus/
│   ├── prometheus.yml                 # Configuração do Prometheus
│   └── rules/
│       └── cidadao-ai-alerts.yml     # Regras de alerta
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   │   └── prometheus.yml         # Configuração do datasource
│   │   └── dashboards/
│   │       └── dashboards.yml         # Configuração dos dashboards
│   └── dashboards/
│       ├── cidadao-ai-overview.json   # Dashboard principal
│       ├── zumbi-agent-dashboard.json # Dashboard do agente Zumbi
│       └── system-performance.json    # Dashboard de performance
└── docker-compose.monitoring.yml       # Definição dos serviços
```

## 🔧 Configuração Avançada

### Customizando Intervalos de Coleta

No arquivo `prometheus/prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'cidadao-ai-backend'
    static_configs:
      - targets: ['cidadao-ai:7860']
    scrape_interval: 10s  # Alterar para intervalo desejado
```

### Adicionando Novos Alertas

Edite `prometheus/rules/cidadao-ai-alerts.yml`:

```yaml
- alert: NovoAlerta
  expr: sua_metrica > threshold
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Descrição do alerta"
    description: "Detalhes do que aconteceu"
```

### Customizando Dashboards

1. Acesse o Grafana em http://localhost:3000
2. Faça login (admin/cidadao123)
3. Edite os dashboards existentes ou crie novos
4. Exporte como JSON e salve em `grafana/dashboards/`

## 🐛 Troubleshooting

### Serviços não iniciam
```bash
# Verificar logs
./monitoring/manage-monitoring.sh logs

# Verificar Docker
docker info

# Verificar portas ocupadas
netstat -tulpn | grep -E "(3000|9090|7860|9100|8080)"
```

### Grafana não consegue conectar ao Prometheus
```bash
# Verificar se o Prometheus está rodando
curl http://localhost:9090/-/healthy

# Verificar logs do Grafana
./monitoring/manage-monitoring.sh logs grafana
```

### Métricas não aparecem
```bash
# Verificar endpoint de métricas
curl http://localhost:7860/health/metrics

# Verificar configuração do Prometheus
./monitoring/manage-monitoring.sh logs prometheus
```

## 📚 Recursos Adicionais

- [Documentação do Prometheus](https://prometheus.io/docs/)
- [Documentação do Grafana](https://grafana.com/docs/)
- [Best Practices de Monitoramento](https://prometheus.io/docs/practices/)
- [Query Language (PromQL)](https://prometheus.io/docs/prometheus/latest/querying/)

---

**Desenvolvido para o projeto Cidadão.AI** 🏛️  
Sistema de transparência pública com IA para o Brasil 🇧🇷