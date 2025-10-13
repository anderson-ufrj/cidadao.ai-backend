# Railway Multi-Service Deployment Guide

**Author**: Anderson Henrique da Silva
**Date**: 2025-10-13
**Architecture**: Multi-service with Procfile

---

## 🏗️ Architecture Overview

Your Railway project uses a **multi-service architecture** with 5 separate services:

```
┌─────────────────────────────────────────────────────────────┐
│                    Railway Project: cidadao.ai               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │  Postgres    │───▶│  cidadao-api │◀───│ cidadao-redis│ │
│  │  (Database)  │    │   (FastAPI)  │    │   (Cache)    │ │
│  └──────────────┘    └──────┬───────┘    └──────┬───────┘ │
│                              │                    │          │
│                              │                    │          │
│                              ▼                    ▼          │
│                       ┌──────────────┐    ┌──────────────┐ │
│                       │ cidadao.ai-  │    │ cidadao.ai-  │ │
│                       │   worker     │    │    beat      │ │
│                       │  (Celery)    │    │ (Scheduler)  │ │
│                       └──────────────┘    └──────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Service Definitions (Procfile)

```bash
# Database migrations (runs before deployment)
release: python -m alembic upgrade head

# Main API server (cidadao-api)
web: uvicorn src.api.app:app --host 0.0.0.0 --port $PORT

# Background task worker (cidadao.ai-worker)
worker: celery -A src.infrastructure.queue.celery_app worker \
        --loglevel=info \
        --queues=critical,high,default,low,background \
        --concurrency=4

# Scheduled task runner (cidadao.ai-beat)
beat: celery -A src.infrastructure.queue.celery_app beat \
      --loglevel=info
```

---

## 📊 Service Dependencies

### cidadao-api (Web Service)
**Depends on**:
- ✅ Postgres (DATABASE_URL)
- ✅ Redis (REDIS_URL)
- ✅ GROQ_API_KEY (LLM provider)
- ✅ JWT/SECRET keys

**Purpose**: Main FastAPI application serving HTTP requests

### cidadao.ai-worker (Celery Worker)
**Depends on**:
- ✅ Redis (REDIS_URL - message broker)
- ✅ Postgres (DATABASE_URL - result backend)
- ✅ All API keys (for background tasks)

**Purpose**: Process background tasks asynchronously

### cidadao.ai-beat (Celery Beat)
**Depends on**:
- ✅ Redis (REDIS_URL - message broker)
- ✅ Postgres (DATABASE_URL - schedule persistence)

**Purpose**: Schedule and trigger periodic tasks

### cidadao-redis (Redis Service)
**Depends on**: None (standalone)

**Purpose**:
- Message broker for Celery
- Cache layer for API
- Session storage

### Postgres (Database Service)
**Depends on**: None (standalone)

**Purpose**:
- Persistent data storage
- Investigation records
- User data
- Task results

---

## 🚀 Deployment Process

### 1. Railway Service Creation

Railway automatically creates services from your Procfile:

```
Procfile detected → Railway creates:
├── web → cidadao-api service
├── worker → cidadao.ai-worker service
├── beat → cidadao.ai-beat service
└── release → Pre-deployment migration job
```

### 2. Add Supporting Services

You manually added:
- **Postgres**: Database service
- **cidadao-redis**: Redis cache/broker

### 3. Environment Variables

All services share the same project environment variables:

#### Required for ALL services:
```bash
# Database
DATABASE_URL=${POSTGRES_CONNECTION_STRING}  # Auto-provided by Railway

# Redis
REDIS_URL=${REDIS_CONNECTION_STRING}  # Auto-provided by Railway

# Security
JWT_SECRET_KEY=your-jwt-secret
SECRET_KEY=your-app-secret
API_SECRET_KEY=your-api-secret

# LLM Provider
GROQ_API_KEY=your-groq-key

# Application
APP_ENV=production
LOG_LEVEL=INFO
```

#### Optional:
```bash
# Supabase (backup persistence)
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Portal da Transparência
TRANSPARENCY_API_KEY=your-transparency-key

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

---

## ⚙️ Service-Specific Configuration

### cidadao-api (Web Service) ⚡

#### Health Check Configuration

**Railway Dashboard** → **cidadao-api** → **Settings** → **Deploy**

```
Health Check Path: /health
Initial Delay: 15 seconds
Timeout: 5 seconds
Interval: 30 seconds
Failure Threshold: 3
```

**Why these settings?**
- `/health` is ultra-fast (<10ms), no external dependencies
- 15s delay allows application startup time
- 5s timeout sufficient for fast endpoint
- 30s interval balances monitoring frequency

#### Port Configuration

```bash
# Railway automatically provides $PORT
# Application must bind to: 0.0.0.0:$PORT
PORT=8080  # Default, Railway overrides
```

#### Resource Recommendations

- **Memory**: 512MB minimum, 1GB recommended
- **CPU**: 0.5 vCPU minimum, 1 vCPU recommended
- **Replicas**: Start with 1, scale as needed

