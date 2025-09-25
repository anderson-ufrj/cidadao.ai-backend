# 🏗️ Arquitetura - Cidadão.AI Backend

**Autor**: Anderson Henrique da Silva  
**Última Atualização**: 2025-09-25 18:15:00 -03:00 (São Paulo, Brasil)

[English version below](#-architecture---cidadãoai-backend-english)

## 📊 Visão Geral

O Cidadão.AI é um sistema multi-agente de IA para análise de transparência governamental brasileira, construído com arquitetura modular e escalável.

## 🧠 Sistema Multi-Agente

### Hierarquia de Agentes

```
┌─────────────────────────────────────────────────────────────┐
│                     Usuário / Frontend                       │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (FastAPI)                     │
│                  Rate Limiting | Auth | CORS                 │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                 🏎️ Ayrton Senna (Router)                    │
│              Detecção de Intenção | Roteamento              │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                ┌─────────────────┴─────────────────┐
                ▼                                   ▼
┌───────────────────────────────┐   ┌─────────────────────────┐
│    🎯 Abaporu (Master)        │   │   Agentes Diretos       │
│   Orquestração Complexa       │   │  (Para tarefas simples) │
└───────────────┬───────────────┘   └─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Pool de Agentes                           │
├─────────────────────────────────────────────────────────────┤
│ 🔍 Zumbi      │ 📊 Anita     │ 📝 Tiradentes │ 🧠 Nanã     │
│ Anomalias     │ Padrões     │ Relatórios   │ Memória     │
├───────────────┼──────────────┼──────────────┼──────────────┤
│ ⚖️ Bonifácio  │ 📚 Machado   │ 🛡️ Dandara   │ 🌍 Lampião  │
│ Políticas     │ Textos      │ Justiça      │ Regional    │
└─────────────────────────────────────────────────────────────┘
```

### Classes Base

1. **BaseAgent**
   - Retry logic com backoff exponencial
   - Monitoramento integrado (Prometheus)
   - Lifecycle management
   - Error handling

2. **ReflectiveAgent**
   - Auto-reflexão com threshold de qualidade (0.8)
   - Máximo 3 iterações de melhoria
   - Self-improvement loop

### Estados dos Agentes

```python
class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"
```

## 💾 Estratégia de Cache

### Multi-Layer Cache

```
┌─────────────────┐
│   Request       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ L1: Memory      │ ← 5ms latency
│ (LRU Cache)     │   TTL: 5 min
└────────┬────────┘
         ▼ miss
┌─────────────────┐
│ L2: Redis       │ ← 20ms latency
│ (Distributed)   │   TTL: 1 hour
└────────┬────────┘
         ▼ miss
┌─────────────────┐
│ L3: Database    │ ← 100ms latency
│ (PostgreSQL)    │   TTL: 24 hours
└─────────────────┘
```

### Cache Keys Strategy

```
chat:session:{session_id}:messages
investigation:{id}:results
agent:{agent_name}:state
portal:contracts:{org_code}:{page}
```

## 🚀 Otimizações de Performance

### 1. Agent Pool
- Pré-inicialização de instâncias
- Warm-up automático
- Lifecycle management
- Health checks

### 2. Parallel Processing
```python
# Estratégias disponíveis
- SEQUENTIAL: Execução em ordem
- PARALLEL: Todos ao mesmo tempo
- ADAPTIVE: Baseado em dependências
- PRIORITY: Por prioridade
```

### 3. JSON Optimization
- orjson para serialização 3x mais rápida
- Streaming responses
- Compression (Brotli/Gzip)

## 📊 Análise Espectral (FFT)

### Detecção de Padrões Periódicos

```python
# Pipeline de análise
1. Preprocessamento dos dados
2. Aplicação de FFT/RFFT
3. Detecção de picos no domínio da frequência
4. Classificação de componentes sazonais
5. Cálculo de entropia espectral
```

### Thresholds de Anomalia

- **Preço**: 2.5 desvios padrão
- **Concentração de fornecedor**: > 70%
- **Contratos duplicados**: > 85% similaridade
- **Frequência anômala**: > 3 desvios no espectro

## 🔒 Segurança

### Autenticação e Autorização

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│  JWT Auth   │────▶│   API       │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Rate Limit  │
                    │  by Tier    │
                    └─────────────┘
```

### Rate Limiting Tiers

```python
RATE_LIMIT_TIERS = {
    "anonymous": "10/minute",
    "authenticated": "60/minute",
    "premium": "300/minute",
    "admin": "unlimited"
}
```

## 📈 Monitoramento

### Métricas Prometheus

```python
# Métricas de agentes
agent_task_duration_seconds
agent_task_total
agent_errors_total
agent_reflection_iterations

# Métricas de API
http_request_duration_seconds
http_requests_total
active_websocket_connections

# Métricas de cache
cache_hits_total
cache_misses_total
cache_hit_rate
```

### Dashboards Grafana

1. **System Overview**: Visão geral do sistema
2. **Agent Performance**: Performance por agente
3. **API Metrics**: Latência e throughput
4. **Cache Analytics**: Hit rate e eficiência

## 🌐 Integração Portal da Transparência

### Endpoints Funcionais (22%)

```
/contracts  → GET com codigoOrgao obrigatório
/servants   → GET por CPF apenas
/agencies   → GET informações de órgãos
```

### Limitações Descobertas

- 78% dos endpoints retornam 403 Forbidden
- Sem documentação oficial sobre níveis de acesso
- Dados de salário não disponíveis

## 🔄 Fluxo de Dados

```
1. Request → API Gateway
2. Auth/Rate Limit Check
3. Intent Detection (Senna)
4. Cache Check (L1 → L2 → L3)
5. Agent Selection/Orchestration
6. External API Calls (if needed)
7. Result Processing
8. Cache Update
9. Response → Client
```

---

# 🏗️ Architecture - Cidadão.AI Backend (English)

**Author**: Anderson Henrique da Silva  
**Last Updated**: 2025-09-25 18:15:00 -03:00 (São Paulo, Brazil)

## 📊 Overview

Cidadão.AI is a multi-agent AI system for Brazilian government transparency analysis, built with modular and scalable architecture.

## 🧠 Multi-Agent System

### Agent Hierarchy

[Same diagram as above]

### Base Classes

1. **BaseAgent**
   - Retry logic with exponential backoff
   - Integrated monitoring (Prometheus)
   - Lifecycle management
   - Error handling

2. **ReflectiveAgent**
   - Self-reflection with quality threshold (0.8)
   - Maximum 3 improvement iterations
   - Self-improvement loop

### Agent States

[Same states as above]

## 💾 Cache Strategy

### Multi-Layer Cache

[Same diagram as above]

### Cache Keys Strategy

[Same keys as above]

## 🚀 Performance Optimizations

### 1. Agent Pool
- Pre-initialized instances
- Automatic warm-up
- Lifecycle management
- Health checks

### 2. Parallel Processing
[Same strategies as above]

### 3. JSON Optimization
- orjson for 3x faster serialization
- Streaming responses
- Compression (Brotli/Gzip)

## 📊 Spectral Analysis (FFT)

### Periodic Pattern Detection

[Same pipeline as above]

### Anomaly Thresholds

- **Price**: 2.5 standard deviations
- **Supplier concentration**: > 70%
- **Duplicate contracts**: > 85% similarity
- **Anomalous frequency**: > 3 deviations in spectrum

## 🔒 Security

### Authentication and Authorization

[Same diagram as above]

### Rate Limiting Tiers

[Same tiers as above]

## 📈 Monitoring

### Prometheus Metrics

[Same metrics as above]

### Grafana Dashboards

1. **System Overview**: System overview
2. **Agent Performance**: Performance by agent
3. **API Metrics**: Latency and throughput
4. **Cache Analytics**: Hit rate and efficiency

## 🌐 Portal da Transparência Integration

### Functional Endpoints (22%)

[Same endpoints as above]

### Discovered Limitations

- 78% of endpoints return 403 Forbidden
- No official documentation about access levels
- Salary data not available

## 🔄 Data Flow

[Same flow as above]