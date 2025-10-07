# 🚀 Deploying 24/7 Workers (HuggingFace + Separate Workers)

**Author**: Anderson Henrique da Silva
**Date**: 2025-10-07 18:20:00
**Architecture**: Hybrid (HF Spaces + VPS Workers)

## 🎯 Problema

HuggingFace Spaces **NÃO suporta** Celery workers porque:
- ❌ Só roda 1 processo (FastAPI)
- ❌ Não tem Redis incluído
- ❌ Não pode rodar múltiplos containers
- ❌ Não tem scheduler (cron)

## ✅ Solução: Hybrid Architecture

```
┌──────────────────────────────────────────────────────┐
│          HuggingFace Spaces (GRÁTIS)                 │
│                                                       │
│  ✅ FastAPI API pública                              │
│  ✅ Investigações sob demanda                        │
│  ✅ Documentação Swagger                             │
│  ✅ CORS configurado                                 │
│  ✅ https://neural-thinker-...hf.space               │
│                                                       │
└───────────────────┬──────────────────────────────────┘
                    │
                    │ Ambos salvam no mesmo banco
                    │
                    ▼
┌──────────────────────────────────────────────────────┐
│             Supabase (GRÁTIS)                        │
│                                                       │
│  📊 PostgreSQL Database                              │
│  📊 investigations table                             │
│  📊 investigation_feedback                           │
│  📊 ml_training_datasets                             │
│                                                       │
└───────────────────┬──────────────────────────────────┘
                    │
                    │ Workers leem/escrevem aqui também
                    │
                    ▼
┌──────────────────────────────────────────────────────┐
│          VPS/Cloud ($5-10/mês)                       │
│                                                       │
│  🤖 Celery Worker (4 concurrent)                     │
│  ⏰ Celery Beat (scheduler)                          │
│  🔴 Redis (message broker)                           │
│  📊 Flower (monitoring UI - opcional)                │
│                                                       │
│  🔄 Roda 24/7 automaticamente:                       │
│     - Monitor contratos novos (6h)                   │
│     - Monitor órgãos prioritários (4h)               │
│     - Reanálise histórica (semanal)                  │
│     - Health checks (hourly)                         │
│                                                       │
└──────────────────────────────────────────────────────┘
```

## 💰 Opções de Hospedagem para Workers

### Opção 1: VPS Tradicional (Mais Controle)

| Provider | Plano | CPU | RAM | Preço/mês |
|----------|-------|-----|-----|-----------|
| **DigitalOcean** | Basic Droplet | 1 CPU | 1 GB | $6 |
| **Linode** | Nanode 1GB | 1 CPU | 1 GB | $5 |
| **Vultr** | Cloud Compute | 1 CPU | 1 GB | $6 |
| **Hetzner** | CX11 | 1 CPU | 2 GB | €4.15 (~$4.50) |

**Vantagens**:
- ✅ Controle total
- ✅ SSH access
- ✅ Pode rodar outros serviços
- ✅ IP fixo

### Opção 2: Container Platforms (Mais Fácil)

| Provider | Plano | Preço/mês |
|----------|-------|-----------|
| **Railway.app** | Hobby | $5 + usage (~$10 total) |
| **Render.com** | Individual | $7/service ($21 para 3 services) |
| **Fly.io** | Free tier | $0 (256MB RAM limit) → $5+ |

**Vantagens**:
- ✅ Deploy automático via Git
- ✅ Logs centralizados
- ✅ Scaling fácil
- ✅ Menos manutenção

### Opção 3: Serverless (Mais Barato mas Limitado)

| Provider | Serviço | Preço/mês |
|----------|---------|-----------|
| **AWS** | Lambda + EventBridge | ~$1-2 |
| **Google Cloud** | Cloud Functions + Scheduler | ~$1-2 |
| **Vercel** | Cron Jobs | Grátis (limited) |

**Limitações**:
- ❌ Cold starts
- ❌ Timeout limits (15 min AWS, 9 min GCP)
- ❌ Menos controle

## 🚀 Deploy Methods

### Method 1: VPS com Script Automático (RECOMENDADO)

**Pré-requisitos**:
- VPS com Ubuntu 20.04+ ou Debian 11+
- Acesso SSH como root
- 1GB+ RAM

**Steps**:

```bash
# 1. SSH no seu VPS
ssh root@seu-vps-ip

# 2. Download do script
wget https://raw.githubusercontent.com/anderson-ufrj/cidadao.ai-backend/main/deploy/celery-workers-only.sh

# 3. Tornar executável
chmod +x celery-workers-only.sh

# 4. Executar (como root)
sudo ./celery-workers-only.sh

# 5. Editar credenciais
nano /opt/cidadao-ai-backend/.env

# Adicionar:
# SUPABASE_URL=https://seu-projeto.supabase.co
# SUPABASE_SERVICE_ROLE_KEY=eyJhbG...sua-chave
# GROQ_API_KEY=gsk_...sua-chave
# TRANSPARENCY_API_KEY=...sua-chave (opcional)

# 6. Reiniciar services
supervisorctl restart cidadao-ai-worker cidadao-ai-beat

# 7. Verificar logs
tail -f /var/log/celery/worker.log
```

### Method 2: Docker Compose (Portável)

**Pré-requisitos**:
- Docker e Docker Compose instalados
- Qualquer servidor/VPS

**Steps**:

