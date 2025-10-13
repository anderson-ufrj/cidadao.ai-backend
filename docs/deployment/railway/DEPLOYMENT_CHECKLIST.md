# Railway Deployment Checklist

**Project**: Cidadão.AI Backend
**Date**: 2025-10-13
**Deployment Target**: Railway (Production)

---

## Pre-Deployment Checklist

### 1. Environment Variables ✅

- [ ] **GROQ_API_KEY** - LLM provider key (REQUIRED)
- [ ] **JWT_SECRET_KEY** - JWT authentication (REQUIRED)
- [ ] **SECRET_KEY** - Application secret (REQUIRED)
- [ ] **API_SECRET_KEY** - API authentication (REQUIRED)
- [ ] **SUPABASE_URL** - Supabase project URL (REQUIRED for persistence)
- [ ] **SUPABASE_SERVICE_ROLE_KEY** - Supabase service key (REQUIRED for persistence)
- [ ] **TRANSPARENCY_API_KEY** - Portal da Transparência (OPTIONAL)
- [ ] **APP_ENV** - Set to "production" (RECOMMENDED)
- [ ] **LOG_LEVEL** - Set to "INFO" or "WARNING" (RECOMMENDED)

### 2. Code Quality ✅

```bash
# Run all checks before deploying
make check

# Or run individually:
make format          # Black + isort
make lint            # Ruff
make type-check      # MyPy
make test            # Pytest (80% coverage)
```

### 3. Railway Configuration ✅

#### railway.json
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "bash start.sh",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### Health Check Settings (Railway Dashboard)
- **Path**: `/health`
- **Initial Delay**: 15 seconds
- **Timeout**: 5 seconds
- **Interval**: 30 seconds
- **Failure Threshold**: 3

### 4. Files to Deploy ✅

- [ ] `railway.json` - Railway configuration
- [ ] `start.sh` - Startup script
- [ ] `src/api/routes/health.py` - Health check endpoints
- [ ] `alembic/` - Database migrations (optional)
- [ ] `requirements.txt` or `requirements-minimal.txt` - Dependencies
- [ ] `.gitignore` - Ensure .env not committed

---

## Deployment Steps

### Option A: Auto-Deploy (Recommended)

1. **Connect GitHub Repository**
   ```
   Railway Dashboard → New Project → Deploy from GitHub
   ```

2. **Configure Service**
   - Select repository: `cidadao.ai-backend`
   - Branch: `main`
   - Enable auto-deploy on push

3. **Set Environment Variables**
   ```
   Settings → Variables → Add from list above
   ```

4. **Configure Health Check**
   ```
   Settings → Deploy → Health Check Path: /health
   ```

5. **Deploy**
   - Push to main branch
   - Railway auto-deploys
   - Monitor logs

### Option B: Railway CLI

1. **Authenticate**
   ```bash
   # Verify token is set
   echo $RAILWAY_TOKEN

   # Or login interactively
   railway login
   ```

2. **Link Project**
   ```bash
   cd /path/to/cidadao.ai-backend
   railway link
   ```

3. **Set Variables**
   ```bash
   railway variables set GROQ_API_KEY=your-key
   railway variables set SUPABASE_URL=your-url
   # ... (repeat for all required vars)
   ```

4. **Deploy**
   ```bash
   railway up
   ```

5. **Monitor**
   ```bash
   railway logs --tail 100 --follow
   ```

---

## Post-Deployment Verification

### 1. Check Deployment Status

```bash
# Via CLI
railway status

# Or check Railway Dashboard
# https://railway.app/dashboard
```

### 2. Verify Health Endpoints

```bash
# Replace with your Railway domain
DOMAIN="your-app.railway.app"

# Test ultra-fast health check (<1s)
time curl https://$DOMAIN/health

# Expected: {"status":"ok","timestamp":"..."}

# Test other endpoints
curl https://$DOMAIN/health/live
curl https://$DOMAIN/health/status
```

### 3. Test API Functionality

```bash
# Check agents status
curl https://$DOMAIN/api/v1/agents/status

# Test chat endpoint
curl -X POST https://$DOMAIN/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Olá!"}'
```

### 4. Monitor Logs

```bash
railway logs --tail 100 --follow
```

**Expected output**:
```
[inf] Starting Container
[inf] 🔄 Running database migrations...
[inf] ⚠️  WARNING: No valid DATABASE_URL found. Skipping migrations.
[inf] ✅ Migrations completed successfully
[inf] 🚀 Starting Uvicorn server...
[inf] 🚀 Using Supabase REST service for investigations
[inf] Cidadão.AI API started (env: production)
[err] INFO: Application startup complete.
[err] INFO: Uvicorn running on http://0.0.0.0:8080
```

