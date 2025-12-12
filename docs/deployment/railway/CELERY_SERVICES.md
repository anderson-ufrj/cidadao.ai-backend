# Configuração de Serviços Celery no Railway

## Problema Identificado (2025-12-12)

As investigações estavam ficando **travadas** com status "running" porque:

1. O Railway só executa o serviço `web` do Procfile por padrão
2. Os serviços `worker` e `beat` do Celery **não estavam rodando**
3. Sem workers, as tarefas assíncronas nunca são processadas

## Solução

### Opção 1: Múltiplos Serviços no Railway (Recomendado)

O Railway permite criar múltiplos serviços a partir do mesmo repositório.

#### Passo a Passo:

1. **No Dashboard do Railway**, vá para o projeto `cidadao-api`

2. **Crie o serviço Worker**:
   - Clique em "New Service" → "GitHub Repo"
   - Selecione o mesmo repositório
   - Configure:
     - **Name**: `cidadao-worker`
     - **Start Command**: `celery -A src.infrastructure.queue.celery_app worker --loglevel=info --queues=critical,high,default,low,background --concurrency=4`
   - **Variables**: Copie todas as variáveis do serviço web
   - **NÃO** configure health check (workers não expõem HTTP)

3. **Crie o serviço Beat**:
   - Clique em "New Service" → "GitHub Repo"
   - Selecione o mesmo repositório
   - Configure:
     - **Name**: `cidadao-beat`
     - **Start Command**: `celery -A src.infrastructure.queue.celery_app beat --loglevel=info`
   - **Variables**: Copie todas as variáveis do serviço web
   - **NÃO** configure health check (beat não expõe HTTP)

4. **Verifique as variáveis de ambiente** estão presentes em todos os serviços:
   - `DATABASE_URL` (PostgreSQL)
   - `REDIS_URL` (Redis)
   - `SECRET_KEY`
   - `JWT_SECRET_KEY`
   - `MARITACA_API_KEY` ou `ANTHROPIC_API_KEY`

#### Custo Estimado:
- Web: ~$5-10/mês
- Worker: ~$3-5/mês (pode escalar para 0 quando idle)
- Beat: ~$1-2/mês (muito leve)

### Opção 2: Serviço Único com Multi-Processo (Alternativo)

Se preferir manter um único serviço (para economizar):

1. **Altere o Start Command do serviço web**:
   ```bash
   python scripts/deployment/start_all_services.py
   ```

2. **Desvantagens**:
   - Menos controle sobre cada serviço
   - Se um processo morrer, todos morrem
   - Mais difícil debugar problemas
   - Não escala workers independentemente

## Variáveis de Ambiente Necessárias

```env
# Obrigatórias
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
JWT_SECRET_KEY=...

# LLM (pelo menos uma)
MARITACA_API_KEY=...
# ou
ANTHROPIC_API_KEY=...

# Opcional
TRANSPARENCY_API_KEY=...
APP_ENV=production
```

## Verificando se Funciona

### 1. Verificar Health dos Serviços

```bash
curl https://cidadao-api-production.up.railway.app/health/status
```

Deve mostrar:
```json
{
  "status": "healthy",
  "services": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"}
  }
}
```

### 2. Verificar Tasks Agendadas

```bash
curl https://cidadao-api-production.up.railway.app/tasks/list/scheduled
```

Deve listar as 22 tarefas agendadas.

### 3. Verificar Auto-Investigation

```bash
curl https://cidadao-api-production.up.railway.app/tasks/health/auto-investigation
```

### 4. Verificar Investigações no Banco

```bash
curl https://cidadao-api-production.up.railway.app/api/v1/debug/list-all-investigations
```

Se as investigações estiverem completando (status != "running" depois de alguns minutos), está funcionando!

## Limpando Investigações Travadas

Se houver investigações travadas de antes da correção:

```bash
# Ver estatísticas
python scripts/deployment/cleanup_stuck_investigations.py --stats-only

# Dry run (ver o que seria alterado)
python scripts/deployment/cleanup_stuck_investigations.py --dry-run

# Executar limpeza (marca como cancelled)
python scripts/deployment/cleanup_stuck_investigations.py

# Marcar como failed (para análise posterior)
python scripts/deployment/cleanup_stuck_investigations.py --force
```

## Monitoramento

### Logs dos Workers (Railway Dashboard)

- Vá para o serviço `cidadao-worker`
- Clique em "Logs"
- Procure por:
  - `Task started: tasks.xxx`
  - `Task completed: tasks.xxx`
  - `Task failed: tasks.xxx`

### Métricas Celery

```bash
# Se Flower estiver habilitado
# Descomente a linha no Procfile:
# flower: celery -A src.infrastructure.queue.celery_app flower --port=5555
```

## Troubleshooting

### Worker não conecta ao Redis

```
Error: Cannot connect to redis://...
```

**Solução**: Verifique se `REDIS_URL` está correto e se o serviço Redis está rodando.

### Worker não encontra tarefas

```
[celery] Received unregistered task
```

**Solução**: Verifique se o `include` em `celery_app.py` lista todos os módulos de tasks.

### Beat não agenda tarefas

```
beat: Scheduler database not available
```

**Solução**: Verifique se `REDIS_URL` está acessível. O beat precisa do Redis para persistir o schedule.

## Arquitetura dos Serviços

```
┌─────────────────────────────────────────────────────────────────┐
│                         Railway Project                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │  cidadao-   │    │  cidadao-   │    │  cidadao-   │        │
│  │    web      │    │   worker    │    │    beat     │        │
│  │  (FastAPI)  │    │  (Celery)   │    │  (Celery)   │        │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘        │
│         │                  │                  │                 │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                   ┌────────▼────────┐                          │
│                   │     Redis       │                          │
│                   │  (Message Broker)│                          │
│                   └─────────────────┘                          │
│                                                                 │
│                   ┌─────────────────┐                          │
│                   │   PostgreSQL    │                          │
│                   │   (Database)    │                          │
│                   └─────────────────┘                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Tarefas Agendadas (Beat Schedule)

| Tarefa | Frequência | Descrição |
|--------|------------|-----------|
| cleanup-old-results | 24h | Limpa resultados antigos |
| health-check | 5min | Verifica saúde dos workers |
| auto-monitor-new-contracts-6h | 6h | Monitora novos contratos |
| auto-monitor-priority-orgs-4h | 4h | Monitora órgãos prioritários |
| cleanup-stuck-investigations-15m | 15min | Limpa investigações travadas |
| katana-monitor-dispensas-6h | 6h | Monitora dispensas de licitação |
| calculate-network-metrics-daily | 24h | Calcula métricas de rede |
| detect-suspicious-networks-6h | 6h | Detecta redes suspeitas |
| memory-decay-daily | 24h | Decay de memória (Nanã) |

Total: **22 tarefas agendadas**
