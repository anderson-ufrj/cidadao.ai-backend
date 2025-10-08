# 🤖 Sistema de Investigação Autônoma 24/7

**Autor**: Anderson Henrique da Silva
**Data**: 2025-10-07 18:11:37
**Status**: ✅ Implementado e Pronto para Produção

## 📋 Visão Geral

Sistema completamente autônomo que monitora contratos governamentais 24 horas por dia, 7 dias por semana, detectando automaticamente padrões suspeitos e criando investigações forenses detalhadas SEM intervenção humana.

## 🎯 O Que o Sistema Faz

### 1. Monitoramento Contínuo de Contratos Novos
- **Frequência**: A cada 6 horas
- **Lookback**: Últimas 6 horas de contratos
- **Fonte**: Portal da Transparência API
- **Ação**: Cria investigações automáticas para contratos suspeitos

### 2. Monitoramento Prioritário de Órgãos Críticos
- **Frequência**: A cada 4 horas
- **Fila**: High Priority
- **Órgãos**: Lista configurável de órgãos com histórico de irregularidades
- **Ação**: Análise mais frequente e detalhada

### 3. Reanálise de Contratos Históricos
- **Frequência**: Semanal (domingos 3h)
- **Lookback**: 6 meses
- **Propósito**: Encontrar anomalias previamente perdidas com modelos atualizados
- **Processamento**: Lotes de 100 contratos por vez

### 4. Health Check do Sistema
- **Frequência**: A cada hora
- **Verifica**: API Transparência, Investigation Service, Agent Pool
- **Alertas**: Logs de componentes com problemas

## 🔍 Critérios de Pré-Triagem (Suspicion Score)

O sistema calcula automaticamente um "suspicion score" baseado em:

| Critério | Pontos | Descrição |
|----------|--------|-----------|
| **Valor Alto** | +2 | Contratos acima de R$ 100.000 |
| **Processo Emergencial** | +3 | Dispensa ou inexigibilidade de licitação |
| **Licitante Único** | +2 | Apenas 1 proponente no processo |
| **Fornecedor em Watchlist** | +3 | Fornecedor com histórico de problemas |
| **Prazo Curto de Licitação** | +1 | Tempo insuficiente para competição |

**Threshold para Investigação**: Score ≥ 3 pontos

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                   Celery Beat Scheduler                      │
│         (Agenda e dispara tarefas periodicamente)            │
└───────────────┬─────────────────────────────────────────────┘
                │
    ┌───────────┼───────────┬────────────┬───────────────┐
    │           │           │            │               │
    ▼           ▼           ▼            ▼               ▼
 [6h Task]  [4h Task]  [Weekly]    [Hourly]      [On-Demand]
New Contracts Priority Historical  Health     User-Triggered
Monitor      Orgs     Reanalysis   Check      Investigations
    │           │           │            │               │
    └───────────┴───────────┴────────────┴───────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │ Auto Investigation Service     │
            │ - Fetch contracts from API     │
            │ - Pre-screen for suspicion     │
            │ - Trigger full investigation   │
            └───────────────┬───────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │ Zumbi (InvestigatorAgent)     │
            │ - Full anomaly detection       │
            │ - Forensic enrichment          │
            │ - Evidence collection          │
            └───────────────┬───────────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │ Supabase (Database)            │
            │ - Investigation records        │
            │ - Forensic results             │
            │ - ML feedback data             │
            └───────────────────────────────┘
```

## 🚀 Como Ativar

### Pré-requisitos

1. **Redis** instalado e rodando:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis

# Docker
docker run -d -p 6379:6379 redis:7-alpine
```

2. **Variáveis de ambiente configuradas**:
```bash
# .env
REDIS_URL=redis://localhost:6379/0
TRANSPARENCY_API_KEY=sua-chave-aqui  # Opcional mas recomendado
SUPABASE_URL=sua-url-supabase
SUPABASE_SERVICE_ROLE_KEY=sua-chave-supabase
GROQ_API_KEY=sua-chave-groq  # Para LLM dos agentes
```

### Iniciar o Sistema

#### Opção 1: Desenvolvimento Local

```bash
# Terminal 1: Celery Worker
celery -A src.infrastructure.queue.celery_app worker \
  --loglevel=info \
  --queues=critical,high,default,low,background \
  --concurrency=4

# Terminal 2: Celery Beat (Scheduler)
celery -A src.infrastructure.queue.celery_app beat \
  --loglevel=info
```

#### Opção 2: Produção (Supervisor)

Criar `/etc/supervisor/conf.d/cidadao-ai-celery.conf`:

```ini
[program:cidadao-ai-worker]
command=/path/to/venv/bin/celery -A src.infrastructure.queue.celery_app worker --loglevel=info --queues=critical,high,default,low,background --concurrency=8
directory=/path/to/cidadao.ai-backend
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log

[program:cidadao-ai-beat]
command=/path/to/venv/bin/celery -A src.infrastructure.queue.celery_app beat --loglevel=info
directory=/path/to/cidadao.ai-backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/beat.log
```