### 5. Stability Check

Wait 10-15 minutes and verify:
- [ ] No health check errors in logs
- [ ] No unexpected restarts
- [ ] API responds correctly
- [ ] No memory/CPU issues

---

## Common Issues & Quick Fixes

### Issue: "Project Token not found"

**Fix**:
```bash
# Reload environment
source ~/.bashrc

# Or set manually
export RAILWAY_TOKEN=your-token
```

### Issue: Health check failing

**Fix**:
1. Verify endpoint responds quickly:
   ```bash
   time curl https://your-app.railway.app/health
   ```
2. Should be <1 second
3. If slow, check application logs
4. Verify health check path is `/health` not `/health/ready`

### Issue: "No valid DATABASE_URL found"

**Status**: ✅ **Expected behavior**

This warning is normal when using Supabase REST API instead of direct PostgreSQL.
The application works correctly with this warning.

**To suppress** (optional):
- Add PostgreSQL service in Railway
- DATABASE_URL will be auto-configured

### Issue: Application crashes on startup

**Debug**:
```bash
# Check logs
railway logs --tail 50

# Verify environment variables
railway variables | grep -E "(GROQ|SUPABASE|SECRET)"

# Test locally
python -m src.api.app
```

---

## Performance Optimization

### After Successful Deployment

1. **Monitor Resource Usage**
   ```
   Railway Dashboard → Service → Metrics
   ```

2. **Scale if Needed**
   ```
   Settings → Resources → Adjust RAM/CPU
   ```

3. **Add Redis Caching** (Optional)
   ```bash
   railway add
   # Select Redis
   # REDIS_URL automatically provided
   ```

4. **Add PostgreSQL** (Optional)
   ```bash
   railway add
   # Select PostgreSQL
   # DATABASE_URL automatically provided
   ```

---

## Rollback Procedure

### Quick Rollback (Railway Dashboard)

1. Go to **Deployments** tab
2. Find last working deployment
3. Click **Redeploy**

### Git Rollback

```bash
# Revert last commit
git revert HEAD

# Push
git push origin main

# Railway auto-deploys previous version
```

### Emergency: Disable Service

```bash
# Stop service temporarily
railway down

# Fix issues locally
# Test thoroughly

# Redeploy
railway up
```

---

## Success Criteria

✅ **Deployment is successful when ALL of the following are true**:

- [ ] Application starts without errors
- [ ] Health endpoint responds in <1 second
- [ ] No health check failures in logs for 15+ minutes
- [ ] API endpoints return correct responses
- [ ] Agents can process queries
- [ ] Supabase persistence working (investigations saved)
- [ ] No memory leaks or CPU spikes
- [ ] Railway domain accessible from browser

---

## Monitoring & Maintenance

### Daily Checks

```bash
# Check service status
railway status

# Quick log check
railway logs --tail 20

# Test health endpoint
curl https://your-app.railway.app/health
```

### Weekly Checks

- Review Railway metrics (CPU, Memory, Network)
- Check error rates in logs
- Verify disk usage
- Update dependencies if needed

### Monthly Checks

- Review Railway costs
- Analyze performance trends
- Plan capacity upgrades
- Update documentation

---

## Documentation References

- **Full Deployment Guide**: `docs/deployment/RAILWAY_DEPLOYMENT_GUIDE.md`
- **Quick Fix Guide**: `docs/deployment/RAILWAY_QUICK_FIX.md`
- **Environment Template**: `.env.example`
- **Health Check Code**: `src/api/routes/health.py`
- **Startup Script**: `start.sh`
- **Railway Config**: `railway.json`

---

## Support Resources

### Railway
- **Dashboard**: https://railway.app/dashboard
- **Documentation**: https://docs.railway.app
- **Status Page**: https://status.railway.app
- **Community**: https://discord.gg/railway

### Project
- **Repository**: https://github.com/anderson-ufrj/cidadao.ai-backend
- **Issues**: Use GitHub Issues for bug reports
- **Maintainer**: Anderson Henrique da Silva

---

## Version History

| Date | Version | Changes | Deployed By |
|------|---------|---------|-------------|
| 2025-10-13 | 1.0.0 | Initial Railway deployment with health check fix | Anderson H. Silva |

---

**Last Updated**: 2025-10-13
**Status**: ✅ Ready for deployment
