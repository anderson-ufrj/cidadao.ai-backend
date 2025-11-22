# Investigation Persistence Issue - Diagnosis & Resolution

**Date**: 2025-10-29
**Status**: 🔍 Under Investigation
**Priority**: HIGH

---

## 🎯 Problem Statement

Investigations are not being persisted to the PostgreSQL database in production (Railway). This means:
- Investigations are created and processed
- Results are returned to users
- BUT: Records are not saved to the database for historical queries
- Frontend cannot retrieve past investigations

---

## 🔍 Investigation Steps Taken

### 1. Code Review (✅ Complete)

**Investigation Model** (`src/models/investigation.py`):
- ✅ Model correctly defined with all fields
- ✅ Inherits from `BaseModel` with SQLAlchemy
- ✅ Has proper indexes and constraints

**Investigation Service** (`src/services/investigation_service.py`):
- ✅ Creates Investigation objects correctly (line 55)
- ✅ Uses `db.add(investigation)` (line 66)
- ✅ Calls `await db.commit()` (line 67)
- ✅ Refreshes object after commit (line 68)

**Database Session** (`src/db/simple_session.py`):
- ✅ Correctly configured for async PostgreSQL
- ✅ Auto-converts `postgres://` to `postgresql+asyncpg://`
- ✅ Uses async session maker
- ✅ Has proper transaction handling (commit/rollback)

**Conclusion**: Code appears correct. Issue likely environmental.

### 2. Debug Endpoint Created (✅ Complete)

Added `/api/v1/debug/database-config` endpoint to check:
- DATABASE_URL environment variable status
- Database type (PostgreSQL vs SQLite)
- Connection status
- Table existence
- Investigation count

**Commit**: ca53922
**Deployed**: Awaiting Railway deployment

---

## 🤔 Possible Root Causes

### Theory #1: DATABASE_URL Not Configured (Most Likely)
**Symptoms**:
- System would fall back to SQLite (`cidadao_ai.db`)
- Investigations saved to ephemeral file system
- Data lost on container restart/redeploy

**How to Verify**:
```bash
curl https://cidadao-api-production.up.railway.app/api/v1/debug/database-config | jq '.environment'
```

**Expected (Healthy)**:
```json
{
  "DATABASE_URL_configured": true,
  "DATABASE_URL_type": "PostgreSQL",
  "DATABASE_URL_preview": "postgresql://...@..."
}
```

**If Broken**:
```json
{
  "DATABASE_URL_configured": false,
  "DATABASE_URL_type": "Not configured"
}
```

**Fix**:
```bash
# In Railway dashboard, add environment variable:
DATABASE_URL=postgresql://user:pass@host:port/database

# Or link PostgreSQL service:
railway link --environment production
railway up
```

### Theory #2: Table Not Created (Migrations Not Run)
**Symptoms**:
- DATABASE_URL is configured correctly
- Connection works
- But `investigations` table doesn't exist

**How to Verify**:
```bash
curl https://cidadao-api-production.up.railway.app/api/v1/debug/database-config | jq '.tables'
```

**Expected**:
```json
{
  "investigations_exists": true
}
```

**If Broken**:
```json
{
  "investigations_exists": false
}
```

**Fix**:
```bash
# Run migrations in Railway
railway run alembic upgrade head

# Or add to startup script
python -c "from alembic import command; from alembic.config import Config; cfg = Config('alembic.ini'); command.upgrade(cfg, 'head')"
```

### Theory #3: Transaction Not Committing
**Symptoms**:
- DATABASE_URL configured
- Table exists
- But commit() fails silently

**How to Verify**:
Check Railway logs for:
- `sqlalchemy.exc.` errors
- `asyncpg.` connection errors
- Transaction rollback messages

**Fix**:
- Check connection pool settings
- Verify PostgreSQL accepts connections
- Check for database locks

---

## 🧪 Testing Protocol

### Step 1: Check Database Configuration
```bash
curl https://cidadao-api-production.up.railway.app/api/v1/debug/database-config | jq '.'
```

### Step 2: Create Test Investigation
```bash
# TODO: Need to find correct endpoint
# Candidates:
# - POST /api/v1/investigations/start
# - POST /api/v1/investigations/public/create
# - POST /api/v1/cqrs/investigations
```

### Step 3: Verify Persistence
```bash
# Check investigation count increased
curl https://cidadao-api-production.up.railway.app/api/v1/debug/database-config | jq '.investigations.total_count'

# List recent investigations
curl https://cidadao-api-production.up.railway.app/api/v1/debug/database-config | jq '.investigations.recent_investigations'
```

---

## 🔧 Resolution Checklist

- [ ] Deploy debug endpoint (commit ca53922)
- [ ] Test `/api/v1/debug/database-config` in production
- [ ] Verify DATABASE_URL is configured in Railway
- [ ] Verify PostgreSQL service is linked
- [ ] Check if `investigations` table exists
- [ ] Run migrations if table missing
- [ ] Create test investigation
- [ ] Verify test investigation persists
- [ ] Document solution

---

## 📊 Expected Diagnostic Results

### Healthy System:
```json
{
  "status": "success",
  "connection_test": "✅ Connection successful",
  "environment": {
    "DATABASE_URL_configured": true,
    "DATABASE_URL_type": "PostgreSQL"
  },
  "database": {
    "database_type": "PostgreSQL",
    "async_driver": "asyncpg"
  },
  "tables": {
    "investigations_exists": true
  },
  "investigations": {
    "total_count": 42,
    "table_accessible": true,
    "recent_investigations": [...]
  }
}
```

### Unhealthy System (SQLite Fallback):
```json
{
  "status": "success",
  "connection_test": "✅ Connection successful",
  "environment": {
    "DATABASE_URL_configured": false,
    "DATABASE_URL_type": "Not configured"
  },
  "database": {
    "database_type": "SQLite",
    "async_driver": "aiosqlite",
    "active_url_preview": "sqlite+aiosqlite:///./cidadao_ai.db"
  }
}
```

---

## 🚀 Next Steps

1. **Wait for Railway Deployment** (~2-3 min from commit ca53922)
2. **Run Diagnostic Endpoint**
3. **Identify Root Cause** (most likely DATABASE_URL missing)
4. **Apply Fix** (configure DATABASE_URL in Railway)
5. **Verify Resolution** (test investigation persistence)
6. **Document Solution**

---

## 📝 Related Files

- Model: `src/models/investigation.py`
- Service: `src/services/investigation_service.py`
- Session: `src/db/simple_session.py`
- Debug Endpoint: `src/api/routes/debug.py` (line 638)

---

## 🔗 Useful Links

- Railway Dashboard: https://railway.app/
- API Docs: https://cidadao-api-production.up.railway.app/docs
- Debug Endpoint: https://cidadao-api-production.up.railway.app/api/v1/debug/database-config

---

**Status**: Awaiting Railway deployment to run diagnostics.
**ETA**: Diagnosis complete within 10 minutes of deployment.
