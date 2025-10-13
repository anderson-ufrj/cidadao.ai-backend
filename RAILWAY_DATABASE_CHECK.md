# Railway Database Configuration Check

**Date**: 2025-10-13
**Status**: Needs Verification

---

## 🔍 Current Database Configuration

Based on deployment logs, your application is using **Supabase REST API** for investigations:

```
🚀 Using Supabase REST service for investigations (Railway/VPS)
```

This means:
- ✅ Investigations are persisted in Supabase
- ⚠️ Railway Postgres may not be connected
- ⚠️ Migrations may not be running

---

## 🎯 Verification Steps

### 1. Check Railway Dashboard

#### A. Verify Postgres Service Exists

```
Railway Dashboard → cidadao.ai → Services

Look for:
├── cidadao-api ✅
├── cidadao.ai-worker ✅
├── cidadao.ai-beat ✅
├── cidadao-redis ✅
└── Postgres ❓ (verify this exists)
```

#### B. Check Environment Variables

```
Railway Dashboard → cidadao.ai → Variables

Look for:
- DATABASE_URL (should be automatically provided by Railway Postgres)
- SUPABASE_URL (for Supabase connection)
- SUPABASE_SERVICE_ROLE_KEY (for Supabase auth)
```

### 2. Check Database Connection String

#### If Using Railway Postgres:

The `DATABASE_URL` should look like:
```bash
postgresql://postgres:password@host.railway.internal:5432/railway
```

Railway automatically provides this when you add a Postgres service.

#### If Using Supabase:

You need both:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
```

---

## 📊 Database Service Options

### Option 1: Railway Postgres (Recommended for Production)

**Advantages**:
- ✅ Integrated with Railway
- ✅ Automatic backups
- ✅ Low latency (same network)
- ✅ DATABASE_URL auto-configured
- ✅ Migrations via Alembic

**Setup**:
1. Go to Railway Dashboard → cidadao.ai
2. Click "New Service" → "Database" → "Add PostgreSQL"
3. Railway automatically sets `DATABASE_URL`
4. Redeploy application
5. Migrations run automatically via `release` command

**Cost**: Starts at $5/month for 1GB storage

### Option 2: Supabase (Current Setup)

**Advantages**:
- ✅ Free tier available
- ✅ Built-in auth and storage
- ✅ REST API and GraphQL
- ✅ Real-time subscriptions
- ✅ Works with Railway

**Current Status**:
- ✅ Working for investigations
- ⚠️ Not using migrations (REST API doesn't need them)
- ⚠️ Need to manage schema in Supabase dashboard

**Configuration**:
Already set up - no changes needed

### Option 3: Hybrid (Recommended)

**Use both**:
- Railway Postgres: For core application data (users, sessions, etc.)
- Supabase: For investigations (already working)

**Advantages**:
- ✅ Best of both worlds
- ✅ Separation of concerns
- ✅ Railway Postgres for transactional data
- ✅ Supabase for investigation logs

**Setup**:
1. Add Railway Postgres (as in Option 1)
2. Keep Supabase configuration
3. Application automatically uses both:
   - DATABASE_URL → Railway Postgres
   - SUPABASE_URL → Supabase REST

---

## 🔧 Verify Current Configuration

### Check Which Database is Being Used

Run this in Railway CLI:

```bash
# Check if DATABASE_URL is set
railway run --service cidadao-api env | grep DATABASE_URL

# If empty → Using Supabase only
# If shows URL → Using Railway Postgres
```

### Check Supabase Configuration

```bash
# Check Supabase variables
railway run --service cidadao-api env | grep SUPABASE

