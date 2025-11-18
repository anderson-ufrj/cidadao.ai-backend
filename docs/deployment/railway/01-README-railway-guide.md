# Railway Deployment Guide

**Author:** Anderson Henrique da Silva
**Location:** Minas Gerais, Brasil
**Last Updated:** 2025-10-16

---

## 📋 Overview

This directory contains all documentation related to Railway deployment for the cidadao.ai backend.

## ✅ Current Status

**Deployment:** ✅ Live and operational
**Database:** ✅ PostgreSQL connected
**Cache:** ✅ Redis operational
**Migrations:** ✅ Running at startup

**Railway URL:** https://cidadao-api-production.up.railway.app

---

## 🚀 Quick Start

### Prerequisites
- Railway CLI installed
- Railway account with project access
- Git repository connected

### Deploy New Version

```bash
# Push to main branch (auto-deploys)
git push origin main

# Railway will automatically:
# 1. Pull latest code
# 2. Build Docker image
# 3. Run migrations
# 4. Deploy new version
# 5. Zero-downtime rollout
```

### View Logs

```bash
# View live logs
railway logs

# View logs for specific service
railway logs --service cidadao-api

# Follow logs in real-time
railway logs --follow
```

---

## 🔧 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://postgres:...@postgres.railway.internal:5432/railway` |
| `REDIS_URL` | Redis connection | `redis://default:...@cidadao-redis.railway.internal:6379` |
| `JWT_SECRET_KEY` | JWT authentication | `<generate-secure-key>` |
| `SECRET_KEY` | General encryption | `<generate-secure-key>` |
| `GROQ_API_KEY` | LLM provider | `gsk_...` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TRANSPARENCY_API_KEY` | Portal da Transparência | None |
| `MAX_EPISODIC_MEMORIES` | Memory system limit | 10000 |
| `MEMORY_DECAY_DAYS` | Memory retention | 90 |

---

## 🗄️ Database Configuration

### PostgreSQL

**Connection:** Internal Railway network
**Host:** `postgres.railway.internal`
**Port:** `5432`
**Database:** `railway`

### Migrations

Migrations run automatically at startup:

```python
# src/api/app.py
@app.on_event("startup")
async def run_migrations():
    await run_alembic_migrations()
```

### Manual Migration

```bash
# SSH into Railway container
railway run alembic upgrade head
```

---

## 🔴 Redis Configuration

**Connection:** Internal Railway network
**Host:** `cidadao-redis.railway.internal`
**Port:** `6379`

### Test Connection

```bash
railway run python -c "import redis; r = redis.from_url('$REDIS_URL'); print(r.ping())"
```

---

## 📊 Monitoring

### Health Check

```bash
curl https://cidadao-api-production.up.railway.app/health

# Response:
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "1.0.0"
}
```

### Performance Metrics

Railway provides built-in metrics:
- CPU usage
- Memory usage
- Request latency
- Error rates

Access via Railway Dashboard → Metrics tab

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Failed

```bash
# Check DATABASE_URL is set
railway variables --service cidadao-api | grep DATABASE_URL

# Verify PostgreSQL is running
railway status
```

#### 2. Redis Connection Failed

```bash
# Check REDIS_URL is set
railway variables --service cidadao-api | grep REDIS_URL

# Test Redis connectivity
railway run redis-cli -u $REDIS_URL ping
```

#### 3. Migration Errors

```bash
# View migration logs
railway logs | grep alembic

# Manually run migrations
railway run alembic upgrade head
```

#### 4. App Won't Start

```bash
# Check for errors in logs
railway logs --service cidadao-api | tail -100

# Verify environment variables
railway variables --service cidadao-api
```

---

## 📝 Archived Documentation

Historical deployment documentation is available in the `archive/` directory:

- [Railway Configuration Guide](archive/RAILWAY_CONFIGURAR_VARIAVEIS_DASHBOARD.md)
- [Database URL Fix](archive/RAILWAY_DATABASE_URL_FIX.md)
- [Deployment Fixes 2025-10-16](archive/RAILWAY_DEPLOYMENT_FIX_2025-10-16.md)
- [PostgreSQL Setup](archive/RAILWAY_POSTGRESQL_SETUP.md)
- [Log Viewing Guide](archive/COMO_VER_LOGS_RAILWAY.md)

---

## 🔗 Related Documentation

- [Architecture Overview](../../architecture/README.md)
- [Multi-API Integration](../../architecture/MULTI_API_INTEGRATION.md)
- [Agent Pool Architecture](../../architecture/AGENT_POOL_ARCHITECTURE.md)
- [Development Guide](../../development/README.md)

---

## 📞 Support

**Author:** Anderson Henrique da Silva
**Email:** andersonhs27@gmail.com
**Location:** Minas Gerais, Brasil

For deployment issues, check:
1. Railway Dashboard logs
2. Archived documentation
3. Project issue tracker

---

**Last Updated:** 2025-10-16 16:50:00 -03:00