```bash
# 1. Clone repo
git clone https://github.com/anderson-ufrj/cidadao.ai-backend.git
cd cidadao-ai-backend/deploy

# 2. Criar .env
cp .env.example .env
nano .env  # Adicionar credenciais

# 3. Iniciar
docker-compose -f docker-compose.workers-only.yml up -d

# 4. Ver logs
docker-compose -f docker-compose.workers-only.yml logs -f

# 5. Ver status
docker-compose -f docker-compose.workers-only.yml ps

# 6. Acessar Flower (monitoring)
# http://seu-vps-ip:5555
docker-compose -f docker-compose.workers-only.yml --profile monitoring up -d
```

### Method 3: Railway.app (1-Click Deploy)

1. Fork o repositório no GitHub
2. Acesse https://railway.app
3. New Project → Deploy from GitHub
4. Selecione o repositório
5. Adicione 3 services:
   - **Redis**: New → Database → Redis
   - **Worker**: New → GitHub → selecione repo
     - Start Command: `celery -A src.infrastructure.queue.celery_app worker --loglevel=info`
   - **Beat**: New → GitHub → selecione repo
     - Start Command: `celery -A src.infrastructure.queue.celery_app beat --loglevel=info`
6. Configure variáveis em cada service:
   - `REDIS_URL` (gerado automaticamente)
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `GROQ_API_KEY`

## 🔐 Configuração de Credenciais

### Necessárias (Mesmas do HuggingFace Spaces):

```bash
# Supabase (mesmo projeto do HF)
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# LLM para agentes
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Redis (local se VPS, ou Railway fornece)
REDIS_URL=redis://localhost:6379/0
```

### Opcionais:

```bash
# Portal da Transparência (melhor rate limit)
TRANSPARENCY_API_KEY=xxxxxxxxxxxxxxxxx

# Sentry (error tracking)
SENTRY_DSN=https://xxxxxxx@sentry.io/xxxxxxx

# Environment
ENVIRONMENT=production
ENABLE_CELERY_WORKERS=true
```

## 📊 Monitoramento

### Logs

**VPS (Supervisor)**:
```bash
# Worker
tail -f /var/log/celery/worker.log

# Beat
tail -f /var/log/celery/beat.log

# Ambos
tail -f /var/log/celery/*.log
```

**Docker**:
```bash
# Worker
docker logs -f cidadao-ai-worker

# Beat
docker logs -f cidadao-ai-beat

# Redis
docker logs -f cidadao-ai-redis
```

### Flower UI

Interface web para monitorar workers:

**VPS**:
```bash
pip install flower
celery -A src.infrastructure.queue.celery_app flower
# Acesse: http://seu-vps-ip:5555
```

**Docker**:
```bash
docker-compose --profile monitoring up -d
# Acesse: http://seu-vps-ip:5555
```

### Métricas Importantes

- **Tasks Succeeded**: Investigações completadas
- **Tasks Failed**: Erros (ver logs)
- **Active Tasks**: Investigações em andamento
- **Queue Length**: Tasks esperando processamento
- **Worker Uptime**: Tempo desde último restart

## 🔧 Troubleshooting

### Workers não iniciam

```bash
# Verificar logs
tail -100 /var/log/celery/worker.log

# Verificar se Redis está rodando
redis-cli ping  # Deve retornar PONG

# Testar manualmente
cd /opt/cidadao-ai-backend
source venv/bin/activate
celery -A src.infrastructure.queue.celery_app worker --loglevel=debug
```

### Tasks não executam

```bash
# Verificar se Beat está rodando
ps aux | grep celery

# Ver tasks agendadas
celery -A src.infrastructure.queue.celery_app inspect scheduled

# Forçar execução manual
python -c "from src.infrastructure.queue.tasks.auto_investigation_tasks import auto_monitor_new_contracts; auto_monitor_new_contracts.delay(6)"
```

### Erro de conexão com Supabase

```bash
# Testar conexão
python -c "
from src.services.supabase_service_rest import get_supabase_service_rest
import asyncio
client = asyncio.run(get_supabase_service_rest())
print('✅ Supabase conectado!')
"
```

### Alto uso de CPU/RAM

```bash
# Reduzir concurrency
# Editar /etc/supervisor/conf.d/cidadao-ai-worker.conf
# Mudar --concurrency=4 para --concurrency=2

# Reiniciar
supervisorctl restart cidadao-ai-worker
```

## ✅ Checklist de Validação

- [ ] Redis está rodando e acessível
- [ ] Worker iniciou sem erros
- [ ] Beat iniciou sem erros
- [ ] Variáveis de ambiente configuradas
- [ ] Conexão com Supabase testada
- [ ] Logs não mostram erros
- [ ] Flower UI acessível (se habilitado)
- [ ] Primeira task executou com sucesso
- [ ] Investigações aparecem no Supabase

## 💡 Dicas de Otimização

1. **Use SSD**: Workers fazem muitas operações I/O
2. **Monitore RAM**: 1GB mínimo, 2GB recomendado
3. **Backup Redis**: Habilite persistence (AOF)
4. **Logs rotativos**: Configurar logrotate
5. **Alertas**: Configurar notificações se worker cair

## 📚 Recursos Úteis

- [Celery Documentation](https://docs.celeryq.dev/)
- [Supervisor Documentation](http://supervisord.org/)
- [Redis Documentation](https://redis.io/docs/)
- [Railway Documentation](https://docs.railway.app/)

---

**Custo Total Estimado**: $5-15/mês
**Setup Time**: 15-30 minutos
**Manutenção**: Mínima (auto-restart configurado)
