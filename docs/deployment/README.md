# 🚀 Guia de Deployment - Cidadão.AI Backend

**Autor**: Anderson Henrique da Silva
**Última Atualização**: 2025-12-17
**Plataforma Atual**: Railway (produção desde 07/10/2025)

[English version below](#-deployment-guide---cidadãoai-backend-english)

## 📊 Estado Atual

O sistema está **em produção** no Railway com PostgreSQL e Redis gerenciados, oferecendo:
- 99.9% de uptime desde outubro 2025
- Celery workers para processamento assíncrono
- Monitoramento com Prometheus/Grafana

**URL de Produção**: https://cidadao-api-production.up.railway.app

## 🎯 Opções de Deploy

### 1. Railway (Atual - Recomendado) ✅

**Prós**: PostgreSQL/Redis gerenciados, Celery support, CI/CD via GitHub
**Contras**: Custo (plano gratuito limitado)

```bash
# Deploy automático via GitHub
# Commits na branch main são automaticamente deployed
git push origin main
```

**Configuração no Railway**:
1. Conecte seu repositório GitHub
2. Configure as variáveis de ambiente:
   - `MARITACA_API_KEY` ou `ANTHROPIC_API_KEY`
   - `JWT_SECRET_KEY`
   - `SECRET_KEY`
   - `DATABASE_URL` (automático se usar Railway PostgreSQL)
   - `REDIS_URL` (automático se usar Railway Redis)

Veja: [docs/deployment/railway/README.md](railway/README.md)

### 2. Docker Local 🐳

**Para desenvolvimento e testes**:

```bash
# Build e execução básica
docker build -t cidadao-ai .
docker run -p 8000:8000 --env-file .env cidadao-ai

# Com docker-compose (inclui Redis)
docker-compose up -d

# Com monitoramento completo
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

### 3. VPS com Docker 🖥️

**Para produção completa com banco de dados**:

```bash
# 1. Configure o servidor (Ubuntu 22.04)
ssh usuario@seu-servidor
sudo apt update && sudo apt install docker.io docker-compose

# 2. Clone o projeto
git clone https://github.com/anderson-ufrj/cidadao.ai-backend
cd cidadao.ai-backend

# 3. Configure variáveis
cp .env.example .env
nano .env  # Configure todas as variáveis

# 4. Execute
docker-compose -f docker-compose.production.yml up -d
```

### 4. Kubernetes ☸️

**Para alta disponibilidade**:

```bash
# Apply configurações
kubectl apply -f k8s/

# Verificar pods
kubectl get pods -n cidadao-ai

# Expor serviço
kubectl expose deployment cidadao-api --type=LoadBalancer --port=80
```

## 🔑 Variáveis de Ambiente

### Essenciais (Obrigatórias)
```bash
# Autenticação
JWT_SECRET_KEY=gere-com-openssl-rand-hex-32
SECRET_KEY=outra-chave-aleatoria

# LLM Provider (escolha um)
LLM_PROVIDER=maritaca
MARITACA_API_KEY=sua-chave-maritaca
# ou
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sua-chave-anthropic
```

### Opcionais (Recursos Extras)
```bash
# Portal da Transparência (sem isso usa dados demo)
TRANSPARENCY_API_KEY=sua-chave-api

# Banco de Dados (sem isso usa SQLite em memória)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cidadao

# Cache Redis (sem isso usa memória)
REDIS_URL=redis://localhost:6379

# Configurações de Performance
WORKERS=4
MAX_AGENTS=10
CACHE_TTL=3600
```

## 📋 Checklist de Deploy

### Produção Railway (Recomendado)
- [ ] Repositório GitHub conectado ao Railway
- [ ] Variáveis de ambiente configuradas
- [ ] PostgreSQL addon ativado
- [ ] Redis addon ativado (para cache/Celery)
- [ ] Domínio customizado (opcional)
- [ ] Monitoramento configurado

### Produção Completa (VPS/Cloud)
- [ ] Servidor com mínimo 2GB RAM
- [ ] Docker e docker-compose instalados
- [ ] PostgreSQL configurado
- [ ] Redis configurado (opcional)
- [ ] SSL/TLS configurado (Nginx + Certbot)
- [ ] Backup configurado
- [ ] Monitoramento ativo

## 📊 Monitoramento

### Endpoints de Health Check
```bash
# Básico
curl https://cidadao-api-production.up.railway.app/health

# Detalhado (requer auth)
curl -H "Authorization: Bearer $TOKEN" https://cidadao-api-production.up.railway.app/health/detailed

# Métricas Prometheus
curl https://cidadao-api-production.up.railway.app/health/metrics
```

### Grafana Dashboards
Se usando docker-compose com monitoramento:
- **URL**: http://localhost:3000
- **User**: admin
- **Pass**: cidadao123

Dashboards disponíveis:
- System Overview
- Agent Performance
- API Metrics
- Cache Analytics

## 🚨 Troubleshooting

### Erro: "No module named 'src'"
```bash
# Adicione ao Dockerfile ou startup
export PYTHONPATH=/app:$PYTHONPATH
```

### Erro: Redis connection failed
O sistema funciona sem Redis, mas se quiser ativar:
```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

### Erro: Database connection failed
O sistema usa memória se não encontrar PostgreSQL. Para ativar:
```bash
docker run -d --name postgres \
  -e POSTGRES_DB=cidadao \
  -e POSTGRES_USER=cidadao \
  -e POSTGRES_PASSWORD=senha \
  -p 5432:5432 \
  postgres:15-alpine
```

### Performance Lenta
1. Verifique CPU/RAM: `docker stats`
2. Aumente workers: `WORKERS=8`
3. Ative cache Redis
4. Use agent pooling

## 🔒 Segurança

### Configurações Essenciais
1. **Sempre** gere novas chaves secretas
2. **Nunca** commite .env no git
3. Use HTTPS em produção
4. Configure rate limiting
5. Mantenha dependências atualizadas

### Gerar Chaves Seguras
```bash
# JWT Secret
openssl rand -hex 32

# Secret Key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

# 🚀 Deployment Guide - Cidadão.AI Backend (English)

**Author**: Anderson Henrique da Silva
**Last Updated**: 2025-12-17
**Current Platform**: Railway (production since 07/10/2025)

## 📊 Current Status

The system is **in production** on Railway with managed PostgreSQL and Redis, offering:
- 99.9% uptime since October 2025
- Celery workers for async processing
- Monitoring with Prometheus/Grafana

**Production URL**: https://cidadao-api-production.up.railway.app

## 🎯 Deployment Options

### 1. Railway (Current - Recommended) ✅

**Pros**: Managed PostgreSQL/Redis, Celery support, CI/CD via GitHub
**Cons**: Cost (free tier limited)

```bash
# Automatic deployment via GitHub
# Commits to main branch are automatically deployed
git push origin main
```

**Railway Configuration**:
1. Connect your GitHub repository
2. Configure environment variables:
   - `MARITACA_API_KEY` or `ANTHROPIC_API_KEY`
   - `JWT_SECRET_KEY`
   - `SECRET_KEY`
   - `DATABASE_URL` (automatic if using Railway PostgreSQL)
   - `REDIS_URL` (automatic if using Railway Redis)

See: [docs/deployment/railway/README.md](railway/README.md)

### 2. Local Docker 🐳

**For development and testing**:

```bash
# Basic build and run
docker build -t cidadao-ai .
docker run -p 8000:8000 --env-file .env cidadao-ai

# With docker-compose (includes Redis)
docker-compose up -d

# With complete monitoring
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

### 3. VPS with Docker 🖥️

**For complete production with database**:

```bash
# 1. Configure server (Ubuntu 22.04)
ssh user@your-server
sudo apt update && sudo apt install docker.io docker-compose

# 2. Clone project
git clone https://github.com/anderson-ufrj/cidadao.ai-backend
cd cidadao.ai-backend

# 3. Configure variables
cp .env.example .env
nano .env  # Configure all variables

# 4. Run
docker-compose -f docker-compose.production.yml up -d
```

### 4. Kubernetes ☸️

**For high availability**:

```bash
# Apply configurations
kubectl apply -f k8s/

# Check pods
kubectl get pods -n cidadao-ai

# Expose service
kubectl expose deployment cidadao-api --type=LoadBalancer --port=80
```

## 🔑 Environment Variables

### Essential (Required)
```bash
# Authentication
JWT_SECRET_KEY=generate-with-openssl-rand-hex-32
SECRET_KEY=another-random-key

# LLM Provider (choose one)
LLM_PROVIDER=maritaca
MARITACA_API_KEY=your-maritaca-key
# or
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-anthropic-key
```

### Optional (Extra Features)
```bash
# Portal da Transparência (without this uses demo data)
TRANSPARENCY_API_KEY=your-api-key

# Database (without this uses in-memory SQLite)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cidadao

# Redis Cache (without this uses memory)
REDIS_URL=redis://localhost:6379

# Performance Settings
WORKERS=4
MAX_AGENTS=10
CACHE_TTL=3600
```

## 📋 Deployment Checklist

### Railway Production (Recommended)
- [ ] GitHub repository connected to Railway
- [ ] Environment variables configured
- [ ] PostgreSQL addon activated
- [ ] Redis addon activated (for cache/Celery)
- [ ] Custom domain (optional)
- [ ] Monitoring configured

### Complete Production (VPS/Cloud)
- [ ] Server with minimum 2GB RAM
- [ ] Docker and docker-compose installed
- [ ] PostgreSQL configured
- [ ] Redis configured (optional)
- [ ] SSL/TLS configured (Nginx + Certbot)
- [ ] Backup configured
- [ ] Active monitoring

## 📊 Monitoring

### Health Check Endpoints
```bash
# Basic
curl https://cidadao-api-production.up.railway.app/health

# Detailed (requires auth)
curl -H "Authorization: Bearer $TOKEN" https://cidadao-api-production.up.railway.app/health/detailed

# Prometheus metrics
curl https://cidadao-api-production.up.railway.app/health/metrics
```

### Grafana Dashboards
If using docker-compose with monitoring:
- **URL**: http://localhost:3000
- **User**: admin
- **Pass**: cidadao123

Available dashboards:
- System Overview
- Agent Performance
- API Metrics
- Cache Analytics

## 🚨 Troubleshooting

### Error: "No module named 'src'"
```bash
# Add to Dockerfile or startup
export PYTHONPATH=/app:$PYTHONPATH
```

### Error: Redis connection failed
System works without Redis, but to enable:
```bash
docker run -d --name redis -p 6379:6379 redis:alpine
```

### Error: Database connection failed
System uses memory if PostgreSQL not found. To enable:
```bash
docker run -d --name postgres \
  -e POSTGRES_DB=cidadao \
  -e POSTGRES_USER=cidadao \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  postgres:15-alpine
```

### Slow Performance
1. Check CPU/RAM: `docker stats`
2. Increase workers: `WORKERS=8`
3. Enable Redis cache
4. Use agent pooling

## 🔒 Security

### Essential Settings
1. **Always** generate new secret keys
2. **Never** commit .env to git
3. Use HTTPS in production
4. Configure rate limiting
5. Keep dependencies updated

### Generate Secure Keys
```bash
# JWT Secret
openssl rand -hex 32

# Secret Key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 📚 Additional Resources

- [Railway Deployment Guide](railway/README.md)
- [Migration from HuggingFace](migration-hf-to-railway.md) (historical reference)
- [Docker Configuration](docker.md)
- [Celery Workers Setup](railway/CELERY_SERVICES.md)
