# 🚀 Guia de Deployment - Cidadão.AI Backend

**Autor**: Anderson Henrique da Silva  
**Última Atualização**: 2025-09-25 18:30:00 -03:00 (São Paulo, Brasil)

[English version below](#-deployment-guide---cidadãoai-backend-english)

## 📊 Estado Atual

O sistema está **atualmente em produção** no HuggingFace Spaces com configuração simplificada (sem PostgreSQL/Redis).

## 🎯 Opções de Deploy

### 1. HuggingFace Spaces (Atual) ✅

**Prós**: Gratuito, fácil, CI/CD automático  
**Contras**: Sem banco de dados persistente, recursos limitados

```bash
# Deploy automático via push
git remote add hf https://huggingface.co/spaces/SEU_USUARIO/cidadao-ai
git push hf main
```

**Configuração no HuggingFace**:
1. Crie um Space com SDK Docker
2. Configure as secrets:
   - `GROQ_API_KEY`
   - `JWT_SECRET_KEY`
   - `TRANSPARENCY_API_KEY` (opcional)

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
git clone https://github.com/seu-usuario/cidadao.ai-backend
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

# LLM Provider
GROQ_API_KEY=sua-chave-groq
```

### Opcionais (Recursos Extras)
```bash
# Portal da Transparência (sem isso usa dados demo)
TRANSPARENCY_API_KEY=sua-chave-api

# Banco de Dados (sem isso usa memória)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cidadao

# Cache Redis (sem isso usa memória)
REDIS_URL=redis://localhost:6379

# Configurações de Performance
WORKERS=4
MAX_AGENTS=10
CACHE_TTL=3600
```

## 📋 Checklist de Deploy

### Produção Mínima (HuggingFace)
- [ ] Configurar secrets no HF Spaces
- [ ] Verificar app.py está usando configuração minimal
- [ ] Push para branch hf-fastapi
- [ ] Testar endpoints básicos

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
curl https://seu-dominio/health

# Detalhado (requer auth)
curl -H "Authorization: Bearer $TOKEN" https://seu-dominio/health/detailed

# Métricas Prometheus
curl https://seu-dominio/metrics
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
**Last Updated**: 2025-09-25 18:30:00 -03:00 (São Paulo, Brazil)

## 📊 Current Status

The system is **currently in production** on HuggingFace Spaces with simplified configuration (no PostgreSQL/Redis).

## 🎯 Deployment Options

### 1. HuggingFace Spaces (Current) ✅

**Pros**: Free, easy, automatic CI/CD  
**Cons**: No persistent database, limited resources

```bash
# Automatic deployment via push
git remote add hf https://huggingface.co/spaces/YOUR_USER/cidadao-ai
git push hf main
```

**HuggingFace Configuration**:
1. Create a Space with Docker SDK
2. Configure secrets:
   - `GROQ_API_KEY`
   - `JWT_SECRET_KEY`
   - `TRANSPARENCY_API_KEY` (optional)

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
git clone https://github.com/your-user/cidadao.ai-backend
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

# LLM Provider
GROQ_API_KEY=your-groq-key
```

### Optional (Extra Features)
```bash
# Portal da Transparência (without this uses demo data)
TRANSPARENCY_API_KEY=your-api-key

# Database (without this uses memory)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/cidadao

# Redis Cache (without this uses memory)
REDIS_URL=redis://localhost:6379

# Performance Settings
WORKERS=4
MAX_AGENTS=10
CACHE_TTL=3600
```

## 📋 Deployment Checklist

### Minimum Production (HuggingFace)
- [ ] Configure secrets in HF Spaces
- [ ] Verify app.py is using minimal configuration
- [ ] Push to hf-fastapi branch
- [ ] Test basic endpoints

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
curl https://your-domain/health

# Detailed (requires auth)
curl -H "Authorization: Bearer $TOKEN" https://your-domain/health/detailed

# Prometheus metrics
curl https://your-domain/metrics
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