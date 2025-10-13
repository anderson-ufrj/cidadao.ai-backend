# Railway Deployment Quick Fix Guide

**Autor**: Anderson Henrique da Silva
**Localização**: Minas Gerais, Brasil
**Última Atualização**: 2025-10-13 15:15:18 -0300

---

**Date**: 2025-10-13
**Issue**: Health check timeouts causing deployment issues
**Status**: ✅ FIXED

---

## Problem Summary

The Railway deployment was experiencing health check failures after ~5 minutes of runtime, causing service instability.

### Root Cause

The `/ready` endpoint was making external HTTP requests to Portal da Transparência API, which:
- Takes 5-30 seconds to respond
- Has 78% of endpoints returning 403 Forbidden
- Caused Railway health checks to timeout
- Triggered service restarts

---

## Solution Applied

### 1. Health Check Endpoints Reorganized

| Endpoint | Speed | Purpose | Railway Compatible |
|----------|-------|---------|-------------------|
| `/health` | ⚡ Ultra-fast (<10ms) | **Railway health checks** | ✅ YES - RECOMMENDED |
| `/health/live` | ⚡ Ultra-fast (<10ms) | Kubernetes liveness | ✅ YES |
| `/health/status` | 🐢 Slow (1-5s) | Comprehensive check | ❌ NO |
| `/health/detailed` | 🐢 Slow (1-5s) | Detailed diagnostics | ❌ NO |
| `/health/ready` | 🐌 Very slow (5-30s) | External API checks | ❌ NO |

### 2. Code Changes

**File**: `src/api/routes/health.py`

**Added ultra-fast endpoint**:
```python
@router.get("/")
async def simple_health():
    """Simple health check - RECOMMENDED for Railway."""
    return {"status": "ok", "timestamp": datetime.utcnow()}
```

**Modified `/ready` endpoint**:
- Now returns degraded status instead of 503 when external APIs fail
- Service remains functional even if Portal da Transparência is down
- Prevents unnecessary container restarts

---

## Railway Configuration

### Dashboard Settings

1. Go to: **Railway Dashboard** → **Your Service** → **Settings** → **Deploy**

2. Configure Health Check:
   ```
   Health Check Path: /health
   Initial Delay: 15 seconds
   Timeout: 5 seconds
   Interval: 30 seconds
   Failure Threshold: 3
   ```

3. Save and redeploy

### Why These Settings?

- **Path `/health`**: Ultra-fast, no external dependencies
- **15s Initial Delay**: Allows application startup time
- **5s Timeout**: Sufficient for fast endpoint
- **30s Interval**: Balanced monitoring frequency
- **3 Failures**: Prevents false positives

---

## Verification Steps

### 1. Test Health Endpoints Locally

```bash
# Test ultra-fast endpoint (should respond <10ms)
curl http://localhost:8080/health

# Expected response:
# {"status":"ok","timestamp":"2025-10-13T12:30:00.000Z"}

# Test other endpoints
curl http://localhost:8080/health/live
curl http://localhost:8080/health/status
curl http://localhost:8080/health/detailed
```

### 2. Deploy to Railway

```bash
# Commit changes
git add src/api/routes/health.py docs/deployment/
git commit -m "fix: optimize health checks for Railway compatibility"

# Push to repository
git push origin main

# Railway will auto-deploy (if configured)
# OR manually trigger:
railway redeploy
```

### 3. Monitor Deployment

```bash
# Watch logs in real-time
railway logs --tail 100 --follow

# Look for these indicators:
# ✅ "Application startup complete"
# ✅ "Uvicorn running on http://0.0.0.0:8080"
# ✅ No health check errors after 5 minutes
```

### 4. Test Live Deployment

```bash
# Replace with your Railway domain
RAILWAY_DOMAIN="your-app.railway.app"

# Test health endpoint
curl https://$RAILWAY_DOMAIN/health

# Test API functionality
curl https://$RAILWAY_DOMAIN/api/v1/agents/status
```

---

## Database Configuration Status

### Current Setup

✅ **Working Configuration**:
- Using Supabase REST API for persistence
- No PostgreSQL DATABASE_URL required
- Alembic gracefully skips migrations
- Application fully functional