### cidadao.ai-worker (Celery Worker) 🔧

#### Health Check Configuration

Celery workers don't expose HTTP endpoints, so **disable health checks** or use custom script:

**Option 1: Disable Health Check** (Recommended)
```
Railway Dashboard → cidadao.ai-worker → Settings → Deploy
Health Check: DISABLED
```

**Option 2: Custom Health Check Script**
```bash
# Add to project root: check_celery_worker.sh
#!/bin/bash
celery -A src.infrastructure.queue.celery_app inspect ping
```

#### Worker Configuration

```bash
# Celery worker options (defined in Procfile)
--loglevel=info                              # Logging level
--queues=critical,high,default,low,background # Queue priorities
--concurrency=4                              # Parallel tasks
```

#### Resource Recommendations

- **Memory**: 1GB minimum, 2GB recommended (handles multiple tasks)
- **CPU**: 1 vCPU minimum, 2 vCPU recommended
- **Replicas**: Scale horizontally based on queue depth

### cidadao.ai-beat (Celery Beat) ⏰

#### Health Check Configuration

**Disable health checks** for beat scheduler:

```
Railway Dashboard → cidadao.ai-beat → Settings → Deploy
Health Check: DISABLED
```

**Why?** Beat is a scheduler, not a worker. It only needs to stay running.

#### Beat Configuration

```bash
# Celery beat options (defined in Procfile)
--loglevel=info  # Logging level
```

**Important**: Only run **ONE** beat instance per project. Multiple beat instances will cause duplicate scheduled tasks.

#### Resource Recommendations

- **Memory**: 256MB minimum, 512MB recommended
- **CPU**: 0.25 vCPU minimum, 0.5 vCPU recommended
- **Replicas**: ALWAYS 1 (never scale beat)

### cidadao-redis (Redis Service) 💾

#### Health Check Configuration

Railway provides automatic health checks for managed Redis. No configuration needed.

#### Resource Recommendations

- **Memory**: 256MB minimum, 512MB recommended
- **Persistence**: Enabled (AOF + RDB)

### Postgres (Database Service) 🗄️

#### Health Check Configuration

Railway provides automatic health checks for managed Postgres. No configuration needed.

#### Resource Recommendations

- **Storage**: 1GB minimum, 5GB+ for production
- **Memory**: 256MB minimum, 1GB recommended
- **Backups**: Enable automatic backups

---

## 🔍 Troubleshooting by Service

### cidadao-api Issues

#### Symptom: Health check failures
```
[wrn] Health check failed
[err] Connection timeout
```

**Solution**:
1. Verify `/health` endpoint responds quickly:
   ```bash
   curl https://your-app.railway.app/health
   ```
2. Check logs for startup errors:
   ```bash
   railway logs --service cidadao-api --tail 50
   ```
3. Verify environment variables:
   ```bash
   railway variables --service cidadao-api
   ```

#### Symptom: Port binding errors
```
[err] Failed to bind to 0.0.0.0:8080
```

**Solution**: Ensure application uses `$PORT`:
```python
# In start.sh or Procfile
uvicorn src.api.app:app --host 0.0.0.0 --port $PORT
```

### cidadao.ai-worker Issues

#### Symptom: Worker not processing tasks
```
[inf] Worker started
[wrn] No tasks received for 5 minutes
```

**Solution**:
1. Verify Redis connection:
   ```bash
   railway logs --service cidadao.ai-worker | grep -i redis
   ```
2. Check queue status:
   ```bash
   railway run --service cidadao.ai-worker \
     celery -A src.infrastructure.queue.celery_app inspect active
   ```
3. Monitor queue depth in Railway dashboard

#### Symptom: Worker crashes with OOM
```
[err] MemoryError
[err] Worker killed by OOM
```

**Solution**: Increase worker memory:
```
Railway Dashboard → cidadao.ai-worker → Settings → Resources
Memory: Increase to 2GB
```

### cidadao.ai-beat Issues

#### Symptom: Duplicate scheduled tasks
```
[wrn] Task 'auto-monitor-new-contracts-6h' executed twice
```

**Solution**: Ensure only ONE beat instance:
```
Railway Dashboard → cidadao.ai-beat → Settings → Deploy
Replicas: Set to 1 (NEVER scale beat)
```

#### Symptom: Beat scheduler not running
```
[err] Beat scheduler failed to start
[err] Cannot connect to Redis
```

**Solution**: Verify Redis connection:
```bash
railway logs --service cidadao.ai-beat | grep -i redis
```

### cidadao-redis Issues

#### Symptom: Connection refused
```
[err] redis.exceptions.ConnectionError
```

**Solution**:
1. Verify Redis service is running
2. Check REDIS_URL format:
   ```bash
   # Should be: redis://:password@host:port/0
   echo $REDIS_URL
   ```

### Postgres Issues

#### Symptom: Connection pool exhausted
```
[err] FATAL: too many connections
```

