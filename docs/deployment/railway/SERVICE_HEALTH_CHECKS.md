# Railway Service Health Check Configuration

**Quick Reference Guide**
**Date**: 2025-10-13

---

## 🎯 Health Check Configuration by Service

### 📊 Summary Table

| Service | Health Check | Path | Timeout | Interval | Notes |
|---------|-------------|------|---------|----------|-------|
| **cidadao-api** | ✅ ENABLED | `/health` | 5s | 30s | Main API endpoint |
| **cidadao.ai-worker** | ❌ DISABLED | N/A | N/A | N/A | No HTTP endpoint |
| **cidadao.ai-beat** | ❌ DISABLED | N/A | N/A | N/A | No HTTP endpoint |
| **cidadao-redis** | ✅ AUTO | N/A | N/A | N/A | Railway managed |
| **Postgres** | ✅ AUTO | N/A | N/A | N/A | Railway managed |

---

## 🌐 cidadao-api (Web Service)

### Configuration Steps

1. **Open Railway Dashboard**
   - Go to: https://railway.app/dashboard
   - Select project: **cidadao.ai**
   - Click service: **cidadao-api**

2. **Navigate to Settings**
   - Click: **Settings** tab
   - Scroll to: **Deploy** section

3. **Configure Health Check**
   ```
   ✅ Enable Health Check

   Path: /health
   Initial Delay: 15 seconds
   Timeout: 5 seconds
   Interval: 30 seconds
   Failure Threshold: 3 consecutive failures
   ```

4. **Save Configuration**
   - Click: **Save Settings**
   - Redeploy: **Redeploy** button

### Testing

```bash
# Test locally
curl http://localhost:8080/health

# Test on Railway
curl https://cidadao-api-production.up.railway.app/health

# Expected response (< 100ms):
{
  "status": "ok",
  "timestamp": "2025-10-13T12:30:00.000Z"
}
```

### Troubleshooting

**Issue: Health check failing**

Check logs:
```bash
railway logs --service cidadao-api --tail 50 | grep -i health
```

Common causes:
- Application not bound to `0.0.0.0:$PORT`
- Database connection hanging on startup
- External API calls in health check (use `/health` not `/health/ready`)

**Solution**:
1. Verify app binds to correct port
2. Use ultra-fast health endpoint
3. Increase timeout to 10s if needed

---

## 🔧 cidadao.ai-worker (Celery Worker)

### Configuration Steps

1. **Open Railway Dashboard**
   - Select service: **cidadao.ai-worker**
   - Click: **Settings** tab

2. **Disable Health Check**
   ```
   ❌ Disable Health Check
   ```

   **Why?** Celery workers don't expose HTTP endpoints.

3. **Alternative: Monitor via Logs**
   ```bash
   # Check worker is processing tasks
   railway logs --service cidadao.ai-worker --tail 20

   # Look for:
   # [inf] celery@worker ready
   # [inf] Task received: tasks.process_investigation
   ```

### Testing

```bash
# Inspect active tasks
railway run --service cidadao.ai-worker \
  celery -A src.infrastructure.queue.celery_app inspect active

# Check registered tasks
railway run --service cidadao.ai-worker \
  celery -A src.infrastructure.queue.celery_app inspect registered

# Ping workers
railway run --service cidadao.ai-worker \
  celery -A src.infrastructure.queue.celery_app inspect ping
```

### Monitoring

Worker is healthy when:
- ✅ Logs show "celery@worker ready"
- ✅ Tasks are being received and processed
- ✅ No OOM (out of memory) errors
- ✅ Memory usage stable (not growing)

---

## ⏰ cidadao.ai-beat (Celery Beat)

### Configuration Steps

1. **Open Railway Dashboard**
   - Select service: **cidadao.ai-beat**
   - Click: **Settings** tab

2. **Disable Health Check**
   ```
   ❌ Disable Health Check
   ```

   **Why?** Beat scheduler has no HTTP endpoint.

3. **CRITICAL: Set Replicas to 1**
   ```
   ⚠️ IMPORTANT: Always keep replicas = 1

   Settings → Deploy → Replicas: 1
   ```

   **Why?** Multiple beat instances create duplicate scheduled tasks.

### Testing

```bash
# Check beat is scheduling tasks
railway logs --service cidadao.ai-beat --tail 20

# Look for:
# [inf] beat: Starting...
# [inf] Scheduler: Sending due task auto-monitor-new-contracts-6h
```

### Monitoring

Beat is healthy when:
- ✅ Logs show "beat: Starting..."
- ✅ Scheduled tasks appear in logs
- ✅ Only ONE beat instance running
- ✅ No connection errors to Redis

---

## 💾 cidadao-redis (Redis Service)

### Configuration

Railway automatically manages health checks for Redis:

```
✅ Automatic Health Check
   Type: redis-cli PING
   Interval: 5 seconds
   Timeout: 3 seconds
```

**No manual configuration needed.**

### Testing

```bash
# Test Redis connection from API
railway run --service cidadao-api \
  python -c "import redis; r=redis.from_url('$REDIS_URL'); print(r.ping())"

# Expected output: True
```

### Monitoring

Redis is healthy when:
- ✅ Connection successful
- ✅ PING returns PONG
- ✅ Memory usage < 80%
- ✅ No eviction warnings

---