# Should show:
# SUPABASE_URL=https://...
# SUPABASE_SERVICE_ROLE_KEY=eyJ...
```

---

## ⚠️ Migration Issue

### Problem

The `release` command in Procfile should run migrations:

```bash
release: python -m alembic upgrade head
```

But we didn't see it in the deployment logs.

### Possible Causes

1. **Railway doesn't support `release` in Procfile**
   - Railway may not recognize the `release` process type
   - Only `web`, `worker`, and `beat` are standard

2. **Migrations ran but logs were truncated**
   - Logs may not show all output
   - Check earlier in deployment logs

3. **No DATABASE_URL set**
   - Migrations gracefully skip when no DATABASE_URL
   - This is OK if using Supabase only

### Solution: Move Migrations to start.sh

Since Railway may not support `release` process type, we should:

1. **Keep Procfile for services**:
   ```bash
   web: bash start.sh
   worker: celery -A src.infrastructure.queue.celery_app worker ...
   beat: celery -A src.infrastructure.queue.celery_app beat ...
   ```

2. **Update start.sh to include migrations**:
   ```bash
   #!/bin/bash
   set -e

   echo "🔄 Running database migrations..."
   python -m alembic upgrade head || echo "⚠️ Migrations skipped (no DATABASE_URL)"

   echo "🚀 Starting Uvicorn server..."
   exec uvicorn src.api.app:app --host 0.0.0.0 --port ${PORT:-8080}
   ```

---

## 📋 Recommended Actions

### Immediate (If You Want Railway Postgres)

1. **Add PostgreSQL Service in Railway**:
   ```
   Railway Dashboard → cidadao.ai → New Service → Database → PostgreSQL
   ```

2. **Verify DATABASE_URL is Set**:
   ```
   Railway Dashboard → Variables → Check for DATABASE_URL
   ```

3. **Update Procfile** (if Railway doesn't support `release`):
   ```bash
   # Remove release line if migrations aren't running
   # Or move migrations to start.sh
   ```

4. **Redeploy**:
   ```bash
   # Trigger redeploy in Railway Dashboard
   # or push a small change to GitHub
   ```

### If Keeping Supabase Only

**No action needed!** Your current setup is working:
- ✅ Supabase for investigations
- ✅ Application running successfully
- ✅ No PostgreSQL migrations needed

---

## 🧪 Testing Database Connection

### Test Railway Postgres (if configured)

```bash
# Via Railway CLI
railway run --service cidadao-api \
  python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('$DATABASE_URL')); print('✅ Connected')"
```

### Test Supabase Connection

```bash
# Via Railway CLI
railway run --service cidadao-api \
  python -c "import httpx; r=httpx.get('$SUPABASE_URL/rest/v1/', headers={'apikey': '$SUPABASE_SERVICE_ROLE_KEY'}); print('✅ Connected' if r.status_code == 200 else f'❌ Error: {r.status_code}')"
```

---

## 📊 Current Status Summary

Based on logs:

| Component | Status | Notes |
|-----------|--------|-------|
| **Application** | ✅ Running | Uvicorn started on port 8080 |
| **Supabase** | ✅ Connected | Using REST API for investigations |
| **Railway Postgres** | ❓ Unknown | Need to verify if service exists |
| **Migrations** | ⚠️ Not Running | No logs showing migration execution |
| **Redis** | ✅ Assumed OK | No errors in logs |

---

## 🎯 Decision Matrix

### Use Railway Postgres If:

- ✅ You want centralized database management
- ✅ You need complex queries and joins
- ✅ You want automatic backups
- ✅ You prefer SQL over REST API
- ✅ You need ACID transactions

### Use Supabase If:

- ✅ You want to stay on free tier
- ✅ You need real-time features
- ✅ You prefer REST/GraphQL API
- ✅ You want built-in auth
- ✅ Current setup is working fine

### Use Both If:

- ✅ You want best of both worlds
- ✅ You need different data access patterns
- ✅ You want to separate concerns
- ✅ You have budget for both

---

## 🔍 Next Steps

### To Verify Current Setup:

```bash
# 1. Check services in Railway Dashboard
# Go to: https://railway.app/dashboard

# 2. Check environment variables
# Railway Dashboard → cidadao.ai → Variables

# 3. Look for:
#    - DATABASE_URL (Railway Postgres)
#    - SUPABASE_URL (Supabase)
#    - REDIS_URL (Redis)

# 4. Verify all 5 services are running:
#    - cidadao-api
#    - cidadao.ai-worker
#    - cidadao.ai-beat
#    - cidadao-redis
#    - Postgres (if using Railway Postgres)
```

### To Add Railway Postgres:

```bash
# 1. Railway Dashboard → Add PostgreSQL service
# 2. Wait for DATABASE_URL to be auto-configured
# 3. Update Procfile or start.sh for migrations
# 4. Redeploy application
# 5. Verify migrations ran in logs
```

---

## 📚 Related Documentation

- **Multi-Service Guide**: `docs/deployment/RAILWAY_MULTI_SERVICE_GUIDE.md`
- **Health Checks**: `RAILWAY_SERVICE_HEALTH_CHECKS.md`
- **Deployment Summary**: `RAILWAY_DEPLOYMENT_FINAL_SUMMARY.md`

---

**Last Updated**: 2025-10-13
**Status**: Verification Needed
**Action**: Check Railway Dashboard for database configuration