Aplicar configuração:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start cidadao-ai-worker
sudo supervisorctl start cidadao-ai-beat
```

#### Opção 3: Docker Compose

Adicionar ao `docker-compose.yml`:

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  celery-worker:
    build: .
    command: celery -A src.infrastructure.queue.celery_app worker --loglevel=info --queues=critical,high,default,low,background
    depends_on:
      - redis
    env_file:
      - .env
    volumes:
      - .:/app

  celery-beat:
    build: .
    command: celery -A src.infrastructure.queue.celery_app beat --loglevel=info
    depends_on:
      - redis
      - celery-worker
    env_file:
      - .env
    volumes:
      - .:/app

volumes:
  redis_data:
```

Iniciar:
```bash
docker-compose up -d redis celery-worker celery-beat
```

## 📊 Monitoramento

### Ver Tarefas Agendadas

```bash
celery -A src.infrastructure.queue.celery_app inspect scheduled
```

### Ver Tarefas Ativas

```bash
celery -A src.infrastructure.queue.celery_app inspect active
```

### Ver Estatísticas

```bash
celery -A src.infrastructure.queue.celery_app inspect stats
```

### Flower (Web UI)

```bash
pip install flower
celery -A src.infrastructure.queue.celery_app flower
# Acesse: http://localhost:5555
```

## 🎛️ Configuração Avançada

### Ajustar Frequência de Monitoramento

Edite `src/infrastructure/queue/celery_app.py`:

```python
celery_app.conf.beat_schedule = {
    "auto-monitor-new-contracts-6h": {
        "schedule": timedelta(hours=3),  # Mude de 6h para 3h
        "args": (3,),  # Lookback de 3h
    },
}
```

### Adicionar Órgãos Prioritários

Edite `src/infrastructure/queue/tasks/auto_investigation_tasks.py`:

```python
priority_orgs = [
    "26101",  # Ministério da Saúde
    "20101",  # Ministério da Educação
    "53000",  # Prefeitura de São Paulo
    # Adicione mais códigos aqui
]
```

### Ajustar Thresholds de Detecção

Edite `src/services/auto_investigation_service.py`:

```python
self.value_threshold = 50000.0  # Reduzir para R$ 50k
self.daily_contract_limit = 1000  # Aumentar limite diário
```

## 📈 Métricas e KPIs

O sistema automaticamente coleta:

- **Contratos Analisados**: Total de contratos processados
- **Taxa de Suspeição**: % de contratos que passam pré-triagem
- **Investigações Criadas**: Quantidade de investigações automáticas
- **Anomalias Detectadas**: Total de irregularidades encontradas
- **Tempo de Processamento**: Duração média das investigações
- **Taxa de Sucesso**: % de investigações completadas com sucesso

Acesse via Flower ou logs estruturados.

## 🛠️ Troubleshooting

### Problema: Tasks não executam

**Causa**: Redis não está rodando ou configuração incorreta

**Solução**:
```bash
# Verificar Redis
redis-cli ping
# Deve retornar: PONG

# Verificar configuração
echo $REDIS_URL
# Deve retornar: redis://localhost:6379/0
```

### Problema: Muitos erros de API

**Causa**: Rate limit do Portal da Transparência

**Solução**: Ajustar delays no código ou adicionar `TRANSPARENCY_API_KEY`

### Problema: Investigações não aparecem no frontend

**Causa**: Supabase não configurado ou credenciais inválidas

**Solução**:
```bash
# Verificar variáveis
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_ROLE_KEY

# Testar conexão
python -c "from src.services.supabase_service_rest import get_supabase_service_rest; import asyncio; print(asyncio.run(get_supabase_service_rest()))"
```

## 🔐 Segurança

- ✅ Tasks rodando com user `system_auto_monitor`
- ✅ Rate limiting configurado para APIs externas
- ✅ Logs estruturados com rastreabilidade completa
- ✅ Retry automático com backoff exponencial
- ✅ Timeout configurado para evitar tasks travadas

## 📝 Próximos Passos

1. **Aprendizado Automático**: Treinar modelos ML com dados coletados
2. **Notificações**: Alertas quando anomalias críticas são encontradas
3. **Dashboard Analytics**: Visualização de descobertas em tempo real
4. **Watchlist Dinâmica**: Atualização automática de fornecedores suspeitos
5. **Cross-referência**: Integração com outros sistemas de fiscalização

## 📚 Referências

- [Documentação Celery](https://docs.celeryq.dev/)
- [Portal da Transparência API](https://api.portaldatransparencia.gov.br/swagger-ui.html)
- [Supabase Python Client](https://supabase.com/docs/reference/python)

---

**Status**: ✅ Sistema operacional e pronto para produção
**Última atualização**: 2025-10-07 18:11:37 (America/Sao_Paulo)
**Autor**: Anderson Henrique da Silva