### Environment Variables Required

```bash
# Supabase (for investigations persistence)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# LLM Provider
GROQ_API_KEY=your-groq-api-key

# Security
JWT_SECRET_KEY=your-jwt-secret
SECRET_KEY=your-app-secret
API_SECRET_KEY=your-api-secret
```

### Optional: Add PostgreSQL

If you want to use PostgreSQL directly instead of Supabase REST:

```bash
# Add PostgreSQL service in Railway
railway add

# Railway automatically provides:
DATABASE_URL=postgresql://...

# Redeploy to run migrations
railway redeploy
```

---

## Expected Log Output (Healthy Deployment)

```
[inf] Starting Container
[inf] 🔄 Running database migrations...
[inf] ⚠️  WARNING: No valid DATABASE_URL found. Skipping migrations.
[inf] ✅ Migrations completed successfully
[inf] 🚀 Starting Uvicorn server...
[inf] 🚀 Using Supabase REST service for investigations (Railway/VPS)
[inf] === CHAT.PY LOADING - VERSION 13:45:00 ===
[inf] Cidadão.AI API started (env: production)
[err] INFO: Application startup complete.
[err] INFO: Uvicorn running on http://0.0.0.0:8080

# After 5+ minutes: No errors, service remains stable
```

---

## Rollback Plan

If issues persist after applying this fix:

### 1. Quick Rollback via Railway Dashboard

1. Go to **Deployments** tab
2. Find last working deployment
3. Click **Redeploy**

### 2. Rollback via Git

```bash
# Revert changes
git revert HEAD

# Push
git push origin main

# Railway auto-deploys
```

### 3. Emergency: Disable Health Checks

In Railway Dashboard:
1. Settings → Deploy
2. Temporarily disable health check
3. Investigate issue
4. Re-enable with correct configuration

---

## Additional Improvements

### Future Enhancements

1. **Add Prometheus Metrics**:
   - Track health check response times
   - Monitor external API failures
   - Alert on anomalies

2. **Implement Circuit Breaker**:
   - Automatically disable slow health checks
   - Prevent cascading failures
   - Self-healing behavior

3. **Add Synthetic Monitoring**:
   - External uptime monitoring
   - Performance tracking
   - User experience metrics

---

## Troubleshooting

### Issue: Health check still failing

**Check**:
```bash
# Verify endpoint responds quickly
time curl https://your-app.railway.app/health

# Should be <1 second
```

**Solution**:
- Increase timeout in Railway settings to 10s
- Check Railway service logs for errors
- Verify no network issues

### Issue: Application crashes on startup

**Check**:
```bash
railway logs --tail 50
```

**Common causes**:
- Missing environment variables
- Port binding issues
- Import errors

**Solution**:
```bash
# Verify all required env vars
railway variables | grep -E "(GROQ|SUPABASE|SECRET)"

# Check PORT variable
railway variables | grep PORT
```

### Issue: Slow response times

**Check**:
```bash
# Test health endpoint speed
for i in {1..10}; do
  time curl -s https://your-app.railway.app/health > /dev/null
done
```

**Solution**:
- Scale up Railway service (more RAM/CPU)
- Enable Redis caching
- Optimize database queries

---

## Success Criteria

✅ Deployment is successful when:

- [ ] Application starts without errors
- [ ] Health check endpoint responds <1s
- [ ] No health check failures in logs
- [ ] Service remains stable for 30+ minutes
- [ ] API endpoints respond correctly
- [ ] Agents can be queried successfully

---

## Support

### Internal Documentation
- Full guide: `docs/deployment/RAILWAY_DEPLOYMENT_GUIDE.md`
- Environment setup: `.env.example`
- Agent testing: `docs/agents/TESTING_GUIDE.md`

### Railway Resources
- Dashboard: https://railway.app/dashboard
- Documentation: https://docs.railway.app
- Status: https://status.railway.app

### Project Maintainer
- **Anderson Henrique da Silva**
- Minas Gerais, Brasil
- GitHub: @anderson-ufrj

---

**Last Updated**: 2025-10-13
**Status**: ✅ Applied and tested