## 🗄️ Postgres (Database Service)

### Configuration

Railway automatically manages health checks for Postgres:

```
✅ Automatic Health Check
   Type: pg_isready
   Interval: 5 seconds
   Timeout: 5 seconds
```

**No manual configuration needed.**

### Testing

```bash
# Test database connection from API
railway run --service cidadao-api \
  python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('$DATABASE_URL'))"

# Test via alembic
railway run --service cidadao-api \
  alembic current
```

### Monitoring

Postgres is healthy when:
- ✅ Connection successful
- ✅ Query response < 100ms
- ✅ Connection count < max_connections
- ✅ Disk usage < 80%

---

## 🚨 Alert Configuration

### Railway Notification Settings

Configure alerts for critical events:

1. **Open Project Settings**
   - Railway Dashboard → cidadao.ai → Settings

2. **Configure Notifications**
   ```
   ✅ Email on service crash
   ✅ Email on deployment failure
   ✅ Slack/Discord webhook (optional)
   ```

### Recommended Alerts

**Critical Alerts** (immediate action):
- Service crash loop (3+ restarts in 5 min)
- OOM (out of memory) kills
- Database connection failures
- Redis connection failures

**Warning Alerts** (monitor):
- Health check failures (but service running)
- High memory usage (>80%)
- High CPU usage (>80%)
- Slow response times (>5s)

---

## 📊 Health Check Best Practices

### DO ✅

1. **Use fast health checks** (<100ms response)
   ```python
   @router.get("/health")
   async def health():
       return {"status": "ok"}
   ```

2. **Disable health checks for non-HTTP services**
   - Celery workers
   - Celery beat
   - Background jobs

3. **Use appropriate timeouts**
   - API: 5s timeout, 30s interval
   - Database: Auto-managed
   - Redis: Auto-managed

4. **Monitor logs regularly**
   ```bash
   railway logs --tail 100 --follow
   ```

### DON'T ❌

1. **Don't check external APIs in health checks**
   ```python
   # BAD - This can timeout
   @router.get("/health")
   async def health():
       await check_transparency_api()  # SLOW!
       return {"status": "ok"}
   ```

2. **Don't scale Celery Beat**
   - Always keep beat replicas = 1

3. **Don't use slow database queries in health checks**
   ```python
   # BAD - Can cause cascading failures
   @router.get("/health")
   async def health():
       await db.execute("SELECT COUNT(*) FROM huge_table")
   ```

4. **Don't restart services on first failure**
   - Use failure threshold: 3 consecutive failures

---

## 🔧 Quick Reference Commands

### Check Service Health

```bash
# API health
curl https://your-api.railway.app/health

# Worker status
railway logs --service cidadao.ai-worker | grep -i "ready\|error"

# Beat status
railway logs --service cidadao.ai-beat | grep -i "Scheduler\|error"

# Redis status
railway logs --service cidadao-redis | tail -20

# Postgres status
railway logs --service postgres | tail -20
```

### Monitor All Services

```bash
# Watch all logs in real-time
railway logs --tail 100 --follow

# Check specific service
railway logs --service <service-name> --tail 50 --follow

# Filter errors only
railway logs | grep -E "\[err\]|\[wrn\]"
```

### Force Service Restart

```bash
# Restart specific service
railway service restart <service-name>

# Example
railway service restart cidadao-api
railway service restart cidadao.ai-worker
```

---

## 📝 Checklist: Verify All Health Checks

After deployment, verify:

- [ ] **cidadao-api**: Health check enabled at `/health`
- [ ] **cidadao-api**: Responds in <1 second
- [ ] **cidadao.ai-worker**: Health check disabled
- [ ] **cidadao.ai-worker**: Logs show "celery@worker ready"
- [ ] **cidadao.ai-beat**: Health check disabled
- [ ] **cidadao.ai-beat**: Replicas set to 1
- [ ] **cidadao.ai-beat**: Logs show scheduled tasks
- [ ] **cidadao-redis**: Automatic health check active
- [ ] **Postgres**: Automatic health check active
- [ ] **All services**: No crash loops for 15+ minutes

---

## 🆘 Troubleshooting Matrix

| Symptom | Likely Service | Solution |
|---------|---------------|----------|
| 503 errors | cidadao-api | Check health check config, verify `/health` responds |
| Tasks not processing | cidadao.ai-worker | Check Redis connection, verify worker logs |
| Duplicate scheduled tasks | cidadao.ai-beat | Ensure only 1 beat replica |
| Connection timeouts | Redis/Postgres | Check service status, verify connection strings |
| OOM crashes | cidadao.ai-worker | Increase memory, reduce concurrency |
| High CPU | cidadao-api | Scale horizontally (add replicas) |

---

## 📚 Related Documentation

- **Multi-Service Guide**: `docs/deployment/RAILWAY_MULTI_SERVICE_GUIDE.md`
- **Full Deployment Guide**: `docs/deployment/RAILWAY_DEPLOYMENT_GUIDE.md`
- **Quick Fix Guide**: `docs/deployment/RAILWAY_QUICK_FIX.md`
- **Health Check Code**: `src/api/routes/health.py`
- **Procfile**: `/Procfile`

---

**Last Updated**: 2025-10-13
**Quick Access**: Keep this file bookmarked for reference
**Maintainer**: Anderson Henrique da Silva