**Solution**:
1. Scale Postgres plan (more connections)
2. Implement connection pooling in application
3. Review worker concurrency settings

---

## 📈 Monitoring & Observability

### Service Health Dashboard

**Railway Dashboard** → **cidadao.ai** → **Services**

Monitor for each service:
- ✅ CPU usage
- ✅ Memory usage
- ✅ Restart count
- ✅ Error rate
- ✅ Response time (API only)

### Log Aggregation

View logs from all services:

```bash
# All services
railway logs --tail 100

# Specific service
railway logs --service cidadao-api --tail 50 --follow

# Filter by level
railway logs | grep -E "\[err\]|\[wrn\]"
```

### Celery Monitoring

#### Via Railway Run

```bash
# Worker status
railway run --service cidadao.ai-worker \
  celery -A src.infrastructure.queue.celery_app inspect active

# Queue depth
railway run --service cidadao.ai-worker \
  celery -A src.infrastructure.queue.celery_app inspect reserved

# Beat schedule
railway run --service cidadao.ai-beat \
  celery -A src.infrastructure.queue.celery_app inspect scheduled
```

#### Optional: Deploy Flower (Celery Web UI)

Uncomment in Procfile:
```bash
flower: celery -A src.infrastructure.queue.celery_app flower --port=5555
```

Access at: `https://your-flower-service.railway.app`

---

## 🔐 Security Considerations

### Environment Variable Management

**DO NOT** store secrets in:
- ❌ Git repository
- ❌ Procfile
- ❌ Dockerfile
- ❌ docker-compose.yml

**DO** store secrets in:
- ✅ Railway environment variables
- ✅ Railway project secrets
- ✅ External secret management (Vault, AWS Secrets)

### Service Communication

All services communicate via:
- **Internal network**: Railway private network (encrypted)
- **No external IPs**: Services use internal DNS
- **Automatic TLS**: Railway provides TLS for public endpoints

### Database Security

- ✅ Use connection pooling
- ✅ Enable SSL/TLS for database connections
- ✅ Regular backups enabled
- ✅ Restricted access (only your services)

---

## 🚀 Scaling Strategy

### Horizontal Scaling (Multiple Replicas)

**Can scale**:
- ✅ cidadao-api (web) - Scale for more HTTP throughput
- ✅ cidadao.ai-worker - Scale for more task processing

**CANNOT scale**:
- ❌ cidadao.ai-beat - MUST be 1 replica (duplicate tasks otherwise)
- ❌ Postgres - Scale vertically (upgrade plan)
- ❌ cidadao-redis - Scale vertically (upgrade plan)

### Vertical Scaling (More Resources)

All services can be scaled vertically:
```
Railway Dashboard → Service → Settings → Resources
- Memory: Adjust based on usage
- CPU: Adjust based on load
```

### Auto-scaling (Future)

Railway supports auto-scaling based on metrics:
- CPU usage threshold
- Memory usage threshold
- Request rate (API only)

---

## 📝 Deployment Checklist

### Pre-Deployment

- [ ] All environment variables set
- [ ] Database migrations tested locally
- [ ] Celery tasks tested locally
- [ ] Health checks configured correctly
- [ ] Resource limits appropriate

### Deployment

- [ ] Push code to repository (triggers auto-deploy)
- [ ] Monitor deployment logs for all services
- [ ] Verify all services start successfully
- [ ] Check service health in Railway dashboard

### Post-Deployment

- [ ] Test API endpoints
- [ ] Verify worker processing tasks
- [ ] Confirm beat schedule running
- [ ] Monitor for 15+ minutes (check stability)
- [ ] Verify no memory leaks or crashes

---

## 📚 Additional Resources

- **Procfile Reference**: `/Procfile`
- **Celery Configuration**: `/src/infrastructure/queue/celery_app.py`
- **Health Check Code**: `/src/api/routes/health.py`
- **Docker Compose**: `/config/docker/docker-compose.production.yml`

---

## 🆘 Emergency Procedures

### Service Crash Loop

1. **Identify crashing service**:
   ```bash
   railway logs --service <service-name> --tail 100
   ```

2. **Common causes**:
   - Missing environment variables
   - Database connection issues
   - Redis connection issues
   - OOM (out of memory)

3. **Quick fix**:
   ```bash
   # Restart specific service
   railway service restart <service-name>

   # Or rollback to previous deployment
   railway rollback --service <service-name>
   ```

### Complete System Failure

1. **Disable auto-deploy**:
   ```
   Railway Dashboard → Settings → Disable auto-deploy
   ```

2. **Rollback all services**:
   ```bash
   # Via Railway Dashboard → Deployments → Redeploy previous
   ```

3. **Debug locally**:
   ```bash
   docker-compose -f config/docker/docker-compose.production.yml up
   ```

4. **Fix and redeploy**:
   ```bash
   git commit -m "fix: emergency hotfix"
   git push origin main
   ```

---

**Last Updated**: 2025-10-13
**Status**: Production multi-service deployment
**Maintainer**: Anderson Henrique da Silva
